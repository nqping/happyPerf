#encoding:utf-8
from locust import events
import logging
from logging.handlers import RotatingFileHandler
import pytz
import datetime
import os

PERF_HOST = 'https://www.baidu.com'  # 日志接收的服务地址
REPORT_LOCUST_LOGS_URL = '/test/logs'  # 日志API url
# 项目路径下创建log目录保存日志文件
time = datetime.datetime.now().strftime('%Y-%m-%d')
path = os.path.join(os.path.dirname(os.getcwd()), "logs")  # 拼接指定路径
#print(path)
#logpath=os.chdir(path)
logname='%s_locust.log' % time
# 判断目录是否存在，不存在则创建新的目录
if not os.path.isdir(path):
    os.makedirs(path)
    #REPORT_LOCUST_LOGS_URL =logpath
LOGGING_SECURE = False  # logging 发送请求方式 False ->http; True->https

class LocustLogHTTPHandler(logging.handlers.HTTPHandler):
    """用于发送日志"""

    def __init__(self, host, url, method="POST", secure=False, credentials=None, context=None, report_id=None,encoding='utf-8'):
        super().__init__(host, url, method=method, secure=secure, credentials=credentials, context=context)
        self.report_id = report_id

    def mapLogRecord(self, record):
        tz = pytz.timezone('Asia/Shanghai')
        asctime = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(record, 'name') and hasattr(record, 'message'):
            data = {"asctime": asctime, "name": record.name, "message": record.message}
        else:
            data = {"asctime": asctime, "name": 'requests', "message": str(record)}
        record_ = '%(asctime)s | %(name)s | %(message)s' % dict(data)
        record_msg = {'record': record_}
        return record_msg


class LocustLogger():
    """日志记录"""

    #def __init__(self, filePath, fileName):
    def __init__(self):
        self.filePath = path  # 存放文件的路径
        self.fileName = logname  # 存放文件的名字
        self.BACK_UP_COUNT = 100                    # 文件分割上限数
        self.MAX_LOG_BYTES = 1024 * 1024 * 20        # 单个文件最大记录数10M
        self.create_handler()  # 初始化创建日志handler
        self.create_logger()  # 初始化创建Logger
        self.LocutHttpHandler = None

    def create_handler(self):
        """建立handler"""
        self.handler = RotatingFileHandler(filename=os.path.join(self.filePath, self.fileName),
                                           # maxBytes=self.MAX_LOG_BYTES,
                                           # backupCount=self.BACK_UP_COUNT,
                                           delay=1
                                           )
        # 设定输出格式
        formatter = logging.Formatter('%(asctime)s | %(name)s | %(message)s')
        # formatter.converter = time.localtime                                      # 时间转换
        self.handler.setFormatter(formatter)  # 格式加载到handler
        log_host = PERF_HOST.replace('https://', '').replace('http://', '')
        #log_host = PERF_HOST
        if not all([log_host, REPORT_LOCUST_LOGS_URL, LOGGING_SECURE]):
            self.LocutHttpHandler = LocustLogHTTPHandler(log_host, url=REPORT_LOCUST_LOGS_URL, method="POST",
                                                         secure=LOGGING_SECURE)
            self.LocutHttpHandler.setFormatter(formatter)

    def create_logger(self):
        """建立Logger"""
        self.success_logger = logging.getLogger('Success')
        self.success_logger.propagate = False
        self.success_logger.addHandler(self.handler)

        self.failure_logger = logging.getLogger('Failure')
        self.failure_logger.propagate = False
        self.failure_logger.addHandler(self.handler)

        self.failure_logger = logging.getLogger('stderr')
        self.failure_logger.propagate = False
        self.failure_logger.addHandler(self.handler)

        #self.requests_logger = logging.getLogger('requests')
        self.requests_logger = logging.getLogger('Info')
        self.requests_logger.propagate = False
        self.requests_logger.addHandler(self.handler)

        if self.LocutHttpHandler:
            self.add_httphandler()

    def add_httphandler(self):
        self.success_logger.addHandler(self.LocutHttpHandler)
        self.failure_logger.addHandler(self.LocutHttpHandler)
        self.requests_logger.addHandler(self.LocutHttpHandler)

    def success_request(self, request_type, name, response_time, response_length):
        # 成功日志输出格式加载到Logger中
        msg = ' | '.join([str(request_type), name, str(response_time), str(response_length)])
        self.success_logger.info(msg)

    def failure_request(self, request_type, name, response_time,response_length, exception):
        msg = ' | '.join([str(request_type), name, str(response_time), str(response_length),str(exception)])
        self.failure_logger.info(msg)

    def execpt_error(self, locust_instance, exception, tb, *args, **kwargs):
        stderr_logger = logging.getLogger("stderr")
        stderr_logger.exception(exception)
        stderr_logger.exception('-' * 12)

    def get_locust_Hook(self):
        """钩子挂载到Locust中"""
        events.request_success.fire= self.success_request
        events.request_failure.fire= self.failure_request
        events.locust_error = self.execpt_error

    def get_locust_success_Hook(self):
        events.request_success += self.success_request

    def get_locust_failure_Hook(self):
        events.request_failure += self.failure_request

    def get_locust_error_Hook(self):
        events.locust_error += self.execpt_error

    def get_requests_log(self, method, path, requests, response):
        msg = ' | '.join([method, path, '请求数据: {}'.format(str(requests)), '返回数据: {}'.format(str(response))])
        self.requests_logger.info(msg)
        if self.LocutHttpHandler:
            self.LocutHttpHandler.emit(record=msg)  # 发送日志
if __name__=='__main__':
    LocustLogger()