import pytest
from selenium import webdriver


@pytest.fixture(autouse=True)
def browser():
    driver = webdriver.Chrome()

    yield driver
    driver.quit()
