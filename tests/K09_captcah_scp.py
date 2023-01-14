from selenium import webdriver
from selenium.webdriver.common.by import By     # 搜尋物件使用 By
from webdriver_manager.chrome import ChromeDriverManager
import time
import base64
from PIL import Image
import pytesseract
import os

# 記得安裝 Tesseract-OCR 外部程式
os.environ['PATH'] = "C:\Program Files\Tesseract-OCR;" + os.environ['PATH']     # Tesseract-OCR 目錄 加入系統 PATH
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www3.hl.gov.tw/ght/modify_adv.asp')        # 鄉親票查詢時間已過就不能再查
time.sleep(5)

img_base64 = driver.execute_script("""
    var ele = arguments[0];
    var cnv = document.createElement('canvas');
    cnv.width = ele.width; cnv.height = ele.height;
    cnv.getContext('2d').drawImage(ele, 0, 0);
    return cnv.toDataURL('image/jpeg').substring(22);    
    """, driver.find_element(By.XPATH, '//*[@id="imgCaptcha"]'))        # 原圖片的 XPATH

img_name = "captcha_login.png"
with open(img_name, 'wb') as image:
    image.write(base64.b64decode(img_base64))
    # 另存圖片檔, pytesseract 才能正常解讀文字
    # 如果不能解讀則可另用 2captcha

img = Image.open(img_name)
print(img.format, img.size, img.mode)
img.show()
text = pytesseract.image_to_string(img, lang='eng')
print("'" + text + "'")

driver.find_element(By.XPATH, '//*[@id="txtCaptcha"]').send_keys(text)

time.sleep(10)
driver.close()
