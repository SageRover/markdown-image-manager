#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复路径分隔符混用问题
"""

import os
import re

def analyze_path_separator_issue():
    """分析路径分隔符混用问题"""
    
    print("🔍 路径分隔符混用问题分析")
    print("=" * 50)
    
    # 问题路径示例
    problematic_path = "D:/坚果云笔记/Typora云笔记\\images\\20250828092612341.png"
    
    print(f"问题路径: {problematic_path}")
    print(f"问题分析:")
    print(f"  前半部分: D:/坚果云笔记/Typora云笔记 (使用 /)")
    print(f"  后半部分: \\images\\20250828092612341.png (使用 \\)")
    
    print(f"\n🔧 可能的原因:")
    print(f"1. 字符串拼接时使用了不同的分隔符")
    print(f"2. 不同的代码路径使用了不同的路径处理方式")
    print(f"3. 从不同来源获取的路径片段未统一处理")
    
    print(f"\n💡 修复方案:")
    
    # 方案1: 使用os.path.normpath
    normalized_1 = os.path.normpath(problematic_path)
    print(f"方案1 - os.path.normpath:")
    print(f"  结果: {normalized_1}")
    
    # 方案2: 替换所有分隔符
    normalized_2 = problematic_path.replace('\\', '/').replace('//', '/')
    print(f"方案2 - 统一为正斜杠:")
    print(f"  结果: {normalized_2}")
    
    # 方案3: 使用pathlib
    from pathlib import Path
    normalized_3 = str(Path(problematic_path))
    print(f"方案3 - pathlib.Path:")
    print(f"  结果: {normalized_3}")
    
    # 方案4: 自定义规范化函数
    def normalize_path_custom(path):
        """自定义路径规范化"""
        # 统一分隔符
        normalized = path.replace('\\', '/')
        # 去除重复分隔符
        normalized = re.sub(r'/+', '/', normalized)
        # Windows绝对路径处理
        if len(normalized) > 1 and normalized[1] == ':':
            # 保持Windows驱动器格式
            return normalized
        return normalized
    
    normalized_4 = normalize_path_custom(problematic_path)
    print(f"方案4 - 自定义规范化:")
    print(f"  结果: {normalized_4}")
    
    print(f"\n🎯 推荐方案: 方案4 (自定义规范化)")
    print(f"  优点: 跨平台兼容，保持一致的正斜杠风格")

def find_path_separator_issues():
    """查找代码中可能导致路径分隔符混用的地方"""
    
    print(f"\n" + "=" * 50)
    print(f"🔍 查找可能的问题代码")
    print(f"=" * 50)
    
    potential_issues = [
        {
            "location": "路径拼接",
            "problem": "使用字符串拼接而不是os.path.join",
            "example": 'path = base_path + "\\" + filename',
            "solution": 'path = os.path.join(base_path, filename)'
        },
        {
            "location": "硬编码路径分隔符",
            "problem": "直接使用\\或/",
            "example": 'if "\\" in path or "/" in path:',
            "solution": 'if os.sep in path:'
        },
        {
            "location": "正则表达式",
            "problem": "正则中硬编码分隔符",
            "example": r're.split(r"[/\\]", path)',
            "solution": 'path.split(os.sep)'
        },
        {
            "location": "文件路径处理",
            "problem": "未统一处理不同来源的路径",
            "example": "直接使用从不同API获取的路径",
            "solution": "所有路径都通过normalize_path处理"
        }
    ]
    
    for i, issue in enumerate(potential_issues, 1):
        print(f"{i}. {issue['location']}")
        print(f"   问题: {issue['problem']}")
        print(f"   示例: {issue['example']}")
        print(f"   解决: {issue['solution']}")
        print()

def create_path_normalization_utility():
    """创建路径规范化工具函数"""
    
    print(f"📝 路径规范化工具函数:")
    print(f"=" * 50)
    
    utility_code = '''
import os
import re
from pathlib import Path

def normalize_path(path):
    """
    统一路径分隔符，确保跨平台兼容性
    
    Args:
        path (str): 原始路径
        
    Returns:
        str: 规范化后的路径
    """
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

def safe_path_join(*parts):
    """
    安全的路径拼接，自动处理分隔符
    
    Args:
        *parts: 路径组件
        
    Returns:
        str: 拼接后的规范化路径
    """
    # 使用os.path.join然后规范化
    joined = os.path.join(*parts)
    return normalize_path(joined)

def is_absolute_path(path):
    """
    检查是否为绝对路径（跨平台）
    
    Args:
        path (str): 路径
        
    Returns:
        bool: 是否为绝对路径
    """
    normalized = normalize_path(path)
    
    # Windows绝对路径: C:/ 或 D:/ 等
    if len(normalized) >= 3 and normalized[1:3] == ':/':
        return True
    
    # Unix绝对路径: /
    if normalized.startswith('/'):
        return True
    
    return False

# 使用示例
if __name__ == "__main__":
    test_paths = [
        "D:/坚果云笔记/Typora云笔记\\\\images\\\\test.png",
        "C:\\\\Users\\\\test//folder/file.txt",
        "../relative/path\\\\to\\\\file.jpg",
        "/unix/style/path/file.png"
    ]
    
    print("路径规范化测试:")
    for path in test_paths:
        normalized = normalize_path(path)
        print(f"原始: {path}")
        print(f"规范: {normalized}")
        print(f"绝对: {is_absolute_path(normalized)}")
        print("-" * 40)
'''
    
    print(utility_code)

def suggest_code_fixes():
    """建议代码修复方案"""
    
    print(f"\n🔧 建议的代码修复:")
    print(f"=" * 50)
    
    print(f"1. 在markdown_image_manager.py中添加路径规范化:")
    print(f"""
# 在类的开头添加工具方法
def normalize_path(self, path):
    \"\"\"统一路径分隔符\"\"\"
    if not path:
        return path
    normalized = path.replace('\\\\', '/').replace('\\', '/')
    return re.sub(r'/+', '/', normalized)

# 在所有路径处理的地方使用
def process_image_path(self, img_path):
    # 规范化路径
    img_path = self.normalize_path(img_path)
    # 其他处理...
""")
    
    print(f"\n2. 修复路径拼接:")
    print(f"""
# 错误的方式
image_path = base_path + "\\\\" + filename

# 正确的方式
image_path = self.normalize_path(os.path.join(base_path, filename))
""")
    
    print(f"\n3. 统一处理所有输入路径:")
    print(f"""
# 在扫描图片引用时
for img_path in image_references:
    img_path = self.normalize_path(img_path)
    # 继续处理...
""")

if __name__ == "__main__":
    analyze_path_separator_issue()
    find_path_separator_issues()
    create_path_normalization_utility()
    suggest_code_fixes()