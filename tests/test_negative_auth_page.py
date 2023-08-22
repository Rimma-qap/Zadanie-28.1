import time

import pytest
from selenium.common.exceptions import NoSuchElementException

from pages.auth import AuthPage
from pages.locators import AuthLocators
from pages.settings import (
    fake_email,
    fake_login,
    fake_ls,
    fake_password,
    fake_phone,
    valid_email,
    valid_login,
    valid_ls,
    valid_pass_reg,
    valid_password,
    valid_phone,
)

MESSAGES = {
    "invalid_account_or_password": "Неверный логин или пароль",
    "invalid_phone_mask": "Неверный формат телефона",
    "inputs": [
        "Введите номер телефона",
        "Введите адрес, указанный при регистрации",
        "Введите логин, указанный при регистрации",
        "Введите номер вашего лицевого счета",
    ],
}
COLOR = "#ff4f12"


def run_script(browser, username, password, is_ls=False):
    page = AuthPage(browser)

    # Поскольку лицевой счет определяется автоматически только
    # с вкладки 'Почта', то нажимаем на эту вкладку
    if is_ls:
        browser.find_element(*AuthLocators.AUTH_TAB_MAIL).click()

    page.enter_username(username)
    page.enter_password(password)

    # Пауза на ввод капчи при ее появлении
    try:
        if browser.find_element(*AuthLocators.AUTH_CAPTCHA):
            time.sleep(20)
    except NoSuchElementException:
        pass

    page.btn_click_enter()
    browser.implicitly_wait(10)
    return page


@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.parametrize(
    "username",
    [fake_phone, fake_login, fake_ls],
    ids=["fake phone", "fake login", "fake service account"],
)
def test_auth_page_fake_phone_login_account(browser, username):
    """
    TC-RIT-018
    Проверка авторизации по номеру телефона, логину, лицевому счету и паролю,
    неверный номер/логин/лицевой счет.
    """

    page = run_script(browser, username, valid_password, True)

    error_mess = browser.find_element(*AuthLocators.AUTH_FORM_ERROR)
    forgot_pass = browser.find_element(*AuthLocators.AUTH_FORGOT_PASSWORD)

    assert (
        error_mess.text == MESSAGES["invalid_account_or_password"]
        and page.check_color(forgot_pass) == COLOR
    )


@pytest.mark.auth
@pytest.mark.negative
def test_auth_page_fake_email(browser):
    """
    TC-RIT-025
    Проверка авторизации по почте и паролю, неверная почта
    """

    page = run_script(browser, fake_email, valid_pass_reg)

    error_mess = browser.find_element(*AuthLocators.AUTH_FORM_ERROR)
    forgot_pass = browser.find_element(*AuthLocators.AUTH_FORGOT_PASSWORD)

    assert (
        error_mess.text == MESSAGES["invalid_account_or_password"]
        and page.check_color(forgot_pass) == COLOR
    )


@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.parametrize(
    "username",
    [valid_phone, valid_email, valid_login, valid_ls],
    ids=["valid phone", "valid login", "valid email", "valid_ls"],
)
def test_auth_page_fake_password(browser, username):
    """
    TC-RIT-017, TC-RIT-020, TC-RIT-022, TC-RIT-024
    Проверка авторизации по номеру телефона/почте/логину/лицевому счету
    и паролю.
    Неверный пароль.
    """

    page = run_script(browser, username, fake_password, True)

    error_mess = browser.find_element(*AuthLocators.AUTH_FORM_ERROR)
    forgot_pass = browser.find_element(*AuthLocators.AUTH_FORGOT_PASSWORD)

    assert (
        error_mess.text == MESSAGES["invalid_account_or_password"]
        and page.check_color(forgot_pass) == COLOR
    )


@pytest.mark.auth
@pytest.mark.negative
def test_auth_page_empty_username(browser):
    """
    TC-RIT-027, TC-RIT-028, TC-RIT-029, TC-RIT-030
    Проверка авторизации по номеру телефона/почте/логину/лицевому счету -
    пустой строке и паролю
    """

    run_script(browser, "", valid_password, True)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text in MESSAGES["inputs"]


@pytest.mark.auth
@pytest.mark.negative
@pytest.mark.parametrize(
    "username", [1, 111111111], ids=["one digit", "9 digits"]
)
def test_auth_page_invalid_phone(browser, username):
    """
    TC-RIT-031, TC-RIT-032
    Проверка авторизации по номеру телефона и паролю, неверный формат телефона
    """

    run_script(browser, username, valid_password)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == MESSAGES["invalid_phone_mask"]
