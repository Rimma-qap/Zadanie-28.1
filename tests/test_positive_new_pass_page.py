import time

import pytest

from pages.locators import NewPassLocators
from pages.settings import fake_password
from tests.test_negative_new_pass_page import run_script

ENV_FILE = ".env"


@pytest.mark.newpass
@pytest.mark.positive
def test_forgot_password_page_positive(browser):
    """
    TC-RIT-044
    Проверка восстановления пароля по почте.
    """

    page = run_script(browser)
    time.sleep(10)

    new_pass = fake_password
    browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS).send_keys(new_pass)
    time.sleep(3)
    browser.find_element(*NewPassLocators.NEWPASS_NEW_PASS_CONFIRM).send_keys(
        new_pass
    )
    browser.find_element(*NewPassLocators.NEWPASS_BTN_SAVE).click()
    time.sleep(60)

    assert (
        page.get_relative_link()
        == "/auth/realms/b2c/login-actions/authenticate"
    )

    # В случае успешной смены пароля перезаписываем его в файл .env
    with open(ENV_FILE, "r", encoding="utf8") as file:
        lines = []
        for line in file.readlines():
            if "PASSWORD_REG=" in line:
                lines.append(f'PASSWORD_REG="{fake_password}"\n')
            else:
                lines.append(line)

    with open(ENV_FILE, "w", encoding="utf8") as file:
        file.writelines(lines)
