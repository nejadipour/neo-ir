import pandas as pd
from pandas import lreshape

from src.infra.repositories import DocumentRepository
from src.usecases.search import QueryProcessor, CandidatesRetriever, SimilarityCalculator


class SearchQuery:
    @staticmethod
    def paginate_response(similarities: pd.DataFrame, page: int, page_size: int) -> pd.DataFrame:
        start = (page - 1) * page_size
        end = start + page_size

        return similarities.iloc[start:end]


    def main(self, query: str, page: int = 1, page_size: int = 10) -> list[dict]:
        query_df = QueryProcessor().process_query(query=query)

        if len(query_df) == 0:
            return []

        candidates_df = CandidatesRetriever().retrieve_candidates(query_terms=query_df['term'].tolist())
        similarities = SimilarityCalculator().calculate_similarity(query_df=query_df, candidates_df=candidates_df)

        similarities = similarities.sort_values(by='similarity', ascending=False)
        similarities = self.paginate_response(similarities=similarities, page=page, page_size=page_size)

        doc_ids = similarities['doc_id'].tolist()
        documents = DocumentRepository.get_documents_by_doc_ids(doc_ids)

        result = []
        for _, row in similarities.iterrows():

            doc = next((doc for doc in documents if doc['doc_id'] == row['doc_id']), {})
            result.append({
                'doc_id': row['doc_id'],
                'similarity': row['similarity'],
                'title': doc.get('title'),
                'url': doc.get('url')
            })

        return result
