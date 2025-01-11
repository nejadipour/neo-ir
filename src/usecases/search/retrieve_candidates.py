import pandas as pd

from src.infra.repositories import DocumentRepository, TermRepository


class CandidatesRetriever:
    def __init__(self):
        self.total_documents = DocumentRepository.get_total_documents_count()

    @staticmethod
    def _get_term_with_lowest_document_frequency(query_terms: list[str]) -> str:
        term_frequencies = TermRepository.get_terms_document_frequencies(query_terms)
        return term_frequencies.sort_values(by='document_frequency').iloc[0]['term']

    @staticmethod
    def _get_document_frequency_threshold(query_terms: list[str]) -> float:
        term_frequencies = TermRepository.get_terms_document_frequencies(query_terms)
        return term_frequencies['document_frequency'].mean()

    def get_candidates_by_filter_level(self, query_terms: list[str], filter_level: int = 1) -> pd.DataFrame:
        match filter_level:
            case 1:
                return DocumentRepository.get_documents_matching_all_query_terms(
                    query_terms=query_terms,
                    total_documents=self.total_documents,
                    term_with_lowest_document_frequency=self._get_term_with_lowest_document_frequency(
                        query_terms=query_terms))
            case 2:
                return DocumentRepository.get_champion_documents_by_query_terms(
                    query_terms=query_terms,
                    total_documents=self.total_documents)
            case 3:
                return DocumentRepository.get_high_idf_documents_by_query_terms(
                    query_terms=query_terms,
                    document_frequency_threshold=self._get_document_frequency_threshold(query_terms=query_terms),
                    total_documents=self.total_documents
                )
            case 4:
                return DocumentRepository.get_all_documents_by_query_terms(
                    query_terms=query_terms,
                    total_documents=self.total_documents
                )

    def retrieve_candidates(self, query_terms: list[str], count: int = 10) -> pd.DataFrame:
        filter_level = 1
        candidates = pd.DataFrame()
        while len(candidates) < count and filter_level <= 4:
            new_candidates = self.get_candidates_by_filter_level(query_terms=query_terms, filter_level=filter_level)
            candidates = pd.concat([candidates, new_candidates]).drop_duplicates()
            filter_level += 1

        return candidates
