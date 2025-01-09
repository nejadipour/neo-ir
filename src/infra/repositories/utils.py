from neomodel import db
import pandas as pd


def bulk_create_with_batches(query: str, data: pd.DataFrame, batch_size: int =2000):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        db.cypher_query(query, {"rows": batch.to_dict('records')})


def detach_delete_all():
    query = """
    match (n) detach delete n;
    """

    db.cypher_query(query)
