from selenium import webdriver      # install selenium
from selenium.webdriver.common.by import By     # 搜尋物件使用 By
from selenium.common.exceptions import NoSuchElementException       # 等待出現 web 元素用
from webdriver_manager.chrome import ChromeDriverManager    # install webdriver-manager 自動安裝,自動更新
from time import sleep
import base64       # 在此用於影像編碼
from PIL import Image       # install Pillow
import pytesseract          # install pytesseract
import os


def next_():
    anykey = input("EnterKey : ")


def captcha():
    driver.get('https://eip.epbks.com.tw/Account/Login')
    while True:
        try:  # 等待搜尋的元素出現才繼續下一步
            driver.find_element(By.XPATH, '//*[@id="_verification_img"]')
        except NoSuchElementException:
            continue  # implicitly_wait() 超過時間找不到,回到迴圈最前面

        # 用 JavaScript 的方式讀取 driver.find_element(...) 找到的影像
        img_base64 = driver.execute_script("""
            var ele = arguments[0];
            var cnv = document.createElement('canvas');
            cnv.width = ele.width; cnv.height = ele.height;
            cnv.getContext('2d').drawImage(ele, 0, 0);
            return cnv.toDataURL('image/jpeg').substring(22);    
            """, driver.find_element(By.XPATH, '//*[@id="_verification_img"]'))

        img_name = os.getenv('temp') + "\everpro_captcha_login.png"     # 取得系統環境變數 temp
        with open(img_name, 'wb') as image:  # 以這個方式存圖片檔, pytesseract 比 screenshot() 較可以正常辨識文字
            image.write(base64.b64decode(img_base64))
        img = Image.open(img_name)
        text = pytesseract.image_to_string(img, lang='eng')  # OCR 辨識,如辨識率不佳，可改用 2captcha 要花一點錢
        for replace_c in ['\n', '‘', '.', '“', '-']:  # 刪除 "\n" (換行) ... 等不必要的資料
            text = text.replace(replace_c, "")
        text = text.replace("O", "0")
        os.remove(img_name)  # 刪除已辨識的暫存圖檔
        if len(text) == 4:  # 此網站 captcha 用 4 個字元
            break
        else:
            driver.find_element(By.ID, '_verification_btnChange').click()  # 點選 產生新的驗證碼
            sleep(1)
            continue
    return text


def login(accountID, password, verify, text):
    driver.find_element(By.XPATH, '//*[@id="accountID"]').clear()
    driver.find_element(By.XPATH, '//*[@id="accountID"]').send_keys(accountID)
    driver.find_element(By.XPATH, '//*[@id="password"]').clear()
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="verify"]').clear()
    driver.find_element(By.XPATH, '//*[@id="verify"]').send_keys(verify)
    driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/div/div[5]/div/input[2]').clear()
    driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/div/div[5]/div/input[2]').send_keys(text)
    sleep(1)
    driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/div/div[6]/input').click()  # 登入
    sleep(1)


def check_login():
    while True:
        login(accountID, password, verify, captcha())       # 登入
        try:  # 等待搜尋的元素出現才繼續下一步
            captcha_error = driver.find_element(By.XPATH, '//*[@id="_verification_img"]')      # 定義 “驗證碼錯誤”
            if captcha_error.is_displayed():        # 找到 "驗證碼錯誤"
                continue        # 從頭跑迴圈,重新登入
        except NoSuchElementException:      # 找不到 "驗證碼錯誤"
            break       # 驗證碼正確, 離開迴圈
    return True


