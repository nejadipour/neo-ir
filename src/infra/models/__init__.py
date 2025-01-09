from src.infra.models.term import Term
from src.infra.models.exists_in import ExistsIn
from src.infra.models.document import Document

from src.utils.config import config
from neomodel import config as neo_config, install_all_labels

neo_config.DATABASE_URL = config.DATABASE_URL

__all__ = ['Term', 'Document', 'ExistsIn' ,'install_all_labels']
