#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为主程序添加图片映射表迁移功能的代码补丁
"""

def create_migration_methods():
    """创建需要添加到MarkdownImageManager类的迁移方法"""
    
    migration_code = '''
    def migrate_image_mapping(self):
        """迁移现有图片映射表，修复路径分隔符问题"""
        
        mapping_file = os.path.join(self.workspace_path, self.mapping_file)
        
        if not os.path.exists(mapping_file):
            self.log("📁 未找到现有映射文件，无需迁移")
            return True
        
        try:
            # 读取现有映射
            with open(mapping_file, 'r', encoding='utf-8') as f:
                original_mapping = json.load(f)
            
            if not original_mapping:
                self.log("📁 映射文件为空，无需迁移")
                return True
            
            # 分析是否需要迁移
            needs_migration = False
            problematic_count = 0
            
            for local_path in original_mapping.keys():
                if '\\\\' in local_path and '/' in local_path:
                    needs_migration = True
                    problematic_count += 1
            
            if not needs_migration:
                self.log("✅ 映射表路径已规范化，无需迁移")
                return True
            
            self.log(f"🔍 发现 {problematic_count} 个需要修复的路径")
            
            # 创建备份
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{mapping_file}.backup_{timestamp}"
            shutil.copy2(mapping_file, backup_file)
            self.log(f"💾 已创建备份: {os.path.basename(backup_file)}")
            
            # 执行迁移
            new_mapping = {}
            normalized_count = 0
            duplicate_count = 0
            
            for local_path, remote_url in original_mapping.items():
                normalized_path = self.normalize_path(local_path)
                
                if normalized_path != local_path:
                    normalized_count += 1
                    self.log(f"🔧 规范化: {local_path} -> {normalized_path}")
                
                # 处理重复项
                if normalized_path in new_mapping:
                    if new_mapping[normalized_path] != remote_url:
                        duplicate_count += 1
                        self.log(f"⚠️ 发现重复路径，保留第一个: {normalized_path}")
                    # 保留第一个，跳过重复项
                    continue
                
                new_mapping[normalized_path] = remote_url
            
            # 保存新映射
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(new_mapping, f, ensure_ascii=False, indent=2)
            
            # 更新内存中的映射
            self.image_mapping = new_mapping
            
            self.log(f"✅ 迁移完成!")
            self.log(f"  原始条目: {len(original_mapping)}")
            self.log(f"  迁移后条目: {len(new_mapping)}")
            self.log(f"  路径规范化: {normalized_count}")
            self.log(f"  重复项处理: {duplicate_count}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ 迁移失败: {e}")
            return False
    
    def load_image_mapping_with_migration(self):
        """加载图片映射表，如果需要则自动迁移"""
        
        # 先尝试迁移
        self.migrate_image_mapping()
        
        # 然后加载映射表
        mapping_file = os.path.join(self.workspace_path, self.mapping_file)
        
        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    self.image_mapping = json.load(f)
                
                # 确保所有路径都是规范化的
                normalized_mapping = {}
                for local_path, remote_url in self.image_mapping.items():
                    normalized_path = self.normalize_path(local_path)
                    normalized_mapping[normalized_path] = remote_url
                
                self.image_mapping = normalized_mapping
                
                self.log(f"📁 已加载图片映射表: {len(self.image_mapping)} 条记录")
                
            except Exception as e:
                self.log(f"❌ 加载映射表失败: {e}")
                self.image_mapping = {}
        else:
            self.image_mapping = {}
    
    def save_image_mapping_normalized(self):
        """保存图片映射表，确保所有路径都是规范化的"""
        
        if not self.image_mapping:
            return
        
        # 规范化所有路径
        normalized_mapping = {}
        for local_path, remote_url in self.image_mapping.items():
            normalized_path = self.normalize_path(local_path)
            normalized_mapping[normalized_path] = remote_url
        
        mapping_file = os.path.join(self.workspace_path, self.mapping_file)
        
        try:
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(normalized_mapping, f, ensure_ascii=False, indent=2)
            
            # 更新内存中的映射
            self.image_mapping = normalized_mapping
            
        except Exception as e:
            self.log(f"❌ 保存映射表失败: {e}")
'''
    
    return migration_code

def create_integration_instructions():
    """创建集成说明"""
    
    instructions = '''
📝 集成说明：

1. 将迁移方法添加到 MarkdownImageManager 类中：
   - migrate_image_mapping()
   - load_image_mapping_with_migration()  
   - save_image_mapping_normalized()

2. 修改现有的加载映射表的地方：
   
   原来的代码：
   ```python
   if os.path.exists(mapping_file):
       with open(mapping_file, 'r', encoding='utf-8') as f:
           self.image_mapping = json.load(f)
   ```
   
   替换为：
   ```python
   self.load_image_mapping_with_migration()
   ```

3. 修改保存映射表的地方：
   
   原来的代码：
   ```python
   with open(mapping_file, 'w', encoding='utf-8') as f:
       json.dump(self.image_mapping, f, ensure_ascii=False, indent=2)
   ```
   
   替换为：
   ```python
   self.save_image_mapping_normalized()
   ```

4. 在程序启动时自动检查和迁移：
   
   在 __init__ 方法中添加：
   ```python
   # 加载并迁移图片映射表
   self.load_image_mapping_with_migration()
   ```

5. 添加手动迁移按钮（可选）：
   
   在GUI中添加一个"迁移映射表"按钮，调用：
   ```python
   def manual_migrate_mapping(self):
       if self.migrate_image_mapping():
           messagebox.showinfo("完成", "映射表迁移完成！")
       else:
           messagebox.showerror("错误", "映射表迁移失败！")
   ```
'''
    
    return instructions

def main():
    """主函数"""
    
    print("🔧 图片映射表迁移集成方案")
    print("=" * 60)
    
    print("📝 需要添加的方法:")
    print(create_migration_methods())
    
    print("\\n" + "=" * 60)
    print(create_integration_instructions())
    
    print("\\n" + "=" * 60)
    print("🎯 推荐实施步骤:")
    print("1. 先运行独立的迁移脚本 (migrate_image_mapping.py)")
    print("2. 验证迁移结果")
    print("3. 将迁移方法集成到主程序")
    print("4. 测试集成后的功能")
    print("5. 部署更新")

if __name__ == "__main__":
    main()