def e_learning():
    main_window = driver.current_window_handle  # main_window 為現在分頁
    driver.find_element(By.XPATH, '//*[@id="CategoryMenu"]/li[8]/a').click()  # 點選 平台代登
    sleep(1)
    driver.find_element(By.XPATH, '//*[@id="CategoryMenu"]/li[8]/ul/li[4]/a').click()  # 點選 E-Learning (會開啟新分頁)
    sleep(3)
    all_handles = driver.window_handles  # 所有分頁
    print(all_handles)
    e_learning_window = all_handles[-1]
    print(e_learning_window)
    next_()
    for handle in all_handles:
        if handle != main_window:
            e_learning_window = handle
            driver.switch_to.window(e_learning_window)    # 切換分頁
            # 點選待修課程 icon
            driver.find_element(By.XPATH, '/html/body/ctms-root/ctms-layout/div/ctms-header/mat-toolbar/div[3]/button[1]').click()
            while True:
                try:  # 等待搜尋的元素出現才繼續下一步
                    # 定義物件 “ehrd-no-content”
                    ehrd_no_content = driver.find_element(By.XPATH, '/html/body/ctms-root/ctms-layout/div/mat-sidenav-container/mat-sidenav-content/div/ctms-incomplete-courses/div/ehrd-container/ehrd-no-content')
                    if ehrd_no_content.is_displayed():  # 找到 "ehrd-no-content"
                        print("沒有課可以上")
                        break
                except NoSuchElementException:  # 找不到 "沒有學習內容"
                    lean_1 = driver.find_element(By.XPATH, '/html/body/ctms-root/ctms-layout/div/mat-sidenav-container/mat-sidenav-content/div/ctms-incomplete-courses/div/ehrd-container/mat-card[1]/mat-card-content/div/div[3]/div[1]/a')
                    print(lean_1.text)      # 顯示第一個 課程名稱
                    lean_1.click()      # 點選第一個 課程名稱
                    # 點選 "課程清單" 的第一個 "開始學習"
                    driver.find_element(By.XPATH, '//*[@id="mat-tab-content-0-0"]/div/div/div[2]/div[1]/ctms-program-lesson/mat-card/mat-card-actions/div/a').click()
                    class_1 = driver.find_element(By.XPATH, '/html/body/ctms-root/ctms-layout/div/mat-sidenav-container/mat-sidenav-content/div/ctms-course-enrollment/div/ehrd-container/div[1]/div/div/div[1]/p')
                    print(class_1.text)     # 顯示 課程名稱
                    # 點選 會另開一個視窗, 開啟課程影片連結
                    driver.find_element(By.XPATH, '/html/body/ctms-root/ctms-layout/div/mat-sidenav-container/mat-sidenav-content/div/ctms-course-enrollment/div/ehrd-container/div[2]/mat-card[1]/mat-card-content/div/div[1]/div[1]/a').click()
                    sleep(2)
                    all_handles = driver.window_handles  # 所有分頁
                    class_video_window = all_handles[-1]
                    driver.switch_to.window(class_video_window)  # 切換分頁
                    driver.find_element(By.XPATH, '//*[@id="content"]').click()     # 點選影片播放

                    # 切入三層 iframe
                    video_frame = driver.find_element(By.CSS_SELECTOR, "iframe#content")
                    driver.switch_to.frame(video_frame)
                    video_frame = driver.find_element(By.CSS_SELECTOR, "iframe#playContent")
                    driver.switch_to.frame(video_frame)
                    video_frame = driver.find_element(By.CSS_SELECTOR, "iframe#Content")
                    driver.switch_to.frame(video_frame)
                    next_()

                    try:  # 等待搜尋的元素出現才繼續下一步
                        # 定義物件 “ehrd-no-content”
                        next_btn = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[1]/button[7]/div')
                        if next_btn.is_displayed():  # 找到 "next_btn"
                            next_btn.click()
                            next_()
                            break
                    except NoSuchElementException:  # 找不到 "next_btn"
                        while True:
                            # 影片個數
                            video_no_element = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/nav/div[1]/div/div[1]/div[1]')
                            video_check_no = video_no_element.get_attribute('aria-label').split(" / ")  # 影片個數
                            video_now_no = int(video_check_no[0])
                            video_total = int(video_check_no[1])
                            print("共", video_total, "個影片", "目前在第", video_now_no, "個")

                            # 影片時間長度
                            video_time_element = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/nav/div[1]/div/div[1]/div[2]')
                            video_ttime = video_time_element.get_attribute('aria-label').split(" / ")[1].split(":")  # 影片時間長度
                            video_ttime_min = int(video_ttime[0])
                            video_ttime_sec = int(video_ttime[1])
                            video_ttime_sec_total = (video_ttime_min * 60) + video_ttime_sec
                            print("目前影片長度共", video_ttime_sec_total, "秒")
                            sleep(video_ttime_sec_total + 1)     # 等待播完影片加 1 秒緩衝

                            # 目前影片時間
                            print("時間到了,檢查播放時間")
                            video_ntime = video_time_element.get_attribute('aria-label').split(" / ")[1].split(":")  # 影片時間長度
                            video_ntime_min = int(video_ntime[0])
                            video_ntime_sec = int(video_ntime[1])
                            video_ntime_sec_total = (video_ntime_min * 60) + video_ntime_sec
                            if video_total != video_now_no:
                                print("還有影片沒有播放完畢")
                                if video_ttime_sec_total == video_ntime_sec_total:
                                    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/nav/div[2]/button[2]').click()
                                    print("按下一頁")
                                else:
                                    print("播放影片中")

                            else:
                                break
                next_()
                break
            driver.close()
            driver.switch_to.window(main_window)  # 切回 main_window 分頁


os.environ['PATH'] = "C:\Program Files\Tesseract-OCR;" + os.environ['PATH']     # Tesseract-OCR 目錄 加入系統 PATH
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(5)     # 找不到物件的逾時時間(秒)
driver.maximize_window()

'''
accountID = 'F224719666'
password = 'Iven1101'
verify = 's7641'
'''
accountID = 'N201419794'
password = 'Aa6666666'
verify = 'u8080'
li_no = '0079202419'
pi_no = 'N15J340507'


if check_login():
    e_learning()
# print(driver.title)
driver.quit()

# install tesseract-ocr-w64-setup-5.3.0.20221222.exe

