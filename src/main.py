import re
import logging
from collections import defaultdict

import requests_cache
from requests import ConnectionError
from tqdm import tqdm
from urllib.parse import urljoin

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, MAIN_DOC_URL, MAIN_PEP_URL, EXPECTED_STATUS, DOWNLOAD
)
from outputs import control_output
from utils import find_tag, get_soup


EMPTY_RESULT_MESSAGE = 'Ничего не нашлось'
LOADING_COMPLETE_MESSAGE = 'Архив был загружен и сохранён: {archive_path}'
LOG_INFO_ARG_MESSAGE = 'Аргументы командной строки: {args}'
LOG_ERROR_MESSAGE = 'Возникла ошибка: {error}'
SOUP_ERROR_MESSAGE = 'Не удалось создать "суп" ссылки: {url}: {error}'
PASRER_START = 'Парсер запущен!'
PARSER_COMPLETE = 'Парсер завершил работу.'
WRONG_STATUSES_MESSAGE = (
    'Несовпадающие статусы: {row_link}. '
    'Статус в карточке:{pep_status}. '
    'Ожидаемые статусы:{expect_status}.'
)


def whats_new(session):
    # Строка селекторов длинной 88 символов, требуется "+" - "Конкатенация".
    logs = []
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for a_tag in tqdm(
        get_soup(
            session, whats_new_url
        ).select(
            '#what-s-new-in-python div.toctree-wrapper ' +
            'li.toctree-l1 a:-soup-contains("What’s New")'
        )
    ):
        href = a_tag['href']
        version_link = urljoin(whats_new_url, href)
        try:
            soup = get_soup(session, version_link)
            result.append((
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
            ))
        except ConnectionError as error:
            logs.append(
                SOUP_ERROR_MESSAGE.format(url=version_link, error=error)
            )
    list(map(logging.error, logs))
    return result


def latest_versions(session):
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for ul in get_soup(
        session, MAIN_DOC_URL
    ).select(
      'div.sphinxsidebarwrapper > ul'
    ):
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise RuntimeError(EMPTY_RESULT_MESSAGE)
    result = [('Ссылка на документацию', 'Версия', 'Статус')]
    for tag in a_tags:
        link = tag['href']
        text_match = re.search(pattern, tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = tag.text, ''
        result.append((link, version, status))
    return result


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    table = find_tag(get_soup(session, downloads_url), 'table')
    pdf_a4_link = find_tag(
        table,
        'a',
        {
            'href': re.compile(r'.+pdf-a4\.zip$')
        }
    )['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOAD
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(LOADING_COMPLETE_MESSAGE.format(archive_path=archive_path))


def pep(session):
    count_pep_status = defaultdict(int)
    logs = []
    wrong_statuses_message = []
    for row in tqdm(get_soup(session, MAIN_PEP_URL
                             ).select('#numerical-index tr')[1:]):
        row_href = find_tag(
            row, 'a', attrs={'class': 'pep reference internal'}
        )['href']
        row_type_and_status = find_tag(row, 'abbr').text
        if len(row_type_and_status) != 1:
            preview_status = row_type_and_status[1]
        row_link = urljoin(MAIN_PEP_URL, row_href)
        try:
            soup = get_soup(session, row_link)
        except ConnectionError as error:
            logs.append(
                SOUP_ERROR_MESSAGE.format(url=row_link, error=error)
            )
            continue
        pep_title = find_tag(
            soup, 'dl', attrs={'class': 'rfc2822 field-list simple'}
        )
        for tag in pep_title:
            if tag.name != 'dt' or tag.text != 'Status:':
                continue
            pep_status = tag.next_sibling.next_sibling.string
            if pep_status[0] != preview_status:
                wrong_statuses_message.append(
                    WRONG_STATUSES_MESSAGE.format(
                        row_link=row_link,
                        pep_status=pep_status,
                        expect_status=EXPECTED_STATUS[preview_status]
                    )
                )
            else:
                count_pep_status[pep_status] += 1
    list(map(logging.error, logs))
    list(map(logging.info, wrong_statuses_message))
    return [
        ('Статус', 'Количество'),
        count_pep_status.items(),
        ('Всего', sum(count_pep_status.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info(PASRER_START)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(LOG_INFO_ARG_MESSAGE.format(args=args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        logging.error(LOG_ERROR_MESSAGE.format(error=error), stack_info=True)
    logging.info(PARSER_COMPLETE)


if __name__ == '__main__':
    main()
