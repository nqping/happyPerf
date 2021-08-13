#coding:utf-8
#import assemble_message
import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.requests import Request
from typing import TypeVar, Generic, Type, Any
#from xml.etree.ElementTree import fromstring
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import json,datetime,time

app = FastAPI(title="实时数据mock",version="1.0")  # 必须实例化该类，启动的时候调用
#T = TypeVar("T", bound=BaseModel)
nowtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())


class gzbank_req(BaseModel):  # 必须继承
   #贵州银行
    nsrsbh: str
    nsrmc: str
    yhsqdh: str
    yhxyysbh: str
    cpmc: str
#天津农行预警
class tjnh_ycmd(BaseModel):  # 必须继承
   reqDate: str
   acqTrace: str
   trancode: str
   reqTime: str
   abnormalPayerList: list
   #payerId: str
#天津农行税局认证

class tjnh_auth(BaseModel):  # 必须继承

    banklpbm:str
    bankId:str
    nsrsbh:str
    data:str
"""
class tjnh_auth(Generic[T]):
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
    @app.post('/tjnhauth')
    async def tjnhauth(self, request: Request) -> T:
        # the following check is unnecessary if always using xml,
        # but enables the use of json too
        print(request.headers.get("Content-Type"))
        if '/xml' in request.headers.get("Content-Type", ""):
        #if request.headers.get("Content-Type")== "text/xml":
            body = await request.body()
            doc = fromstring(body)
            print(doc)
            dict_data = {}
            for node in doc.getchildren():
                dict_data[node.tag] = node.text
        else:
            dict_data = await request.json()
            print(dict_data)
        return self.model_class.parse_obj(dict_data)
        #return tjnhauth
"""
#天津农行取数-五要素
class tjnh_fetchdata(BaseModel):  # 必须继承
   banklpbm:str
   biztype: str
   #shxydm:str
   bankId:str
   nsrsbh:str
   #ywlsh:str
   #isRefetch:str
   #cpbm:str
   #qslx:str
   #type:#str
   data:str

# 天津农行-贷前订单推送税务数据给银行
class tjnh_prepush(BaseModel):  # 必须继承
    trancode: str
    channel: str
    encryptFlag: str
    accsta: str
    timestamp: str
    data:dict
    #resCode: str
    #resMessage: str

# 天津农行-贷后税务数据推送银行
class tjnh_loanpush(BaseModel):  # 必须继承
    #businessContent: dict
    trancode: str
    channel: str
    encryptFlag: str
    accsta: str
    timestamp: str
    data: dict
# 天津农行-贷后反馈放款明细
class tjnh_fkxx(BaseModel):  # 必须继承
    """
    banklpbm:str
    biztype: str
    #shxydm:str
    bankId:str
    nsrsbh:str
    data:str
    """
    pass
"""
#泉州银行腾讯反欺诈
class qzyh_fqz(BaseModel):  # 必须继承
    #CLIENT_NAME: str
    #GLOBAL_ID: str
    #MOBILE: str
    #APP_HEAD:dict
    #FILE_SVR_IP:str
    #FILE_SVR_PORT:str
    #FILE_PATH:str
    #FILE_NAME:str
    #SYS_HEAD:dict
    #BODY:dict
    pass
"""

with open(r'F:\测试项目\贵州银行\response.json', 'r') as load_f:
    load_dict = json.load(load_f, encoding='UTF-8')
    # print(load_dict)
gzbankbody = load_dict
with open(r'F:\测试项目\天津发改委\tjnhycmd_response.json', 'r') as load_f:
    load_dict = json.load(load_f,encoding='UTF-8')
    #print(load_dict)
tjnhycmd=load_dict
#认证返回报文
with open(r'F:\测试项目\天津发改委\auth_response.json', 'r') as load_f:
    load_dict = json.load(load_f,encoding='UTF-8')
tjnhauth=load_dict
#取数五要素返回报文
with open(r'F:\测试项目\天津发改委\fetchdata_response.json', 'r') as load_f:
    load_dict = json.load(load_f,encoding='UTF-8')
tjnhfetchdata=load_dict
#贷后反馈放款明细
with open(r'F:\测试项目\天津发改委\fkmx_response.json', 'r') as load_f:
    load_dict = json.load(load_f,encoding='UTF-8')
fkxx=load_dict
#贷后反馈授信明细
with open(r'F:\测试项目\天津发改委\sxxx_response.json', 'r') as load_f:
    load_dict = json.load(load_f,encoding='UTF-8')
sxxx=load_dict
#贷后反馈明细
with open(r'F:\测试项目\天津发改委\mxxx_response.json', 'r') as load_f:
    load_dict = json.load(load_f,encoding='UTF-8')
