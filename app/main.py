import logging
import pickle
import time
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import Path
from random import uniform

# from typing import Self

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote import webelement
from webdriver_manager.chrome import ChromeDriverManager

from app.logger import Logger
from app.settings import get_env, Settings


@dataclass(frozen=True, kw_only=True, slots=True)
class LocateElementBy:
    XPATH: str | None = None
    LINK_TEXT: str | None = None
    CLASS_NAME: str | None = None
    CSS_SELECTOR: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class PageElements:
    enter_button: LocateElementBy
    link_pseudo: LocateElementBy
    login_input: LocateElementBy
    password_input: LocateElementBy
    login_button: LocateElementBy
    captcha: LocateElementBy
    resumes: LocateElementBy
    resume_title: LocateElementBy
    resume_update_button: LocateElementBy


# fmt: off
page_elements = PageElements(
    enter_button=LocateElementBy(
        LINK_TEXT="Войти"
    ),
    link_pseudo=LocateElementBy(
        XPATH="//div[@class='account-login-actions']//button[@class='bloko-link bloko-link_pseudo']"
    ),
    login_input=LocateElementBy(
        XPATH="//div[@class='bloko-form-item']//input[""@type='text']"
    ),
    password_input=LocateElementBy(
        XPATH="//input[@type='password']"
    ),
    login_button=LocateElementBy(
        CLASS_NAME="bloko-form-row",  # id: 1
        CSS_SELECTOR=".account-login-actions > button:nth-child(1)"
    ),
    captcha=LocateElementBy(
        XPATH="//*[@data-qa='mainmenu_myResumes']"
    ),
    resumes=LocateElementBy(
        XPATH="//a[contains(text(),'Мои резюме')]",
    ),
    resume_title=LocateElementBy(
        XPATH="//*[@data-qa='resume-title']",
        CSS_SELECTOR="a.applicant-resumes-title span.b-marker"
    ),
    resume_update_button=LocateElementBy(
        XPATH="//button[@data-qa='resume-update-button']"
    )
)
# fmt: on

settings: Settings = get_env()

log = Logger(logger_name=__name__, logger_level=logging.DEBUG).get(
    only_console=False,
    tg_logger=settings.telegram_logging,
    tg_token=settings.TG_API_KEY.get_secret_value(),
    tg_chat_id=settings.TG_CHAT_ID,
)


class ChromeBrowserOptions:
    def __init__(self):
        self.__options: Options = webdriver.ChromeOptions()

    def __call__(self) -> Options:
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


def sleep(
    secs: float | int = 1.0,
):
    secs = min(secs, 600.0)
    secs += uniform(0.1, 3.5)
    return time.sleep(secs)


