import pluggy
import inspect

NAMESPACE = 'cnipa-jszx-peizhi'
# test_spec = pluggy.HookspecMarker(NAMESPACE)
# test_impl = pluggy.HookimplMarker(NAMESPACE)

# class TestSpec:
#     """
#     这是插件的测试类接口实现
#     """
#     @test_spec
#     def test_hook(self):
#         """
#         第一个可实现的方法
#         """
#         pass

#     @test_spec
#     def peizhi(self):
#         """
#         第二个可实现的方法
#         """
#         pass


# 非正常校验核心插件类接口实现
verify_spec = pluggy.HookspecMarker(NAMESPACE)
verify_impl = pluggy.HookimplMarker(NAMESPACE)


class VerifySpec:
    """
     非正常案件校验插件接口实现
     
     pre_verify： 校验前的数据处理工作，选择实现
        input：
            row： Ddf的每一行
            **args： 可以自定义其他输入信息
            
    run_verify： 实际校验逻辑，必须实现
        input：
            row： df的每一行
            **args： 可以自定义其他输入信息
    
    after_verify： 校验完成后的数据处理工作，选择实现
        input：
            row： df的每一行
            **args： 可以自定义其他输入信息
    """

    @verify_spec
    def pre_verify(self, index, row):
        """
        如需要返回值，返回值必须为{self.__class__.__name__:ret_date}
        其中 ret_date 是实际返回的内容，self.__class__.__name__用于区分哪个插件返回
        """
        pass

    @verify_spec
    def run_verify(self, index, row):
        """
        如需要返回值，返回值必须为{self.__class__.__name__:ret_dict}
        简单的做法就是加上装饰器@plugin_return
        """
        pass

    @verify_spec
    def after_verify(self, df, tags):
        """
        无返回值
        """
        pass


def plugin_return(func):
    def wrapper(index, row):
        ret = func(index, row)
        module_name = inspect.getmodule(func).__name__
        return {module_name: ret}

    return wrapper
