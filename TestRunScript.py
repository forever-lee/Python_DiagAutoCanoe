import os

import allure
import pytest

from RunScript import DiagnoseRun


@allure.feature("诊断测试类")
class TestDiagnose:

    @classmethod
    def setup_class(cls):
        cls.run_script = DiagnoseRun()
        cls.run_script.initialize("DiagCANoeProject/DiagCANoeProject.cfg", "CAN1", "DiagTest")
        print("初始化CANoe测试工程环境")

    @classmethod
    def teardown_class(cls):
        cls.run_script.cleanup()
        print("清理CANoe测试工程环境")

    @allure.title("诊断测试10服务")
    @allure.description("测试10 01服务")
    def test_diag_0x10_1(self):
        self.run_script.diag_test("", "10 01", "50 01 00")

    # @allure.title("诊断测试11服务")
    # @allure.description("测试11 01服务")
    # def test_diag_0x11_1(self):
    #     self.run_script.diag_test("", "11 01", "51 00 00")

    # @allure.title("诊断测试14服务")
    # @allure.description("测试14 01服务")
    # def test_diag_0x14_1(self):
    #     self.run_script.diag_test("", "14 01", "54", all_match=False)

    @allure.title("诊断测试10服务进入扩展会话")
    @allure.description("测试10 03服务进入扩展会话")
    def test_diag_0x10_3(self):
        self.run_script.diag_test("03", "10 03", "50 03 00")

    # @allure.title("诊断测试27服务")
    # @allure.description("测试27 03服务")
    # def test_diag_0x27_1(self):
    #     self.run_script.diag_test("", "27 00 01", "67 00 00")

    @allure.title("诊断测试22服务")
    @allure.description("测试22 F1 86服务")
    def test_diag_0x22_1(self):
        self.run_script.diag_test("", "22 F1 86", "62 F1 86 03")

    # @allure.title("诊断测试28服务")
    # @allure.description("测试28 01服务")
    # def test_diag_0x28_1(self):
    #     self.run_script.diag_test("", "28 00 01", "68 00")

    # @allure.title("诊断测试85服务")
    # @allure.description("测试85 01服务")
    # def test_diag_0x85_1(self):
    #     self.run_script.diag_test("", "85 00 00", "C5 00")



if __name__ == '__main__':
    pytest.main([__file__, '-sv', '--alluredir', './report/report', '--clean-alluredir'])   #
    os.system('allure serve ./report/report')
