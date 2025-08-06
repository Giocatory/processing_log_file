import json
from datetime import datetime, date

class BaseReport:
    """Базовый класс для отчетов."""
    def __init__(self, logs, filter_date=None):
        self.logs = logs
        self.filter_date = filter_date

    def get_data(self):
        """
        Обрабатывает логи и возвращает данные для отчета.
        """
        raise NotImplementedError

class AverageReport(BaseReport):
    """Класс для отчета по среднему времени ответа."""
    def get_data(self):
        endpoints = {}
        for log_line in self.logs:
            try:
                log_entry = json.loads(log_line)
                log_date_str = log_entry.get('@timestamp', '')[:10]
                if self.filter_date and log_date_str != self.filter_date:
                    continue

                handler = log_entry.get('url')
                response_time = log_entry.get('response_time')

                if handler and response_time is not None:
                    if handler not in endpoints:
                        endpoints[handler] = {
                            'total_requests': 0,
                            'total_response_time': 0.0
                        }
                    endpoints[handler]['total_requests'] += 1
                    endpoints[handler]['total_response_time'] += response_time
            except json.JSONDecodeError:
                # Игнорируем некорректные строки в логе
                continue

        report_data = []
        for handler, data in endpoints.items():
            avg_response_time = data['total_response_time'] / data['total_requests']
            report_data.append({
                'handler': handler,
                'total_requests': data['total_requests'],
                'avg_response_time': avg_response_time
            })
        
        # Сортировка по количеству запросов в порядке убывания
        report_data.sort(key=lambda x: x['total_requests'], reverse=True)
        return report_data