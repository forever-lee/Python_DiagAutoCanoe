import os

import time
from pathlib import Path

from win32com.client import *
from win32com.client.connect import *


def DoEvents():
    pythoncom.PumpWaitingMessages()
    time.sleep(.1)


def DoEventsUntil(cond):
    while not cond():
        DoEvents()


# Vector Canoe Class
class CANoe:
    Started = False
    Stopped = False
    ConfigPath = ""

    def __init__(self, visible=True):
        """
        产生一个canoe的com对象，启动了canoe软件,但是未加载任何工程
        :param visible: 其实可以设置canoe对于cfg文件是否保存
        """
        self.application = None
        self.application = DispatchEx("CANoe.Application")
        self.ver = self.application.Version
        print('Loaded CANoe version ',
              self.ver.major, '.',
              self.ver.minor, '.',
              self.ver.Build, '...')
        # 这里是可以获取到canoe工程是否在启动,这个数值是True或者False
        self.Measurement = self.application.Measurement.Running

    def open_cfg(self, cfg_path_file):
        """
        加载cfg工程文件
        :param cfg_path_file:cfg文件的路径,这是是canoe加载cfg文件成功
        :return:
        """
        cfg_path_file = os.path.abspath(cfg_path_file)
        self.ConfigPath = cfg_path_file
        if (self.application != None):
            if os.path.isfile(cfg_path_file) and (os.path.splitext(cfg_path_file)[1] == ".cfg"):
                self.application.Open(cfg_path_file)
                print("opening..." + cfg_path_file)
            else:
                raise RuntimeError("Can't find CANoe cfg file")
        else:
            raise RuntimeError("CANoe Application is missing,unable to open simulation")

    def close_cfg(self):
        """
        退出canoe
        :return:
        """
        if (self.application != None):
            print("close cfg ...")
            # self.stop_Measurement()
            self.application.Quit()
            self.application = None

    def start_measurement(self):
        """
        启动测量
        :return:
        """
        retry = 0
        retry_counter = 5
        # try to establish measurement within 5s timeout
        while not self.application.Measurement.Running and (retry < retry_counter):
            self.application.Measurement.Start()
            time.sleep(1)
            retry += 1
        if (retry == retry_counter):
            raise RuntimeWarning("CANoe start measuremet failed, Please Check Connection!")

    def stop_measurement(self):
        """
        停止测量
        :return:
        """
        if self.application.Measurement.Running:
            self.application.Measurement.Stop()
        else:
            pass

    def get_sigval(self, channel_num, msg_name, sig_name, bus_type="CAN"):
        """
        获取信号的值
        :param channel_num:
        :param msg_name:
        :param sig_name:
        :param bus_type:
        :return:
        """
        if (self.application != None):
            result = self.application.GetBus(bus_type).GetSignal(channel_num, msg_name, sig_name)
            return result.Value
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def set_sigval(self, channel_num, msg_name, sig_name, bus_type, setValue):
        """
        设置信号的值
        :param channel_num:
        :param msg_name:
        :param sig_name:
        :param bus_type:
        :param setValue:
        :return:
        """
        if (self.application != None):
            result = self.application.GetBus(bus_type).GetSignal(channel_num, msg_name, sig_name)
            result.Value = setValue
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def get_EnvVar(self, var):
        if (self.application != None):
            result = self.application.Environment.GetVariable(var)
            return result.Value
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def set_EnvVar(self, var, value):
        result = None
        if (self.application != None):
            # set the environment varible
            result = self.application.Environment.GetVariable(var)
            result.Value = value
            checker = self.get_EnvVar(var)
            # check the environment varible is set properly?
            while (checker != value):
                checker = self.get_EnvVar(var)
        else:
            raise RuntimeError("CANoe is not open,unable to SetVariable")

    def get_system_variable_value(self, sys_var_name):
        """获取系统环境变量的值
        参数:
            sys_var_name (str): "sys_var_demo::speed"
        Returns:
            返回该系统变量的值
        """
        namespace = '::'.join(sys_var_name.split('::')[:-1])
        variable_name = sys_var_name.split('::')[-1]
        return_value = None
        try:
            namespace_com_object = self.application.System.Namespaces(namespace)
            variable_com_object = namespace_com_object.Variables(variable_name)
            return_value = variable_com_object.Value
        except Exception as e:
            raise RuntimeError("CANoe is not open,unable to")
        return return_value

    def set_system_variable_value(self, ns_name, sysvar_name, var):
        """
        设置系统环境变量的值,这里对该值进行了判断,如果类型不对设置会直接报错
        :param ns_name:
        :param sysvar_name:
        :param var:
        :return:
        """
        try:
            namespace_com_object = self.application.System.Namespaces(ns_name)
            variable_com_object = namespace_com_object.Variables(sysvar_name)
            if isinstance(variable_com_object.Value, int):
                variable_com_object.Value = int(var)
            elif isinstance(variable_com_object.Value, float):
                variable_com_object.Value = float(var)
            else:
                variable_com_object.Value = var
            self.log.info(f'system variable({sysvar_name}) value set to -> {var}.')
        except Exception as e:
            self.log.info(f'failed to set system variable({sysvar_name}) value. {e}')

    def init_service(self, network, device):
        """
        建立诊断服务
        :param network: 网段
        :param device: ECU qualifier
        :return:
        """
        time.sleep(10)
        self.__gDiag = self.application.Networks(network).Devices(device).Diagnostic

    def start_TesterPresent(self):
        """
        开启诊断仪在线
        :return:
        """
        self.__gDiag.DiagStartTesterPresent()

    def stop_TesterPresent(self):
        """
        停止诊断仪在线
        :return:
        """
        self.__gDiag.DiagStopTesterPresent()

    def _diag_Request(self, qualifier, stream_flag=False):
        """
        执行服务
        :param qualifier:
        :param stream_flag: True以字节流形式发送，False根据具体限定符发送
        :return:
        """

        global diag_request
        if not stream_flag:
            diag_request = self.__gDiag.CreateRequest(qualifier)
        else:
            diag_request = self.__gDiag.CreateRequestFromStream(bytes.fromhex(qualifier.replace(" ", "")))

        diag_request.Send()

    def send_Diag_Request(self, qualifier, stream_flag=False):
        """
        发送请求
        :param qualifier:
        :param stream_flag: True以字节流形式发送，False根据具体限定符发送
        :return:
        """
        try:
            self._diag_Request(qualifier, stream_flag)
            return True
        except Exception as e:
            print(f'failed to send request. {e}')
            return False

    def check_Diag_Positive(self):
        _, positive = self._diag_Response()
        return positive
    def check_Diag_Response(self):
        Res, _ = self._diag_Response()
        return Res

    def _diag_Response(self):
        """
        诊断响应
        :return:
        """
        global diag_request
        Res = ''
        positive = True
        while diag_request.Pending:
            time.sleep(1)
        if diag_request.Responses.Count == 0:
            Res = "NO RESPONSE"
        else:
            for k in range(1, diag_request.Responses.Count + 1):
                diag_resp = diag_request.Responses(k)
                stream = diag_resp.Stream
            if diag_resp.Positive:
                positive = True
            else:
                positive = False
            for i in stream:
                Res = Res + '{:02X} '.format(i)
        return Res, positive

    def init_logging_collection(self):
        """
        :return:
        """
        self.logging_collection = self.application.Configuration.OnlineSetup.LoggingCollection

    def select_logger(self, logger_number: int = None):
        """
        :param logger_number:
        :return:
        """
        self.logger = self.logging_collection.Item(logger_number)

    def set_log_target_dir(self, abs_path_to_dir=None):
        """
        :param abs_path_to_dir: log存放位置
        :return:
        """
        path = Path(abs_path_to_dir)
        if path.exists():
            self.log_target_dir = path
        else:
            raise Exception("CANoe Wrapper: Log target directory does not exist")

    def set_logfile_name(self, file_name: str = None):
        """
        设置日志名字
        :param file_name:
        :return:
        """
        file = Path(file_name)
        if file.suffix == '.blf':
            full_path = Path.joinpath(self.log_target_dir, file)
            self.logger.fullName = str(full_path)
        else:
            raise Exception("CANoe Wrapper: Log target file has incorrect extension")

    def start_logging(self):
        """
        开始记录日志
        :return:
        """
        if self.logger is not None:
            self.logger.Trigger.Start()
        else:
            raise Exception("CANoe Wrapper: No active logger was set")

    def stop_logging(self):
        """
        停止记录日志
        :return:
        """
        if self.logger is not None:
            self.logger.Trigger.Stop()
        else:
            raise Exception("CANoe Wrapper: No active logger was set")

    def get_logger_status(self):
        """
        获取日志状态
        :return: 返回TRUE 表示log状态为running，返回FALSE 表示log状态为stopped
        """
        if self.logger is not None:
            return str(self.logger.Trigger.Active)

    def sleep(self, ms: int):
        time.sleep(ms / 1000)

if __name__ == '__main__':
    canoe = CANoe()
    canoe.open_cfg("DiagCANoeProject/DiagCANoeProject.cfg")
    canoe.start_measurement()
    #开始记录日志
    
    canoe.init_service("CAN1", "DiagTest")
    canoe._diag_Request("10 01", stream_flag=True)
    canoe._diag_Response()
    canoe._diag_Request("10 03", stream_flag=True)
    canoe._diag_Response()
    canoe._diag_Request("22 F1 86", stream_flag=True)
    canoe._diag_Response()
