import json,requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import sys,ssl
#from locust import TaskSet,SequentialTaskSet,task,between
#from locust.contrib.fasthttp import FastHttpUser
#from pxx.common.readconfig_ex import readconfig
sys.path.append('..')
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
header = {
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
"""
def common(apiname):
    readcfg=readconfig(apiname)
    env=readcfg['allparams']['env']
    channel=readcfg['allparams']['channel']
    apiurl=readcfg['allparams']['apiurl']
    reqdatas=readcfg['reqparams']
    if env=='test' and channel=='pc':
        host='https://bm-test.zzpxx.com/'
    elif env=='uat' and channel=='pc':
        host = 'https://bm-uat.zzpxx.com/'
    elif env=='test' and channel=='app':
        host='https://pxxapi-test.zzpxx.com/'
    elif env=='uat' and channel=='app':
        host = 'https://pxxapi-uat.zzpxx.com/'
    else:
        print('----获取env失败，请检查配置文件是否完整')
        sys.exit()
    return host,apiurl,reqdatas
"""

#class reqmethod(TaskSet):
#def getmethod(apiname,host,pathurl,reqparams):
    #host,pathurl,reqparams=common(apiname)
def getmethod(host,apiurl):
    req=requests.get(url=host+apiurl,headers=header,verify=False)
    contents=req.json()
    assert contents['code']==200
    return contents
#def postmethod(apiname,host,pathurl,reqparams):
    # host, pathurl, reqparams = common(apiname)
def postmethod(host,apiurl,reqparams):
    req = requests.post(url=host + apiurl, data=json.dumps(reqparams), headers=header, verify=False)
    contents = req.json()
    assert contents['code'] == 200
    return contents
