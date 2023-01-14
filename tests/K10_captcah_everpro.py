from selenium import webdriver      # install selenium
from selenium.webdriver.common.by import By     # 搜尋物件使用 By
from selenium.webdriver.support.wait import WebDriverWait       # 等待出現 web 元素用
from selenium.webdriver.support import expected_conditions as EC    # 等待出現 web 元素用
from webdriver_manager.chrome import ChromeDriverManager    # install webdriver-manager 自動安裝,自動更新
import time
import base64       # 在此用於影像編碼
from PIL import Image       # install Pillow
import pytesseract          # install pytesseract
# import subprocess     # 用於執行外部程式
import os






# 記得安裝 Tesseract-OCR 外部程式
os.environ['PATH'] = "C:\Program Files\Tesseract-OCR;" + os.environ['PATH']     # Tesseract-OCR 目錄 加入系統 PATH
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(10)
driver.get('https://eip.epbks.com.tw/Account/Login')
driver.maximize_window()

while True:
    # 等待搜尋的元素出現才繼續下一步
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="_verification_img"]')))

    # 用 JavaScript 的方式讀取 driver.find_element(...) 找到的影像
    img_base64 = driver.execute_script("""
        var ele = arguments[0];
        var cnv = document.createElement('canvas');
        cnv.width = ele.width; cnv.height = ele.height;
        cnv.getContext('2d').drawImage(ele, 0, 0);
        return cnv.toDataURL('image/jpeg').substring(22);    
        """, driver.find_element(By.XPATH, '//*[@id="_verification_img"]'))

    img_name = "captcha_login.png"
    with open(img_name, 'wb') as image:        # 以這個方式存圖片檔, pytesseract 比 screenshot() 較可以正常辨識文字
        image.write(base64.b64decode(img_base64))
    img = Image.open(img_name)
    text = pytesseract.image_to_string(img, lang='eng')     # OCR 辨識,如辨識率不佳，可改用 2captcha 要花一點錢
    for replace_c in ['\n', '‘', '.', '“', '-']:    # 刪除 "\n" (換行) ... 等不必要的資料
        text = text.replace(replace_c, "")
    text = text.replace("O", "0")

    if len(text) == 4:      # 此網站 captcha 用 4 個字元
        break
    else:
        driver.find_element(By.ID, '_verification_btnChange').click()      # 點選 產生新的驗證碼
        continue

# img.show()
# print(img.format, img.size, img.mode)
# print(text, len(text))
driver.find_element(By.XPATH, '//*[@id="accountID"]').send_keys("F224719666")
driver.find_element(By.XPATH, '//*[@id="password"]').send_keys("Iven1101")
driver.find_element(By.XPATH, '//*[@id="verify"]').send_keys("s7641")
driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/div/div[5]/div/input[2]').send_keys(text)
time.sleep(3)
driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/div/div[6]/input').click()    # 登入
time.sleep(3)

# command: tasklist 可以找出所有執行中的程式
# 中止外部程式
# subprocess.Popen('taskkill /IM PhotosApp.exe /F')

main_window = driver.current_window_handle     # main_window 為現在分頁
driver.find_element(By.XPATH, '//*[@id="CategoryMenu"]/li[8]/a').click()       # 點選 平台代登
time.sleep(1)
driver.find_element(By.XPATH, '//*[@id="CategoryMenu"]/li[8]/ul/li[4]/a').click()      # 點選 E-Learning (會開啟新分頁)
time.sleep(3)

all_handles = driver.window_handles        # 所有分頁
driver.switch_to.window(all_handles[-1])       # 切換分頁
print(driver.title)
driver.find_element(By.XPATH, '//*[@id="sidebar-panel"]/div/div/ctms-sidebar/mat-nav-list/ctms-sidebar-menu-item[2]/mat-list-item[2]/div/a/span[2]').click()
time.sleep(1)
driver.find_element(By.LINK_TEXT, '待修課程').click()
enter_key = input("EnterKey to next: ")
driver.close()
driver.switch_to.window(main_window)       # 切回 main_window 分頁
print(driver.title)
driver.quit()
