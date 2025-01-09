import pandas as pd

from src.utils.config import config
from datetime import datetime


class DataLoader:
    def __init__(self, file_path: str, required_columns=None):
        if required_columns is None:
            required_columns = config.REQUIRED_COLUMNS

        self.file_path = file_path
        self.required_columns = required_columns

    def load_data(self) -> pd.DataFrame:
        try:
            df = pd.read_json(self.file_path, orient='index')
            self._validate_data_structure(df)

            df = self._make_text_column(df)

            print(f"[{datetime.now()}] : Loaded {len(df)} documents successfully!")
            return df

        except FileNotFoundError:
            raise Exception(f"File not found: {self.file_path}")
        except ValueError:
            raise Exception("Error decoding json file.")

    def _validate_data_structure(self, df: pd.DataFrame):
        for column in self.required_columns:
            if column not in df.columns:
                raise Exception(f"Dataset is missing required column: {column}")

    @staticmethod
    def _make_text_column(df: pd.DataFrame) -> pd.DataFrame:
        df['text'] = df['title'] + "\n" + df['content']
        return df
