from selenium import webdriver      # install selenium
from selenium.webdriver.common.by import By     # 搜尋物件使用 By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager    # install webdriver-manager 自動安裝,自動更新


def next_():
    anykey = input("EnterKey to next: ")


driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(10)
driver.get('https://www.google.com')
driver.maximize_window()

try:
    driver.find_element(By.ID, 'ken')
except NoSuchElementException as e:
    print("123456789", e)

next_()

