from CANoeCtrlIF import CANoe


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
                assert exp == self.canoe.check_Diag_Response()
            else:
                assert exp in self.canoe.check_Diag_Response()
        else:
            # 先执行会话操作
            assert self.canoe.send_Diag_Request("10 " + session, stream_flag=True)
            assert self.canoe.check_Diag_Positive()
            assert self.canoe.send_Diag_Request(req_data, stream_flag=True)
            if all_match:
                assert exp == self.canoe.check_Diag_Response()
            else:
                assert exp in self.canoe.check_Diag_Response()
