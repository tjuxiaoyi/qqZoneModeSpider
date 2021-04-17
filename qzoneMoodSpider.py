# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 13:55:57 2019

@author: YangShiyuan, all rights reserved.
Redistribution for academic purpose only.
If you find this code useful, please cite our paper Yang et al. Image inpainting based on multi-patch with adaptive size. Apl. Sci. 2020.
"""

#以下为需要使用的库
from selenium.webdriver.support.ui import WebDriverWait as WebWait
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.support  import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
from bs4 import BeautifulSoup

class moodSpider():
    
    #定义QQ账号密码
    user = '670127565'
    passwd = '*********'

    
    def __init__(self):
        
        #初始化，打开浏览器并最大化，以下两句话为设置无头浏览器
        #options = options.Options()
        #options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')#,chrome_options=options)
        self.driver.maximize_window()
        
    def get_to_mood_page(self):
        #本函数用于登录QQ空间并跳转至说说界面
        
        driver = self.driver
        #访问QQ空间
        driver.get('https://i.qq.com')
        #print('geted')
        
        #输入账户密码的frame不是默认的frame 所以需要更改frame 不然找不到元素
        driver.switch_to.frame('login_frame')
        #print('switched')
        
        #显示等待id为switcher_plogin的按钮，该按钮用于更改登录方式为账号密码登录
        switch = WebWait(driver,5).until(EC.element_to_be_clickable((By.ID,'switcher_plogin')))
        switch.click()
        #print('clicked')
        
        #找到输入账号和密码的文本框并输入账号密码
        driver.find_element_by_id('u').send_keys(moodSpider.user)
        driver.find_element_by_id('p').send_keys(moodSpider.passwd)
        login = WebWait(driver,5).until(EC.element_to_be_clickable((By.ID,'login_button')))
        login.click()
        
        #登录后跳转至说说界面
        time.sleep(2)
        driver.get('http://user.qzone.qq.com/'+moodSpider.user+'/311')
    
        
        
    def load_all_resoure(self):
        
        driver = self.driver
        
        #下拉到页面最下方，保证所有说说被加载
        driver.execute_script('window.scrollBy(0,10000)')
        time.sleep(2)
        driver.execute_script('window.scrollBy(0,10000)')
        time.sleep(2)
        driver.execute_script('window.scrollBy(0,10000)')
        time.sleep(2)
        
        #找到说说所在的frame，否则无法找到说说的元素
        driver.switch_to.frame('app_canvas_frame')
        time.sleep(2)
        
        
    def view_full_content(self):
        driver = self.driver
        
        #找到所有展开查看全文的按钮，并点击，保证说说完整加载
        all_extended = False
        while not all_extended:
            try:
                button = driver.find_element_by_link_text('展开查看全文')
                
                try:
                    '''
                    此处的逻辑我写了很久，因为想点击展开查看全文，必须使得按钮在页面中，否则会报未知错误
                    报错的同时也会将页面跳至按钮附近
                    所以我在捕获异常里将页面向上移动
                    下次即可直接点击按钮了
                    '''
                    button.click()
                    time.sleep(2)
                    #actions.click(button)
                    #actions.perform()
                except Exception as e:
                    print('fuck!')
                    driver.switch_to.parent_frame()
                    driver.execute_script('window.scrollBy(0,-200)')
                    time.sleep(1)
                    driver.switch_to.frame('app_canvas_frame')
                    
            #如果找不到展开查看全文的按钮，则结束循环
            except NoSuchElementException as e:
                print(e)
                all_extended = True

    def process_content(self):
        
        #保存所有的说说文本
        self.soup = BeautifulSoup(self.driver.page_source,'xml')
        mood_content = self.soup.find_all('pre',{'class':'content'})
        filename = 'mood.txt'
        #因为有些字符可能不能直接保存为gbk格式，所以此处指明使用utf-8
        with open (filename ,'a',encoding='utf-8') as f:    
            for c in mood_content:
                content_text = c.get_text('pre')
                #以下两句为替换部分表情字符
                content_text = content_text.replace('pre',' ')
                content_text = content_text.replace('\ue412',' ')
                f.write(content_text)        
    
    
    
    def to_next_page(self):
    
        driver = self.driver
        #此函数用于跳转至下一页
        #因为下一页的id是会变化的，所以在文本里识别出来下一页的id
        soup = self.soup
        next_page_id = soup.find('a',{'title':'下一页'})['id']
        to_next = WebWait(driver,5).until(EC.element_to_be_clickable((By.ID,next_page_id)))
        to_next.click()
        driver.switch_to.parent_frame()
        
        #翻页后返回顶端，以保证所以的说说被加载
        driver.execute_script('window.scrollBy(0,-10000)')
        time.sleep(1)
        driver.execute_script('window.scrollBy(0,-10000)')
        time.sleep(1)
        driver.execute_script('window.scrollBy(0,-10000)')
        time.sleep(1)
        
        
    def download_mood(self):
        self.get_to_mood_page()
        finished = False
        #当下一页无法被点击时，到下一页的函数会抛出异常
        #于是结束程序
        while not finished:
            self.load_all_resoure()
            self.view_full_content()
            self.process_content()
            
            try:
                self.to_next_page()
            except NoSuchElementException as e:
                print(e)
                finished = True
            except:
                print('fuck')
        print('done')

spider = moodSpider()
spider.download_mood()
