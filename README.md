# 工程架构
```commandline
DiagAutoCANoe
├── DiagCANoeProject  # CANoe工程文件
├── pic               # 图片文件
├── dataFile          # 数据文件（dll)
├── venv              # python虚拟环境
└── CANoeCtrlIF.py    # CANoe软件工程控制层
├── RunScript.py      # 接口层
├── TestRunScript.py  # 测试脚本
└── 使用说明文档.md
```
# 工程使用说明
`注意1：` 框架中的DiagCANoeProject工程中配置的物理寻址为0x741，功能寻址为0x7df，响应为0x749，由于不同车厂定义不同，请自行适配地址，否则无法正常进行测试。  
`注意2：` 框架中的DiagCANoeProject工程是基于Basic类型进行诊断服务的配置，若本身具备相应的CDD文件，请重新创建对应的诊断工程；  
`注意3：` 框架中测试脚本TestRunScript.py中，需要根据实际使用的CANoe工程信息，对`setup_class`的`run_script.initialize([path], [can], [ECU qualifier])`三个参数进行修改。  
`注意4：` 请根据实际测试场景，对TestRunScript.py的测试脚本Demo进行修改适配。其中`self.run_script.diag_test()`的参数定义如下：
 - 必填参数session： 诊断会话类型，可填空字符串，表示不进入某个会话；
 - 必填参数req_data：诊断请求数据，格式为已空格分割的16进制字符串；
 - 必填参数exp： 期望的诊断响应数据，格式为已空格分割的16进制字符串；
 - 可选参数all_match： 是否要求响应数据全部匹配，默认为True，表示响应数据全部匹配；
```commandline
    @allure.title("诊断测试14服务")
    @allure.description("测试14 01服务")
    def test_diag_0x14_1(self):
        self.run_script.diag_test("", "14 01", "54", all_match=False)
```
在排查并修改完以上注意点后，直接运行测试脚本TestRunScript.py即可。
