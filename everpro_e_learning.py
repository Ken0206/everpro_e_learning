# 必須先安裝軟體: tesseract-ocr-w64-setup-5.3.0.20221222.exe

from selenium import webdriver      # selenium  https://www.selenium.dev/documentation/
from selenium.webdriver.common.by import By     # 搜尋物件使用 By
from selenium.common.exceptions import NoSuchElementException       # 等待出現 web 元素用
from selenium.webdriver.chrome.service import Service as ChromeService      # webdriver-manager 自動安裝,自動更新
from webdriver_manager.chrome import ChromeDriverManager    # webdriver-manager https://github.com/SergeyPirogov/webdriver_manager
from time import sleep
import base64       # 在此用於影像編碼
from PIL import Image       # Pillow    https://python-pillow.org/
import pytesseract          # pytesseract   https://github.com/madmaze/pytesseract
import os
import subprocess


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

        img_name = os.getenv('temp') + '.\everpro_captcha_login.png'     # 取得系統環境變數 temp
        with open(img_name, 'wb') as image:  # 以這個方式存圖片檔, pytesseract 比 screenshot() 較可以正常辨識文字
            image.write(base64.b64decode(img_base64))
        img = Image.open(img_name)
        captcha_text = pytesseract.image_to_string(img, lang='eng')  # OCR 辨識,如辨識率不佳，可改用 2captcha 要花一點錢
        for replace_c in ['\n', '‘', '.', '“', '-']:  # 刪除 "\n" (換行) ... 等不必要的資料
            captcha_text = captcha_text.replace(replace_c, '')
        captcha_text = captcha_text.replace('O', '0')
        os.remove(img_name)  # 刪除已辨識的暫存圖檔
        if len(captcha_text) == 4:  # 此網站 captcha 用 4 個字元
            break
        else:
            driver.find_element(By.ID, '_verification_btnChange').click()  # 點選 產生新的驗證碼
            sleep(1)
            continue
    return captcha_text


def login(accountID, password, verify, captcha_text):
    driver.find_element(By.XPATH, '//*[@id="accountID"]').clear()
    driver.find_element(By.XPATH, '//*[@id="accountID"]').send_keys(accountID)
    driver.find_element(By.XPATH, '//*[@id="password"]').clear()
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="verify"]').clear()
    driver.find_element(By.XPATH, '//*[@id="verify"]').send_keys(verify)
    driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/div/div[5]/div/input[2]').clear()
    driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/div/div[5]/div/input[2]').send_keys(captcha_text)
    sleep(1)
    driver.find_element(By.XPATH, '//*[@id="loginForm"]/div[2]/div/div[6]/input').click()  # 登入
    sleep(1)


def check_login():
    ans = False
    while True:
        login(accountID, password, verify, captcha())       # 登入
        try:  # 等待搜尋的元素出現才繼續下一步
            captcha_error = driver.find_element(By.XPATH, '//*[@id="_verification_img"]')      # 定義 “驗證碼錯誤”
            if captcha_error.is_displayed():        # 找到 "驗證碼錯誤"
                continue        # 從頭跑迴圈,重新登入
        except NoSuchElementException:      # 找不到 "驗證碼錯誤"
            ans = True
            break       # 驗證碼正確, 離開迴圈
    return ans


