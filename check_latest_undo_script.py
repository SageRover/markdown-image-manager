#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查最新的撤销脚本代码
"""

def check_latest_undo_script():
    """检查最新的撤销脚本代码"""
    print("🔍 检查最新的撤销脚本代码")
    print("=" * 50)
    
    # 最新的撤销脚本代码
    latest_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能修复撤销脚本
生成时间: 20250902_173929
修复文件数: 0
修复引用数: 0
"""

import os
import shutil
import json

def undo_fixes():
    backup_dir = r"D:/坚果云笔记/Typora云笔记\.backup\smart_fix_20250902_173929"
    
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
        compile(latest_script, '<string>', 'exec')
        print("   ✅ 语法正确")
    except SyntaxError as e:
        print(f"   ❌ 语法错误: {e}")
        return False
    
    print("\n2. 路径格式检查:")
    
    # 检查备份目录路径
    backup_line = 'backup_dir = r"D:/坚果云笔记/Typora云笔记\.backup\smart_fix_20250902_173929"'
    
    if backup_line in latest_script:
        print("   ❌ 备份目录路径格式仍然有问题!")
        print(f"   当前: {backup_line}")
        print("   问题: 路径中仍然使用了 \.backup\ 而不是 /.backup/")
        print("   正确应该是: backup_dir = r\"D:/坚果云笔记/Typora云笔记/.backup/smart_fix_20250902_173929\"")
    else:
        print("   ✅ 备份目录路径格式正确")
    
    # 检查工作目录路径
    workspace_line = 'workspace_path = r"D:/坚果云笔记/Typora云笔记"'
    if workspace_line in latest_script:
        print("   ✅ 工作目录路径格式正确")
    else:
        print("   ❌ 工作目录路径格式有问题")
    
    print("\n3. 路径分析:")
    
    # 分析路径问题
    problem_path = r"D:/坚果云笔记/Typora云笔记\.backup\smart_fix_20250902_173929"
    correct_path = r"D:/坚果云笔记/Typora云笔记/.backup/smart_fix_20250902_173929"
    
    print(f"   问题路径: {problem_path}")
    print(f"   正确路径: {correct_path}")
    
    print("\n   路径问题详解:")
    print("   - 问题路径使用了 \.backup\ (反斜杠)")
    print("   - 正确路径应该使用 /.backup/ (正斜杠)")
    print("   - 在Windows中，路径分隔符应该统一使用")
    
    print("\n4. 修复建议:")
    print("   需要修改的行:")
    print('   将: backup_dir = r"D:/坚果云笔记/Typora云笔记\.backup\smart_fix_20250902_173929"')
    print('   改为: backup_dir = r"D:/坚果云笔记/Typora云笔记/.backup/smart_fix_20250902_173929"')
    
    print("\n5. 其他检查:")
    
    # 检查修复统计
    if "修复文件数: 0" in latest_script and "修复引用数: 0" in latest_script:
        print("   ⚠️  修复统计显示没有实际修复操作")
        print("   这可能意味着:")
        print("   - 没有找到需要修复的无效引用")
        print("   - 智能修复没有成功执行")
        print("   - 所有图片引用都是正确的")
    
    # 检查必要的导入和函数
    checks = [
        ('import os', '系统操作模块'),
        ('import shutil', '文件操作模块'),
        ('import json', 'JSON处理模块'),
        ('def undo_fixes():', '撤销函数定义'),
        ('if __name__ == "__main__":', '主程序入口')
    ]
    
    print("\n   代码结构检查:")
    for check, desc in checks:
        if check in latest_script:
            print(f"   ✅ {desc}")
        else:
            print(f"   ❌ 缺少: {desc}")
    
    print("\n" + "=" * 50)
    print("📋 检查总结:")
    print("❌ 撤销脚本仍然有路径格式问题")
    print("   主要问题: 备份目录路径中混用了正斜杠和反斜杠")
    print("   影响: 可能导致文件路径无法正确识别")
    print("   解决: 统一使用正斜杠作为路径分隔符")
    
    return False

if __name__ == "__main__":
    check_latest_undo_script()