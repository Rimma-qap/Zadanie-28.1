import time

import pytest

from pages.auth import AuthPage, RegPage
from pages.locators import RegLocators
from pages.settings import fake_firstname, fake_lastname, fake_password
from pages.temp_mail import RegEmail

ENV_FILE = ".env"
LINK = "/auth/realms/b2c/login-actions/registration"


@pytest.mark.reg
@pytest.mark.positive
def test_registration_page_smoke(browser):
    """
    TC-RIT-060
    Проверка страницы регистрации - smoke-тестирование
    """

    page = AuthPage(browser)
    page.enter_reg_page()

    assert page.get_relative_link() == LINK


@pytest.mark.reg
@pytest.mark.positive
def test_registration_page(browser):
    """
    TC-RIT-064
    Валидный вариант регистрации при использовании email
    и получения кода для входа на почту. Используем виртуальный почтовый
    ящик на портале '1secmail.com' и получаем данные через GET запросы.
    Сохраняем созданный email в файл .env.
    """

    # Запрос на получение валидного почтового ящика
    result_email, status_email = RegEmail().get_api_email()

    # Из запроса получаем валидный email
    email_reg = result_email[0]

    # Разделяем email на имя и домен
    # для использования в следующих запросах:
    sign_at = email_reg.find("@")
    mail_name = email_reg[0:sign_at]
    mail_domain = email_reg[sign_at + 1 : len(email_reg)]  # noqa: E203
    assert status_email == 200, "status_email error"
    assert len(result_email) > 0, "len(result_email) > 0 -> error"

    # Активируем окно ввода данных для прохождения регистрации на сайте.
    # Нажимаем на кнопку Зарегистрироваться:
    page = AuthPage(browser)
    page.enter_reg_page()
    browser.implicitly_wait(2)
    assert page.get_relative_link() == LINK

    page = RegPage(browser)

    # Вводим имя:
    page.enter_firstname(fake_firstname)
    browser.implicitly_wait(5)

    # Вводим фамилию:
    page.enter_lastname(fake_lastname)
    browser.implicitly_wait(5)

    # Вводим адрес почты/Email:
    page.enter_email(email_reg)
    browser.implicitly_wait(3)

    # Вводим пароль:
    page.enter_password(fake_password)
    browser.implicitly_wait(3)

    # Вводим подтверждение пароля:
    page.enter_pass_conf(fake_password)
    browser.implicitly_wait(3)

    # Нажимаем на кнопку 'Зарегистрироваться':
    page.btn_click()

    # Ждём, пока на почту придёт письмо
    time.sleep(30)

    # Проверяем почтовый ящик на наличие писем
    # и достаём ID последнего письма
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
    start_text = "Ваш код : "
    start_index = text_body.find(start_text) + len(start_text)
    end_index = start_index + 6
    reg_code = text_body[start_index:end_index]

    # Сверяем полученные данные с нашими ожиданиями
    assert status_code == 200, "status_code error"
    assert reg_code != "", "reg_code != [] error"

    browser.implicitly_wait(30)
    for i in range(0, 6):
        browser.find_elements(*RegLocators.REG_ONETIME_CODE)[i].send_keys(
            reg_code[i]
        )
        browser.implicitly_wait(5)
    browser.implicitly_wait(30)

    # Проверяем, что регистрация пройдена
    # и пользователь перенаправлен в личный кабинет
    assert (
        page.get_relative_link() == "/account_b2c/page"
    ), "Регистрация не пройдена"

    # В случае успешной регистрации
    # перезаписываем созданные пару email/пароль в файл .env
    page.driver.save_screenshot("reg_done.png")

    with open(ENV_FILE, "r", encoding="utf8") as file:
        lines = []
        for line in file.readlines():
            if "EMAIL=" in line:
                lines.append(f"EMAIL={str(email_reg)}\n")
            elif "PASSWORD_REG=" in line:
                lines.append(f'PASSWORD_REG="{fake_password}"\n')
            else:
                lines.append(line)

    with open(ENV_FILE, "w", encoding="utf8") as file:
        file.writelines(lines)
