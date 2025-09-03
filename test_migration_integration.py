#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试迁移功能集成效果
"""

import json
import os
import tempfile
import shutil

def test_migration_integration():
    """测试迁移功能集成"""
    
    print("🧪 测试图片映射表迁移集成")
    print("=" * 50)
    
    # 创建临时测试环境
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 测试目录: {temp_dir}")
        
        # 创建测试映射文件（包含混合分隔符）
        test_mapping = {
            "D:/坚果云笔记/Typora云笔记\\images\\test1.png": "https://example.com/test1.png",
            "D:/坚果云笔记/Typora云笔记\\images\\test2.jpg": "https://example.com/test2.jpg",
            "D:/坚果云笔记/Typora云笔记/images/test3.png": "https://example.com/test3.png",  # 已规范化
            "C:\\Users\\test//folder\\image.png": "https://example.com/image.png"
        }
        
        mapping_file = os.path.join(temp_dir, "image_mapping.json")
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(test_mapping, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 创建测试映射文件: {len(test_mapping)} 条记录")
        
        # 模拟MarkdownImageManager的迁移逻辑
        def normalize_path(path):
            """路径规范化函数"""
            if not path:
                return path
            
            normalized = path.replace('\\\\', '/').replace('\\', '/')
            import re
            normalized = re.sub(r'/+', '/', normalized)
            
            if len(normalized) > 1 and normalized.endswith('/'):
                if not (len(normalized) >= 3 and normalized[1:3] == ':/'):
                    normalized = normalized.rstrip('/')
            
            return normalized
        
        def migrate_mapping(mapping_file_path):
            """迁移映射文件"""
            try:
                # 读取原始映射
                with open(mapping_file_path, 'r', encoding='utf-8') as f:
                    original_mapping = json.load(f)
                
                # 检查是否需要迁移
                needs_migration = False
                for local_path in original_mapping.keys():
                    if '\\' in local_path and '/' in local_path:
                        needs_migration = True
                        break
                
                if not needs_migration:
                    print("✅ 无需迁移")
                    return True
                
                print("🔧 开始迁移...")
                
                # 创建备份
                backup_file = f"{mapping_file_path}.backup_test"
                shutil.copy2(mapping_file_path, backup_file)
                print(f"💾 创建备份: {os.path.basename(backup_file)}")
                
                # 执行迁移
                new_mapping = {}
                normalized_count = 0
                
                for local_path, remote_url in original_mapping.items():
                    normalized_path = normalize_path(local_path)
                    
                    if normalized_path != local_path:
                        normalized_count += 1
                        print(f"  🔧 {local_path} -> {normalized_path}")
                    
                    if normalized_path not in new_mapping:
                        new_mapping[normalized_path] = remote_url
                
                # 保存新映射
                with open(mapping_file_path, 'w', encoding='utf-8') as f:
                    json.dump(new_mapping, f, ensure_ascii=False, indent=2)
                
                print(f"✅ 迁移完成: 规范化了 {normalized_count} 个路径")
                print(f"  原始条目: {len(original_mapping)}")
                print(f"  迁移后条目: {len(new_mapping)}")
                
                return True
                
            except Exception as e:
                print(f"❌ 迁移失败: {e}")
                return False
        
        # 执行迁移测试
        success = migrate_mapping(mapping_file)
        
        if success:
            # 验证迁移结果
            with open(mapping_file, 'r', encoding='utf-8') as f:
                migrated_mapping = json.load(f)
            
            print(f"\n📊 迁移结果验证:")
            all_normalized = True
            
            for local_path in migrated_mapping.keys():
                has_mixed_separators = ('\\' in local_path and '/' in local_path)
                if has_mixed_separators:
                    all_normalized = False
                    print(f"❌ 仍有混合分隔符: {local_path}")
            
            if all_normalized:
                print("✅ 所有路径已规范化")
            
            # 显示迁移后的路径
            print(f"\n📝 迁移后的路径:")
            for i, local_path in enumerate(migrated_mapping.keys(), 1):
                print(f"  {i}. {local_path}")
        
        print(f"\n🎯 测试结果: {'✅ 通过' if success else '❌ 失败'}")

def test_edge_cases():
    """测试边缘情况"""
    
    print(f"\n🔍 测试边缘情况")
    print("=" * 50)
    
    def normalize_path(path):
        if not path:
            return path
        
        normalized = path.replace('\\\\', '/').replace('\\', '/')
        import re
        normalized = re.sub(r'/+', '/', normalized)
        
        if len(normalized) > 1 and normalized.endswith('/'):
            if not (len(normalized) >= 3 and normalized[1:3] == ':/'):
                normalized = normalized.rstrip('/')
        
        return normalized
    
    edge_cases = [
        ("空字符串", ""),
        ("None值", None),
        ("纯正斜杠", "D:/folder/file.png"),
        ("纯反斜杠", "D:\\folder\\file.png"),
        ("混合分隔符", "D:/folder\\subfolder/file.png"),
        ("重复分隔符", "D://folder\\\\subfolder///file.png"),
        ("末尾分隔符", "D:/folder/subfolder/"),
        ("根目录", "D:/"),
        ("相对路径", "../folder\\file.png"),
        ("网络路径", "//server\\share/file.png")
    ]
    
    print("测试用例:")
    for name, test_path in edge_cases:
        if test_path is None:
            result = normalize_path(test_path)
            print(f"  {name}: None -> {result}")
        else:
            result = normalize_path(test_path)
            print(f"  {name}: {test_path} -> {result}")

if __name__ == "__main__":
    test_migration_integration()
    test_edge_cases()