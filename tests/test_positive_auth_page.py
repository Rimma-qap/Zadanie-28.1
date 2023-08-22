import pickle
import time

import pytest
from selenium.common.exceptions import NoSuchElementException

from pages.auth import AuthPage
from pages.locators import AuthLocators
from pages.settings import (
    valid_email,
    valid_login,
    valid_ls,
    valid_pass_reg,
    valid_password,
    valid_phone,
)

LINK = "/account_b2c/page"


def run_script(browser, username, password, file_name):
    page = AuthPage(browser)
    page.enter_username(username)
    page.enter_password(password)

    # Пауза на ввод капчи при ее появлении
    try:
        if browser.find_element(*AuthLocators.AUTH_CAPTCHA):
            time.sleep(20)
    except NoSuchElementException:
        pass

    page.btn_click_enter()
    page.driver.save_screenshot(f"{file_name}.png")

    with open(f"{file_name}_cookies.bin", "wb") as cookies:
        pickle.dump(browser.get_cookies(), cookies)

    assert page.get_relative_link() == LINK


@pytest.mark.auth
@pytest.mark.positive
def test_auth_page_smoke(browser):
    """
    TC-RIT-001
    Проверка страницы авторизации - smoke-тестирование
    """

    page = AuthPage(browser)

    assert (
        page.get_relative_link()
        == "/auth/realms/b2c/protocol/openid-connect/auth"
    )


@pytest.mark.auth
@pytest.mark.positive
@pytest.mark.parametrize(
    "username",
    [valid_phone, valid_email, valid_login, valid_ls],
    ids=["phone", "email", "login", "ls"],
)
def test_active_tab(browser, username):
    """
    TC-RIT-006, TC-RIT-007, TC-RIT-008, TC-RIT-009, TC-RIT-010, TC-RIT-011
    Проверка автоматического переключения табов:
    мобильный телефон/электронная почта/логин/лицевой счет
    """

    page = AuthPage(browser)

    # Поскольку лицевой счет определяется автоматически только
    # с вкладки 'Почта', то нажимаем на эту вкладку
    browser.find_element(*AuthLocators.AUTH_TAB_MAIL).click()

    page.enter_username(username)
    page.enter_password(valid_password)
    tab_text = browser.find_element(*AuthLocators.AUTH_ACTIVE_TAB).text

    if username == valid_phone:
        assert tab_text == "Телефон"

    elif username == valid_email:
        assert tab_text == "Почта"

    elif username == valid_login:
        assert tab_text == "Логин"

    else:
        assert tab_text == "Лицевой счёт"


@pytest.mark.auth
@pytest.mark.positive
@pytest.mark.parametrize(
    "username",
    [valid_phone, valid_login],
    ids=["valid phone", "valid login"],
)
def test_auth_page_phone_login(browser, username):
    """
    TC-RIT-016, TC-RIT-021
    Проверка авторизации по номеру телефона/логину и паролю
    """

    run_script(browser, username, valid_password, "auth_by_phone_login")


@pytest.mark.auth
@pytest.mark.positive
def test_auth_page_email(browser):
    """
    TC-RIT-019
    Проверка авторизации по почте и паролю
    """

    run_script(browser, valid_email, valid_pass_reg, "auth_by_email")
