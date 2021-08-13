#coding:utf-8
import yaml,json
import os,sys
#os.path.abspath(__file__)
def readconfig(locustname):
    f=open(r'../config/configlocust.yml', 'r', encoding='UTF-8')
    try:
        global allparams
        confdata = yaml.safe_load(f)
        allparams=confdata[locustname]
        reqdatas = confdata[locustname]['reqfile']
        #if os.path.exists(reqdatas):
        if os.path.isfile(reqdatas):
            # 读取请求json文件
            # with open(reqdatas, 'r',encoding='UTF-8',errors='ignore') as rf:
            with open(reqdatas, 'r',encoding='utf-8',errors='ignore') as rf:
                reqparams = json.load(rf, encoding='utf-8')
                #print(json.dumps(reqparams,ensure_ascii=False))
                #print(reqparams)
            rf.close()
        else:
            print('当前目录未找到该方法请求body的json文件，系统自动生成空文件')
            with open(r'../reqdatas/%s.json' % locustname, 'w', encoding='UTF-8') as rf:
                rf.writelines('{ }')
                # reqdatas=f
            # f.close()
            with open(r'../reqdatas/%s.json' % locustname, 'r', encoding='UTF-8') as rf:
                reqparams = json.load(rf, encoding='utf-8')
            rf.close()

    except (IOError,ValueError,KeyError) as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(repr(e),exc_value)
        pass
    f.close()
    #print(env,apiurl,reqparams,circle,bf,loginmobilelist,logintokenlist,grade,productid)
    #return env,host,apiurl,reqparams,circle,bf,loginmobilelist,logintokenlist,grade,productid
    # datas={'env':env,'apiurl':apiurl,'circle':circle,'bf':bf,'loginmobile':loginmobilelist,'logintoken':logintokenlist,'grade':grade,'productid':productid,'channel':channel,'reqparams':reqparams}
    datas={'allparams':allparams,'reqjson':reqparams}
    #print(datas)
    return datas
if __name__=='__main__':
   #readconfig('pcaddstu')
   readconfig('getcoupon')