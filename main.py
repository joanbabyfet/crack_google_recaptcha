from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import configparser
import requests

def main():
    url = 'https://www.google.com/recaptcha/api2/demo'

    conf = configparser.ConfigParser()
    conf.read('config.ini', encoding='utf-8') # 这里要加utf-8, 否则会报错, 默认gbk
    config_section  = 'config'
    api_key = conf.get(config_section, 'api_key') 

    options = webdriver.ChromeOptions()
    options.add_experimental_option('detach', True)  # 不自动关闭浏览器
    options.add_experimental_option('prefs', { 
        "profile.default_content_setting_values.notifications": 2 # 防止跳出通知
    })
    browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)
    browser.maximize_window() # 窗口最大化
    browser.get(url)

    el_site_key = browser.find_element(By.CSS_SELECTOR, '[data-sitekey]')
    site_key = el_site_key.get_attribute('data-sitekey')

    data = {
        'key': api_key,
        'method': 'userrecaptcha',
        'googlekey': site_key,
        'pageurl': url
    }
    # 验证码提交地址
    res = requests.post('http://2captcha.com/in.php', data = data)
    print(f'response:{res.text}')
    if res.ok and res.text.find('OK') > -1:
        captcha_id = res.text.split('|')[1]
        for i in range(10):
            # 获取辨识结果
            resp = requests.get(f'http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}')
            print(f'response:{resp.text}')

            if resp.text.find('OK') > -1:
                captcha_text = resp.text.split('|')[1] # 获取辨识结果

                browser.execute_script("""
                    document.querySelector('[name="g-recaptcha-response"]').innerText='{%s}'
                """ % captcha_text)
                btn_login = browser.find_element(By.ID, 'recaptcha-demo-submit')
                btn_login.click()  # 点击登入
                break
            elif resp.text.find('CAPCHA_NOT_READY') > -1: # 未辨识完成
                sleep(3)
        else:
            print('获取验证码错误')
    else:
        print('提交验证码错误')
    browser.close() # 关闭当前tab选项卡, quit关闭整个浏览器

if __name__ == '__main__':
    main()