from selenium import webdriver
from selenium.webdriver.common.by import By     # 搜尋物件使用 By
from webdriver_manager.chrome import ChromeDriverManager
import time
import base64

# 只使用前半段的程式碼一直到另存圖片
# https://www.learncodewithmike.com/2021/08/python-selenium-bypass-captcha.html

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://cart.books.com.tw/member/login')

time.sleep(10)

img_base64 = driver.execute_script("""
    var ele = arguments[0];
    var cnv = document.createElement('canvas');
    cnv.width = ele.width; cnv.height = ele.height;
    cnv.getContext('2d').drawImage(ele, 0, 0);
    return cnv.toDataURL('image/jpeg').substring(22);    
    """, driver.find_element(By.XPATH, "//*[@id='captcha_img']/img"))

# 圖片儲存起來
with open("captcha_login.png", 'wb') as image:
    image.write(base64.b64decode(img_base64))
