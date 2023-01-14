from selenium import webdriver
from selenium.webdriver.common.by import By     # 搜尋物件使用 By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from PIL import Image
import pytesseract
import os

# 記得安裝 Tesseract-OCR 外部程式
os.environ['PATH'] = "C:\Program Files\Tesseract-OCR;" + os.environ['PATH']     # Tesseract-OCR 目錄 加入系統 PATH
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://eip.epbks.com.tw/Account/Login')
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="_verification_img"]')))
img = driver.find_element(By.XPATH, '//*[@id="_verification_img"]')
img_name = "captcha_login.png"
# print(img.screenshot_as_png)
img.screenshot(img_name)        # 這個方式存圖檔比較不適合 pytesseract 辨識率不好
# driver.find_element(By.XPATH, '//*[@id="accountID"]').send_keys("F224719666")
# driver.find_element(By.XPATH, '//*[@id="password"]').send_keys("Iven1101")
# driver.find_element(By.XPATH, '//*[@id="verify"]').send_keys("s7641")
img = Image.open(img_name)
print(img.format, img.size, img.mode)
img.show()
text = pytesseract.image_to_string(img, lang='eng')
text = text.replace("‘", "").replace(".", "").replace("“", "")
print(text)
driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/div/div[5]/div/input[2]').send_keys(text)
