#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本生成问题
"""

import os
import tempfile

def debug_script_generation():
    """调试脚本生成问题"""
    print("🔍 调试脚本生成问题")
    print("=" * 50)
    
    # 模拟实际的路径
    workspace_path = r"D:\坚果云笔记\Typora云笔记"
    backup_dir = r"D:\坚果云笔记\Typora云笔记\.backup\smart_fix_20250902_165834"
    
    fix_records = {
        "timestamp": "2025-09-02 16:58:34",
        "total_files_processed": 2,
        "total_fixes": 3
    }
    
    print(f"工作目录: {workspace_path}")
    print(f"备份目录: {backup_dir}")
    
    # 模拟修复后的generate_undo_script逻辑
    backup_dir_path = backup_dir
    workspace_path_var = workspace_path
    
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能修复撤销脚本
生成时间: {fix_records["timestamp"]}
修复文件数: {fix_records["total_files_processed"]}
修复引用数: {fix_records["total_fixes"]}
"""

import os
import shutil
import json

def undo_fixes():
    backup_dir = r"{backup_dir_path}"
    
    print("开始撤销智能修复操作...")
    
    # 读取修复记录
    with open(os.path.join(backup_dir, "fix_log.json"), 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    restored_count = 0
    
    for mod in records["modifications"]:
        try:
            backup_file = mod["backup_file"]
            original_file = mod["file"]
            
            if os.path.exists(backup_file):
                # 恢复原始文件
                workspace_path = r"{workspace_path_var}"
                target_file = os.path.join(workspace_path, original_file)
                
                shutil.copy2(backup_file, target_file)
                restored_count += 1
                print(f"✅ 已恢复: {{original_file}}")
            else:
                print(f"❌ 备份文件不存在: {{backup_file}}")
        
        except Exception as e:
            print(f"❌ 恢复失败 {{mod['file']}}: {{e}}")
    
    print(f"\\n撤销完成! 共恢复 {{restored_count}} 个文件")
    print("建议重新扫描以更新统计信息")

if __name__ == "__main__":
    undo_fixes()
'''
    
    print("\n生成的脚本内容:")
    print("-" * 30)
    print(script_content)
    print("-" * 30)
    
    print("\n关键行检查:")
    lines = script_content.split('\n')
    for i, line in enumerate(lines):
        if 'backup_dir = r"' in line:
            print(f"第{i+1}行: {line}")
        if 'workspace_path = r"' in line:
            print(f"第{i+1}行: {line}")
    
    print("\n对比原问题:")
    problem_line = r'backup_dir = r"D:/坚果云笔记/Typora云笔记\.backup_smart_fix_20250902_165834"'
    correct_line = f'backup_dir = r"{backup_dir_path}"'
    
    print(f"原问题行: {problem_line}")
    print(f"修复后行: {correct_line}")
    
    if r'\.backup_smart_fix_' in problem_line:
        print("✅ 确认原问题: 路径中使用了 \.backup_smart_fix_")
    
    if r'\.backup\smart_fix_' in correct_line:
        print("✅ 修复正确: 路径中使用了 \.backup\smart_fix_")
    
    print("\n语法检查:")
    try:
        compile(script_content, '<string>', 'exec')
        print("✅ 语法正确")
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")

if __name__ == "__main__":
    debug_script_generation()