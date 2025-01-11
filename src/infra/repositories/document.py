import pandas as pd
from neomodel import db

from src.infra.models import Document


class DocumentRepository:
    """
    Repository for Document Entity
    """
    candidates_columns = ['term', 'doc_id', 'term_frequency', 'document_frequency', 'tf_value', 'idf_value', 'tf_idf']

    """
    Create
    """

    @staticmethod
    def bulk_create(documents_df: pd.DataFrame) -> dict:
        query = """
        UNWIND $rows AS row
        CREATE (d:Document {doc_id: row.doc_id, title: row.title, url: row.url})
        RETURN d.doc_id AS doc_id, elementId(d) AS document_id_in_neo
        """

        cypher_query_params = {"rows": documents_df.to_dict('records')}
        results, _ = db.cypher_query(query, cypher_query_params)

        return {doc_id: document_id_in_neo for doc_id, document_id_in_neo in results}

    """
    Read
    """

    @staticmethod
    def get_total_documents_count() -> int:
        query = """
        MATCH (d:Document)
        RETURN COUNT(d) AS total_documents
        """

        result, _ = db.cypher_query(query)
        return result[0][0]

    @staticmethod
    def get_documents_by_doc_ids(doc_ids: list[int]) -> list[dict]:
        query = """
        MATCH (d: Document)
        WHERE d.doc_id IN $doc_ids
        RETURN
        d.doc_id AS doc_idm,
        d.title AS title,
        d.url AS url
        """

        result, _ = db.cypher_query(query, {'doc_ids': doc_ids})
        return [{'doc_id': row[0], 'title': row[1], 'url': row[2]} for row in result]

    @staticmethod
    def _build_candidates_clause() -> str:
        return """
        RETURN 
        t.value AS term, 
        d.doc_id AS doc_id, 
        e.term_frequency AS term_frequency,
        t.document_frequency AS document_frequency,
        1 + log(e.term_frequency) AS tf_value,
        log($total_documents / t.document_frequency) AS idf_value,
        (1 + log(e.term_frequency)) * log($total_documents / t.document_frequency) AS tf_idf
        """

    @staticmethod
    def get_champion_documents_by_query_terms(query_terms: list[str], total_documents: int) -> pd.DataFrame:
        query = f"""
        UNWIND $query_terms AS term_value
        MATCH (t: Term {{value: term_value}})-[e:EXISTS_IN {{is_champion: True}}]->(d:Document)
        {DocumentRepository._build_candidates_clause()}
        """

        result, _ = db.cypher_query(query, {'query_terms': query_terms, 'total_documents': total_documents})
        return pd.DataFrame(result, columns=DocumentRepository.candidates_columns)

    @staticmethod
    def get_documents_matching_all_query_terms(query_terms: list[str], term_with_lowest_document_frequency: str,
                                               total_documents: int) -> pd.DataFrame:
        query = f"""
        MATCH (t: Term {{value: $term_with_lowest_document_frequency}} )-[:EXISTS_IN]->(d: Document)
        WITH d
        MATCH (t: Term)-[:EXISTS_IN]->(d)
        WITH d.doc_id AS doc_id, COLLECT(t.value) AS terms_in_doc
        WHERE ALL(term IN $query_terms WHERE term IN terms_in_doc)
        WITH doc_id
        UNWIND $query_terms AS term_value
        MATCH (t: Term {{value: term_value}})-[e:EXISTS_IN]->(d:Document {{doc_id: doc_id}})
        {DocumentRepository._build_candidates_clause()}
        """

        result, _ = db.cypher_query(query, {'query_terms': query_terms,
                                            'term_with_lowest_document_frequency': term_with_lowest_document_frequency,
                                            'total_documents': total_documents})
        return pd.DataFrame(result, columns=DocumentRepository.candidates_columns)

    @staticmethod
    def get_high_idf_documents_by_query_terms(query_terms: list[str],
                                              document_frequency_threshold: float,
                                              total_documents: int) -> pd.DataFrame:
        query = f"""
        UNWIND $query_terms AS term_value
        MATCH (t: Term {{value: term_value}})-[e:EXISTS_IN]->(d: Document)
        WHERE t.document_frequency < $document_frequency_threshold
        {DocumentRepository._build_candidates_clause()}
        """

        result, _ = db.cypher_query(query, {'query_terms': query_terms,
                                            'document_frequency_threshold': document_frequency_threshold,
                                            'total_documents': total_documents})
        return pd.DataFrame(result, columns=DocumentRepository.candidates_columns)

    @staticmethod
    def get_all_documents_by_query_terms(query_terms: list[str], total_documents: int) -> pd.DataFrame:
        query = f"""
        UNWIND $query_terms AS term_value
        MATCH (t: Term {{value: term_value}})-[e: EXISTS_IN]->(d: Document)
        {DocumentRepository._build_candidates_clause()}
        """

        result, _ = db.cypher_query(query, {'query_terms': query_terms, 'total_documents': total_documents})
        return pd.DataFrame(result, columns=DocumentRepository.candidates_columns)
