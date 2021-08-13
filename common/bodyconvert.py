#encoding：utf-8
import json,os
import xmltodict
from common.readconfig_ex import readconfig
p=os.path.abspath(__file__)
os.path.dirname(p)
#获取当前文件所在路径
filepath= os.getcwd()
def getfile(locustname):
    readconf=readconfig(locustname)
    bodyfile=readconf['allparams']['reqfile']
    with open(bodyfile,'r',encoding='utf-8') as rf:
        #reqjson = json.load(rf, encoding='UTF-8')
        reqbody=rf.read()
        #print(reqbody)
    rf.close()
    return reqbody,bodyfile
# xml转json的函数
def xml_to_json(xml_str):
    # parse是的xml解析器
    xml_parse = xmltodict.parse(xml_str)
    # json库dumps()是将dict转化成json格式,loads()是将json转化成dict格式。
    # dumps()方法的ident=1,格式化json
    json_str = json.dumps(xml_parse, indent=1)
    return json_str

'''
a = {
    "user_info": {
        "id": 12,
        "name": "Tom",
        "age": 12,
        "height": 160,
        "score": 100,
        "variance": 12
    }
}
'''
# json转xml函数
def json_to_xml(json_str):
    # xmltodict库的unparse()json转xml
    # 参数pretty 是格式化xml
    #xml_str = xmltodict.unparse(json_str, pretty=1)
    xml_str = xmltodict.unparse(json.loads(json_str), pretty=1)
    return xml_str

def bodyconvert(locustname):
    reqbody=getfile(locustname)[0]
    filename=getfile(locustname)[1]
    # 获取请求文件后缀名
    file_extension = os.path.splitext(filename)[-1]
    #print(file_extension)
    if file_extension=='.xml':
        return xml_to_json(reqbody)
    elif file_extension=='.json':
        return json_to_xml(reqbody)
    else:
        print('----该后缀请求文件%s无法识别，请检查后（只处理xml、json后缀名文件）操作-----'% filename)
        exit(0)
if __name__=="__main__":
    t=bodyconvert('apporderlocust')
    print(t)