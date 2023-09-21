from pathlib import Path
from enum import Enum


BASE_DIR = Path(__file__).parent
MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'

class POSTFIX(Enum):
    RESULT = 'results'
    DOWNLOAD = 'downloads'
    LOG = 'logs'
    LOG_FILE = 'parser.log'

    def __str__(self):
        return self.name


class OUTPUT_TYPE(Enum):
    PRETTY = 'pretty'
    FILE = 'file'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '%(asctime)s - [%(levelname)s] - %(message)s'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
