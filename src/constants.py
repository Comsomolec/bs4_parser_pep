from pathlib import Path
from enum import Enum


BASE_DIR = Path(__file__).parent
MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'

OUTPUT_ERROR_MESSAGE = 'Неверный ввод: {s}'


class OUTPUT_TYPE(Enum):
    pretty = 'pretty'
    file = 'file'

    def __str__(self):
        return self.name
    
    @staticmethod
    def from_string(s):
        try:
            return OUTPUT_TYPE[s]
        except KeyError:
            raise ValueError(OUTPUT_ERROR_MESSAGE.format(s=s))


DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '%(asctime)s - [%(levelname)s] - %(message)s'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

RESULT = 'results'
DOWNLOAD = 'downloads'
LOG = 'logs'
LOG_FILE = 'parser.log'

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
