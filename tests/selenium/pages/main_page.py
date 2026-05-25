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
    WEEK_TYPE_RADIO_NUMERATOR = (By.XPATH, "//input[@value='числитель']")
    WEEK_TYPE_RADIO_DENOMINATOR = (By.XPATH, "//input[@value='знаменатель']")
    WEEKDAY_SELECT = (By.ID, "weekday")
    TIME_SLOT_SELECT = (By.ID, "timeSlot")
    SEARCH_BUTTON = (By.XPATH, "//button[contains(text(), 'Найти')]")
    RESULT_CONTAINER = (By.CLASS_NAME, "result")
    FREE_ROOMS_CONTAINER = (By.CLASS_NAME, "rooms-grid")
    LOADING_SPINNER = (By.CLASS_NAME, "loading")
    ERROR_MESSAGE = (By.CLASS_NAME, "error")

    def select_week_type(self, week_type):
        """Выбирает тип недели (числитель/знаменатель)."""
        if week_type == "числитель":
            element = self.driver.find_element(*self.WEEK_TYPE_RADIO_NUMERATOR)
        else:
            element = self.driver.find_element(*self.WEEK_TYPE_RADIO_DENOMINATOR)
        element.click()

    def select_weekday(self, day_name):
        """Выбирает день недели по названию."""
        select = Select(self.driver.find_element(*self.WEEKDAY_SELECT))
        select.select_by_visible_text(day_name)

    def select_time_slot(self, time_slot):
        """Выбирает временной слот."""
        select = Select(self.driver.find_element(*self.TIME_SLOT_SELECT))
        select.select_by_visible_text(time_slot)

    def click_search(self):
        """Нажимает кнопку поиска."""
        button = self.driver.find_element(*self.SEARCH_BUTTON)
        button.click()

    def wait_for_results(self):
        """Ожидает появления результатов."""
        self.wait.until(EC.visibility_of_element_located(self.RESULT_CONTAINER))

    def wait_for_loading_complete(self):
        """Ожидает исчезновения индикатора загрузки."""
        self.wait.until(EC.invisibility_of_element_located(self.LOADING_SPINNER))

    def get_free_rooms(self):
        """Возвращает список свободных аудиторий."""
        container = self.driver.find_element(*self.FREE_ROOMS_CONTAINER)
        room_cards = container.find_elements(By.CLASS_NAME, "room-card")
        return [card.text for card in room_cards]

    def get_occupied_rooms(self):
        """Возвращает список занятых аудиторий."""
        container = self.driver.find_element(*self.FREE_ROOMS_CONTAINER)
        room_cards = container.find_elements(By.CLASS_NAME, "room-card.occupied")
        return [card.text for card in room_cards]

    def has_error(self):
        """Проверяет наличие сообщения об ошибке."""
        return self.driver.find_element(*self.ERROR_MESSAGE).is_displayed()

    def get_error_text(self):
        """Возвращает текст сообщения об ошибке."""
        return self.driver.find_element(*self.ERROR_MESSAGE).text

    def is_result_visible(self):
        """Проверяет, виден ли блок с результатами."""
        return self.driver.find_element(*self.RESULT_CONTAINER).is_displayed()