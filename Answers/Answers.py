#coding:utf-8

import os
import time
import traceback
import random
import ConfigParser
from Tkinter import *
from Logger import GetLog
from selenium import webdriver
import tkSimpleDialog as dl  
import tkMessageBox as mb  


hdszgwslb = 'http://www.hdszgwslb.com/'
lb_log_in = 'http://www.hdszgwslb.com/index/users/login'

question_dict = {}

def load_answer():
    with open('answers.txt') as f:
        for line in f:
            question,answer = line.decode('utf-8').strip('\n').split('#')
            question_dict[question] = answer.split(';')

class ConfigManger():
    cgf = None
    user_name = ''
    pass_word = ''

    def __init__(self):
        self.cfg = ConfigParser.ConfigParser()
        self.cfg.read('config.cfg')
        section = self.cfg.sections()
        if (section):
            self.user_name = self.cfg.get('Admin','Username')
            self.pass_word = self.cfg.get('Admin','Password')
        else:
            self.cfg.add_section("Admin")
            self.cfg.set('Admin','Username','')
            self.cfg.set('Admin','Password','')

    def Save(self):
        with open('config.cfg','wb') as of:
            self.cfg.write(of)

    def get_username(self):
        return self.user_name

    def get_password(self):
        return self.pass_word

    def set_username(self,username):
        self.cfg.set('Admin','Username',username)
    
    def set_password(self,password):
        self.cfg.set('Admin','Password',password)

class ExerciseSystem:
    driver = None
    link = None

    def __init__(self):
        # path = r'%s\chromedriver.exe'%(os.path.abspath('.'))
        self.driver = webdriver.Chrome('chromedriver.exe')
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)

    def __del__(self):
        self.quit()

    def close(self):
        self.driver.close()

    def quit(self):
        self.driver.quit()

    def windows_handles(self):
        return self.driver.window_handles

    def switch_windows(self):
        handles = self.windows_handles()
        self.driver.switch_to_window(handles[-1])

    def open_windows(self,link):
        new_window = 'window.open("%s")'%(link)
        self.driver.execute_script(new_window)

    def is_success(self):
        str = self.driver.find_element_by_xpath('/body/div/div[@class="layui-layer-content"]').text
        if (str.encode('utf-8') == '登录成功'.decode('utf-8')):
            return False
        else:
            return True

    def open_link(self,link):
        self.driver.get(link)
    
    def log_in(self):
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()

    def enter_adm_pwd(self,usr,pwd):
        self.driver.find_element_by_id('username').clear()
        self.driver.find_element_by_id('username').send_keys(usr)
        self.click_wait()
        self.driver.find_element_by_id('password').clear()
        self.driver.find_element_by_id('password').send_keys(pwd)
    
    def input_pin(self,pin):
        # pin = raw_input('please input:')        
        self.driver.find_element_by_id('vercode').clear()
        self.driver.find_element_by_id('vercode').send_keys(pin)

    def answers(self):
        self.click_wait(self.get_rand(6,13))
        self.get_suject()

    def click_wait(self,value=1):
        time.sleep(value)

    def get_rand(self,low,high):
        return random.randint(low,high)

    def get_suject(self):
        subject = self.driver.find_element_by_xpath('//p[@id="title"]').text
        index = subject.find('、'.decode('utf-8'))
        subject = subject[index+1:]
        return subject

    def get_answer(self):
        an_list = []
        ans = self.driver.find_elements_by_xpath('//label/span')
        for an in ans:
            an_list.append(an)
        return an_list

    def get_progress(self):
        try:
            counter = self.driver.find_element_by_xpath('//span[@id="progress"]').text.split('/')
            return [int(i) for i in counter]
        except:
            return [0,0]

    def get_err_num(self):
        return int(self.driver.find_element_by_xpath('//span[@id="errorNum"]').text)

    def next_answer(self):
        self.driver.find_element_by_xpath('//button[@id="next"]').click()

    def next_level(self):
        self.driver.find_element_by_xpath('//button[text()="继续答题"]').click()

    def is_egg(self):
        try:
            self.driver.find_element_by_xpath('//div[@class="egg"]/ul/li/span')
        except:
            return True
        return False

    def easter_egg(self):
        try:
            self.driver.find_element_by_xpath('//div[@class="egg"]/ul/li/span').click() 
            self.click_wait(4)
            prize = self.driver.find_element_by_xpath('//div[@class="egg"]/ul/p[@id="result"]').text.encode('utf-8')
            GetLog().info(prize)
            self.driver.find_element_by_xpath('//div[@class="egg"]/ul/li[@class="curr"]').click() 
        except:
            return True
        return False
        
    def goto_computer(self):
        try:
            self.driver.find_element_by_xpath('//a[@href="/index/cglb/gk/?id=780"]').click()
        except:
            return True
        return False

    def get_level(self):
        link_list = []
        ele_list = self.driver.find_elements_by_xpath('//ul[@class="list"]/li/a[@href]') 
        for ele in ele_list:
            link_list.append(ele.get_attribute('href'))
        return link_list

    def default_option(self):
        answers = self.driver.find_elements_by_xpath('//input[@value]')
        answer = answers[0]
        # str = answer.get_attribute('value').encode('utf-8')
        answer.click()
        return [an.get_attribute('value').encode('utf-8') for an in answers]

