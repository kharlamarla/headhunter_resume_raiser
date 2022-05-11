import time
from random import uniform

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from webdriver_manager.chrome import ChromeDriverManager

from __init__ import *


class ChromeBrowserOptions:
    def __init__(self):
        self.__options: ChromeOptions = webdriver.ChromeOptions()

    def __call__(self):
        self.__options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        self.__options.add_experimental_option("useAutomationExtension", False)
        self.__options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )
        self.__options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )
        self.__options.add_argument("--headless")
        self.__options.add_argument("--no-sandbox")
        self.__options.add_argument("--disable-dev-shm-usage")
        return self.__options


log = get_logger(__name__, only_console=False)

browser_options = ChromeBrowserOptions()
# chrome_driver = webdriver.Chrome(
#     service=Service(ChromeDriverManager().install()),
#     options=browser_options(),
# )

url: str = "https://hh.ru/account/login"


def sleep(
    default_delay: float = 1.0,
    jitter: tuple[float, float] = (0.1, 1.0),
):
    delay: float = min(1.0, default_delay)
    delay += uniform(*jitter)
    return time.sleep(delay)


def slap_resume(driver):
    with driver:
        driver.get(url)
        log.debug(
            "Открыт браузер, зашёл на сайт (%s) поднять резюме..",
            driver.current_url,
        )

        # Войти с паролем
        log.debug("Выбираю 'Войти с паролем' для ввода логина и пароля..")
        driver.find_element(
            by=By.XPATH,
            value=f"""//*[@id="HH-React-Root"]/div/div[4]/div[
            1]/div/div/div/div/div/div[1]/div[1]/div[1]/div[2]/div/div/form/div[4]/button[2]""",
        ).click()
        sleep()

        # Ввод логина
        login_input = driver.find_element(
            by=By.XPATH,
            value="""//*[@id="HH-React-Root"]/div/div[4]/div[
            1]/div/div/div/div/div/div[1]/div[1]/div[1]/div[2]/div/form/div[1]/input""",
        )
        login_input.clear()
        login_input.send_keys(settings.HH_EMAIL_LOGIN)
        log.debug("Ввёл логин..")
        sleep()

        # Ввод пароля
        pass_input = driver.find_element(
            By.XPATH,
            """//*[@id="HH-React-Root"]/div/div[4]/div[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div[2]/div/form/div[2]/span/input""",
        )
        pass_input.clear()
        pass_input.send_keys(settings.HH_PASSWORD)
        log.debug("Ввёл пароль..")
        sleep()

        # Авторизоваться
        try:
            auth = driver.find_elements(
                by=By.CSS_SELECTOR,
                value=".account-login-actions > button:nth-child(1)",
            )
            auth[0].click()
        except NoSuchElementException:
            auth = driver.find_elements(
                by=By.CLASS_NAME, value="bloko-from-row"
            )
            auth[1].click()
        log.debug("Нажал на кнопку авторизации.. (%s)", driver.current_url)
        WebDriverWait(driver, 15).until(EC.url_changes(driver.current_url))
        log.debug(driver.current_url)

        # Переход к списку резюме
        my_resumes = driver.find_element(
            by=By.XPATH,
            value=f"""//*[@id="HH-React-Root"]/div/div[2]/div[1]/div/div/div/div[1]/a""",
        )
        my_resumes.click()
        log.debug(
            "Перехожу к разделу с 'Мои резюме'.. (%s)", driver.current_url
        )
        sleep(5)

        # Обработка всех резюме
        raised_resume: int = 0
        # TODO: обработать элементы с резюме внутри элемента
        for i in range(2, 100, 2):
            # fmt: off
            selector_base = f"div.bloko-column.bloko-column_xs-4.bloko-column_s-8.bloko-column_m-8.bloko-column_l-11 > div:nth-child({i})"
            title_selector = " > div > h3"
            raise_button_selector = " > div > " \
                               "div.applicant-resumes-recommendations > div.applicant-resumes-recommendations-buttons > div:nth-child(1)"
            assert_text = "Поднять в поиске"
            # fmt: on
            try:
                resume_title = driver.find_element(
                    by=By.CSS_SELECTOR, value=selector_base + title_selector
                ).text
                resume_raise_button = driver.find_element(
                    by=By.CSS_SELECTOR,
                    value=selector_base + raise_button_selector,
                )
                if resume_raise_button.text == assert_text:
                    log.info("Резюме '%s' поднято в поиске", resume_title)
                    resume_raise_button.click()
                    raised_resume += 1
                else:
                    log.info(
                        "Резюме '%s' было поднято в поиске ранее", resume_title
                    )
                sleep()
            except NoSuchElementException:
                if raised_resume:
                    log.info(
                        f"Обновление резюме на HH.ru: Обход завершен, "
                        f"в поиске поднято %s резюме",
                        raised_resume,
                    )
                else:
                    log.info(
                        f"Обновление резюме на HH.ru: Нет объявлений для "
                        f"поднятия в поиске :("
                    )
                break
        log.debug("Закрыл браузер..")


if __name__ == "__main__":
    while True:
        slap_resume(
            driver=webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=browser_options(),
            )
        )
        log.info("Следующая попытка поднять резюме в поиске через ~4 часа")
        sleep(14400.0, (20.0, 600.0))  # 60 * 60 * 4 == 4 hours
        log.info("Автоматическое поднятие резюме в поиске началось")
