#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理重复代码的脚本
"""

def clean_file():
    """清理markdown_image_manager.py中的重复代码"""
    
    with open('markdown_image_manager.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"原始文件行数: {len(lines)}")
    
    # 找到第一个重复的开始位置
    # 查找第二个 "def calculate_similarity" 的位置
    first_calc_sim = -1
    second_calc_sim = -1
    
    for i, line in enumerate(lines):
        if "def calculate_similarity" in line:
            if first_calc_sim == -1:
                first_calc_sim = i
            else:
                second_calc_sim = i
                break
    
    print(f"第一个 calculate_similarity 在第 {first_calc_sim + 1} 行")
    print(f"第二个 calculate_similarity 在第 {second_calc_sim + 1} 行")
    
    if second_calc_sim > 0:
        # 删除从第二个开始的重复部分
        # 但保留最后的 if __name__ == "__main__": 部分
        
        # 找到最后的 if __name__ == "__main__": 位置
        last_main = -1
        for i in range(len(lines) - 1, -1, -1):
            if 'if __name__ == "__main__":' in lines[i] and 'app = MarkdownImageManager()' in lines[i + 1]:
                last_main = i
                break
        
        print(f"最后的 main 在第 {last_main + 1} 行")
        
        if last_main > 0:
            # 保留第一部分 + 最后的main部分
            cleaned_lines = lines[:second_calc_sim] + lines[last_main:]
            
            with open('markdown_image_manager.py', 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            
            print(f"清理后文件行数: {len(cleaned_lines)}")
            print("重复代码已清理完成!")
        else:
            print("未找到最后的main函数")
    else:
        print("未找到重复的代码")

if __name__ == "__main__":
    clean_file()