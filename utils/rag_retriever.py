import os
import glob
import logging
import faiss
import numpy as np
import pickle
from transformers import AutoTokenizer, AutoModel
import torch

class RAGRetriever:
    def __init__(self,
                 data_dir="data/raw_company_texts",
                 cache_dir="data/embedding_cache",
                 model_name="sentence-transformers/all-MiniLM-L6-v2",
                 batch_size=16):
        self.data_dir = data_dir
        self.cache_dir = cache_dir
        self.batch_size = batch_size

        os.makedirs(self.cache_dir, exist_ok=True)

        # Load tokenizer and model for embedding
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

        self.texts = []
        self.index = None

        self._build_index()

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]  # first element is last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask

    def _embed_text(self, texts):
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i: i + self.batch_size]
            with torch.no_grad():
                encoded_input = self.tokenizer(batch, padding=True, truncation=True, return_tensors='pt')
                model_output = self.model(**encoded_input)
                batch_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
                batch_embeddings = batch_embeddings.cpu().numpy()
                # Normalize embeddings
                batch_embeddings /= np.linalg.norm(batch_embeddings, axis=1, keepdims=True) + 1e-10
                embeddings.append(batch_embeddings)
        return np.vstack(embeddings)

    def _build_index(self):
        embeddings_path = os.path.join(self.cache_dir, "embeddings.npy")
        texts_path = os.path.join(self.cache_dir, "texts.pkl")

        # Try loading cached embeddings and texts
        if os.path.exists(embeddings_path) and os.path.exists(texts_path):
            try:
                self.texts = pickle.load(open(texts_path, "rb"))
                embeddings = np.load(embeddings_path)
                logging.info(f"Loaded cached embeddings and texts from {self.cache_dir}")
            except Exception as e:
                logging.warning(f"Failed to load cache: {e}. Recomputing embeddings.")
                self.texts, embeddings = self._compute_and_cache_embeddings(texts_path, embeddings_path)
        else:
            self.texts, embeddings = self._compute_and_cache_embeddings(texts_path, embeddings_path)

        if len(self.texts) == 0:
            logging.error("No texts found for building index.")
            self.index = None
            return

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner product = cosine similarity if normalized
        self.index.add(embeddings)

    def _compute_and_cache_embeddings(self, texts_path, embeddings_path):
        files = glob.glob(os.path.join(self.data_dir, "*.txt"))
        corpus = []

        for file in files:
            try:
                with open(file, encoding="utf-8") as f:
                    text = f.read()
                paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
                corpus.extend(paragraphs)
            except Exception as e:
                logging.error(f"Failed to read {file}: {e}")

        self.texts = corpus
        embeddings = self._embed_text(corpus)

        try:
            with open(texts_path, "wb") as f:
                pickle.dump(corpus, f)
            np.save(embeddings_path, embeddings)
            logging.info(f"Saved embeddings and texts cache to {self.cache_dir}")
        except Exception as e:
            logging.warning(f"Failed to save cache: {e}")

        return corpus, embeddings

    def retrieve(self, company: str, top_k=3):
        if self.index is None or not self.texts:
            logging.error("Index or texts not available.")
            return []

        query_embedding = self._embed_text([company])
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for idx in indices[0]:
            if idx < len(self.texts):
                results.append(self.texts[idx])
        return results
