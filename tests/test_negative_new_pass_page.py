import time

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from pages.auth import NewPassPage
from pages.locators import AuthLocators, NewPassLocators
from pages.settings import (
    generate_string_en,
    generate_string_rus,
    special_chars,
    valid_email,
    valid_pass_reg,
)
from pages.temp_mail import RegEmail


def input_new_pass(browser, new_pass, new_pass_conf):
    elem_new_pass = browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS)
    elem_pass_conf = browser.find_element(
        *NewPassLocators.NEWPASS_NEW_PASS_CONFIRM
    )

    elem_new_pass.send_keys(Keys.CONTROL, "a")
    elem_new_pass.send_keys(Keys.DELETE)

    elem_pass_conf.send_keys(Keys.CONTROL, "a")
    elem_pass_conf.send_keys(Keys.DELETE)

    elem_new_pass.send_keys(new_pass)
    elem_pass_conf.send_keys(new_pass_conf)


def run_script(browser):
    # Разделяем email на имя и домен для использования в следующих запросах:
    sign_at = valid_email.find("@")
    mail_name = valid_email[0:sign_at]
    mail_domain = valid_email[sign_at + 1 : len(valid_email)]  # noqa: E203

    page = NewPassPage(browser)
    page.enter_username(valid_email)

    # Пауза на ввод капчи при ее появлении
    try:
        if browser.find_element(*AuthLocators.AUTH_CAPTCHA):
            time.sleep(20)
    except NoSuchElementException:
        pass

    page.btn_click_continue()

    # Ждём, пока на почту придёт письмо
    time.sleep(30)

    # Проверяем почтовый ящик на наличие писем и достаём ID последнего письма
    result_id, status_id = RegEmail().get_id_letter(mail_name, mail_domain)

    # Получаем id письма с кодом из почтового ящика:
    id_letter = result_id[0].get("id")

    # Сверяем полученные данные с нашими ожиданиями
    assert status_id == 200, "status_id error"
    assert id_letter > 0, "id_letter > 0 error"

    # Получаем код регистрации из письма от Ростелекома
    result_code, status_code = RegEmail().get_reg_code(
        mail_name, mail_domain, str(id_letter)
    )

    # Получаем body из текста письма:
    text_body = result_code.get("body")

    # Извлекаем код из текста методом find:
    start_text = "Ваш код: "
    start_index = text_body.find(start_text) + len(start_text)
    end_index = start_index + 6
    reg_code = text_body[start_index:end_index]

    # Сверяем полученные данные с нашими ожиданиями
    assert status_code == 200, "status_code error"
    assert reg_code != "", "reg_code != [] error"

    browser.implicitly_wait(30)
    for i in range(0, 6):
        browser.find_elements(*NewPassLocators.NEWPASS_ONETIME_CODE)[
            i
        ].send_keys(reg_code[i])

        browser.implicitly_wait(5)

    return page


@pytest.mark.newpass
@pytest.mark.negative
def test_forgot_password_page_negative(browser):
    """
    TC-RIT-051, TC-RIT-053, TC-RIT-054, TC-RIT-055, TC-RIT-056, TC-RIT-057,
    TC-RIT-058
    Проверка восстановления пароля по почте - негативные сценарии.
    Далее уже внутри этого теста рассматриваются 7 различных сценариев.
    """

    run_script(browser)
    time.sleep(10)

    # 1. Новый пароль - менее 8 символов
    new_pass = valid_pass_reg[0:7]
    input_new_pass(browser, new_pass, new_pass)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == "Длина пароля должна быть не менее 8 символов"

    # 2. Новый пароль - более 20 символов
    new_pass = valid_pass_reg[0:7] * 3
    input_new_pass(browser, new_pass, new_pass)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == "Длина пароля должна быть не более 20 символов"

    # 3. Новый пароль - пароль не содержит заглавные буквы
    new_pass = valid_pass_reg.lower()
    input_new_pass(browser, new_pass, new_pass)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert (
        error_mess.text
        == "Пароль должен содержать хотя бы одну заглавную букву"
    )

    # 4. Новый пароль - пароль не содержит строчные буквы
    new_pass = valid_pass_reg.upper()
    input_new_pass(browser, new_pass, new_pass)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert (
        error_mess.text
        == "Пароль должен содержать хотя бы одну строчную букву"
    )

    # 5. Новый пароль - пароль включает в себя кириллицу
    new_pass = f"{valid_pass_reg}{generate_string_rus(1)}"
    input_new_pass(browser, new_pass, new_pass)

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == "Пароль должен содержать только латинские буквы"

    # 6. Новый пароль отличается от пароля в поле 'Подтверждение пароля'
    new_pass = f"{valid_pass_reg[0:8]}{generate_string_en(2)}"
    new_pass_conf = f"{valid_pass_reg[0:8]}{generate_string_en(4)}"

    input_new_pass(browser, new_pass, new_pass_conf)

    browser.find_element(*NewPassLocators.NEWPASS_BTN_SAVE).click()

    error_mess = browser.find_element(*AuthLocators.AUTH_MESS_ERROR)
    assert error_mess.text == "Пароли не совпадают"

    # 7. Новый пароль - идентичен предыдущему
    new_pass = valid_pass_reg
    input_new_pass(browser, new_pass, new_pass)
    browser.find_element(*NewPassLocators.NEWPASS_BTN_SAVE).click()

    error_mess = browser.find_element(*AuthLocators.AUTH_FORM_ERROR)
    assert (
        error_mess.text
        == "Этот пароль уже использовался, укажите другой пароль"
    )
