#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试路径分隔符修复效果
"""

import re

def test_normalize_path():
    """测试路径规范化函数"""
    
    def normalize_path(path):
        """统一路径分隔符，确保跨平台兼容性"""
        if not path:
            return path
        
        # 统一使用正斜杠
        normalized = path.replace('\\\\', '/').replace('\\', '/')
        
        # 去除重复的分隔符
        normalized = re.sub(r'/+', '/', normalized)
        
        # 去除末尾的分隔符（除非是根目录）
        if len(normalized) > 1 and normalized.endswith('/'):
            normalized = normalized.rstrip('/')
        
        return normalized
    
    print("🧪 测试路径规范化修复")
    print("=" * 50)
    
    # 测试用例：包括你遇到的实际问题
    test_cases = [
        {
            "name": "实际问题路径",
            "input": "D:/坚果云笔记/Typora云笔记\\images\\20250828092612341.png",
            "expected": "D:/坚果云笔记/Typora云笔记/images/20250828092612341.png"
        },
        {
            "name": "全反斜杠",
            "input": "D:\\坚果云笔记\\Typora云笔记\\images\\test.jpg",
            "expected": "D:/坚果云笔记/Typora云笔记/images/test.jpg"
        },
        {
            "name": "混合重复分隔符",
            "input": "C:\\Users\\test//folder\\\\file.png",
            "expected": "C:/Users/test/folder/file.png"
        },
        {
            "name": "相对路径",
            "input": "../relative/path\\to\\file.jpg",
            "expected": "../relative/path/to/file.jpg"
        },
        {
            "name": "网络路径",
            "input": "//network\\path\\file.png",
            "expected": "/network/path/file.png"
        },
        {
            "name": "末尾分隔符",
            "input": "D:/folder/subfolder/",
            "expected": "D:/folder/subfolder"
        },
        {
            "name": "根目录",
            "input": "D:/",
            "expected": "D:/"
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        result = normalize_path(case["input"])
        passed = result == case["expected"]
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{i}. {case['name']}: {status}")
        print(f"   输入: {case['input']}")
        print(f"   输出: {result}")
        print(f"   期望: {case['expected']}")
        if not passed:
            print(f"   ❌ 不匹配!")
        print()
    
    print("=" * 50)
    if all_passed:
        print("🎉 所有测试通过！路径规范化修复成功！")
    else:
        print("❌ 部分测试失败，需要进一步调试")
    
    return all_passed

def simulate_path_join_scenarios():
    """模拟路径拼接场景"""
    
    def normalize_path(path):
        if not path:
            return path
        normalized = path.replace('\\\\', '/').replace('\\', '/')
        normalized = re.sub(r'/+', '/', normalized)
        if len(normalized) > 1 and normalized.endswith('/'):
            normalized = normalized.rstrip('/')
        return normalized
    
    print("\n🔧 模拟路径拼接场景")
    print("=" * 50)
    
    # 模拟你的实际使用场景
    workspace = "D:/坚果云笔记/Typora云笔记"
    
    scenarios = [
        {
            "name": "Windows文件扫描结果",
            "relative": "images\\20250828092612341.png",
            "description": "os.walk在Windows下返回的路径"
        },
        {
            "name": "混合路径",
            "relative": "Pic/subfolder\\image.jpg",
            "description": "部分正斜杠，部分反斜杠"
        },
        {
            "name": "深层嵌套",
            "relative": "folder1\\folder2/folder3\\image.png",
            "description": "多层目录的混合分隔符"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   描述: {scenario['description']}")
        
        # 错误的拼接方式（可能导致问题）
        wrong_join = workspace + "/" + scenario['relative']
        print(f"   错误拼接: {wrong_join}")
        
        # 正确的拼接方式
        import os
        correct_join = normalize_path(os.path.join(workspace, scenario['relative']))
        print(f"   正确拼接: {correct_join}")
        
        # 检查是否修复了问题
        has_mixed_separators = ('\\' in correct_join and '/' in correct_join)
        if has_mixed_separators:
            print(f"   ❌ 仍有混合分隔符!")
        else:
            print(f"   ✅ 分隔符统一")
        print()

def test_real_world_example():
    """测试真实世界的例子"""
    
    def normalize_path(path):
        if not path:
            return path
        normalized = path.replace('\\\\', '/').replace('\\', '/')
        normalized = re.sub(r'/+', '/', normalized)
        if len(normalized) > 1 and normalized.endswith('/'):
            normalized = normalized.rstrip('/')
        return normalized
    
    print("\n🌍 真实世界测试")
    print("=" * 50)
    
    # 你实际遇到的问题路径
    problem_paths = [
        "D:/坚果云笔记/Typora云笔记\\images\\20250828092612341.png",
        "D:/坚果云笔记/Typora云笔记\\images\\20250828092546564.png",
        "D:/坚果云笔记/Typora云笔记\\images\\20250828092816267.png",
        "D:/坚果云笔记/Typora云笔记\\images\\20250828093642530.png",
        "D:/坚果云笔记/Typora云笔记\\images\\20250828092906914.png"
    ]
    
    print("修复前后对比:")
    for i, path in enumerate(problem_paths, 1):
        fixed = normalize_path(path)
        print(f"{i}. 原始: {path}")
        print(f"   修复: {fixed}")
        
        # 检查是否还有混合分隔符
        has_mixed = ('\\' in fixed and '/' in fixed)
        if has_mixed:
            print(f"   ❌ 仍有问题")
        else:
            print(f"   ✅ 已修复")
        print()

if __name__ == "__main__":
    test_normalize_path()
    simulate_path_join_scenarios()
    test_real_world_example()