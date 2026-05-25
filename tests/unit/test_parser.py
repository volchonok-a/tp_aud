import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from parser import get_occupied_rooms

pytestmark = pytest.mark.unit


class TestGetOccupiedRooms:
    """Тесты для функции get_occupied_rooms с моками."""

    def test_returns_set_when_no_data(self, mocker):
        """Проверяет, что при отсутствии данных (get_csv_data=[]) функция возвращает пустое множество."""
        mocker.patch('parser.get_csv_data', return_value=[])
        result = get_occupied_rooms('Понедельник', '8:00 - 9:35', 'числитель')
        assert isinstance(result, set)
        assert result == set()

    def test_exact_match_numerator(self, mocker):
        """Проверяет, что для числителя возвращаются правильные аудитории (101,102)."""
        mock_rows = [
            ['Понедельник', '8:00 - 9:35', '101', '102'],
            ['', '', '103', '104'],
        ]
        mocker.patch('parser.get_csv_data', return_value=mock_rows)

        def fake_parse(rows):
            return {
                "числитель": {"Понедельник": {"8:00 - 9:35": {"101", "102"}}},
                "знаменатель": {"Понедельник": {"8:00 - 9:35": {"103", "104"}}}
            }
        mocker.patch('parser.parse_schedule', side_effect=fake_parse)

        result = get_occupied_rooms('Понедельник', '8:00 - 9:35', 'числитель')
        assert result == {"101", "102"}

    def test_week_type_mismatch(self, mocker):
        """Проверяет, что для знаменателя возвращаются другие аудитории (103,104)."""
        mock_rows = [
            ['Понедельник', '8:00 - 9:35', '101', '102'],
            ['', '', '103', '104'],
        ]

        def fake_parse(rows):
            return {
                "числитель": {"Понедельник": {"8:00 - 9:35": {"101", "102"}}},
                "знаменатель": {"Понедельник": {"8:00 - 9:35": {"103", "104"}}}
            }
        mocker.patch('parser.get_csv_data', return_value=mock_rows)
        mocker.patch('parser.parse_schedule', side_effect=fake_parse)

        result = get_occupied_rooms('Понедельник', '8:00 - 9:35', 'знаменатель')
        assert result == {"103", "104"}

    def test_normalizes_day_names(self, mocker):
        """Проверяет, что английское название дня 'monday' преобразуется в 'Понедельник'."""
        mock_rows = [['Понедельник', '8:00 - 9:35', '101']]

        def fake_parse(rows):
            return {
                "числитель": {"Понедельник": {"8:00 - 9:35": {"101"}}},
                "знаменатель": {}
            }
        mocker.patch('parser.get_csv_data', return_value=mock_rows)
        mocker.patch('parser.parse_schedule', side_effect=fake_parse)

        result = get_occupied_rooms('monday', '8:00 - 9:35', 'числитель')
        assert result == {"101"}

    def test_empty_when_file_not_found(self, mocker):
        """Проверяет, что при отсутствии файла CSV функция возвращает пустое множество (не падает)."""
        mocker.patch('parser.get_csv_data', return_value=[])
        result = get_occupied_rooms('Понедельник', '8:00 - 9:35', 'числитель')
        assert result == set()