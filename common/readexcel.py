import pandas as pd
from common.readconfig_ex import readconfig
def readdatas(locustname):
    '''
    df=pd.DataFrame(pd.read_excel(data_file))
    mobiles=df.iloc[:1]
    mobiles1 = df.loc[0]
    print(mobiles)
    '''
    rdconfig = readconfig(locustname)
    if 'datas' in rdconfig['allparams']:
        data_file = rdconfig['allparams']['datas']
        if data_file is None:
            print('---读取参数化文件为空，请补充configlocust.yml中datas文件路径-----')
            exit(0)
        #判断data_file是字典，那么解析读取
        #if type(data_file) is dict:
        #if isinstance(data_file,dict):
        datas={}
        #读取列为‘mobiles’的所有行,nrows读取前10行,将“mobiles”列数据类型强制规定为字符串（pandas默认将文本类的数据读取为整型）,header指定表头
            #df=pd.read_excel(io=data_file,sheet_name='Sheet1',usecols=['mobiles'],#header=1,nrows = 10,
             #                   converters = {'mobiles': str, 'stuid': int})#converters强制转换数据类型
        #读取所有列
        df=pd.read_excel(io=data_file, sheet_name='Sheet1')
        #获取所有列名,array转list（tolist()）
        #col_name=(df.columns.values).tolist()
        #获取指定列名的所有行值（返回array数组），即excel中所填写需要参数化的列头名称（可自定义修改）
        account=df['loginaccount'].values
        pwd=df['password'].values
        clsid=df['classid'].values
        #通过索引取第一列的值a_text
        #a_text=df.values[:-1,0]
        #array转list（tolist()函数）
        datas['loginaccount']=account.tolist()
        datas['password']=pwd.tolist()
        datas['classid'] = clsid.tolist()
        #print(datas)
        return datas
        #查询列为‘mobiles’的前两行
        #search=datas[['mobiles']].head(2)
        #search = datas['mobiles'].head(2)
    else:
        print('----不需要读取excel，已在yaml配置中字段参数化-----')
        exit(0)
def wrdatas(data_file,sheetname,datas):
    df = pd.DataFrame(datas)
    df.to_excel(io=data_file, sheet_name=sheetname,index=False)
if __name__=='__main__':
   #readdatas('../datas/locustname.xlsx')
   readdatas('usecoupon')