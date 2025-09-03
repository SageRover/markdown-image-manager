#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试修复计数问题
"""

import re
import os

def debug_fix_count_issue():
    """调试修复计数问题"""
    print("🔍 调试修复计数问题")
    print("=" * 50)
    
    # 模拟问题场景
    test_content = '''# Matlab学习笔记

这是一个测试文档。

![图片](C:\\Users\\Sage\\AppData\\Roaming\\Typora\\typora-user-images\\image-20201207204857620.png)

其他内容...
'''
    
    print("原始文档内容:")
    print("-" * 30)
    print(test_content)
    print("-" * 30)
    
    # 模拟无效路径
    invalid_path = r"C:\Users\Sage\AppData\Roaming\Typora\typora-user-images\image-20201207204857620.png"
    print(f"\n无效路径: {invalid_path}")
    
    # 检查是否找到匹配
    print(f"是否找到同名文件: 否")
    print(f"URL解码结果: {invalid_path} (无变化)")
    print(f"智能匹配结果: 无匹配")
    
    # 模拟替换逻辑
    original_content = test_content
    content = test_content
    fixed_count = 0
    
    print(f"\n开始替换逻辑检查:")
    print(f"原始 fixed_count: {fixed_count}")
    
    # 检查替换模式
    old_patterns = [
        f'!\\[([^\\]]*)\\]\\({re.escape(invalid_path)}\\)',
        f'<img([^>]+)src=["\']{re.escape(invalid_path)}["\'](.*?)>',
    ]
    
    for i, pattern in enumerate(old_patterns):
        print(f"\n检查模式 {i+1}: {pattern}")
        
        # 检查是否匹配
        matches = re.findall(pattern, content)
        print(f"找到匹配: {len(matches)} 个")
        if matches:
            print(f"匹配内容: {matches}")
        
        # 模拟替换（但没有实际的替换目标）
        if '!\\[' in pattern:
            # 这里应该有一个有效的替换路径，但现在没有
            # new_content = re.sub(pattern, f'![\\1]({rel_correct_path})', content)
            print("  应该替换为: ![\\1]({rel_correct_path}) - 但没有有效的替换路径")
        else:
            # new_content = re.sub(pattern, f'<img\\1src="{rel_correct_path}"\\2>', content)
            print("  应该替换为: <img\\1src=\"{rel_correct_path}\"\\2> - 但没有有效的替换路径")
    
    print(f"\n最终 fixed_count: {fixed_count}")
    print(f"内容是否改变: {content != original_content}")
    
    # 检查可能的问题
    print(f"\n🔍 问题分析:")
    
    # 问题1: 是否有其他地方修改了content
    print("1. 检查是否有其他代码路径修改了content")
    
    # 问题2: 是否有错误的计数逻辑
    print("2. 检查是否有错误的fixed_count增加")
    
    # 问题3: 是否有正则表达式意外匹配
    print("3. 检查正则表达式是否意外匹配了其他内容")
    
    # 测试正则表达式
    test_patterns = [
        r'!\[([^\]]*)\]\(C:\\Users\\Sage\\AppData\\Roaming\\Typora\\typora-user-images\\image-20201207204857620\.png\)',
        r'<img([^>]+)src=["\']C:\\Users\\Sage\\AppData\\Roaming\\Typora\\typora-user-images\\image-20201207204857620\.png["\'](.*)>'
    ]
    
    print(f"\n测试转义后的正则表达式:")
    for i, pattern in enumerate(test_patterns):
        matches = re.findall(pattern, test_content)
        print(f"模式 {i+1}: {len(matches)} 个匹配")
        if matches:
            print(f"  匹配内容: {matches}")
    
    # 检查re.escape的结果
    escaped_path = re.escape(invalid_path)
    print(f"\nre.escape结果: {escaped_path}")
    
    # 构建实际使用的模式
    actual_pattern = f'!\\[([^\\]]*)\\]\\({escaped_path}\\)'
    print(f"实际模式: {actual_pattern}")
    
    matches = re.findall(actual_pattern, test_content)
    print(f"实际匹配: {len(matches)} 个")
    
    if matches:
        print(f"匹配详情: {matches}")
        
        # 如果有匹配，但没有有效的替换路径，会发生什么？
        print("\n⚠️ 发现问题!")
        print("正则表达式找到了匹配，但由于没有找到有效的图片文件，")
        print("不应该进行替换操作，fixed_count也不应该增加。")
        print("这说明代码中存在逻辑错误！")
    
    print(f"\n" + "=" * 50)
    print("📋 问题总结:")
    print("如果程序显示'❌ 未找到同名文件'但仍然报告'修复了1个引用'，")
    print("说明存在以下可能的问题:")
    print("1. 正则表达式匹配了内容，但替换逻辑有误")
    print("2. fixed_count的计数逻辑在错误的地方被触发")
    print("3. 文件内容被意外修改，即使没有找到有效的替换路径")

if __name__ == "__main__":
    debug_fix_count_issue()