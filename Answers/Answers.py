#coding:utf-8

import os
import time
import traceback
import random
import ConfigParser
import threading
from Tkinter import *
from Logger import GetLog
from selenium import webdriver
import tkSimpleDialog as dl  
import tkMessageBox as mb  


hdszgwslb = 'http://www.hdszgwslb.com/'
lb_log_in = 'http://www.hdszgwslb.com/index/users/login'

question_dict = {}
exer = None
anlv = 0

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
    times = [1,1]
    state = False
    level = 0

    def __init__(self):
        # path = r'%s\chromedriver.exe'%(os.path.abspath('.'))
        self.driver = webdriver.Chrome('chromedriver.exe')
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)

    def close_windows(self):
        self.driver.close()

    def quit_chrome(self):
        self.driver.quit()

    def refresh_page(self):
        self.driver.refresh()

    def windows_handles(self):
        return self.driver.window_handles

    def switch_windows(self):
        handles = self.windows_handles()
        self.driver.switch_to_window(handles[-1])

    def open_windows(self,link):
        new_window = 'window.open("%s")'%(link)
        self.driver.execute_script(new_window)

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
        self.click_wait(self.get_rand())
        self.get_suject()

    def click_wait(self,value=1):
        time.sleep(value)

    def get_rand(self):
        return random.randint(self.times[0],self.times[1])

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

    def get_levels(self):
        link_list = []
        ele_list = self.driver.find_elements_by_xpath('//ul[@class="list"]/li/a[@href]') 
        for ele in ele_list:
            link_list.append(ele.get_attribute('href'))
        return link_list

    def default_option(self):
        answers = self.driver.find_elements_by_xpath('//input[@value]')
        answer = answers[0]
        answer.click()
        ans = self.driver.find_elements_by_xpath('//label/span')
        return [an.text.encode('utf-8') for an in ans]

    def set_times(self,li):
        if ((li[0]<2 or li[1]<2) and (li[0] > li[1])):
            pass
        else:
            self.times = li
    
    def log_out(self):
        if self.state :
            self.state = False
            return True
        else:
            return False
    
    def set_state(self,flage):
        self.state = flage

def do_title(file):
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
        file.write(line)
        time.sleep(1)
    exer.next_answer()

def working(file,num):
    egg_clock = 0
    egg_flage = 0
    err_clock = 0
    while(True):
        if exer.log_out():
            # exer.quit_chrome()
            # file.close()
            raise Exception('退出答题！')
        egg_clock += 1
        try:
            do_title(file)
            err_clock = 0
        except:
            err_clock += 1
            if (err_clock == 5):
                exer.refresh_page()
                egg_clock = 0
            print('traceback.format_exc():\n%s'%(traceback.format_exc()))
        time.sleep(exer.get_rand())
        total = exer.get_progress()[1]
        if (total == 0):
            exer.next_level()
            egg_clock = 0
            egg_flage = 0
            time.sleep(7)
            if (num == 9):
                return
        if (egg_clock>=15 and egg_flage==0):
            if (exer.easter_egg()):
                continue
            else:
                egg_clock = 0
                egg_flage = 1

def auto_answer(config):
    try:
        of = open('new_answer.txt','ab+')
        exer.switch_windows()
        lev_link = exer.get_levels()
        # lev_link.reverse()
        size = len(lev_link)
        for i in range(anlv,size):
            link = lev_link[i]
            exer.open_windows(link)
            time.sleep(7)
            exer.switch_windows()
            working(of,i)
            exer.close_windows()
            exer.switch_windows()            
    except :
        GetLog().info('traceback.format_exc():\n%s'%(traceback.format_exc()))
    exer.quit_chrome()
    of.close()