mxxx=load_dict
#贷前推送税务数据
with open(r'F:\测试项目\天津发改委\prepush_response.json', 'r') as load_f:
    load_dict = json.load(load_f,encoding='UTF-8')
tjnhprepush=load_dict
#贷后税务数据推送银行
with open(r'F:\测试项目\天津发改委\loanpush_response.json', 'r') as load_f:
    load_dict = json.load(load_f,encoding='UTF-8')
tjnhloanpush=load_dict
"""
#泉州银行腾讯反欺诈
with open(r'F:\测试项目\泉州银行\tencentfqz.json', 'r') as load_f:
    load_dict = json.load(load_f,encoding='UTF-8')
qzyhfqz=load_dict
"""
#resbody=json.dumps(load_dict)
#读取接口文档excel获取返回body
#resbody=assemble_message.readexcel()
#print('返回body：%s'% resbody)

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    #print(f"请求参数错误{request.method} {request.url} {await request.body()}")
    return JSONResponse({"code": "422", "message": exc.errors(),"reqbody":exc.body})
    #return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}))


# 请求根目录
@app.get('/')
async def index():
    return gzbankbody

# get请求带参数数据
@app.get('/getDksqxx_gzyh/{item_id}')
async def get_data(item_id: int):
    #assemble_message.wrexcelbody()
    return {'message': '欢迎来到mock接口'}


# post请求带参数数据,贵州银行
@app.post('/getDksqxx_gzyh')
async def gzbankdata(loan:gzbank_req,request: Request):
    '''
    #age = loan.age
    #msg = f'名字：{loan.name}，年龄：{age}'
    #assemble_message.wrexcelbody()
    #print(f"请求参数{request.method} {request.client} {request.scope}")
    '''
    reqbody=loan.json(ensure_ascii=False)
    print("请求时间：{},请求参数：{}" .format(nowtime,reqbody))
    return gzbankbody
@app.post('/tjnhycmd')
async def fetchdata(loan:tjnh_ycmd,request: Request):
    reqbody=loan.json(ensure_ascii=False)
    print("请求时间：{},请求参数：{}" .format(nowtime,reqbody))
    return tjnhycmd
#授权认证
@app.post('/tjnhauth')
async def auth(loan:tjnh_auth,request: Request):
    reqbody=loan.json(ensure_ascii=False)
    print("请求时间：{},请求参数：{}" .format(nowtime,reqbody))
    return tjnhauth
#采集取数
@app.post('/tjnhqs')
async def fetchdata(loan:tjnh_fetchdata,request: Request):
    reqbody=loan.json(ensure_ascii=False)
    print("请求时间：{},请求参数：{}" .format(nowtime,reqbody))
    return tjnhfetchdata
#贷前推数给银行
@app.post('/tjnhprepush')
async def fetchdata(loan:tjnh_prepush,request: Request):
    reqbody=loan.json(ensure_ascii=False)
    print("请求时间：{},请求参数：{}" .format(nowtime,reqbody))
    return tjnhprepush

#贷后推数给银行
@app.post('/tjnhloanpush')
async def fetchdata(loan:tjnh_loanpush,request: Request):
    reqbody=loan.json(ensure_ascii=False)
    print("请求时间：{},请求参数：{}" .format(nowtime,reqbody))
    return tjnhloanpush
#贷后反馈放款明细
@app.post('/tjnhfkxx')
async def fetchdata(loan:tjnh_fkxx,request: Request):
    reqbody=loan.json(ensure_ascii=False)
    print("请求时间：{},请求参数：{}" .format(nowtime,reqbody))
    return fkxx
#贷后反馈授信明细
@app.post('/tjnhsxxx')
async def fetchdata(loan:tjnh_fkxx,request: Request):
    reqbody=loan.json(ensure_ascii=False)
    print("请求时间：{},请求参数：{}" .format(nowtime,reqbody))
    return sxxx
#贷后反馈明细
@app.post('/tjnhmxxx')
async def fetchdata(loan:tjnh_fkxx,request: Request):
    reqbody=loan.json(ensure_ascii=False)
    print("请求时间：{},请求参数：{}" .format(nowtime,reqbody))
    return mxxx
"""
#泉州银行腾讯分反欺诈
@app.post('/qzyhfqz')
async def qzbank(loan:qzyh_fqz,request: Request):
    #reqbody=loan.json(ensure_ascii=False)
    #reqbody=loan.value
    #print("请求参数：%s" % reqbody)
    return qzyhfqz
"""

if __name__ == '__main__':
    #uvicorn.run(app=app, host="127.0.0.1", port=8086)
    uvicorn.run(app='mock:app', host="0.0.0.0", port=8088,reload=True, debug=True)


