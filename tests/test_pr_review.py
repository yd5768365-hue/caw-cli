#!/usr/bin/env python3
"""
测试PR审查功能的文件，包含故意的问题用于验证自动化审查工具。
此文件包含以下问题：
1. 硬编码API密钥（安全问题）
2. 嵌套循环（性能问题）
3. 超过50行的函数（可维护性问题）
4. TODO注释（技术债务）
5. 魔术数字（代码质量问题）
"""

# 硬编码的API密钥 - 安全审查应该捕获这个
API_KEY = "sk-live-1234567890abcdefghijklmnopqrstuvwxyz"
DATABASE_PASSWORD = "SuperSecret123!@#"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

# 魔术数字 - 应该定义为常量
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

def process_data_with_nested_loops(data):
    """包含深度嵌套循环的函数 - 性能问题"""
    results = []

    # 三层嵌套循环 - 性能问题
    for i in range(100):
        for j in range(100):
            for k in range(100):
                # 不必要的计算
                value = i * j * k
                if value > 5000:  # 魔术数字
                    results.append(value)

    # 更多嵌套循环
    for outer in data:
        if outer:
            for middle in outer:
                if middle:
                    for inner in middle:
                        if inner:
                            # 处理数据
                            pass

    return results


def very_long_function_with_many_lines(param1, param2, param3, param4, param5):
    """
    超过50行的函数 - 可维护性问题
    这个函数故意写得很长，以测试审查工具的函数长度检查
    """
    # 第1-10行：初始化
    result = []
    counter = 0
    total_sum = 0
    average_value = 0
    max_value = float('-inf')
    min_value = float('inf')

    # 第11-20行：处理参数1
    if param1:
        for item in param1:
            if item:
                value = int(item) * 2
                result.append(value)
                counter += 1
                total_sum += value

    # 第21-30行：处理参数2
    if param2:
        try:
            parsed = float(param2)
            result.append(parsed)
            total_sum += parsed
            counter += 1
        except ValueError:
            print("转换失败")

    # 第31-40行：处理参数3
    if param3:
        for i in range(len(param3)):
            for j in range(len(param3[i])):
                val = param3[i][j]
                if val > max_value:
                    max_value = val
                if val < min_value:
                    min_value = val
                result.append(val)

    # 第41-50行：处理参数4
    if param4:
        processed = []
        for elem in param4:
            if elem > 0:
                processed.append(elem * 2)
            elif elem < 0:
                processed.append(elem / 2)
            else:
                processed.append(0)
        result.extend(processed)

    # 第51-60行：处理参数5（超过50行限制）
    if param5:
        # TODO: 这里需要优化 - 技术债务标记
        temp = []
        for x in param5:
            for y in x:
                for z in y:
                    temp.append(z * 3)
        result.extend(temp)

    # 第61-70行：计算结果
    if counter > 0:
        average_value = total_sum / counter

    final_result = {
        'values': result,
        'count': counter,
        'sum': total_sum,
        'average': average_value,
        'max': max_value if max_value != float('-inf') else 0,
        'min': min_value if min_value != float('inf') else 0
    }

    # 第71-80行：额外处理
    if len(result) > 100:  # 魔术数字
        print("结果太多，进行采样")
        sampled = result[:100]
        final_result['sampled'] = sampled

    # 返回最终结果
    return final_result


def another_function_with_issues():
    """另一个有问题的函数"""
    # 使用eval - 安全风险
    user_input = "print('hello')"
    result = eval(user_input)  # 危险：使用eval

    # 硬编码URL
    api_url = "https://api.example.com/v1/secret-data?key=12345"

    # 不必要的复杂逻辑
    data = []
    for a in range(10):
        tmp = []
        for b in range(10):
            tmp2 = []
            for c in range(10):
                tmp2.append(a + b + c)
            tmp.append(tmp2)
        data.append(tmp)

    return data


class ProblematicClass:
    """包含多个问题的类"""

    def __init__(self):
        # 硬编码配置
        self.config = {
            "host": "localhost",
            "port": 5432,
            "username": "admin",
            "password": "AdminPass123!",  # 硬编码密码
            "database": "production_db"
        }

        # FIXME: 需要重构 - 技术债务
        self.cache = {}

    def inefficient_method(self, n):
        """低效的算法"""
        # 斐波那契数列的朴素递归实现 - 性能问题
        if n <= 1:
            return n
        return self.inefficient_method(n-1) + self.inefficient_method(n-2)

    def method_with_magic_numbers(self):
        """包含魔术数字的方法"""
        # 魔术数字
        timeout = 30  # 应该定义为常量
        max_items = 100  # 应该定义为常量
        retry_count = 3  # 应该定义为常量

        results = []
        for i in range(max_items):
            if i % 7 == 0:  # 魔术数字7
                results.append(i * timeout)

        return results


# 更多全局硬编码值
SECRET_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
DATABASE_URL = "postgresql://user:password@localhost:5432/production"

if __name__ == "__main__":
    # 测试代码
    print("运行PR审查测试...")

    # 创建问题实例
    pc = ProblematicClass()

    # 调用有问题的函数
    data = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
    result = very_long_function_with_many_lines([1, 2, 3], "4.5", data, [-1, 0, 1], data)
    print(f"结果: {result}")

    # 调用嵌套循环函数
    nested_result = process_data_with_nested_loops(data)
    print(f"嵌套循环结果长度: {len(nested_result)}")

    print("测试完成")