def log_in(config):
    global exer
    exer = ExerciseSystem()
    exer.open_link(lb_log_in)
    while(True):
        adm = adm_input.get()
        pwd = pwd_input.get()
        if (adm=='' or pwd==''):
            mb.showwarning(title='输入提示框',message='账号或密码输入错误,请重新输入！')
            # raise Exception('账号或密码输入错误')
            continue
        exer.enter_adm_pwd(adm,pwd)
        vervode=dl.askstring('验证码提示框','请输入验证码')
        exer.input_pin(vervode)
        exer.log_in()
        time.sleep(5)
        if (exer.goto_computer()==False):
            time.sleep(5)
            break
    config.set_username(adm)
    config.set_password(pwd)
    config.Save()

def begin_answers(config):
    set_mainwin_state(DISABLED)
    log_in(config)
    t = threading.Thread(target=auto_answer, args=(config,))
    t.setDaemon(True) # 守护线程  
    t.start()

def set_mainwin_state(states):
    login_btn.config(state=states)
    adm_input.config(state=states)
    pwd_input.config(state=states)

def end_answers():
    exer.set_state(True)
    set_mainwin_state(NORMAL)

def enter(handles):
    if (handles[1]['state']==NORMAL and handles[2]['state']==NORMAL):
        exer.set_times([int(handles[1].get()),int(handles[2].get())])
    elif (handles[3]['state']==NORMAL):
        global anlv
        anlv = abs(int(handles[3].get())-1)
        if (anlv>10):
            anlv = 9
    handles[0].destroy() 

def option_windows():
    opt_win = Toplevel(tk)
    opt_win.title('选项')
    opt_win.geometry(screen_center(opt_win,200,200))
    opt_win.resizable(width=False, height=False)

    # enter_state = NORMAL
    if login_btn['state'] == DISABLED:
        enter_state = NORMAL
    else:
        enter_state = DISABLED

    lb_gap = Label(opt_win,text='答题间隔')
    lb_gap.place(x=35, y=10)

    btn_low = Entry(opt_win,state=enter_state)
    btn_low.place(x=35, y=40, width=50, height=25)

    lb_line = Label(opt_win,text='——')
    lb_line.place(x=90, y=40, width=20, height=20)

    btn_hight = Entry(opt_win,state=enter_state)
    btn_hight.place(x=115, y=40, width=50, height=25)

    lb_level = Label(opt_win,text='答题关卡')
    lb_level.place(x=35, y=80)

    btn_level = Entry(opt_win)
    btn_level.place(x=35, y=110, width=50, height=25)
    
    handles=[opt_win,btn_low,btn_hight,btn_level]
    btn_enter=Button(opt_win,text='确定',command=lambda: enter(handles)) # 不使用lambda会自动执行回调函数
    btn_enter.place(x=75, y=150, width=50, height=25)
    tk.mainloop()

def screen_center(handles,width,height):
    screenwidth = tk.winfo_screenwidth()
    screenheight = tk.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth-width)/2, (screenheight-height)/2)
    return alignstr

if '__main__'==__name__:
    # chcp 65001 UTF-8
    # chcp 936   GB2312
    load_answer()
    cfg = ConfigManger()
    tk = Tk()
    tk.title('自动答题系统')
    tk.geometry(screen_center(tk,240,200))
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

    login_btn = Button(tk, text='登录', command=lambda: begin_answers(cfg))
    login_btn.place(x=70, y=160, width=40, height=25)

    logout_btn = Button(tk, text='登出', command=end_answers)
    logout_btn.place(x=130, y=160, width=40, height=25)

    main_menu = Menu(tk)
    menu_set = Menu(main_menu,tearoff=0)  # 设置分组, tearoff=0 去掉虚线
    main_menu.add_cascade(label='设置',menu=menu_set)
    menu_set.add_command(label='选项',command=option_windows)
    tk.config(menu=main_menu)
    
    if (cfg.get_username()!='' and cfg.get_password()!=''):
        adm_input.insert (0,cfg.get_username())
        pwd_input.insert (0,cfg.get_password())

    tk.mainloop()
