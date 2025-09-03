#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能修复功能
"""

from urllib.parse import unquote
import os
import difflib

def test_path_matching():
    """测试路径匹配逻辑"""
    
    # 模拟的图片文件列表
    image_files = [
        "D:/坚果云笔记/Typora云笔记/Pic/image-20210308141502669.png",
        "D:/坚果云笔记/Typora云笔记/Pic/image-20210307205003625.png", 
        "D:/坚果云笔记/Typora云笔记/Pic/image-20210308135737402.png",
        "D:/坚果云笔记/Typora云笔记/Pic/image-20211206155034128.png",
        "D:/坚果云笔记/Typora云笔记/Pic/b219ebc4b74543a9ca86611616178a82b801144e.jpg"
    ]
    
    # 测试用例
    test_cases = [
        "C:\\Users\\Sage\\AppData\\Roaming\\Typora\\typora-user-images\\image-20210307114930669.png",
        "C:\\Users\\Sage\\AppData\\Roaming\\Typora\\typora-user-images\\image-20210307115005143.png",
        "./Pic/b219ebc4b74543a9ca86611616178a82b801144e-166256434505243.jpg"
    ]
    
    print("智能修复测试:")
    print("=" * 60)
    
    for i, invalid_path in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {invalid_path}")
        
        # 提取文件名
        filename = os.path.basename(invalid_path).lower()
        print(f"  文件名: {filename}")
        
        # 查找匹配的文件
        matches = []
        for img_file in image_files:
            img_filename = os.path.basename(img_file).lower()
            if filename == img_filename:
                matches.append(img_file)
                print(f"  ✅ 精确匹配: {img_file}")
        
        if not matches:
            # 尝试相似度匹配
            best_score = 0
            best_match = None
            
            for img_file in image_files:
                img_filename = os.path.basename(img_file).lower()
                similarity = difflib.SequenceMatcher(None, filename, img_filename).ratio()
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = img_file
            
            if best_score > 0.6:
                print(f"  🔍 相似匹配: {best_match} (相似度: {best_score:.2f})")
                if best_score < 0.9:
                    print(f"  ⚠️  警告: 相似度较低，可能不是正确的匹配")
            else:
                print(f"  ❌ 未找到匹配文件")

if __name__ == "__main__":
    test_path_matching()