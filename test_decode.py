#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试URL解码功能
"""

from urllib.parse import unquote
import os

def test_url_decode():
    """测试URL解码功能"""
    
    # 测试用例
    test_cases = [
        "Pic/%E8%80%83%E4%BD%93%E5%88%B6/%E8%B5%84%E6%96%99%E5%88%86%E6%9E%90%E5%85%AC%E5%BC%8F.png",
        "images/%E6%B5%8B%E8%AF%95%E5%9B%BE%E7%89%87.png",
        "normal/path/image.png",  # 正常路径
        "%E4%B8%AD%E6%96%87%E6%96%87%E4%BB%B6%E5%A4%B9/test.jpg"  # 中文文件夹
    ]
    
    print("URL解码测试:")
    print("=" * 50)
    
    for i, encoded_path in enumerate(test_cases, 1):
        decoded_path = unquote(encoded_path)
        print(f"测试 {i}:")
        print(f"  原始: {encoded_path}")
        print(f"  解码: {decoded_path}")
        print(f"  是否相同: {encoded_path == decoded_path}")
        print()
    
    # 检查实际文件是否存在
    print("文件存在性检查:")
    print("=" * 50)
    
    actual_files = [
        "Pic/考体制/资料分析公式.png",
        "images/测试图片.png"
    ]
    
    for file_path in actual_files:
        exists = os.path.exists(file_path)
        print(f"  {file_path}: {'✅ 存在' if exists else '❌ 不存在'}")

if __name__ == "__main__":
    test_url_decode()