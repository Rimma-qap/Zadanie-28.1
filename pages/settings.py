import os
from string import punctuation

from dotenv import load_dotenv
from faker import Faker

load_dotenv()

# Генерация данных для авторизации в системе
fake_ru = Faker("ru_RU")
fake_firstname = fake_ru.first_name()
fake_lastname = fake_ru.last_name()
fake_phone = fake_ru.phone_number()
fake_password = fake_ru.password()
fake_login = fake_ru.user_name()
fake_email = fake_ru.email()
fake_ls = 123456789012

valid_phone = os.getenv("PHONE")
valid_login = os.getenv("LOGIN")
valid_password = os.getenv("PASSWORD")
valid_email = os.getenv("EMAIL")
valid_pass_reg = os.getenv("PASSWORD_REG")
valid_ls = os.getenv("ACCOUNT")


def generate_string_rus(n):
    return "б" * n


def generate_string_en(n):
    return "x" * n


def english_chars():
    return "qwertyuiopasdfghjklzxcvbnm"


def russian_chars():
    return "абвгдеёжзиклмнопрстуфхцчшщъыьэюя"


def chinese_chars():  # 20 популярных китайских иероглифов
    return "的一是不了人我在有他这为之大来以个中上们"


def special_chars():
    return f"{punctuation}"