class ResumeRaising:
    def __init__(self, cookies_path: str, base_url: str = "https://hh.ru/"):
        self.driver: WebDriver | None = None
        self.cookies_path: str = cookies_path
        self.base_url: str = base_url

    @contextmanager
    def __call__(
        self,
        service: ChromeDriverManager,
        options: ChromeBrowserOptions,
    ):
        self.driver: WebDriver = webdriver.Chrome(
            service=Service(service.install()), options=options()
        )

        self.driver.get(self.base_url)
        log.debug("Opened Browser")
        self.driver.implicitly_wait(12)

        try:
            yield self
        finally:
            self.driver.quit()
            self.driver = None
            sleep(12)
            log.debug("Closed Browser")

    def load_cookies(self) -> bool:
        try:
            with open(file=self.cookies_path, mode="rb") as f:
                cookies = pickle.load(f)
        except FileNotFoundError:
            if not Path(self.cookies_path).parent.exists():
                Path(self.cookies_path).parent.mkdir(
                    parents=True, exist_ok=True
                )
            log.debug("Cookies not found")
            return False
        else:
            if not cookies:
                log.warning("Cookie is empty")
                return False
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            else:
                log.debug("Cookies added")
            return True

    def save_cookies(self):  # -> Self:
        with open(file=self.cookies_path, mode="wb") as f:
            pickle.dump(self.driver.get_cookies(), f)
        log.debug("Cookies saved")
        return self

    def remove_cookie_file(self):  # -> Self:
        try:
            Path(self.cookies_path).unlink(missing_ok=False)
        except FileNotFoundError:
            log.warning("Cookies not found to delete")
        else:
            log.debug("Deleting any cookies")
        finally:
            return self

    def try_finding_captcha(self):  # -> Self:
        try:
            self.driver.find_element(
                by=By.XPATH, value=page_elements.captcha.XPATH
            )
        except NoSuchElementException:
            log.debug("Captcha found. Pass it and push the button")
            sleep(12)
            log.info("Logged into the site")
        return self

    def login(self):  # -
        self.driver.find_element(
            by=By.LINK_TEXT, value=page_elements.enter_button.LINK_TEXT
        ).click()
        log.debug("'Enter' button pressed")
        # WebDriverWait(self.driver, 15).until(
        #     EC.url_changes(self.driver.current_url)
        # )
        self.driver.implicitly_wait(10)
        return self

    def auth(self, username: str, password: str):  # -> Self:

        try:
            self.driver.find_element(
                by=By.XPATH, value=page_elements.password_input.XPATH
            )
        except NoSuchElementException:
            self.driver.find_element(
                by=By.XPATH, value=page_elements.link_pseudo.XPATH
            ).click()
        log.debug("Authorization start")

        # Input email login
        login_input = self.driver.find_element(
            by=By.XPATH, value=page_elements.login_input.XPATH
        )
        login_input.clear()
        login_input.send_keys(username)
        log.debug("Username entered")

        # Input password
        password_input = self.driver.find_element(
            by=By.XPATH, value=page_elements.password_input.XPATH
        )
        password_input.send_keys(password)
        log.debug("Password entered")

        # Login with creds
        try:
            self.driver.find_element(
                by=By.CSS_SELECTOR,
                value=page_elements.login_button.CSS_SELECTOR,
            ).click()
        except NoSuchElementException:
            self.driver.find_elements(
                by=By.CLASS_NAME,
                value=page_elements.login_button.CLASS_NAME,
            )[1].click()
        log.debug("'Login' button pressed after input")

        WebDriverWait(self.driver, 15).until(
            EC.url_changes(self.driver.current_url)
        )
        self.try_finding_captcha()
        return self

    def open_resumes(self):  # -> Self:
        try:
            self.driver.find_element(
                # by=By.CSS_SELECTOR, value=page_elements.resumes.CSS_SELECTOR
                by=By.XPATH, value=page_elements.resumes.XPATH
            ).click()
        except NoSuchElementException:
            self.login()
        except ElementClickInterceptedException:
            pass
        else:
            WebDriverWait(self.driver, 15).until(
                EC.url_changes(self.driver.current_url)
            )
        finally:
            log.debug("Open Resumes")
            return self

    def raise_resume(self):  # -> Self:
        assert_text: str = "Поднять в поиске"

        resume_titles: list[webelement] = self.driver.find_elements(
            by=By.XPATH, value=page_elements.resume_title.XPATH
        )
        update_buttons: list[webelement] = self.driver.find_elements(
            by=By.XPATH, value=page_elements.resume_update_button.XPATH
        )
        raised_resume: int = 0

        for title, button in zip_longest(resume_titles, update_buttons):
            try:
                if button.text != assert_text:
                    log.info(
                        "● Резюме '*%s*' было поднято ранее",
                        title.text
                    )
                    continue

                button.click()
                try:
                    log.info(
                        "● Резюме '*%s*' поднято",
                        title.text
                    )
                    raised_resume += 1
                except AttributeError:
                    log.debug(title, button)
                    
            except ElementClickInterceptedException:
                log.info(
                    "● Резюме '*%s*' было поднято ранее",
                    title,
                )
            except StaleElementReferenceException:
                pass
            finally:
                sleep()
        else:
            if raised_resume:
                log.info(
                    "\nОбновление завершено, в поиске поднято %s резюме",
                    raised_resume,
                )
            else:
                log.info(
                    "\nОбновление завершено, Нет возможных резюме для "
                    "обновления"
                )
        return self


if __name__ == "__main__":
    # self.driver_manager = Service(ChromeDriverManager().install())
    resume = ResumeRaising(cookies_path=settings.COOKIES_PATH)

    with resume(
        options=ChromeBrowserOptions(), service=ChromeDriverManager()
    ) as rr:
        rr: ResumeRaising

        log.debug("Started raising resume")
        if rr.load_cookies():
            rr.login()
        else:
            rr.login().auth(
                username=settings.HH_EMAIL_LOGIN.get_secret_value(),
                password=settings.HH_PASSWORD.get_secret_value(),
            )
        
        rr.open_resumes().save_cookies().raise_resume()

        # log.info("Следующая попытка поднять резюме в поиске через ~4 часа")
        # time.sleep(
        #     60 * 60 * 4 + uniform(20.0, 600.0)
        # )  # 60 * 60  * 4 == 4 hours
        # log.info("Автоматическое поднятие резюме в поиске началось")
