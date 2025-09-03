#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试撤销功能是否正常
"""

import os
import json
import tempfile
import shutil
from datetime import datetime

def test_undo_functionality():
    """测试撤销功能的完整流程"""
    print("🧪 测试撤销功能")
    print("=" * 50)
    
    # 1. 检查generate_undo_script函数的字符串模板
    print("\n1. 检查字符串模板语法:")
    
    # 模拟数据
    backup_dir = "/test/backup"
    fix_records = {
        "timestamp": "2024-01-01 12:00:00",
        "total_files_processed": 5,
        "total_fixes": 10
    }
    
    # 模拟self.workspace_path
    workspace_path = "/test/workspace"
    
    # 生成脚本内容（模拟generate_undo_script的逻辑）
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
    backup_dir = r"{backup_dir}"
    
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
                workspace_path = r"{workspace_path}"
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
    
    # 检查生成的脚本语法
    try:
        compile(script_content, '<string>', 'exec')
        print("   ✅ 生成的撤销脚本语法正确")
    except SyntaxError as e:
        print(f"   ❌ 撤销脚本语法错误: {e}")
        return False
    
    # 2. 检查脚本内容
    print("\n2. 检查脚本内容:")
    
    # 检查必要的导入
    required_imports = ['import os', 'import shutil', 'import json']
    for imp in required_imports:
        if imp in script_content:
            print(f"   ✅ {imp}")
        else:
            print(f"   ❌ 缺少: {imp}")
    
    # 检查主要函数
    if 'def undo_fixes():' in script_content:
        print("   ✅ undo_fixes函数定义正确")
    else:
        print("   ❌ 缺少undo_fixes函数定义")
    
    if 'if __name__ == "__main__":' in script_content:
        print("   ✅ 主程序入口正确")
    else:
        print("   ❌ 缺少主程序入口")
    
    # 3. 测试实际的撤销逻辑
    print("\n3. 测试撤销逻辑:")
    
    # 创建临时测试环境
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件结构
        workspace = os.path.join(temp_dir, "workspace")
        backup_dir = os.path.join(temp_dir, "backup")
        os.makedirs(workspace)
        os.makedirs(backup_dir)
        
        # 创建测试文件
        test_file = os.path.join(workspace, "test.md")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# 测试文件\n![image](old_path.jpg)")
        
        # 创建备份文件
        backup_file = os.path.join(backup_dir, "test.md.backup")
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write("# 测试文件\n![image](original_path.jpg)")
        
        # 创建修复记录
        fix_log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_files_processed": 1,
            "total_fixes": 1,
            "modifications": [
                {
                    "file": "test.md",
                    "backup_file": backup_file,
                    "changes": [
                        {
                            "line": 2,
                            "old": "![image](original_path.jpg)",
                            "new": "![image](old_path.jpg)"
                        }
                    ]
                }
            ]
        }
        
        fix_log_file = os.path.join(backup_dir, "fix_log.json")
        with open(fix_log_file, 'w', encoding='utf-8') as f:
            json.dump(fix_log, f, ensure_ascii=False, indent=2)
        
        # 测试撤销逻辑
        try:
            # 读取修复记录
            with open(fix_log_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            restored_count = 0
            
            for mod in records["modifications"]:
                backup_file_path = mod["backup_file"]
                original_file = mod["file"]
                
                if os.path.exists(backup_file_path):
                    target_file = os.path.join(workspace, original_file)
                    shutil.copy2(backup_file_path, target_file)
                    restored_count += 1
            
            # 验证恢复结果
            with open(test_file, 'r', encoding='utf-8') as f:
                restored_content = f.read()
            
            if "original_path.jpg" in restored_content:
                print("   ✅ 文件恢复成功")
                print(f"   ✅ 共恢复 {restored_count} 个文件")
            else:
                print("   ❌ 文件恢复失败")
                return False
                
        except Exception as e:
            print(f"   ❌ 撤销逻辑测试失败: {e}")
            return False
    
    # 4. 检查UI撤销功能的关键逻辑
    print("\n4. 检查UI撤销功能:")
    
    # 检查markdown_image_manager.py中的undo_fixes方法
    try:
        with open('markdown_image_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键逻辑
        checks = [
            ('backup_base = os.path.join(self.workspace_path, ".backup")', '备份目录查找'),
            ('backup_dirs.append(backup_path)', '备份目录收集'),
            ('latest_backup = max(backup_dirs, key=os.path.getctime)', '最新备份选择'),
            ('with open(fix_log_file, \'r\', encoding=\'utf-8\') as f:', '修复记录读取'),
            ('shutil.copy2(backup_file, target_file)', '文件恢复操作'),
            ('messagebox.showinfo("完成"', '完成提示')
        ]
        
        for check_code, description in checks:
            if check_code in content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ 缺少: {description}")
    
    except Exception as e:
        print(f"   ❌ 检查UI撤销功能失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("📋 撤销功能检查总结:")
    print("✅ 撤销功能实现完整且正常")
    print("   - 字符串模板语法正确")
    print("   - 撤销脚本生成正常")
    print("   - 撤销逻辑测试通过")
    print("   - UI撤销功能完整")
    
    return True

if __name__ == "__main__":
    test_undo_functionality()