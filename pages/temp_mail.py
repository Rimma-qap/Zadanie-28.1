from json.decoder import JSONDecodeError

import requests

# Используем сайт 1secmail.com для создания виртуального email
TEMP_EMAIL_URL = "https://www.1secmail.com/api/v1/"


class RegEmail:
    def __init__(self):
        self.base_url = TEMP_EMAIL_URL

    def get_api_email(self) -> tuple:
        """Получаем случайный адрес электронной почты"""

        action = {"action": "genRandomMailbox", "count": 1}
        res = requests.get(self.base_url, params=action)
        status_email = res.status_code

        try:
            result_email = res.json()
        except JSONDecodeError:
            result_email = res.text
        return result_email, status_email

    def get_id_letter(self, login: str, domain: str) -> tuple:
        """Проверяем mailbox, получаем mail_id"""

        action = {"action": "getMessages", "login": login, "domain": domain}
        res = requests.get(self.base_url, params=action)
        status_id = res.status_code

        try:
            result_id = res.json()
        except JSONDecodeError:
            result_id = res.text
        return result_id, status_id

    def get_reg_code(self, login: str, domain: str, ids: str) -> tuple:
        """Получаем письмо с кодом регистрации от Ростелекома (id=ids)"""

        action = {
            "action": "readMessage",
            "login": login,
            "domain": domain,
            "id": ids,
        }
        res = requests.get(self.base_url, params=action)
        status_code = res.status_code

        try:
            result_code = res.json()
        except JSONDecodeError:
            result_code = res.text
        return result_code, status_code
