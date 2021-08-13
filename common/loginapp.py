#encoding='utf-8'
import json,requests, yaml
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

'''
env=input('请输入登陆的环境 test 或 uat：')
#productid = input('请输入报名课程productid：')
#env=confdata['loginapp']['env']

if env=='':
    #print('请正确填写测试的hostenv--test or uat')
    env = input('请正确填写测试的hostenv test 或 uat：')
elif env=='test':
    host='https://pxxapi-test.zzpxx.com/'
elif env=='uat':
    host = 'https://pxxapi-uat.zzpxx.com/'
else:
    print('-----see you later-----')
    exit(0)
'''
#grade=input('请输入年级：')
class loginapp(object):
    def __init__(self, env, host):
        print('------模拟登陆，获取登陆信息--------')
        self.env = env
        self.host = host
    def login(self,mobiles):
        #self.productid = input('请输入课程productid：')
        #mobiles = ['18603035521', '18566655875', '18565667162', '19921360101', '19921360102', '19921360103']
        self.mobiles=mobiles
        # mobiles = ['13528730220', '17740948369', '13528730223', '13603023939']
        #self.mobile = random.choice(self.mobiles)
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
        #self.mobiles=mobiles
        self.stus = []
        self.heads = []
        for self.mobile in self.mobiles:
            #print(self.mobile)
            self.codedata = {
                "phone": self.mobile
            }
            #print(self.codedata)
            self.url = self.host + 'oauth/send/code'
            # req = sessions.post(url=url,data=json.dumps(self.codedata),headers=getheaders(),verify=False)
            self.req = requests.post(url=self.url, data=json.dumps(self.codedata), headers=self.openheads, verify=False)
            self.rsp = self.req.json()
            #print(self.rsp)
            self.phonecode = self.rsp['data']['code']


            # 普通登录
            normallogin_url = self.host + 'oauth/loginByCode'
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
                print(self.mobile,'登录成功')
                self.logintoken = self.loginrsp['data']['token']
                #return self.logintoken
            else:
                print(self.mobile,'登录失败',self.loginrsp)
                exit(0)


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

            stu_url = self.host + 'hall/parent/findParentInfo'
            self.stu_data = {}
            stureq = requests.post(url=stu_url, data=json.dumps(self.stu_data), headers=self.stu_headers, verify=False)
            stursp = stureq.json()
            #print('学生信息：',stursp)
            self.stuid = stursp['data']['studentList'][0]['studentId']
            # print(self.stuid)
            self.stus.append(self.stuid)
            #print(self.stus)

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

                #return self.stuid, self.all_headers
            self.heads.append(self.all_headers)
        return self.heads
if __name__=='__main__':
    #mobiles = ['18603035521', '18566655875', '18565667162', '19921360101', '19921360102', '19921360103']
    f = open(r'../config/login.yml', 'r', encoding='UTF-8')
    confdata = yaml.load(f)
    tellist = confdata['loginapp']['telno']
    env=confdata['loginapp']['env']
    mobiles=tellist
    testlogin=loginapp(env=env,host='https://pxxapi-test.zzpxx.com/')
    testlogin.login(mobiles)

