import pandas as pd
from neomodel import db


class TermRepository:
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
