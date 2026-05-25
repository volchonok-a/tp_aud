import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app import app
from config import ALL_ROOMS, TIME_SLOTS

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestApiEndpoints:
    """Интеграционные тесты API (Flask)."""

    def test_api_free_rooms_valid_request(self, client):
        """Проверяет корректный запрос: мок занятых аудиторий, ответ 200 и возвращает список занятых."""
        mock_occupied = {'101', '102', '103'}
        with patch('app.get_occupied_rooms', return_value=mock_occupied):
            response = client.post('/api/free_rooms',
                                   data=json.dumps({
                                       'weekday': 'monday',
                                       'time_slot': TIME_SLOTS[0],   # "8:00 - 9:35"
                                       'week_type': 'числитель'
                                   }),
                                   content_type='application/json')
            data = json.loads(response.data)
            assert response.status_code == 200
            assert data['success'] is True
            assert data['occupied_rooms'] == sorted(['101', '102', '103'])

    def test_api_free_rooms_all_free(self, client):
        """Проверяет, что когда занятых аудиторий нет, в free_rooms попадают все возможные аудитории."""
        with patch('app.get_occupied_rooms', return_value=set()):
            response = client.post('/api/free_rooms',
                                   data=json.dumps({
                                       'weekday': 'monday',
                                       'time_slot': TIME_SLOTS[0],
                                       'week_type': 'числитель'
                                   }),
                                   content_type='application/json')
            data = json.loads(response.data)
            assert response.status_code == 200
            assert data['free_rooms'] == sorted(ALL_ROOMS)

    def test_api_free_rooms_all_occupied(self, client):
        """Проверяет, что если заняты все аудитории, список свободных пуст."""
        with patch('app.get_occupied_rooms', return_value=set(ALL_ROOMS)):
            response = client.post('/api/free_rooms',
                                   data=json.dumps({
                                       'weekday': 'monday',
                                       'time_slot': TIME_SLOTS[0],
                                       'week_type': 'числитель'
                                   }),
                                   content_type='application/json')
            data = json.loads(response.data)
            assert response.status_code == 200
            assert data['free_rooms'] == []

    def test_api_free_rooms_missing_data(self, client):
        """Проверяет, что при отсутствии обязательных полей в JSON сервер возвращает 500 и ошибку."""
        response = client.post('/api/free_rooms',
                               data=json.dumps({}),
                               content_type='application/json')
        data = json.loads(response.data)
        assert response.status_code == 500
        assert data['success'] is False
        assert 'error' in data

    def test_api_free_rooms_invalid_json(self, client):
        """Проверяет, что при отправке невалидного JSON сервер отвечает 500 с ошибкой."""
        response = client.post('/api/free_rooms',
                               data='not valid json',
                               content_type='application/json')
        data = json.loads(response.data)
        assert response.status_code == 500
        assert data['success'] is False