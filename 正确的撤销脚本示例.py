#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能修复撤销脚本
生成时间: 20250902_173929
修复文件数: 2
修复引用数: 3
"""

import os
import shutil
import json

def undo_fixes():
    backup_dir = r"D:/坚果云笔记/Typora云笔记/.backup/smart_fix_20250902_173929"
    
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
                workspace_path = r"D:/坚果云笔记/Typora云笔记"
                target_file = os.path.join(workspace_path, original_file)
                
                shutil.copy2(backup_file, target_file)
                restored_count += 1
                print(f"✅ 已恢复: {original_file}")
            else:
                print(f"❌ 备份文件不存在: {backup_file}")
        
        except Exception as e:
            print(f"❌ 恢复失败 {mod['file']}: {e}")
    
    print(f"\n撤销完成! 共恢复 {restored_count} 个文件")
    print("建议重新扫描以更新统计信息")

if __name__ == "__main__":
    undo_fixes()