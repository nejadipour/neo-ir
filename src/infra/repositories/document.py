import pandas as pd
from neomodel import db


class DocumentRepository:
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
