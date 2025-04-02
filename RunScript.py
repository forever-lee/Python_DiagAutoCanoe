import ctypes
from CANoeCtrlIF import CANoe
from ctypes import *

class DiagnoseRun:
    def __init__(self):
        self.canoe = None

    def initialize(self, project_path, can_channel, diag_name):
        self.canoe = CANoe()
        self.canoe.open_cfg(project_path)
        self.canoe.start_measurement()
        self.canoe.init_service(can_channel, diag_name)

    def cleanup(self):
        self.canoe.stop_measurement()
        self.canoe.close_cfg()
        self.canoe = None

    def diag_test(self, session, req_data, exp, all_match=True):
        if len(session) == 0:
            # 不需要执行会话操作
            assert self.canoe.send_Diag_Request(req_data, stream_flag=True)
            if all_match:
                result = self.canoe.check_Diag_Response()
                # # 调试信息
                # print(f"期望值类型: {type(exp)}, 实际值类型: {type(result)}")
                # print(f"期望值长度: {len(exp)}, 实际值长度: {len(result)}")
                # print(f"期望值表示: {repr(exp)}")
                # print(f"实际值表示: {repr(result)}")
                # # 比较每个字符找出差异
                # for i, (c1, c2) in enumerate(zip(exp, result)):
                #     if c1 != c2:
                #         print(f"第{i}位不同: {repr(c1)} vs {repr(c2)}")
                # # 如果长度不同，检查哪部分多出
                # if len(exp) != len(result):
                #     print(f"长度不同，多余部分: {repr(exp[min(len(exp), len(result)):] if len(exp) > len(result) else result[min(len(exp), len(result)):])}")
                #忽略空白字符不区分大小写比较
                exp = exp.replace(" ", "").lower()
                result = result.replace(" ", "").lower()
                assert str(exp) == str(result)
            else:
                assert exp in result
        else:
            # 先执行会话操作
            assert self.canoe.send_Diag_Request("10 " + session, stream_flag=True)
            assert self.canoe.check_Diag_Positive()
            assert self.canoe.send_Diag_Request(req_data, stream_flag=True)
            if all_match:
                result = self.canoe.check_Diag_Response()
                exp = exp.replace(" ", "").lower()
                result = result.replace(" ", "").lower()
                assert str(exp) == str(result)
                # assert exp == self.canoe.check_Diag_Response()
            else:
                assert exp in self.canoe.check_Diag_Response()

    def security_access(self, gSecurityLevel):
        file_path = "./dataFile/EP37-E03_HZ_SeednKey_DDCU.dll"
        mylib = ctypes.WinDLL(file_path)
        # 发送27服务请求种子
        assert self.canoe.send_Diag_Request("27 " + gSecurityLevel, stream_flag=True)
        Seed = list(self.canoe.check_Diag_Response().split(" ")[2:6])
        # example Seed: ['5F', 'CC', '11', '79']，将seed转换为ctypes类型
        Seed = (ctypes.c_ubyte * len(Seed))(*[int(x, 16) for x in Seed])
        key =(ctypes.c_byte * 16)()
        keylength = ctypes.c_int(16)
        # 调用dll库，生成密钥
        mylib.GenerateKeyEx(
            ctypes.pointer(Seed),  # array for Sees [In]
            ctypes.c_short(len(Seed)),  #length of the array for the seed[In]
            ctypes.c_int(int(gSecurityLevel)), #security level[IN]
            POINTER(c_int)(), #Name of the active variant[In]
            ctypes.pointer(key), #array for the key[Out]
            ctypes.c_int(16), #Maximum length of the key[IN]
            ctypes.pointer(keylength) #length of the key[Out]
        )
        
        #遍历打印key，debug用
        # for i in range(keylength.value):
        #     print("key[%d]: %02X, 类型: %s" % (i, key[i]&0xFF, type(key[i])))
        
         # 将key转换为十六进制字符串格式
        key_hex_str = ' '.join(["%02X" % (key[i]&0xFF) for i in range(keylength.value)])
        # print(f"发送的key字符串: {key_hex_str}")
        
        assert self.canoe.send_Diag_Request("27 " + str(int(gSecurityLevel) + 1).zfill(2) + key_hex_str , stream_flag=True)
        assert self.canoe.check_Diag_Positive()
