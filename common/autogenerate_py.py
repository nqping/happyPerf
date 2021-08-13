from common import readconfig_ex
import os,sys

#当前文件绝对路径
p=os.path.abspath(__file__)
#当前文件所在目录
currdir=os.path.dirname(p)
#加入上级目录
path=sys.path.append('..')
pyname=input('请输入需要生成的压测pyname脚本名称:')
print('----开始自动化生成脚本----')
readcfg= readconfig_ex.readconfig(pyname)
channel=readcfg['allparams']['channel']
def generatepy():
    #获取当前文件上级目录并把生成脚本放到testcase目录
    testcasepath=os.path.abspath(os.path.join(os.getcwd(),"../testcase"))
    pyfilepath=r'%s\%s.py' % (testcasepath,pyname)
    print('脚本生成路径：%s ' % pyfilepath)
    # 写文件
    pyfile = open(pyfilepath, 'w',encoding='UTF-8')
    if channel=='pc':
        # 需要生成的脚本
        locust_script= """#coding='utf-8'
from gevent import monkey
monkey.patch_all()
import sys,os
sys.path.append(os.pardir)
os.path.abspath('..')
import yaml
from locust_plugins import jmeter_listener
from gevent._semaphore import Semaphore
from locust.contrib.fasthttp import FastHttpUser
import json,datetime,time
from locust import TaskSet, task,HttpUser,between,SequentialTaskSet,events,user,tag
import os,requests,ssl,random
import queue
from threading import Lock
from common import readconfig_ex,logger,readenv,readexcel
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#import sys
#sys.setrecursionlimit(15000)
ssl._create_default_https_context = ssl._create_unverified_context
readcfg=readconfig_ex.readconfig('%s')
logintoken=readcfg['allparams']['x-token']
startlogintoken=logintoken[0]
endlogintoken=logintoken[-1]
loginmobile=readcfg['allparams']['telno']
startloginmobile=loginmobile[0]
endloginmobile=loginmobile[-1]
circle=readcfg['allparams']['iscircle']
bf=readcfg['allparams']['isbf']
env=readcfg['allparams']['env']
reqparams=readcfg['reqjson']
apiurl=readcfg['allparams']['apiurl']
channel=readcfg['allparams']['channel']
try:
    ycnums=readcfg['allparams']['yctotals']
except (IOError,ValueError,KeyError) as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print(repr(e),exc_value,'配置文件yaml中未找到，取默认值100')
    ycnums=100
    pass

'''
#判断文件参数化配置，读取excel文件获取参数化数据
if 'datas' in readcfg['allparams']:
    paramdatas = readexcel.readdatas('%s')
    loginuser=paramdatas['loginaccount']
else:
    loginuser = readcfg['allparams']['username']
    #startloginmobile = loginmobile[0]
    #endloginmobile = loginmobile[-1]
'''
rdenv=readenv.readenv(channel)
# 判断压测环境test or uat
if env == 'test':
    host=rdenv[0]
elif env == 'uat':
    host=rdenv[1]
else:
    print('请正确填写测试的hostenv--test or uat')
    exit(0)
#把压测数据写入日志
logger = logger.LocustLogger()
#创建计数器用作集合点，当locust实例产生完成时触发（即所有用户启动完毕）
all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()
def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()
    logger.get_locust_Hook()
#挂在到locust钩子函数（所有的Locust示例产生完成时触发）
events.spawning_complete.add_listener(on_hatch_complete)
class %s(TaskSet):
    def on_start(self):
        print('-----star------')
    @task(20)#权重，数字越大占比越高
    def %s(self):
        try:
            #get_nowait() 取不到数据直接崩溃；get() 取不到数据会一直等待
            self.data=self.user.user_data_queue.get_nowait()
        except queue.Empty:  # 取不到数据时，走这里
            print('account data run out, test ended.')
            exit(0)
        #lock=Lock()
        #lock.acquire()
        self.turl = host + apiurl
        #对请求body进行参数化设置
        reqparams['name']=self.data['name']
        reqparams['grade']=grade
        reqparams['mobile']=self.data['phone']
        reqparams['token']=self.data['token']
        reqdatas=reqparams

        if bf=='true':
            all_locusts_spawned.wait()  # 集合点等待并发
        else:
            pass
        #print('------用户到达集合点了，开始执行------')
        nowtime = datetime.datetime.now().strftime('%%Y-%%m-%%d %%H:%%M:%%S.%%f')
        with self.client.post(path=self.turl,json=json.loads(json.dumps(reqdatas)),catch_response=True,verify=False) as checkresponse:
            contents=json.loads(checkresponse.text)
            if contents['code']==10000:
                #print(self.data['phone'],'操作时间',nowtime,'学员手机号' ,self.data['phone'],'成功', contents)
                checkresponse.success()
            else:
                #print(self.data['phone'],'操作时间',nowtime,'学员手机号' ,self.data['phone'],'失败', contents)
                checkresponse.failure('失败')
                #sys.exit()

        #lock.release()
        logger.get_requests_log(method='POST', path=apiurl, requests=orderdata, response=checkresponse.text)
        if circle=='true':
            self.user.user_data_queue.put_nowait(self.data)  # 把取出来的数据重新加入队列，如果不设置，队列取完后就停止
        else:
            exit(0)
    def on_stop(self):
        print('------stop--------')

class Websiteuser(FastHttpUser):
    print('-----准备压测-----')
    tasks = [%s]
    putdatas=[]
    for mobile in range(startloginmobile,endloginmobile):
        tokenlist=logintoken
        names=''.join(random.sample('没人满后是他竟然同时将投入时间可以考虑的讨论权限撒村刷卡机低收入家庭因为不同职能部门内哦该螯合钙染膏该阿后继人家饿哦还让二号然而还让就让他我今天人生就是可是冉冉尔何如嗯嗯我刚好',3))
        token=random.choice(tokenlist)
        datas={'mobile':mobile,'token':token,'name':names}
        putdatas.append(datas)
    user_data_queue = queue.Queue(maxsize=-1)  # 创建队列，先进先出,设置队列长度-1为无限
    #nowtime = datetime.datetime.now().strftime('%%Y-%%m-%%d %%H:%%M:%%S.%%f')
    #多用户唯一取数压测，循环插入队列
    if len(params)>1:
        for head in params:
            #eg：循环取出班级id（读取配置文件yaml获得），如不需要删除该for语句
            for cls in classids:
                data = {
                        "stus": dict(head)['studentid'],
                        "classid": cls，
                        "heads": head
                        # "threads":heads.index(head) #获取索引
                        }
                user_data_queue.put_nowait(data)  # 循环加入队列<全部>,循环完，继续执行
    #单用户压测
    else:
        # 单用户循环插入队列
        for ycnum in range(0,ycnums):
            #eg：循环取出班级id（读取配置文件yaml获得），如不需要删除该for语句
            for cls in classids:
                data = {
                    "stus": dict(params[0])['studentid'],
                    "heads": params[0],
                    #"threads": params.index(params[0]), # 获取索引
                    "classid": cls
                    }
                #print(data)
                user_data_queue.put_nowait(data)  # 循环加入队列<全部>,循环完，继续执行
    wait_time=between(1,2)#模拟用户在执行任务之间将等待时间
    host=host
    min_wait = 0  # 用户执行任务之间等待时间的下界，单位：毫秒;
    max_wait = 10  # 用户执行任务之间等待时间的上界，单位：毫秒;
    """ % (pyname,pyname,pyname,pyname,pyname)
        pyfile.writelines(locust_script)
    elif channel=='app':
        locust_script="""#coding='utf-8'
from gevent import monkey
monkey.patch_all()
import sys,os,yaml
sys.path.append(os.pardir)
os.path.abspath('..')
from gevent._semaphore import Semaphore 
from locust.contrib.fasthttp import FastHttpUser
import json,datetime,time
from locust import TaskSet, task,HttpUser,between,SequentialTaskSet,events,user
import os,requests,ssl
import queue,re
from threading import Lock
from common import readconfig_ex,loginapp,loginappthread,logger,readenv,readexcel
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#import sys
#sys.setrecursionlimit(5000)
ssl._create_default_https_context = ssl._create_unverified_context
#读取yaml配置文件，获取压测参数
readcfg=readconfig_ex.readconfig('%s')
circle=readcfg['allparams']['iscircle']
bf=readcfg['allparams']['isbf']
env=readcfg['allparams']['env']
reqparams=readcfg['reqjson']
apiurl=readcfg['allparams']['apiurl']
channel=readcfg['allparams']['channel']
try:
    ycnums=readcfg['allparams']['yctotals']
except (IOError,ValueError,KeyError) as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print(repr(e),exc_value,'配置文件yaml中未找到，取默认值100')
    ycnums=100
    pass

#判断配置文件参数化设置，读取excel文件获取参数化数据
if 'datas' in readcfg['allparams']:
    paramdatas = readexcel.readdatas('%s')
    loginmobile=paramdatas['loginaccount']
else:
    loginmobile = readcfg['allparams']['telno']
    #startloginmobile = loginmobile[0]
    #endloginmobile = loginmobile[-1]
rdenv=readenv.readenv(channel)
# 判断压测环境test or uat
if env == 'test':
    host = rdenv[0]
elif env == 'uat':
    host = rdenv[1]
else:
    print('请正确填写测试的hostaddr--test or uat')
    exit(0)
#初始化登陆获取信息
#多线程登陆
params = loginappthread.mythreads(loginmobile,host,channel)
#单线程登陆
#params = loginapp.loginapp().login(loginmobile)
#把压测数据写入日志
logger = logger.LocustLogger()
#创建计数器用作集合点，当locust实例产生完成时触发（即所有用户启动完毕）
all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()
def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()
    logger.get_locust_Hook()
#挂在到locust钩子函数（所有的Locust示例产生完成时触发）
events.spawning_complete.add_listener(on_hatch_complete)
class %s(TaskSet):
    def on_start(self):
        print('-----star------')
    @task(20)#权重，数字越大占比越高
    def %s(self):
        try:
            self.data = self.user.user_data_queue.get_nowait()  # 取值顺序
        except queue.Empty:  # 取不到数据时或压测用户设置总数大于队列大小时，退出程序
            print('account data run out, test ended.')
            exit(0)
        #lock=Lock()
        #lock.acquire()
        self.turl = host + apiurl
        #对请求body进行参数化设置
        reqparams['studentId']=self.data['stus']
        orderdata=reqparams
        self.headers=self.data['heads']
        if bf=='true':
            all_locusts_spawned.wait()  # 设置集合点等待并发，限制在所有用户准备完成前处于等待状态
        else:
            pass
        #print('------用户到达集合点了，开始执行------')
        nowtime=datetime.datetime.now().strftime('%%Y-%%m-%%d %%H:%%M:%%S.%%f')
        #catch_response=True通过判断返回状态码设置检查点
        with self.client.post(path=self.turl, data=json.dumps(orderdata),headers=self.headers,catch_response=True,verify=False) as checkresponse:
            contents=json.loads(checkresponse.text)
            if contents['code']==200:
                #print('提交时间',nowtime,'学员stuid' ,self.data['stus'],'提交生成订单成功', contents)
                checkresponse.success()
            elif contents['code']==1000110010:
                #print('提交时间',nowtime,'学员stuid' ,self.data['stus'],'提交数据过期', contents)
                checkresponse.failure('提交失败')
                #sys.exit()
            else:
                #print('提交时间',nowtime,'学员stuid' ,self.data['stus'],'提交生成失败', contents)
                checkresponse.failure('提交失败')
                #sys.exit()

        #lock.release()
        logger.get_requests_log(method='POST', path=apiurl, requests=orderdata, response=checkresponse.text)
        if circle=='true':
            self.user.user_data_queue.put_nowait(self.data)  # 把取出来的数据重新加入队列，如果不设置，队列取完后就停止
        else:
            exit(0)
    def on_stop(self):
        print('------stop--------')

class Websiteuser(FastHttpUser):
    print('-----准备压测-----')
    tasks = [%s]
    user_data_queue = queue.Queue(maxsize=-1)  # 创建队列，先进先出,设置队列长度
    #多用户压测保证数据唯一性，循环插入队列
    if len(params)>1:
        for head in params:
            #eg：循环取出班级id（读取配置文件yaml获得），如不需要删除该for语句
            for cls in classids:
                data = {
                        "stus": dict(head)['studentid'],
                        "classid": cls,
                        "heads": head
                        # "threads":heads.index(head) #获取索引
                        }
                user_data_queue.put_nowait(data)  # 循环加入队列<全部>,循环完，继续执行
    #单用户压测
    else:
        # 单用户循环取数，插入队列,数据重复使用
        for ycnum in range(0,ycnums):
            #eg：循环取出班级id（读取配置文件yaml获得），如不需要删除该for语句
            for cls in classids:
                data = {
                    "stus": dict(params[0])['studentid'],
                    "heads": params[0],
                    #"threads": params.index(params[0]), # 获取索引
                    "classid": cls
                    }
                #print(data)
                user_data_queue.put_nowait(data)  # 循环加入队列<全部>,循环完，继续执行
    wait_time=between(1,2)#模拟用户在执行任务之间将等待时间
    host= host
    min_wait = 0  # 用户执行任务之间等待时间的下界，单位：毫秒;
    max_wait = 10  # 用户执行任务之间等待时间的上界，单位：毫秒;
    """ % (pyname,pyname,pyname,pyname,pyname)
        pyfile.writelines(locust_script)
    pyfile.close()
    print('----压测脚本已自动生成，请手动对脚本中请求body进行参数化，如不需要参数化可直接使用----')

if __name__=="__main__":
    generatepy()
