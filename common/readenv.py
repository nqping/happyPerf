from configparser import ConfigParser
import json
#import os,sys
#os.path.abspath('../config/')
#os.chdir('../config/')
def readenv(channel):
    envconf = r'../config/env.ini'
    rf = ConfigParser(allow_no_value=True)
    rf.read(envconf, encoding='utf-8')
    #print(rf.sections())
    #print(rf.options('appenv'))
    #print(rf.items('appenv'))
    if channel=='app':
        sithost=rf['appenv']['sithost']
        uathost=rf.get('appenv','uathost')
        allheads=rf['appenv']['publicheader']
    elif channel=='pc':
        sithost=rf['pcenv']['sithost']
        uathost=rf.get('pcenv','uathost')
        allheads=rf['pcenv']['publicheader']
    else:
        print('-----请检查配置文件中channel为空-----')
    return sithost,uathost,allheads

if __name__=='__main__':
    readenv('app')