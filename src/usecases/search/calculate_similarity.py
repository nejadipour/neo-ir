import numpy as np
import pandas as pd


class SimilarityCalculator:
    @staticmethod
    def normalize_vector(vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 0 else vector

    def get_documents_vectors(self, candidates_df: pd.DataFrame, query_terms: list[str]) -> dict:
        unique_doc_ids = candidates_df['doc_id'].unique()
        doc_vectors = {doc_id: np.zeros(len(query_terms)) for doc_id in unique_doc_ids}

        for _, row in candidates_df.iterrows():
            term = row['term']
            term_index = query_terms.index(term)
            doc_vectors[row['doc_id']][term_index] = row['tf_idf']

        for doc_id in doc_vectors.keys():
            doc_vectors[doc_id] = self.normalize_vector(doc_vectors[doc_id])

        return doc_vectors

    def calculate_similarity(self, query_df: pd.DataFrame, candidates_df: pd.DataFrame) -> pd.DataFrame:
        query_terms = query_df['term'].tolist()
        query_vector = query_df['term_frequency'].values

        query_vector = self.normalize_vector(vector=query_vector)

        doc_vectors = self.get_documents_vectors(candidates_df=candidates_df, query_terms=query_terms)

        similarities = [
            {'doc_id': doc_id, 'similarity': np.dot(query_vector, doc_vector)}
            for doc_id, doc_vector in doc_vectors.items()
        ]

        return pd.DataFrame(similarities)