def e_learning():
    ans = False
    # main_window = driver.current_window_handle  # main_window 為現在分頁
    driver.find_element(By.XPATH, '//*[@id="CategoryMenu"]/li[8]/a').click()  # 點選 平台代登
    sleep(1)
    driver.find_element(By.XPATH, '//*[@id="CategoryMenu"]/li[8]/ul/li[4]/a').click()  # 點選 E-Learning (會開啟新分頁)
    sleep(3)
    all_handles = driver.window_handles  # 所有分頁
    e_learning_window = all_handles[-1]
    driver.switch_to.window(e_learning_window)    # 切換分頁
    # 點選待修課程 icon
    driver.find_element(By.XPATH, '/html/body/ctms-root/ctms-layout/div/ctms-header/mat-toolbar/div[3]/button[1]').click()
    while True:
        try:  # 等待搜尋的元素出現才繼續下一步
            # 定義物件 “ehrd-no-content”
            ehrd_no_content = driver.find_element(By.XPATH, '/html/body/ctms-root/ctms-layout/div/mat-sidenav-container/mat-sidenav-content/div/ctms-incomplete-courses/div/ehrd-container/ehrd-no-content')
            if ehrd_no_content.is_displayed():  # 找到 "ehrd-no-content"
                print("沒有課可以上")
                ans = False
                break
        except NoSuchElementException:  # 找不到 "沒有學習內容"
            lean_1 = driver.find_element(By.XPATH, '/html/body/ctms-root/ctms-layout/div/mat-sidenav-container/mat-sidenav-content/div/ctms-incomplete-courses/div/ehrd-container/mat-card[1]/mat-card-content/div/div[3]/div[1]/a')
            print(lean_1.text)      # 顯示第一個 課程名稱
            if '『壽險』' in lean_1.text:
                insuranceNo = insuranceNo1
                insurance_type = 1
                print('『壽險』登錄字號 :', insuranceNo)
            if '『產險』' in lean_1.text:
                insuranceNo = insuranceNo2
                insurance_type = 2
                print('『產險』登錄字號 :', insuranceNo)
            lean_1.click()      # 點選第一個 課程名稱
            try:
                # 點選 "課程清單" 的第一個 "未完成"
                driver.find_element(By.PARTIAL_LINK_TEXT, '未完成').click()
            except NoSuchElementException:
                # 點選 "課程清單" 的第一個 "未曾觀看"
                driver.find_element(By.PARTIAL_LINK_TEXT, '未曾觀看').click()
            class_1 = driver.find_element(By.XPATH, '/html/body/ctms-root/ctms-layout/div/mat-sidenav-container/mat-sidenav-content/div/ctms-course-enrollment/div/ehrd-container/div[1]/div/div/div[1]/p')
            print(class_1.text)     # 顯示 課程名稱
            # 點選 會另開一個視窗, 開啟課程影片連結
            driver.find_element(By.XPATH, '/html/body/ctms-root/ctms-layout/div/mat-sidenav-container/mat-sidenav-content/div/ctms-course-enrollment/div/ehrd-container/div[2]/mat-card[1]/mat-card-content/div/div[1]/div[1]/a').click()
            sleep(5)
            driver.maximize_window()
            all_handles = driver.window_handles  # 所有分頁
            class_video_window = all_handles[-1]
            driver.switch_to.window(class_video_window)  # 切換播放影片分頁
            driver.find_element(By.XPATH, '//*[@id="content"]').click()     # 點選影片播放

            # 切入三層 iframe 以取得影片數量,影片長度
            video_iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#content')
            driver.switch_to.frame(video_iframe)
            video_iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#playContent')
            driver.switch_to.frame(video_iframe)
            video_iframe = driver.find_element(By.CSS_SELECTOR, 'iframe#Content')
            driver.switch_to.frame(video_iframe)
            # print("已進入 3 層 iframe")

            find_test_result_button()

            if authentication(insuranceNo, insurance_type):
                ans = True
                break

            if in_video():
                ans = True
                break

            if find_start_ans_button():
                ans_questions()
                if authentication(insuranceNo, insurance_type):
                    ans = True
                    break

            if find_ans_button():
                ans_questions()
                if authentication(insuranceNo, insurance_type):
                    ans = True
                    break

            if find_retest_button():
                ans_questions()
                if authentication(insuranceNo, insurance_type):
                    ans = True
                    break

            v_to_main()
            ans = True
            break

    print('離開 e_learning')
    return ans


def in_video():
    ans = False
    try:
        # 找 影片數量
        video_no_element = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/nav/div[1]/div/div[1]/div[1]')
        if video_no_element.is_displayed():
            while True:
                # 影片個數
                video_no_element = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/nav/div[1]/div/div[1]/div[1]')
                video_check_no = video_no_element.get_attribute('aria-label').split(' / ')  # 影片個數
                video_now_no = int(video_check_no[0])
                video_total = int(video_check_no[1])
                print('共', video_total, '個影片', '目前在第', video_now_no, '個')

                # 影片時間長度
                video_time_element = driver.find_element(By.XPATH,
                                                          '/html/body/div[2]/div/div[1]/nav/div[1]/div/div[1]/div[2]')
                video_ttime = video_time_element.get_attribute('aria-label').split(" / ")[1].split(":")  # 影片時間長度
                video_ttime_min = int(video_ttime[0])
                video_ttime_sec = int(video_ttime[1])
                video_ttime_sec_total = (video_ttime_min * 60) + video_ttime_sec
                print('目前影片長度共', video_ttime_sec_total, '秒')
                sleep(video_ttime_sec_total + 2)  # 等待播完影片加 2 秒緩衝

                # 目前影片時間
                # 時間到了,檢查播放時間
                video_ntime = video_time_element.get_attribute('aria-label').split(' / ')[1].split(':')  # 影片時間長度
                video_ntime_min = int(video_ntime[0])
                video_ntime_sec = int(video_ntime[1])
                video_ntime_sec_total = (video_ntime_min * 60) + video_ntime_sec
                if video_total == video_now_no:
                    print('影片播放完畢')
                    break
                else:
                    if video_ttime_sec_total == video_ntime_sec_total:
                        print('按 "下一頁"')
                        driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/nav/div[2]/button[2]').click()
        ans = True
    except NoSuchElementException:
        print('不在 影片區段')
    return ans


def find_test_result_button():
    ans = False
    try:  # 等待搜尋的元素出現才繼續下一步
        # 定義物件 “start_ans_button”
        test_result_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[1]/button[8]')
        if test_result_button.is_displayed():  # 找到 "測驗結果" 按鈕
            print('按下 "測驗結果" 按鈕')
            test_result_button.click()
            sleep(1)
            print('按 "下一頁"')
            driver.find_element(By.XPATH, '//*[@id="content"]/div/div[1]/div[3]/div[1]/button[10]').click()
            ans = True
    except NoSuchElementException:
        print('沒有 "測驗結果" 按鈕')
    return ans


