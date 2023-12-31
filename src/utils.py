from exceptions import ParserFindTagException

from bs4 import BeautifulSoup
from requests import RequestException, ConnectionError


REQUEST_MESSAGE_ERROR = 'Возникла ошибка при загрузке страницы {url}: {error}'
FIND_TAG_MESSAGE_ERROR = 'Не найден тег {tag} {attrs}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as error:
        raise ConnectionError(
            REQUEST_MESSAGE_ERROR.format(url=url, error=error)
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs={} if attrs is None else attrs)
    if searched_tag is None:
        raise ParserFindTagException(
            FIND_TAG_MESSAGE_ERROR.format(tag=tag, attrs=attrs)
            )
    return searched_tag


def get_soup(session, url, format='lxml'):
    return BeautifulSoup(get_response(session, url).text, features=format)
