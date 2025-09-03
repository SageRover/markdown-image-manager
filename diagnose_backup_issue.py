#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断备份目录问题
"""

import os
import tkinter as tk
from tkinter import filedialog

def diagnose_backup_issue():
    """诊断备份目录问题"""
    print("🔍 诊断备份目录问题")
    print("=" * 50)
    
    # 1. 让用户选择工作目录
    print("\n请选择你的工作目录（Markdown文件所在的目录）...")
    
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    workspace_path = filedialog.askdirectory(title="选择工作目录")
    root.destroy()
    
    if not workspace_path:
        print("❌ 未选择工作目录")
        return
    
    print(f"工作目录: {workspace_path}")
    
    # 2. 检查工作目录
    print(f"\n1. 工作目录检查:")
    if os.path.exists(workspace_path):
        print(f"   ✅ 工作目录存在: {workspace_path}")
    else:
        print(f"   ❌ 工作目录不存在: {workspace_path}")
        return
    
    # 3. 检查备份目录
    print(f"\n2. 备份目录检查:")
    backup_base = os.path.join(workspace_path, ".backup")
    print(f"   备份基础目录: {backup_base}")
    
    if os.path.exists(backup_base):
        print(f"   ✅ 备份基础目录存在")
        
        # 列出所有备份目录
        try:
            items = os.listdir(backup_base)
            backup_dirs = [item for item in items if os.path.isdir(os.path.join(backup_base, item)) and item.startswith("smart_fix_")]
            
            if backup_dirs:
                print(f"   ✅ 找到 {len(backup_dirs)} 个备份目录:")
                for backup_dir in sorted(backup_dirs):
                    backup_path = os.path.join(backup_base, backup_dir)
                    print(f"      - {backup_dir}")
                    
                    # 检查备份目录内容
                    try:
                        backup_items = os.listdir(backup_path)
                        print(f"        内容: {backup_items}")
                        
                        # 检查fix_log.json
                        fix_log_file = os.path.join(backup_path, "fix_log.json")
                        if os.path.exists(fix_log_file):
                            print(f"        ✅ 修复记录文件存在")
                            
                            # 读取记录内容
                            try:
                                import json
                                with open(fix_log_file, 'r', encoding='utf-8') as f:
                                    records = json.load(f)
                                print(f"        修复文件数: {records.get('total_files_processed', 0)}")
                                print(f"        修复引用数: {records.get('total_fixes', 0)}")
                                print(f"        修复时间: {records.get('timestamp', 'N/A')}")
                            except Exception as e:
                                print(f"        ❌ 读取修复记录失败: {e}")
                        else:
                            print(f"        ❌ 修复记录文件不存在")
                    except Exception as e:
                        print(f"        ❌ 读取备份目录失败: {e}")
            else:
                print(f"   ❌ 没有找到智能修复的备份目录")
                print(f"   提示: 备份目录应该以 'smart_fix_' 开头")
                
                # 列出所有目录
                try:
                    all_items = os.listdir(backup_base)
                    if all_items:
                        print(f"   备份目录中的所有内容: {all_items}")
                    else:
                        print(f"   备份目录为空")
                except Exception as e:
                    print(f"   ❌ 读取备份目录失败: {e}")
                    
        except Exception as e:
            print(f"   ❌ 访问备份目录失败: {e}")
    else:
        print(f"   ❌ 备份基础目录不存在")
        print(f"   这意味着还没有执行过智能修复操作")
    
    # 4. 检查权限
    print(f"\n3. 权限检查:")
    try:
        # 尝试创建测试目录
        test_dir = os.path.join(workspace_path, ".test_backup")
        os.makedirs(test_dir, exist_ok=True)
        
        # 尝试创建测试文件
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        # 清理测试文件
        os.remove(test_file)
        os.rmdir(test_dir)
        
        print(f"   ✅ 工作目录有读写权限")
    except Exception as e:
        print(f"   ❌ 工作目录权限问题: {e}")
    
    # 5. 检查Markdown文件
    print(f"\n4. Markdown文件检查:")
    try:
        md_files = []
        for root, dirs, files in os.walk(workspace_path):
            for file in files:
                if file.lower().endswith('.md'):
                    md_files.append(os.path.join(root, file))
        
        if md_files:
            print(f"   ✅ 找到 {len(md_files)} 个Markdown文件")
            for md_file in md_files[:5]:  # 只显示前5个
                rel_path = os.path.relpath(md_file, workspace_path)
                print(f"      - {rel_path}")
            if len(md_files) > 5:
                print(f"      ... 还有 {len(md_files) - 5} 个文件")
        else:
            print(f"   ❌ 没有找到Markdown文件")
            print(f"   请确保选择了正确的工作目录")
    except Exception as e:
        print(f"   ❌ 扫描Markdown文件失败: {e}")
    
    # 6. 解决方案建议
    print(f"\n" + "=" * 50)
    print(f"📋 诊断结果和建议:")
    
    if not os.path.exists(backup_base):
        print(f"❌ 问题: 没有备份目录")
        print(f"💡 解决方案:")
        print(f"   1. 确保已经执行过'智能修复路径'功能")
        print(f"   2. 检查工作目录是否正确")
        print(f"   3. 确保有足够的磁盘空间和权限")
    elif not backup_dirs:
        print(f"❌ 问题: 备份目录存在但没有智能修复记录")
        print(f"💡 解决方案:")
        print(f"   1. 重新执行'智能修复路径'功能")
        print(f"   2. 确保有无效的图片引用需要修复")
    else:
        print(f"✅ 备份目录正常，可能是程序读取问题")
        print(f"💡 建议:")
        print(f"   1. 重启程序再试")
        print(f"   2. 检查程序中的工作目录设置")

if __name__ == "__main__":
    diagnose_backup_issue()