def find_start_ans_button():
    ans = False
    try:  # 等待搜尋的元素出現才繼續下一步
        # 定義物件 “start_ans_button”
        start_ans_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[1]/button[7]')
        if start_ans_button.is_displayed():  # 找到 "開始測驗" 按鈕
            print('按下 "開始測驗"')
            start_ans_button.click()
            ans = True
    except NoSuchElementException:
        print('沒有 "開始測驗"')
    return ans


def find_ans_button():
    ans = False
    try:  # 等待搜尋的元素出現才繼續下一步
        # 定義物件 “ans_button”
        ans_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[1]/button[1]')
        if ans_button.is_displayed():  # 找到 "答題"
            print('按下 "答題"')
            ans_button.click()
            ans = True
    except NoSuchElementException:
        print('沒有 "答題"')
    return ans


def find_retest_button():
    ans = False
    try:  # 等待搜尋的元素出現才繼續下一步
        # 定義物件 “retest_button”
        retest_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[2]/div/div[7]/div[2]/div[1]/div[1]/div/div[2]/div/div[10]')
        if retest_button.is_displayed():  # 找到 "重新測驗" 按鈕
            print('按下 "重新測驗"')
            retest_button.click()
            ans = True
    except NoSuchElementException:
        print('沒有 "重新測驗"')
    return ans


def v_to_main():
    all_handles = driver.window_handles
    driver.close()
    sleep(2)
    driver.switch_to.window(all_handles[1])  # 切回 e_learning_window 分頁
    sleep(2)
    driver.close()
    sleep(2)
    driver.switch_to.window(all_handles[0])  # 切回 main_window 分頁
    sleep(2)


def ans_questions():
    quit_while = 0
    while True:
        if quit_while == 1:
            break
        questions = driver.find_elements(By.CLASS_NAME, 'choice-view__active-element-container')
        a_times = 0
        for question in questions:
            a_times = a_times + 1
            print(a_times)
            question.click()    # 按答案選項
            # 按 "答題"
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[1]/button[1]').click()
            sleep(1)
            print('已按 "答題"')
            ans_text = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[2]/div/div[7]/div[2]/div[1]/div[2]/div/div[1]').text
            print(ans_text)
            if ans_text == '錯誤':
                print('回答錯誤, 再次作答')
                # 按 "再次作答"
                driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div[3]/div[1]/button[3]").click()
                sleep(1)
                continue
            else:
                last_question = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[1]/div[3]').text
                print('第幾道題 : ', last_question)
                if last_question == '問題 5/5':
                    print('按 "測驗結果" 按鈕')
                    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[1]/button[8]').click()
                    sleep(3)
                    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[1]/button[10]').click()
                    sleep(10)
                    quit_while = 1
                    break
                print('回答正確, 按 "繼續作答" 按鈕')
                # 按 "繼續作答" 按鈕
                driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[1]/button[2]').click()
                sleep(1)
                break


def authentication(insuranceNo, insurance_type):
    ans = False
    try:
        sleep(5)
        authentication_iframe = driver.find_element(By.CSS_SELECTOR, 'iframe')
        driver.switch_to.frame(authentication_iframe)
        sleep(5)
        authentication_iframe = driver.find_element(By.CSS_SELECTOR, 'iframe')
        driver.switch_to.frame(authentication_iframe)
        sleep(5)
        print("進入身份驗証")

        if insurance_type == 1:
            driver.find_element(By.ID, 'account').send_keys(accountID)
            driver.find_element(By.ID, 'Password').send_keys(password)
            driver.find_element(By.ID, 'insuranceNo').send_keys(insuranceNo)
            sleep(2)
            driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div/form/button').click()
            sleep(5)
        else:
            print("『壽險』")
            enterkey = input('手動身份驗證 送出後 按 Enter ：')
            # subprocess.run('./authentication.exe')    # Tab 算不清楚按幾次
            sleep(5)

        v_to_main()
        ans = True
        print('已 身份驗證')
    except NoSuchElementException:
        print('沒有 身份驗證 進入點')
    return ans


def start():

    if check_login():
        while True:
            if e_learning():
                print('再次 e_learning 課程')
            else:
                break
    else:
        print('登入錯誤')
    print('結束')
    driver.quit()


os.environ['PATH'] = "C:\Program Files\Tesseract-OCR;" + os.environ['PATH']  # Tesseract-OCR 預設安裝目錄 加入系統 PATH
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))  # selenium 4
# driver = webdriver.Chrome(ChromeDriverManager().install())   # selenium 3
driver.implicitly_wait(3)  # 找不到物件的逾時時間(秒)
driver.maximize_window()

accountID = 'A123456789'
password = 'Abcdef1234'
verify = 'a8888'
insuranceNo1 = '0123456789'
insuranceNo2 = 'N123456789'

start()

# https://www.selenium.dev/documentation/