def auto_answer(config):
    of = open('new_answer.txt','ab+')
    try:
        exer = ExerciseSystem()
        exer.open_link(lb_log_in)
        while(True):
            adm = adm_input.get()
            pwd = pwd_input.get()
            if (adm=='' or pwd==''):
                mb.askokcancel('输入提示框','账号或密码输入错误')
                continue
            exer.enter_adm_pwd(adm,pwd)
            vervode=dl.askstring('验证码提示框','请输入验证码')
            exer.input_pin(vervode)
            exer.log_in()
            time.sleep(7)
            if (exer.goto_computer()==False):
                time.sleep(7)
                break
        
        config.set_username(adm)
        config.set_password(pwd)
        config.Save()
        exer.switch_windows()
        lev_link = exer.get_level()
        for link in lev_link:
            exer.open_windows(link)
            time.sleep(7)
            exer.switch_windows()

            egg_clock = 0
            egg_flage = 0
            while(True):
                egg_clock += 1
                try:
                    subject = exer.get_suject()
                    net_ans = exer.get_answer()
                    if question_dict.has_key(subject):
                        local_ans = question_dict[subject]
                        for i in range(len(net_ans)):
                            if net_ans[i].text in local_ans:
                                net_ans[i].click()
                                time.sleep(1)
                    else:
                        wor = exer.default_option()
                        wor_str = ';'.join([str for str in wor])
                        line = '%s#%s\n'%(subject.encode('utf-8'),wor_str)
                        of.write(line)
                        time.sleep(1)
                    exer.next_answer()
                except:
                    print('traceback.format_exc():\n%s'%(traceback.format_exc()))
                time.sleep(exer.get_rand(6,12))
                total = exer.get_progress()[1]
                if (total == 0):
                    exer.next_level()
                    egg_clock = 0
                    egg_flage = 0
                    time.sleep(7)
                if (egg_clock>=15 and egg_flage==0):
                    if (exer.easter_egg()):
                        continue
                    else:
                        egg_clock = 0
                        egg_flage = 1
            exer.close()
            exer.switch_windows()            
    except :
        print('traceback.format_exc():\n%s'%(traceback.format_exc()))
    exer.quit()
    of.close()

if '__main__'==__name__:
    # 'xxzgltb0256'
    load_answer()
    cfg = ConfigManger()
    tk = Tk()
    tk.title('自动答题系统')
    tk.geometry('240x200')
    tk.resizable(width=False, height=False)

    # label如果设置大小，对齐方式将失效
    adm_label = Label(tk, text='Username：', compound='left')
    adm_label.place(x=70, y=10)
    adm_input = Entry(tk)
    adm_input.place(x=70, y=40, width=100, height=25)

    pwd_label = Label(tk, text='Password：', compound='left')
    pwd_label.place(x=70, y=80)
    pwd_input = Entry(tk, show='*')
    pwd_input.place(x=70, y=110, width=100, height=25)

    if (cfg.get_username()!='' and cfg.get_password()!=''):
        adm_input.insert (0,cfg.get_username())
        pwd_input.insert (0,cfg.get_password())

    login_btn = Button(tk, text='登录', command=lambda: auto_answer(cfg))
    login_btn.place(x=70, y=160, width=100, height=25)

    tk.mainloop()
