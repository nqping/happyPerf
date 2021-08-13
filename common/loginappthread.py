#coding='utf-8'
#from common import logout
import gevent
from gevent import monkey
monkey.patch_all()
import json,requests,sys,yaml
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import ssl,os,datetime
from common import readenv
from threading import Thread,Lock
#sys.setrecursionlimit(3000)#设置递归最大次数
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
'''
env = input('请输入登陆的环境 test 或 uat：')
if env == 'test':
    host = 'https://pxxapi-test.zzpxx.com/'
elif env == 'uat':
    host = 'https://pxxapi-uat.zzpxx.com/'
else:
    print('-----see you later-----')
    exit(0)
'''
with open(r'../config/login.yml', 'r', encoding='UTF-8') as f:
    confdatas=yaml.safe_load(f)
    name=confdatas['loginapp']
    codeurl=name['codeurl']
    loginurl=name['apiurl']
    stuurl=name['stuurl']
f.close()
heads = []
stus = []
class loginapp(object):
    def __init__(self,host,channel):
        #self.logger = logout.Loggings()
        print('------模拟登陆开始，获取登陆信息--------')
        self.host=host
        self.channel=channel
        self.envdatas = readenv.readenv(self.channel)
        self.pubhead = json.loads(self.envdatas[2])
    def login(self,mobiles):
        lock=Lock()
        lock.acquire()
        #self.productid = input('请输入课程productid：')
        #mobiles = ['18603035521', '18566655875', '18565667162', '19921360101', '19921360102', '19921360103']
        self.mobile=mobiles
        # mobiles = ['13528730220', '17740948369', '13528730223', '13603023939']
        #self.mobile = random.choice(self.mobiles)
        '''
        self.openheads = {
            # ":method": "POST",
            # ":path": "/oauth/send/code",
            # ":authority": "pxxapi-uat.zzpxx.com",
            # ":scheme": "https",
            "content-type": "application/json;charset=utf-8",
            "app-version": "1.3.0",
            "app-platform": "android",
            "app-id": "pxxedu",
            "app-channel": "official",
            "version": "v1",
            "client": "2",
            "user-agent": "okhttp/3.14.9",
            "small_version": "1",
            "content-type": "application/json; charset=utf-8"
            }
        '''
        #print(self.openheads)
        self.openheads=self.pubhead
        self.codedata = {
                "phone": self.mobile
            }
        #print(self.codedata)
        self.url = self.host + codeurl
        # req = sessions.post(url=url,data=json.dumps(self.codedata),headers=getheaders(),verify=False)
        self.req = requests.post(url=self.url, data=json.dumps(self.codedata), headers=self.openheads, verify=False)
        self.rsp = self.req.json()
        #print(self.rsp)
        self.phonecode = self.rsp['data']['code']

        # 普通登录
        normallogin_url = self.host + loginurl
        # devicelogin_url=self.host+'api/auth/v1/normal/device'+'?t='+self.timestamp
        login_data = {
                    "phone": self.mobile,
                    "code": self.phonecode
                }
        # print(login_data)
        self.loginreq = requests.post(url=normallogin_url, data=json.dumps(login_data), headers=self.openheads,
                                              verify=False)
        self.loginrsp = self.loginreq.json()
        if self.loginrsp['code'] == 200:
            #print(self.mobile,'登录成功')
            self.logintoken = self.loginrsp['data']['token']
            #return self.logintoken
        else:
            print(self.mobile,'登录失败',self.loginrsp)
            exit(0)
        #self.logger.info('请求地址%s,请求参数：%s' % (normallogin_url,login_data))
        #self.logger.info('返回参数：%s' % self.loginrsp)
        # 获取学生id
        self.stu_headers = {
                    "Authorization": self.logintoken,
                    "app-version": "1.3.0",
                    "app-platform": "android",
                    "app-id": "pxxedu",
                    "app-channel": "official",
                    "version": "v1",
                    "client": "2",
                    "user-agent": "okhttp/3.14.9",
                    # "studentid":"452989c413034afe7085fc83c9acd86e",
                    "small_version": "1",
                    "content-type": "application/json; charset=utf-8"
                }
        # 获取学生id

        stu_url = self.host + stuurl
        self.stu_data = {}
        stureq = requests.post(url=stu_url, data=json.dumps(self.stu_data), headers=self.stu_headers, verify=False)
        stursp = stureq.json()
        if len(stursp['data']['studentList'])<1:
            print('-----登陆学员%s信息不全，获取学员studentId失败，请补充完整或更换学员-----'% self.mobile )
            sys.exit()
        else:
            self.stuid = stursp['data']['studentList'][0]['studentId']
        # print(self.stuid)
        stus.append(self.stuid)
        self.all_headers = {
                    "Authorization": self.logintoken,
                    "app-version": "1.3.0",
                    "app-platform": "android",
                    "app-id": "pxxedu",
                    "app-channel": "official",
                    "version": "v1",
                    "client": "2",
                    "user-agent": "okhttp/3.14.9",
                    "studentid": self.stuid,
                    "small_version": "1",
                    "content-type": "application/json; charset=utf-8"
                }

        heads.append(self.all_headers)
        lock.release()
        #return heads
def mythreads(mobiles,host,channel):
    testlogin=loginapp(host=host,channel=channel)
    threads = []
    for mobile in mobiles:
        #name = "%s" % (mobile)
        t = Thread(target=testlogin.login,args=(str(mobile),))
        threads.append(t)

    for t in threads:
        #tm=datetime.datetime.now()
        t.setDaemon(True)
        t.start()
        #print('线程%s，开始时间%s' % (t.name,tm))
        t.join()
    print('------完成登陆***登陆总数%d，登陆账户%s------'% (len(mobiles),mobiles))
    return heads



if __name__=='__main__':
    mythreads(['18565667162','13821370101','13821370102','13821370103','13821370104'],'https://pxxapi-test.zzpxx.com/','app')