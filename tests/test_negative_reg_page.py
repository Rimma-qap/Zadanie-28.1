import pytest

from pages.auth import AuthPage, RegPage
from pages.locators import AuthLocators, RegLocators
from pages.settings import (
    chinese_chars,
    english_chars,
    fake_email,
    fake_firstname,
    fake_lastname,
    fake_password,
    generate_string_rus,
    russian_chars,
    special_chars,
    valid_email,
    valid_pass_reg,
    valid_phone,
)

MESSAGES = {
    "cyrillic": "Необходимо заполнить поле кириллицей. От 2 до 30 символов.",
    "phone_or_email_mask": "Введите телефон в формате +7ХХХХХХХХХХ "
    "или +375XXXXXXXXX, или email в формате example@email.ru",
    "account_exists": "Учётная запись уже существует",
    "passwords": "Пароли не совпадают",
}

LINK = "/auth/realms/b2c/login-actions/registration"


def run_script(
    browser,
    firstname=fake_firstname,
    lastname=fake_lastname,
    email=fake_email,
    password_1=fake_password,
    password_2=fake_password,
):
    # Нажимаем на кнопку Зарегистрироваться:
    page = AuthPage(browser)
    page.enter_reg_page()
    browser.implicitly_wait(2)
    assert page.get_relative_link() == LINK

    page = RegPage(browser)
    # Вводим имя:
    page.enter_firstname(firstname)
    browser.implicitly_wait(5)
    # Вводим фамилию:
    page.enter_lastname(lastname)
    browser.implicitly_wait(5)
    # Вводим адрес почты/Email:
    page.enter_email(email)
    browser.implicitly_wait(3)
    # Вводим пароль:
    page.enter_password(password_1)
    browser.implicitly_wait(3)
    # Вводим подтверждение пароля:
    page.enter_pass_conf(password_2)
    browser.implicitly_wait(3)
    # Нажимаем на кнопку 'Зарегистрироваться':
    page.btn_click()


@pytest.mark.reg
@pytest.mark.negative
@pytest.mark.parametrize(
    "firstname",
    [
        "",
        generate_string_rus(1),
        generate_string_rus(31),
        generate_string_rus(256),
        english_chars(),
        chinese_chars(),
        special_chars(),
        11111,
    ],
    ids=[
        "empty",
        "one char",
        "31 chars",
        "256 chars",
        "english",
        "chinese",
        "special",
        "number",
    ],
)
def test_registration_invalid_firstname(browser, firstname):
    """
    TC-RIT-065, TC-RIT-066, TC-RIT-067, TC-RIT-068, TC-RIT-069, TC-RIT-070,
    TC-RIT-071, TC-RIT-073
    Негативные сценарии регистрации на сайте, невалидный формат имени
    """

    run_script(browser=browser, firstname=firstname)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == MESSAGES["cyrillic"]


@pytest.mark.reg
@pytest.mark.negative
@pytest.mark.parametrize(
    "lastname",
    [
        "",
        generate_string_rus(1),
        generate_string_rus(31),
        generate_string_rus(256),
        english_chars(),
        chinese_chars(),
        special_chars(),
        11111,
    ],
    ids=[
        "empty",
        "one char",
        "31 chars",
        "256 chars",
        "english",
        "chinese",
        "special",
        "number",
    ],
)
def test_registration_invalid_lastname(browser, lastname):
    """
    TC-RIT-074, TC-RIT-075, TC-RIT-076, TC-RIT-077, TC-RIT-078, TC-RIT-079,
    TC-RIT-080, TC-RIT-082
    Негативные сценарии регистрации на сайте, невалидный формат фамилии
    """

    run_script(browser=browser, lastname=lastname)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == MESSAGES["cyrillic"]


@pytest.mark.reg
@pytest.mark.negative
@pytest.mark.parametrize(
    "phone",
    ["", 1, 7111111111, generate_string_rus(11), special_chars()],
    ids=["empty", "one digit", "10 digits", "string", "specials"],
)
def test_registration_invalid_phone(browser, phone):
    """
    TC-RIT-068, TC-RIT-069, TC-RIT-070, TC-RIT-071, TC-RIT-073
    Негативные сценарии регистрации на сайте,
    невалидный формат номера телефона
    """

    run_script(browser=browser, email=phone)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == MESSAGES["phone_or_email_mask"]


@pytest.mark.reg
@pytest.mark.negative
@pytest.mark.parametrize(
    "email",
    [
        "",
        "@",
        "@.",
        ".",
        generate_string_rus(20),
        f"{russian_chars()}@mail.ru",
        f"{chinese_chars()}@mail.ru",
        11111,
    ],
    ids=[
        "empty",
        "at",
        "at point",
        "point",
        "string",
        "russian",
        "chinese",
        "numbers",
    ],
)
def test_registration_invalid_email(browser, email):
    """
    TC-RIT-083, TC-RIT-084, TC-RIT-085, TC-RIT-087, TC-RIT-088
    Негативные сценарии регистрации на сайте,
    невалидный формат электронной почты
    """

    run_script(browser=browser, email=email)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == MESSAGES["phone_or_email_mask"]


@pytest.mark.reg
@pytest.mark.negative
@pytest.mark.parametrize(
    "address", [valid_phone, valid_email], ids=["living phone", "living email"]
)
def test_registration_living_account(browser, address):
    """
    TC-RIT-089
    Негативные сценарии регистрации на сайте, проверка
    на существование аккаунта по номеру мобильного телефона
    или адреса электронной почты
    """

    run_script(browser=browser, email=address)

    card_modal_title = browser.find_element(*RegLocators.REG_CARD_MODAL)
    assert card_modal_title.text == MESSAGES["account_exists"]


@pytest.mark.reg
@pytest.mark.negative
def test_registration_diff_passwords(browser):
    """
    TC-RIT-090
    Негативные сценарии регистрации на сайте,
    проверка на совпадение паролей в полях ввода 'Пароль'
    и 'Подтверждение пароля'.
    """

    run_script(browser=browser, password_2=valid_pass_reg)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == MESSAGES["passwords"]
