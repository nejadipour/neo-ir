import pandas as pd
from src.infra.repositories.utils import bulk_create_with_batches


class ExistsInRepository:
    @staticmethod
    def bulk_create(exists_in_df: pd.DataFrame):
        query = """
        UNWIND $rows AS row
        MATCH (t: Term) WHERE elementId(t) = row.term_id
        MATCH (d: Document) WHERE elementId(d) = row.document_id
        CREATE (t)-[:EXISTS_IN {term_frequency: row.term_frequency, positions: row.positions, is_champion: row.is_champion}]->(d)
        """

        bulk_create_with_batches(
            query=query,
            data=exists_in_df
        )
