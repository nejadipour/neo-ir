from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    REQUIRED_COLUMNS: list = ['content', 'title', 'url']
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter='__')


config = Config()
