from neomodel import db
import pandas as pd


def bulk_create_with_batches(query: str, data: pd.DataFrame, batch_size: int =2000):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        db.cypher_query(query, {"rows": batch.to_dict('records')})


def detach_delete_all(batch_size: int = 20_000):
    def delete_by_query(query):
        while True:
            result, _ = db.cypher_query(query)
            deleted_count = result[0][0]

            if deleted_count == 0:
                break

    delete_rels_query = f"""
    MATCH ()-[r]->()
    WITH r LIMIT {batch_size}
    DELETE r
    RETURN COUNT(r) AS deleted_count
    """

    delete_nodes_query = f"""
    MATCH (n)
    WITH n LIMIT {batch_size}
    DELETE n
    RETURN COUNT (n) AS deleted_count
    """

    delete_by_query(delete_rels_query)
    delete_by_query(delete_nodes_query)
