import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class MainPage:
    """Page Object для главной страницы приложения."""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # Локаторы элементов
    WEEK_TYPE_SELECT = (By.ID, "weekType")
    WEEKDAY_SELECT = (By.ID, "weekday")
    TIME_SLOT_SELECT = (By.ID, "timeSlot")
    SEARCH_BUTTON = (By.XPATH, "//button[@type='submit']")
    LOADING = (By.ID, "loading")
    RESULT = (By.ID, "result")
    ERROR = (By.ID, "error")

    def select_week_type(self, value):
        Select(self.driver.find_element(*self.WEEK_TYPE_SELECT)).select_by_value(value)

    def select_weekday(self, value):
        Select(self.driver.find_element(*self.WEEKDAY_SELECT)).select_by_visible_text(value)

    def select_time_slot(self, value):
        Select(self.driver.find_element(*self.TIME_SLOT_SELECT)).select_by_visible_text(value)

    def click_search(self):
        self.driver.find_element(*self.SEARCH_BUTTON).click()

    def wait_for_result(self):
        self.wait.until(EC.visibility_of_element_located(self.RESULT))

    def wait_loading_hidden(self):
        self.wait.until(EC.invisibility_of_element_located(self.LOADING))

    def get_free_rooms(self):
        result_div = self.driver.find_element(*self.RESULT)
        return [r.text for r in result_div.find_elements(By.CLASS_NAME, "room-card")]

    def is_error_visible(self):
        return self.driver.find_element(*self.ERROR).is_displayed()

    def get_title(self):
        return self.driver.title


pytestmark = pytest.mark.selenium

class TestUISearch:
    """Набор UI тестов (Selenium)."""

    def test_page_loads(self, driver):
        """Проверяет, что главная страница открывается, и заголовок содержит нужную фразу."""
        page = MainPage(driver)
        assert "Свободные аудитории" in page.get_title()

    def test_search_valid_numerator_monday_first_slot(self, driver):
        """Проверяет успешный поиск: числитель, понедельник, первая пара. Результаты отображаются."""
        page = MainPage(driver)
        page.select_week_type("числитель")
        page.select_weekday("Понедельник")
        page.select_time_slot("8:00 - 9:35")
        page.click_search()
        page.wait_loading_hidden()
        page.wait_for_result()
        rooms = page.get_free_rooms()
        assert isinstance(rooms, list)

    def test_loading_indicator(self, driver):
        """Проверяет, что при отправке формы появляется индикатор загрузки, а затем исчезает."""
        page = MainPage(driver)
        page.select_week_type("числитель")
        page.select_weekday("Понедельник")
        page.select_time_slot("8:00 - 9:35")
        page.click_search()
        loading = driver.find_element(*MainPage.LOADING)
        assert loading.is_displayed()
        page.wait_loading_hidden()
        assert not loading.is_displayed()

    @pytest.mark.parametrize("week_type,weekday,time_slot", [
        ("числитель", "Понедельник", "8:00 - 9:35"),
        ("знаменатель", "Вторник", "9:45 - 11:20"),
        ("числитель", "Среда", "11:30-13:05"),
    ])
    def test_multiple_combinations(self, driver, week_type, weekday, time_slot):
        """Параметризованный тест: проверяет разные комбинации (числитель/ПН/8:00-9:35, знаменатель/ВТ/9:45-11:20, числитель/СР/11:30-13:05)."""
        page = MainPage(driver)
        page.select_week_type(week_type)
        page.select_weekday(weekday)
        page.select_time_slot(time_slot)
        page.click_search()
        page.wait_loading_hidden()
        page.wait_for_result()
        rooms = page.get_free_rooms()
        assert isinstance(rooms, list)

    def test_error_missing_data(self, driver):
        """Проверяет, что при попытке поиска без выбора дня и времени появляется блок с ошибкой."""
        page = MainPage(driver)
        page.click_search()
        assert page.is_error_visible()