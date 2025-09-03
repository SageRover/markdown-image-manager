#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复路径分隔符混用的具体bug
"""

import os
import re

def identify_root_cause():
    """识别根本原因"""
    
    print("🔍 路径分隔符混用问题的根本原因")
    print("=" * 60)
    
    print("📍 问题路径示例:")
    problem_path = "D:/坚果云笔记/Typora云笔记\\images\\20250828092612341.png"
    print(f"  {problem_path}")
    
    print(f"\n🔧 分析过程:")
    
    # 模拟可能的代码执行路径
    print(f"1. 初始路径可能来源:")
    print(f"   - 用户输入的workspace_path: D:/坚果云笔记/Typora云笔记")
    print(f"   - 系统扫描到的文件路径: images\\20250828092612341.png")
    
    print(f"\n2. 路径拼接过程:")
    workspace = "D:/坚果云笔记/Typora云笔记"
    relative_part = "images\\20250828092612341.png"  # 来自Windows文件系统
    
    # 错误的拼接方式
    wrong_join = workspace + "/" + relative_part
    print(f"   错误拼接: {workspace} + '/' + {relative_part}")
    print(f"   结果: {wrong_join}")
    
    # 正确的拼接方式
    correct_join = os.path.join(workspace, relative_part).replace('\\', '/')
    print(f"   正确拼接: os.path.join() + normalize")
    print(f"   结果: {correct_join}")
    
    print(f"\n3. 问题出现的具体位置:")
    print(f"   可能在以下代码中:")
    print(f"   - 文件扫描时获取相对路径")
    print(f"   - 路径拼接时未统一分隔符")
    print(f"   - safe_relpath方法的处理逻辑")

def create_comprehensive_fix():
    """创建全面的修复方案"""
    
    print(f"\n" + "=" * 60)
    print(f"🔧 全面修复方案")
    print(f"=" * 60)
    
    fix_code = '''
# 在 MarkdownImageManager 类中添加路径规范化方法

def normalize_path(self, path):
    """
    统一路径分隔符，确保跨平台兼容性
    
    Args:
        path (str): 原始路径
        
    Returns:
        str: 规范化后的路径（统一使用正斜杠）
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

def safe_relpath(self, path, start):
    """安全的相对路径计算，修复版本"""
    try:
        # 先规范化两个路径
        path = self.normalize_path(path)
        start = self.normalize_path(start)
        
        # 计算相对路径
        rel_path = os.path.relpath(path, start)
        
        # 规范化结果
        return self.normalize_path(rel_path)
    except ValueError:
        # 跨驱动器情况，返回规范化的绝对路径
        return self.normalize_path(path)

def safe_path_join(self, *parts):
    """安全的路径拼接"""
    # 使用os.path.join然后规范化
    joined = os.path.join(*parts)
    return self.normalize_path(joined)

# 修复所有使用路径的地方
def scan_images(self):
    """扫描图片时规范化路径"""
    # ... 原有代码 ...
    
    for root, dirs, files in os.walk(self.workspace_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg')):
                full_path = os.path.join(root, file)
                # 规范化路径
                full_path = self.normalize_path(full_path)
                self.image_files.append(full_path)

def extract_image_references(self, md_file):
    """提取图片引用时规范化路径"""
    # ... 原有代码 ...
    
    # 处理找到的图片路径
    for match in matches:
        img_path = match[1]  # 获取路径部分
        # 规范化路径
        img_path = self.normalize_path(img_path)
        # ... 继续处理 ...
'''
    
    print("📝 修复代码:")
    print(fix_code)

def create_specific_fixes():
    """创建具体的修复补丁"""
    
    print(f"\n" + "=" * 60)
    print(f"🎯 具体修复补丁")
    print(f"=" * 60)
    
    patches = [
        {
            "file": "markdown_image_manager.py",
            "location": "safe_relpath方法",
            "old_code": '''def safe_relpath(self, path, start):
        """安全的相对路径计算，处理跨驱动器情况"""
        try:
            rel_path = os.path.relpath(path, start)
            return rel_path.replace('\\\\', '/')
        except ValueError:
            # 跨驱动器情况，返回绝对路径
            return path.replace('\\\\', '/')''',
            "new_code": '''def safe_relpath(self, path, start):
        """安全的相对路径计算，处理跨驱动器情况"""
        try:
            # 先规范化输入路径
            path = self.normalize_path(path)
            start = self.normalize_path(start)
            
            rel_path = os.path.relpath(path, start)
            return self.normalize_path(rel_path)
        except ValueError:
            # 跨驱动器情况，返回规范化的绝对路径
            return self.normalize_path(path)'''
        },
        {
            "file": "markdown_image_manager.py", 
            "location": "类的开头",
            "old_code": "# 在类的开头添加",
            "new_code": '''def normalize_path(self, path):
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
        
        return normalized'''
        }
    ]
    
    for i, patch in enumerate(patches, 1):
        print(f"{i}. 修复 {patch['file']} - {patch['location']}")
        print(f"   替换:")
        print(f"   {patch['old_code']}")
        print(f"   为:")
        print(f"   {patch['new_code']}")
        print()

def test_fix():
    """测试修复效果"""
    
    print(f"🧪 测试修复效果")
    print(f"=" * 60)
    
    def normalize_path(path):
        """测试用的规范化函数"""
        if not path:
            return path
        
        normalized = path.replace('\\\\', '/').replace('\\', '/')
        normalized = re.sub(r'/+', '/', normalized)
        
        if len(normalized) > 1 and normalized.endswith('/'):
            normalized = normalized.rstrip('/')
        
        return normalized
    
    test_cases = [
        "D:/坚果云笔记/Typora云笔记\\images\\20250828092612341.png",
        "D:\\坚果云笔记\\Typora云笔记/images/test.jpg",
        "C:\\Users\\test//folder\\file.png",
        "../relative/path\\to\\file.jpg",
        "//network/path\\file.png"
    ]
    
    print("测试用例:")
    for i, test_path in enumerate(test_cases, 1):
        normalized = normalize_path(test_path)
        print(f"{i}. 原始: {test_path}")
        print(f"   修复: {normalized}")
        print()

if __name__ == "__main__":
    identify_root_cause()
    create_comprehensive_fix()
    create_specific_fixes()
    test_fix()