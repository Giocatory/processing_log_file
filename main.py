import argparse
import sys
from tabulate import tabulate
from datetime import date, datetime
from reports import AverageReport

def get_report_class(report_name):
    """Возвращает класс отчета по имени."""
    reports = {
        "average": AverageReport
    }
    return reports.get(report_name)

def read_log_files(file_paths):
    """Читает содержимое файлов с логами."""
    log_lines = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                log_lines.extend(f.readlines())
        except FileNotFoundError:
            print(f"Ошибка: файл не найден: {file_path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}", file=sys.stderr)
            sys.exit(1)
    return log_lines

def main():
    parser = argparse.ArgumentParser(description='Скрипт для анализа логов HTTP-запросов.')
    parser.add_argument('--file', nargs='+', required=True, help='Пути к одному или нескольким файлам с логами.')
    parser.add_argument('--report', type=str, default='average', help='Название отчета для формирования (по умолчанию: average).')
    parser.add_argument('--date', type=str, help='Дата для фильтрации логов в формате YYYY-MM-DD.')

    args = parser.parse_args()

    # Проверка формата даты
    if args.date:
        try:
            datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print("Ошибка: Неверный формат даты. Используйте YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)

    log_lines = read_log_files(args.file)

    report_class = get_report_class(args.report)
    if not report_class:
        print(f"Ошибка: Отчет '{args.report}' не найден.", file=sys.stderr)
        sys.exit(1)

    report_instance = report_class(log_lines, args.date)
    report_data = report_instance.get_data()

    if report_data:
        headers = ["handler", "total", "avg_response_time"]
        table = []
        for item in report_data:
            table.append([
                item['handler'],
                item['total_requests'],
                f"{item['avg_response_time']:.3f}"
            ])
        print(tabulate(table, headers=headers, tablefmt="plain"))
    else:
        print("Нет данных для формирования отчета.")

if __name__ == '__main__':
    main()