import csv
import logging
import datetime as dt

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT, RESULT, PRETTY, FILE


MESSAGE_PATTERN = 'Файл с результатами был сохранён: {file_path}'


def default_output(results, *args):
    for row in results:
        print(*row)


def pretty_output(results, *args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / RESULT
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now_formatted = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as file:
        csv.writer(file, dialect=csv.unix_dialect).writerows(results)
    logging.info(MESSAGE_PATTERN.format(file_path=file_path))


OUTPUTS = {
    PRETTY: pretty_output,
    FILE: file_output,
    None: default_output
}


def control_output(results, cli_args):
    OUTPUTS[cli_args.output](results, cli_args)
