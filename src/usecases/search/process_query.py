from src.usecases.utils import TextProcessor
from collections import Counter
import pandas as pd


class QueryProcessor:
    @staticmethod
    def extract_terms(query: str, text_processor: TextProcessor) -> list[str]:
        return list(set(text_processor.process_text(text=query)))

    @staticmethod
    def get_term_frequencies(terms: list[str]) -> pd.DataFrame:
        term_counts = Counter(terms)
        tf_df = pd.DataFrame.from_dict(term_counts, orient='index', columns=['term_frequency'])
        tf_df.index.name = 'term'
        tf_df = tf_df.reset_index()

        return tf_df

    def process_query(self, query: str) -> pd.DataFrame:
        text_processor = TextProcessor()
        terms = self.extract_terms(query=query, text_processor=text_processor)

        tf_df = self.get_term_frequencies(terms=terms)

        return tf_df
