import pytest
import tempfile
import csv
from pathlib import Path

@pytest.fixture(scope="session")
def sample_csv_file():
    """Создаёт временный CSV-файл для тестов в формате, понятном парсеру."""
    temp = tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False, encoding='utf-8-sig')
    temp.close()

    data = [
        ['Понедельник', '9:00-10:35', 'числитель', '101, 102'],
        ['Понедельник', '9:00-10:35', 'знаменатель', '103, 104'],
        ['Вторник', '10:50-12:25', 'числитель', '105, 106'],
        ['Среда', '12:45-14:20', 'знаменатель', '107'],
    ]

    with open(temp.name, 'w', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['День недели', 'Время пары', 'Тип недели', 'Аудитории'])
        writer.writerows(data)

    yield temp.name

    Path(temp.name).unlink()