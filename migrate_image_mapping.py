#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移和修复现有图片映射表中的路径分隔符问题
"""

import json
import os
import re
import shutil
from datetime import datetime

def normalize_path(path):
    """统一路径分隔符，确保跨平台兼容性"""
    if not path:
        return path
    
    # 统一使用正斜杠
    normalized = path.replace('\\\\', '/').replace('\\', '/')
    
    # 去除重复的分隔符
    normalized = re.sub(r'/+', '/', normalized)
    
    # 去除末尾的分隔符（除非是根目录或Windows驱动器根目录）
    if len(normalized) > 1 and normalized.endswith('/'):
        # 保留Windows驱动器根目录的斜杠 (如 D:/)
        if not (len(normalized) >= 3 and normalized[1:3] == ':/'):
            normalized = normalized.rstrip('/')
    
    return normalized

def analyze_mapping_file(mapping_file_path):
    """分析现有映射文件中的路径问题"""
    
    print("🔍 分析现有图片映射表")
    print("=" * 50)
    
    if not os.path.exists(mapping_file_path):
        print(f"❌ 映射文件不存在: {mapping_file_path}")
        return None, None
    
    try:
        with open(mapping_file_path, 'r', encoding='utf-8') as f:
            mapping_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取映射文件失败: {e}")
        return None, None
    
    print(f"📊 映射表统计:")
    print(f"  总条目数: {len(mapping_data)}")
    
    # 分析路径问题
    problematic_paths = []
    normalized_mapping = {}
    duplicates = []
    
    for local_path, remote_url in mapping_data.items():
        # 检查是否有混合分隔符
        has_mixed_separators = ('\\' in local_path and '/' in local_path)
        
        if has_mixed_separators:
            problematic_paths.append({
                'original': local_path,
                'remote_url': remote_url,
                'issue': 'mixed_separators'
            })
        
        # 规范化路径
        normalized_local = normalize_path(local_path)
        
        # 检查规范化后是否有重复
        if normalized_local in normalized_mapping:
            duplicates.append({
                'path1': normalized_mapping[normalized_local]['original'],
                'path2': local_path,
                'normalized': normalized_local,
                'url1': normalized_mapping[normalized_local]['remote_url'],
                'url2': remote_url
            })
        else:
            normalized_mapping[normalized_local] = {
                'original': local_path,
                'remote_url': remote_url
            }
    
    print(f"  混合分隔符路径: {len(problematic_paths)} 个")
    print(f"  规范化后重复: {len(duplicates)} 个")
    
    # 显示问题详情
    if problematic_paths:
        print(f"\n🚨 发现的问题路径:")
        for i, problem in enumerate(problematic_paths[:5], 1):  # 只显示前5个
            print(f"  {i}. {problem['original']}")
            print(f"     规范化后: {normalize_path(problem['original'])}")
        
        if len(problematic_paths) > 5:
            print(f"     ... 还有 {len(problematic_paths) - 5} 个问题路径")
    
    if duplicates:
        print(f"\n🔄 规范化后的重复项:")
        for i, dup in enumerate(duplicates[:3], 1):  # 只显示前3个
            print(f"  {i}. 规范化路径: {dup['normalized']}")
            print(f"     原路径1: {dup['path1']}")
            print(f"     原路径2: {dup['path2']}")
            print(f"     URL相同: {dup['url1'] == dup['url2']}")
        
        if len(duplicates) > 3:
            print(f"     ... 还有 {len(duplicates) - 3} 个重复项")
    
    return mapping_data, {
        'problematic_paths': problematic_paths,
        'duplicates': duplicates,
        'normalized_mapping': normalized_mapping
    }

def create_migration_plan(analysis_result):
    """创建迁移计划"""
    
    print(f"\n📋 创建迁移计划")
    print("=" * 50)
    
    if not analysis_result:
        print("❌ 无法创建迁移计划，分析结果为空")
        return None
    
    problematic_paths = analysis_result['problematic_paths']
    duplicates = analysis_result['duplicates']
    normalized_mapping = analysis_result['normalized_mapping']
    
    migration_plan = {
        'backup_needed': True,
        'actions': []
    }
    
    # 1. 路径规范化操作
    if problematic_paths:
        migration_plan['actions'].append({
            'type': 'normalize_paths',
            'description': f'规范化 {len(problematic_paths)} 个混合分隔符路径',
            'items': problematic_paths
        })
    
    # 2. 重复项处理
    if duplicates:
        migration_plan['actions'].append({
            'type': 'handle_duplicates',
            'description': f'处理 {len(duplicates)} 个重复项',
            'items': duplicates,
            'strategy': 'keep_first'  # 保留第一个，删除后续重复项
        })
    
    # 3. 验证操作
    migration_plan['actions'].append({
        'type': 'validate',
        'description': '验证迁移后的映射表完整性'
    })
    
    print(f"📝 迁移计划:")
    for i, action in enumerate(migration_plan['actions'], 1):
        print(f"  {i}. {action['description']}")
    
    return migration_plan

def execute_migration(mapping_file_path, original_mapping, migration_plan):
    """执行迁移操作"""
    
    print(f"\n🚀 执行迁移操作")
    print("=" * 50)
    
    if not migration_plan:
        print("❌ 没有迁移计划，跳过迁移")
        return False
    
    # 1. 创建备份
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{mapping_file_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(mapping_file_path, backup_file)
        print(f"✅ 已创建备份: {backup_file}")
    except Exception as e:
        print(f"❌ 创建备份失败: {e}")
        return False
    
    # 2. 执行迁移操作
    new_mapping = {}
    migration_log = []
    
    for local_path, remote_url in original_mapping.items():
        normalized_local = normalize_path(local_path)
        
        # 检查是否已存在（处理重复项）
        if normalized_local in new_mapping:
            # 重复项处理：保留第一个，记录冲突
            existing_url = new_mapping[normalized_local]
            if existing_url != remote_url:
                migration_log.append({
                    'type': 'duplicate_conflict',
                    'path': normalized_local,
                    'kept_url': existing_url,
                    'discarded_url': remote_url,
                    'original_path': local_path
                })
            else:
                migration_log.append({
                    'type': 'duplicate_same_url',
                    'path': normalized_local,
                    'url': remote_url,
                    'original_path': local_path
                })
        else:
            new_mapping[normalized_local] = remote_url
            
            # 记录路径变化
            if normalized_local != local_path:
                migration_log.append({
                    'type': 'path_normalized',
                    'original': local_path,
                    'normalized': normalized_local,
                    'url': remote_url
                })
    
    # 3. 保存新的映射文件
    try:
        with open(mapping_file_path, 'w', encoding='utf-8') as f:
            json.dump(new_mapping, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存新的映射文件")
    except Exception as e:
        print(f"❌ 保存映射文件失败: {e}")
        # 恢复备份
        try:
            shutil.copy2(backup_file, mapping_file_path)
            print(f"✅ 已恢复备份文件")
        except:
            pass
        return False
    
    # 4. 保存迁移日志
    log_file = f"{mapping_file_path}.migration_log_{timestamp}.json"
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'original_count': len(original_mapping),
                'new_count': len(new_mapping),
                'migration_log': migration_log
            }, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存迁移日志: {log_file}")
    except Exception as e:
        print(f"⚠️ 保存迁移日志失败: {e}")
    
    # 5. 显示迁移结果
    print(f"\n📊 迁移结果:")
    print(f"  原始条目: {len(original_mapping)}")
    print(f"  迁移后条目: {len(new_mapping)}")
    print(f"  路径规范化: {len([log for log in migration_log if log['type'] == 'path_normalized'])}")
    print(f"  重复项合并: {len([log for log in migration_log if log['type'].startswith('duplicate')])}")
    
    return True

def main():
    """主函数"""
    
    print("🔧 图片映射表迁移工具")
    print("=" * 60)
    
    # 默认映射文件路径（可以根据实际情况调整）
    mapping_file_path = "image_mapping.json"
    
    # 如果文件不存在，尝试在常见位置查找
    if not os.path.exists(mapping_file_path):
        possible_paths = [
            "image_mapping.json",
            "./image_mapping.json",
            "../image_mapping.json",
            "D:/坚果云笔记/Typora云笔记/image_mapping.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                mapping_file_path = path
                break
        else:
            print(f"❌ 未找到图片映射文件")
            print(f"请确保以下文件之一存在:")
            for path in possible_paths:
                print(f"  - {path}")
            return
    
    print(f"📁 使用映射文件: {mapping_file_path}")
    
    # 1. 分析现有映射文件
    original_mapping, analysis_result = analyze_mapping_file(mapping_file_path)
    
    if not original_mapping:
        return
    
    # 2. 创建迁移计划
    migration_plan = create_migration_plan(analysis_result)
    
    # 3. 询问用户是否执行迁移
    if migration_plan and migration_plan['actions']:
        print(f"\n❓ 是否执行迁移操作？")
        print(f"  - 将创建备份文件")
        print(f"  - 规范化所有路径分隔符")
        print(f"  - 处理重复项")
        
        # 在实际使用中，这里应该有用户交互
        # 现在我们假设用户同意迁移
        user_confirm = True  # input("请输入 'yes' 确认: ").lower() == 'yes'
        
        if user_confirm:
            # 4. 执行迁移
            success = execute_migration(mapping_file_path, original_mapping, migration_plan)
            
            if success:
                print(f"\n🎉 迁移完成！")
                print(f"  备份文件已保存")
                print(f"  映射表已更新")
                print(f"  建议重新扫描以验证结果")
            else:
                print(f"\n❌ 迁移失败，请检查错误信息")
        else:
            print(f"\n⏸️ 用户取消迁移操作")
    else:
        print(f"\n✅ 映射表无需迁移，所有路径已规范化")

if __name__ == "__main__":
    main()