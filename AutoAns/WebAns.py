# This Python file uses the following encoding: utf-8

from PySide2.QtCore import QThread, QObject, Signal, QWaitCondition, QMutex

from urllib.parse import urlparse, parse_qs, quote
from selenium import webdriver
from lxml import etree
from Logger import GetLog
import requests
import json
import time
import random

class EmittingStream(QObject):
    text_written = Signal(str)  # 定义一个发送str的信号
    def write(self, text):
        self.text_written.emit(str(text))

class SignalSet(QObject):
    vercode_signal = Signal(str)

class Setup:
    UserLogin       = 0x01
    GetVercode      = 0x02
    CheckLogin      = 0x04
    ComputerGroup   = 0x08
    AllSetup        = 0xffff

class AutoAns(QThread):

    hdszgwslb = 'http://www.hdszgwslb.com'
    login_url = 'http://www.hdszgwslb.com/index/users/login'
    logout_url = 'http://www.hdszgwslb.com/index/users/logout'
    vercode_url = 'http://www.hdszgwslb.com/vercode/vercode.php?a=0.7732044146990473'
    check_login = 'http://www.hdszgwslb.com/index/users/chklogin'
    computer_url = 'http://www.hdszgwslb.com/index/cglb/gk/?id=780' # 计算机组的ID基本不会变
    answers_url = 'http://www.hdszgwslb.com/index/cglb/ajaxdt?passid=%s&id=%s&answer=%s&_=1612179898881'
    finish_url = 'http://www.hdszgwslb.com/index/cglb/passresult?passid=%s&matchid=%s'
    pass_url = 'http://www.hdszgwslb.com/index/cglb/gk?id=780&passtype=71&matchid=%s'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Accept-Encoding': 'gzip, deflate',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.hdszgwslb.com',
        'Upgrade-Insecure-Requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56'
    }

    joint = '~'

    post_data = dict()
    m_question = dict()
    m_rands = [1.5,5.5]
    m_err_ans = ''
    m_working = False

    m_cond = QWaitCondition()
    m_mutex = QMutex()

    vercode_signal = Signal(bytes)

    def __init__(self):
        super(AutoAns, self).__init__()
        self.session = requests.Session()
        self.load_answer()
    
    # 加载题库
    def load_answer(self):
        with open('answers.txt', encoding='utf-8') as f:
            for line in f:
                question,answer = line.strip('\n').split(self.joint)
                if (self.joint in question):
                    print(question)
                question = self.trim_space(question)
                if (question in self.m_question):
                    print(question)
                self.m_question[question] = answer.split(';')

    # get请求
    def get_request(self, url, israndom=0):
        if (not israndom):
            times = self.gen_random()
            self.implicitly_wait(times)
        result = self.session.get(url, headers=self.headers)
        if (result.status_code != 200):
            return None
        return result

    # post请求
    def post_request(self, url):
        times = self.gen_random()
        self.implicitly_wait(times)
        result = self.session.post(url, headers=self.headers, data=self.post_data)
        if (result.status_code != 200):
            return None
        return result

    # 打开登陆链接
    def open_login(self):
        if (self.get_request(self.login_url,True)==None):
            return False
        return True

    # 获取验证码图片数据
    def get_vercode(self):
        result = self.get_request(self.vercode_url,True)
        if (result == None):
            return False
        # with open('vercode.jpg','wb') as f:
        #     f.write(result.content)
        self.vercode_signal.emit(result.content)
        return True

    def set_interval(self, min, max):
        self.m_rands[0] = min
        self.m_rands[1] = max

    # 设置随机时间，uniform为浮点随机数
    def gen_random(self):
        return float(format(random.uniform(self.m_rands[0],self.m_rands[1]), '.1f'))

    # 等待
    def implicitly_wait(self, times):
        tick = 0.1
        click = 0
        while(True):
            click += tick
            if (click >= times):
                break
            if (not self.m_working):
                break
            time.sleep(tick)

    # 将BOM头去掉
    def filters_bom(self, text):
        json_text = text
        if json_text.startswith(u'\ufeff'):
            json_text = text.encode('utf8')[3:].decode('utf8') 
        return json_text

    def trim_space(self, title_str):
        return title_str.replace(' ', '')

    # 登陆验证
    def login(self):
        result = self.post_request(self.check_login)
        if (result == None):
            return False
        if result.cookies.get_dict() != {}:
            print("登陆成功!")
        json_text = self.filters_bom(result.text)
        statue_dic = json.loads(json_text)  
        if (statue_dic.get('status') == 2):
            print(statue_dic.get('message'))
            return False
        return True

    def logout(self):
        self.get_request(self.logout_url, True)
        self.get_request(self.hdszgwslb, True)

    def extrac_url(self, list):
        url_list = []
        for li in list:
            cglb = li.xpath('./@href')[0]
            url_list.append(self.hdszgwslb+cglb)
        return url_list

    def get_level(self, text):
        all_ans_url = []
        dom = etree.HTML(text)
        yellow_list = dom.xpath('//li[@class="bg_yellow"]/a')
        if (yellow_list):
            all_ans_url.extend(self.extrac_url(yellow_list)) 
        brown_list = dom.xpath('//li[@class="bg_brown"]/a')
        if (brown_list):
            all_ans_url.extend(self.extrac_url(brown_list))
        return all_ans_url

    def get_ans_total(self, level_url):
        result = self.get_request(level_url)
        try:
            dom = etree.HTML(result.text)
            prog = dom.xpath('//span[@id="progress"]')
            count = prog[0].xpath('text()')[0].split('/')[1]
        except:
            print(result.text)
            count = 0
        return count   

    def record_title(self, data, ans):
        ques = data['question']
        subject = self.trim_space(ques['title'])
        opt_list = ques['option']
        self.m_question[subject] = []
        for opt in opt_list:
            if (opt[0] in ans):
                self.m_question[subject].append(opt[1])
        with open('answers.txt', 'ab+') as of:
            str_data = '%s%s%s\n'%(subject, self.joint, ';'.join(self.m_question[subject]))
            print(str_data)
            of.write(bytes(str_data,'utf-8'))

    def filter_except(self, data):
        if ('answer' in data.keys()):
            ans_str = data['answer']
            # GetLog().info(self.m_err_ans)
            # GetLog().info('答案：%s'%(ans_str))
            # GetLog().info('==============================\n')
            self.record_title(self.m_err_ans,ans_str)
        if (data['isright'] == -1):
            GetLog().info(data)
            self.set_interval(2.5, 7.5)
            return 0
        if ('question' not in data.keys()):
            GetLog().info(data)
            return -1
        return 1
    
    def computer_group(self):
        result = self.get_request(self.computer_url)
        if (result == None):
            return False
        level_list = self.get_level(result.text)
        if (level_list == None):
            return False
        for u in level_list:
            if (not self.m_working):
                return -2
            # 解析URL获取其中的字段
            dest_str = urlparse(u)
            url_dic = dict(parse_qs(dest_str.query))
            # print(url_dic)
            passid = url_dic['id'][0]
            matchid = url_dic['matchid'][0]
            ans_str = '0'
            total = int(self.get_ans_total(u))
            if (total == 0):
                return -1
            print(total)
            for i in range(total+1):
                if (not self.m_working):
                    return -2
                # 获取第一个题目
                new_url = self.answers_url%(passid, matchid, ans_str)
                # print(new_url)
                # 尝试两次，如失败记录link退出
                result = self.get_request(new_url)
                if (result == None):
                    result = self.get_request(new_url)
                    if (result == None):
                        GetLog().info(new_url)
                        return 0
                json_text = self.filters_bom(result.text)
                question_dic = json.loads(json_text)
                ret = self.filter_except(question_dic)
                if (ret < 0):
                    return -3
                elif (ret == 0):
                    continue
                # GetLog().info(question_dic)
                ques = question_dic['question']
                subject = self.trim_space(ques['title'])
                # print('题目：%s'%(subject))
                # print('选项：%s'%(ques['option']))
                # print('类型：%s'%(ques['type']))
                # 题库中存在该题
                ans_str = ''
                if (subject in self.m_question.keys()):
                    local_ans = self.m_question[subject]
                    # print(local_ans)
                    for ans in ques['option']:
                        if (ans[1] in local_ans):
                            ans_str += ans[0]
                else: # 在题库中未找到该题目
                    GetLog().info('not found anawer!\n\ttitle: %s'%(subject))
                    for ans in ques['option']:
                        if (ans[1] == ''): continue
                        ans_str += ans[0]
                        break
                sort_ans = ''
                if (ques['type'] == '多选题'):
                    for s in sorted(ans_str):
                        sort_ans += s
                    ans_str = sort_ans
                # print('选择：%s'%(ans_str))
                ans_str = quote(ans_str, safe=';/?:@&=+$,', encoding='utf-8')
                matchid = ques['id']
                self.m_err_ans = question_dic # 缓存当前答题的数据，如果答错则记录
                print(i)
            finish_new = self.finish_url%(passid,'0')
            result = self.get_request(finish_new)
            print(result.text)
            if (result==None):
                return False

    def set_user_info(self, username, passwd, pin):
        self.post_data['username'] = username
        self.post_data['password'] = passwd
        self.post_data['vercode'] = pin
        self.m_cond.wakeOne()

    def wait_cond(self):
        self.m_mutex.lock()
        self.m_cond.wait(self.m_mutex)
        self.m_mutex.unlock()

    def starts(self):
        self.m_working = True
        self.start()

    def stops(self):
        self.m_mutex.lock()
        self.m_working = False
        self.m_mutex.unlock()

    def is_run(self):
        return self.m_working

    def run(self):
        setup = Setup.AllSetup
        while(self.m_working):
            if (setup & Setup.UserLogin):
                print('打开登陆页')
                if (not self.open_login()):
                    continue
                setup =  setup << 1
            if (setup & Setup.GetVercode):
                print('获取验证码')
                if (not self.get_vercode()):
                    continue
                self.wait_cond()
            if (setup & Setup.CheckLogin):
                print('用户登陆')
                if (not self.login()):
                    continue
                setup =  setup << 2
            if (setup & Setup.ComputerGroup):
                print('开始答题')
                code = self.computer_group()
                if (code == -1):
                    print('今天的闯关时间已用尽，请明天再来...')
                    return
                if (code == -2):
                    print('停止答题，并退出登录...')
                if (code == -3):
                    print('有未知的答题集合')
                    return
                if (code == 0):
                    print('请求错误')
        self.logout()
