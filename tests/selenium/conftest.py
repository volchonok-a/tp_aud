import os
import sys
import threading
import time
from pathlib import Path
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Переходим в корень проекта
ROOT_DIR = Path(__file__).parent.parent.parent
os.chdir(ROOT_DIR)
sys.path.insert(0, str(ROOT_DIR))

# Импортируем app и явно указываем папку шаблонов
from app import app
app.template_folder = str(ROOT_DIR / 'templates')
app.static_folder = str(ROOT_DIR / 'static')

@pytest.fixture(scope="session")
def live_server():
    """Запускает Flask-сервер на порту 5001 для Selenium."""
    server = threading.Thread(target=lambda: app.run(port=5001, debug=False, use_reloader=False))
    server.daemon = True
    server.start()
    time.sleep(2)
    yield "http://127.0.0.1:5001"

@pytest.fixture(scope="function")
def driver(live_server):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.get(live_server)
    yield driver
    driver.quit()