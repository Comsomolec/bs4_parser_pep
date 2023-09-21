import re
import logging
import requests_cache
from requests import ConnectionError

from urllib.parse import urljoin
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, MAIN_DOC_URL, MAIN_PEP_URL, EXPECTED_STATUS,
    POSTFIX, OUTPUT_TYPE
)
from outputs import control_output
from utils import find_tag, get_soup


CONNECTION_ERROR_MESSAGE = 'Ошибка при запросе по адресу: {url}'

def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    try:
        soup = get_soup(session, whats_new_url)
    except ConnectionError:
        raise ValueError(CONNECTION_ERROR_MESSAGE.format(url=whats_new_url))
    # main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'}) 
    # div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'}) 
    # sections_by_python = div_with_ul.find_all( 
    #     'li', attrs={'class': 'toctree-l1'}
    # )
    sections_by_python = soup.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        try:
            soup = get_soup(session, version_link)
        except ConnectionError:
            raise ValueError(
                CONNECTION_ERROR_MESSAGE.format(url=version_link)
            )
        result.append((
            version_link,
            find_tag(soup, 'h1').text,
            find_tag(soup, 'dl').text.replace('\n', ' ')
        ))
    return result


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise RuntimeError('Ничего не нашлось')
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
    soup = get_soup(session, downloads_url)
    table = find_tag(soup, 'table')
    pdf_a4_tag = find_tag(table, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOAD_POSTFIX
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = get_soup(session, MAIN_PEP_URL)
    pep_table = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    rows_table = pep_table.find_all('tr')
    result = [('Статус', 'Количество')]
    for i in tqdm(range(1, len(rows_table))):
        row_href = find_tag(
            rows_table[i], 'a', attrs={'class': 'pep reference internal'}
            )['href']
        row_type_and_status = find_tag(rows_table[i], 'abbr').text
        if len(row_type_and_status) != 1:
            preview_status = row_type_and_status[1]
        row_link = urljoin(MAIN_PEP_URL, row_href)
        soup = get_soup(session, row_link)
        pep_title = find_tag(
            soup, 'dl', attrs={'class': 'rfc2822 field-list simple'}
        )
        for tag in pep_title:
            if tag.name == 'dt' and tag.text == 'Status:':
                pep_status = tag.next_sibling.next_sibling.string
                if pep_status not in SUM_PEP_STATUS or (
                            pep_status[0] != preview_status):
                    logging.info(
                        f'''Несовпадающие статусы:'
                            {row_link}'
                            Статус в карточке:{pep_status}
                            Ожидаемые статусы:{EXPECTED_STATUS[preview_status]}
                        '''
                    )
                else:
                    SUM_PEP_STATUS[pep_status] += 1
    for status, value in SUM_PEP_STATUS.items():
        result.append((status, value))
    result.append(('Итого:', len(rows_table) - 1))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        logging.error(f'Возникла ошибка: {error}', stack_info=True)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
