# Python Docs and PEP Parser

## Описание
Данный проект является учебным и создан в рамках обучения на курсе Python-Backend.
Предназначен для сбора полезной информации о языке Python:
- <a href="https://docs.python.org/3/whatsnew/" target="_blank">whats-new</a> - последние изменения в языке Python
- <a href="https://docs.python.org/3/" target="_blank">latest-versions</a> - ссылки на документацию
- <a href="https://docs.python.org/3/download.html" target="_blank">download</a> - скачать архив с документацией

## Используемые Технологии
- Python
- argparse
- BeautifulSoup (bf4)
- prettytable
- tqdm

## Как запустить проект
- Клонировать репозиторий
```
git clone git@github.com:Comsomolec/bs4_parser_pep.git
```
- Перейти в директорию с проектом
- Установить и активировать виртуальное окружение 

```
python -m venv venv
```

Если у вас Linux/MacOS

    ```
    source venv/bin/activate
    ```

Если у вас windows

    ```
    source venv/scripts/activate
    ```
- Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```
## Как запустить и работать с парсингом
- Перейти в директорию src/ 
- Вызов справки
```
python main.py -h (или --help)
```
- Получить список ссылок с изменениями в различных версиях языка Python
```
python main.py whats-new
```
- Получить список ссылок на документацию всех версий языка Python
```
python main.py latest-versions
```
- Скачать архив документации последней версии языка Python. Архив будет доступен в директории проекта, в каталоге download/
```
python main.py download
```
- Считать статусы всех документов PEP
```
python main.py pep
```
## Дополнительные способы вывода данных:
- -o или --output pretty: выводит данные в терминале в ASCII таблице
- -o или --output file: сохраняет вывод данных в каталоге /results в csv формате.
