#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查撤销脚本代码
"""

def check_undo_script():
    """检查撤销脚本代码是否有问题"""
    print("🔍 检查撤销脚本代码")
    print("=" * 50)
    
    # 你提供的撤销脚本代码
    script_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能修复撤销脚本
生成时间: 20250902_165834
修复文件数: 0
修复引用数: 0
"""

import os
import shutil
import json

def undo_fixes():
    backup_dir = r"D:/坚果云笔记/Typora云笔记\.backup_smart_fix_20250902_165834"
    
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
    
    print(f"\\n撤销完成! 共恢复 {restored_count} 个文件")
    print("建议重新扫描以更新统计信息")

if __name__ == "__main__":
    undo_fixes()'''
    
    print("\n1. 语法检查:")
    try:
        compile(script_code, '<string>', 'exec')
        print("   ✅ 语法正确")
    except SyntaxError as e:
        print(f"   ❌ 语法错误: {e}")
        return False
    
    print("\n2. 代码结构检查:")
    
    # 检查必要的导入
    required_imports = ['import os', 'import shutil', 'import json']
    for imp in required_imports:
        if imp in script_code:
            print(f"   ✅ {imp}")
        else:
            print(f"   ❌ 缺少: {imp}")
    
    # 检查函数定义
    if 'def undo_fixes():' in script_code:
        print("   ✅ undo_fixes函数定义")
    else:
        print("   ❌ 缺少undo_fixes函数定义")
    
    # 检查主程序入口
    if 'if __name__ == "__main__":' in script_code:
        print("   ✅ 主程序入口")
    else:
        print("   ❌ 缺少主程序入口")
    
    print("\n3. 路径检查:")
    
    # 检查备份目录路径
    backup_dir = r"D:/坚果云笔记/Typora云笔记\.backup_smart_fix_20250902_165834"
    print(f"   备份目录: {backup_dir}")
    
    # 检查路径格式
    if backup_dir.endswith('_smart_fix_20250902_165834'):
        print("   ❌ 路径格式错误: 备份目录名应该是 smart_fix_YYYYMMDD_HHMMSS")
        print("   正确格式应该是: D:/坚果云笔记/Typora云笔记/.backup/smart_fix_20250902_165834")
    else:
        print("   ✅ 路径格式正确")
    
    # 检查工作目录路径
    workspace_path = r"D:/坚果云笔记/Typora云笔记"
    print(f"   工作目录: {workspace_path}")
    
    print("\n4. 逻辑检查:")
    
    # 检查关键逻辑
    logic_checks = [
        ('records["modifications"]', '修复记录访问'),
        ('mod["backup_file"]', '备份文件路径获取'),
        ('mod["file"]', '原始文件路径获取'),
        ('os.path.exists(backup_file)', '备份文件存在性检查'),
        ('shutil.copy2(backup_file, target_file)', '文件恢复操作'),
        ('except Exception as e:', '异常处理')
    ]
    
    for check, description in logic_checks:
        if check in script_code:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ 缺少: {description}")
    
    print("\n5. 发现的问题:")
    
    issues = []
    
    # 检查备份目录路径问题
    if '\.backup_smart_fix_' in script_code:
        issues.append("备份目录路径格式错误")
        print("   ❌ 备份目录路径格式错误")
        print("      当前: D:/坚果云笔记/Typora云笔记\.backup_smart_fix_20250902_165834")
        print("      正确: D:/坚果云笔记/Typora云笔记/.backup/smart_fix_20250902_165834")
    
    # 检查修复统计信息
    if '修复文件数: 0' in script_code and '修复引用数: 0' in script_code:
        issues.append("没有实际修复操作")
        print("   ⚠️  修复文件数和修复引用数都是0，说明没有实际的修复操作")
    
    # 检查字符串转义
    if '\\n' in script_code:
        print("   ✅ 字符串转义正确")
    
    print("\n6. 修复建议:")
    
    if issues:
        print("   发现以下问题需要修复:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        if "备份目录路径格式错误" in issues:
            print("\n   修复方案:")
            print("   将备份目录路径从:")
            print('   backup_dir = r"D:/坚果云笔记/Typora云笔记\.backup_smart_fix_20250902_165834"')
            print("   修改为:")
            print('   backup_dir = r"D:/坚果云笔记/Typora云笔记/.backup/smart_fix_20250902_165834"')
    else:
        print("   ✅ 代码结构正常")
    
    print("\n" + "=" * 50)
    print("📋 检查总结:")
    
    if issues:
        print("❌ 发现问题，需要修复")
        return False
    else:
        print("✅ 撤销脚本代码基本正常")
        return True

if __name__ == "__main__":
    check_undo_script()