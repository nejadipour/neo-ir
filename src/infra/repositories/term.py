import pandas as pd
from neomodel import db


class TermRepository:
    """
    Repository for Term Entity
    """

    """
    Create
    """

    @staticmethod
    def bulk_create(terms_df: pd.DataFrame) -> dict:
        query = """
        UNWIND $rows AS row
        CREATE (t:Term {value: row.term, document_frequency: row.document_frequency})
        RETURN t.value AS term, elementId(t) AS term_id_in_neo
        """

        cypher_query_params = {"rows": terms_df.to_dict('records')}
        results, _ = db.cypher_query(query, cypher_query_params)

        return {term: term_id_in_neo for term, term_id_in_neo in results}

    """
    Read
    """

    @staticmethod
    def get_terms_by_query_terms(query_terms: list[str]) -> list[str]:
        query = """
        UNWIND $query_terms AS term_value
        MATCH (t: Term {value: term_value})
        RETURN t.value
        """

        result, _ = db.cypher_query(query, {'query_terms': query_terms})
        return [term[0] for term in result]


    @staticmethod
    def get_terms_document_frequencies(query_terms: list[str]) -> pd.DataFrame:
        query = """
        UNWIND $query_terms AS term_value
        MATCH (t:Term {value: term_value})
        RETURN t.value AS term, t.document_frequency AS document_frequency
        """

        result, _ = db.cypher_query(query, {'query_terms': query_terms})
        return pd.DataFrame(result, columns=['term', 'document_frequency'])
