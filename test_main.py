import pytest
from reports import AverageReport
from main import get_report_class, read_log_files
import json

# Примерные данные логов для тестов
MOCK_LOGS = [
    '{"@timestamp": "2025-06-22T12:00:00+00:00", "url": "/api/homeworks/...", "response_time": 0.1}',
    '{"@timestamp": "2025-06-22T12:00:01+00:00", "url": "/api/homeworks/...", "response_time": 0.2}',
    '{"@timestamp": "2025-06-22T12:00:02+00:00", "url": "/api/users/...", "response_time": 0.05}',
    '{"@timestamp": "2025-06-23T12:00:03+00:00", "url": "/api/homeworks/...", "response_time": 0.3}',
]

@pytest.fixture
def mock_log_files(tmp_path):
    """Фикстура для создания временных файлов логов."""
    file1 = tmp_path / "test1.log"
    file2 = tmp_path / "test2.log"
    file1.write_text(MOCK_LOGS[0] + '\n' + MOCK_LOGS[1])
    file2.write_text(MOCK_LOGS[2] + '\n' + MOCK_LOGS[3])
    return [str(file1), str(file2)]

def test_average_report_get_data_without_date_filter():
    """Тестирование отчета без фильтрации по дате."""
    report = AverageReport(MOCK_LOGS)
    data = report.get_data()
    
    assert len(data) == 2
    assert data[0]['handler'] == '/api/homeworks/...'
    assert data[0]['total_requests'] == 3
    assert abs(data[0]['avg_response_time'] - (0.1 + 0.2 + 0.3) / 3) < 1e-9

    assert data[1]['handler'] == '/api/users/...'
    assert data[1]['total_requests'] == 1
    assert abs(data[1]['avg_response_time'] - 0.05) < 1e-9

def test_average_report_get_data_with_date_filter():
    """Тестирование отчета с фильтрацией по дате."""
    report = AverageReport(MOCK_LOGS, filter_date='2025-06-22')
    data = report.get_data()
    
    assert len(data) == 2
    assert data[0]['handler'] == '/api/homeworks/...'
    assert data[0]['total_requests'] == 2
    assert abs(data[0]['avg_response_time'] - (0.1 + 0.2) / 2) < 1e-9

    assert data[1]['handler'] == '/api/users/...'
    assert data[1]['total_requests'] == 1
    assert abs(data[1]['avg_response_time'] - 0.05) < 1e-9

def test_read_log_files_success(mock_log_files):
    """Тестирование успешного чтения файлов."""
    log_lines = read_log_files(mock_log_files)
    assert len(log_lines) == 4

def test_read_log_files_file_not_found():
    """Тестирование ошибки при отсутствии файла."""
    with pytest.raises(SystemExit):
        read_log_files(["non_existent_file.log"])

def test_get_report_class_existing_report():
    """Тестирование получения существующего класса отчета."""
    report_class = get_report_class("average")
    assert report_class is AverageReport

def test_get_report_class_non_existing_report():
    """Тестирование получения несуществующего класса отчета."""
    report_class = get_report_class("non_existent_report")
    assert report_class is None