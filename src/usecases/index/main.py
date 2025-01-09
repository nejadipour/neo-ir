import pandas as pd

from src.infra.repositories import TermRepository, DocumentRepository, ExistsInRepository
from src.infra.repositories.utils import detach_delete_all
from src.usecases.index import DataLoader, TextProcessor
from datetime import datetime


class Indexer:
    @staticmethod
    def build_index(df: pd.DataFrame, text_processor: TextProcessor) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        df = df.reset_index().rename(columns=dict(index='doc_id'))
        documents_df = df[['doc_id', 'title', 'url']]

        df['tokens'] = df['text'].apply(text_processor.process_text)

        tokens_df = df.explode('tokens')[['doc_id', 'tokens']]
        tokens_df["position"] = tokens_df.groupby('doc_id').cumcount()

        term_doc_df = (
            tokens_df.groupby(['tokens', 'doc_id'])
            .agg(
                term_frequency=('tokens', 'count'),
                positions=('position', list)
            )
            .reset_index()
            .rename(columns=dict(tokens='term'))
        )

        terms_df = term_doc_df.groupby('term').size().reset_index(name='document_frequency')

        return terms_df, term_doc_df, documents_df

    @staticmethod
    def mark_champions(term_doc_df: pd.DataFrame, k: int = 50) -> pd.DataFrame:
        term_doc_df['rank'] = term_doc_df.groupby('term')['term_frequency'].rank(ascending=False, method='first')

        term_doc_df['is_champion'] = term_doc_df['rank'] <= k

        term_doc_df = term_doc_df.drop(columns=['rank'])
        return term_doc_df

    @staticmethod
    def _prepare_relationships(term_doc_df, term_ids, document_ids) -> pd.DataFrame:
        term_doc_df['term_id'] = term_doc_df['term'].map(term_ids)
        term_doc_df['document_id'] = term_doc_df['doc_id'].map(document_ids)
        return term_doc_df[['term_id', 'document_id', 'term_frequency', 'positions', 'is_champion']]

    def save_to_db(self, terms_df: pd.DataFrame, term_doc_df: pd.DataFrame, documents_df: pd.DataFrame):
        detach_delete_all()
        print(f'[{datetime.now()}] : Detach delete done.')

        # Ensure uniqueness
        terms_df = terms_df.drop_duplicates(subset=['term'])
        documents_df = documents_df.drop_duplicates(subset=['doc_id'])
        term_doc_df = term_doc_df.drop_duplicates(subset=['term', 'doc_id'])

        term_ids = TermRepository.bulk_create(terms_df=terms_df)
        print(f'[{datetime.now()}] : Saving terms finished successfully.')

        document_ids = DocumentRepository.bulk_create(documents_df=documents_df)
        print(f'[{datetime.now()}] : Saving documents finished successfully.')

        term_doc_df = self._prepare_relationships(term_doc_df, term_ids, document_ids)
        ExistsInRepository.bulk_create(exists_in_df=term_doc_df)
        print(f'[{datetime.now()}] : Saving EXISTS_IN relations finished successfully.')

    def main(self):
        data_loader = DataLoader("data/IR_data_news_12k.json")
        df = data_loader.load_data()

        text_processor = TextProcessor()
        terms_df, term_doc_df, documents_df = self.build_index(df=df, text_processor=text_processor)
        print(f'[{datetime.now()}] : Text processing finished successfully. Tokens count: {len(terms_df)}, Relations count: {len(term_doc_df)}')

        term_doc_df = self.mark_champions(term_doc_df=term_doc_df)
        print(f'[{datetime.now()}] : Finding champions finished successfully.')

        self.save_to_db(
            terms_df=terms_df,
            term_doc_df=term_doc_df,
            documents_df=documents_df
        )
        print(f'[{datetime.now()}] : Storing into database finished successfully.')
