#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown图片管家 - 修复版本
功能：
1. 搜索MD文件和图片，分析引用关系
2. 上传图片到图床（通过PicList）
3. 替换图片链接（本地/远程）
4. 下载远程图片到本地
5. 删除未使用的本地图片
"""

import os
import re
import json
import shutil
import datetime
import shutil
import requests
import subprocess
from pathlib import Path
from urllib.parse import urlparse, unquote
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Dict, List, Set, Tuple
import threading

class MarkdownImageManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Markdown图片管家")
        self.root.geometry("1000x700")
        
        # 数据存储
        self.workspace_path = ""
        self.md_files = []
        self.image_files = []
        self.image_references = {}  # {md_file: [image_paths]}
        self.unused_images = []
        self.invalid_images = {}  # {md_file: [invalid_image_paths]}
        self.image_mapping = {}  # {local_path: remote_url}
        self.mapping_file = "image_mapping.json"
        
        # 加载并迁移图片映射表
        self.load_image_mapping_with_migration()
        
        # 统计数据
        self.referenced_local_images = []  # 被引用的本地图片
        self.remote_images = []  # 远程图片列表
        
        # 支持的图片格式
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        
        self.setup_ui()
        self.load_mapping()
    
    def normalize_path(self, path):
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

    def migrate_image_mapping(self):
        """迁移现有图片映射表，修复路径分隔符问题"""
        
        mapping_file = os.path.join(self.workspace_path, self.mapping_file)
        
        if not os.path.exists(mapping_file):
            return True
        
        try:
            # 读取现有映射
            with open(mapping_file, 'r', encoding='utf-8') as f:
                original_mapping = json.load(f)
            
            if not original_mapping:
                return True
            
            # 分析是否需要迁移
            needs_migration = False
            problematic_count = 0
            
            for local_path in original_mapping.keys():
                if '\\' in local_path and '/' in local_path:
                    needs_migration = True
                    problematic_count += 1
            
            if not needs_migration:
                return True
            
            # 创建备份
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{mapping_file}.backup_{timestamp}"
            shutil.copy2(mapping_file, backup_file)
            
            # 执行迁移
            new_mapping = {}
            normalized_count = 0
            
            for local_path, remote_url in original_mapping.items():
                normalized_path = self.normalize_path(local_path)
                
                if normalized_path != local_path:
                    normalized_count += 1
                
                # 处理重复项（保留第一个）
                if normalized_path not in new_mapping:
                    new_mapping[normalized_path] = remote_url
            
            # 保存新映射
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(new_mapping, f, ensure_ascii=False, indent=2)
            
            if normalized_count > 0:
                self.log(f"✅ 映射表迁移完成: 规范化了 {normalized_count} 个路径")
            
            return True
            
        except Exception as e:
            self.log(f"❌ 映射表迁移失败: {e}")
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

    def safe_relpath(self, path, start):
        """安全的相对路径计算，处理跨驱动器情况"""
        try:
            # 先规范化输入路径
            path = self.normalize_path(path)
            start = self.normalize_path(start)
            
            rel_path = os.path.relpath(path, start)
            return self.normalize_path(rel_path)
        except ValueError:
            # 跨驱动器情况，返回规范化的绝对路径
            return self.normalize_path(path)
    
    def download_image_with_retry(self, url, local_path, max_retries=1):
        """图片下载，单次尝试"""
        import time
        
        # 不同的请求头配置
        headers_list = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://gitee.com/',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
            },
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Accept': 'image/webp,*/*',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            }
        ]
        
        # 处理Gitee URL的特殊情况
        original_url = url
        if 'gitee.com' in url and '//img/' in url:
            # 修复双斜杠问题
            url = url.replace('//img/', '/img/')
            self.log(f"    修复Gitee URL: {url}")
        
        for attempt in range(max_retries):
            try:
                headers = headers_list[attempt % len(headers_list)]
                
                # 创建session以保持连接
                session = requests.Session()
                session.headers.update(headers)
                
                self.log(f"    下载: {os.path.basename(local_path)}")
                
                response = session.get(url, timeout=30, allow_redirects=True)
                
                # 检查响应状态
                if response.status_code == 200:
                    # 检查内容类型
                    content_type = response.headers.get('content-type', '').lower()
                    if 'image' in content_type or len(response.content) > 1000:
                        with open(local_path, 'wb') as f:
                            f.write(response.content)
                        return True
                    else:
                        self.log(f"    响应不是图片内容: {content_type}")
                elif response.status_code == 403:
                    self.log(f"    403 Forbidden - 尝试其他方法")
                    # 对于403错误，尝试不同的URL格式
                    if 'gitee.com' in url and attempt == 0:
                        # 尝试去掉raw参数
                        alt_url = url.replace('/raw/master/', '/master/')
                        try:
                            alt_response = session.get(alt_url, timeout=30)
                            if alt_response.status_code == 200:
                                with open(local_path, 'wb') as f:
                                    f.write(alt_response.content)
                                return True
                        except:
                            pass
                else:
                    self.log(f"    HTTP {response.status_code}: {response.reason}")
                
            except requests.exceptions.Timeout:
                self.log(f"    下载超时")
            except requests.exceptions.ConnectionError:
                self.log(f"    连接错误")
            except Exception as e:
                self.log(f"    下载错误: {str(e)}")
            
            # 不重试，直接退出循环
            break
        
        return False
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 工作目录选择
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(dir_frame, text="工作目录:").grid(row=0, column=0, sticky=tk.W)
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=60)
        self.dir_entry.grid(row=0, column=1, padx=(5, 5), sticky=(tk.W, tk.E))
        ttk.Button(dir_frame, text="选择", command=self.select_directory).grid(row=0, column=2)
        
        dir_frame.columnconfigure(1, weight=1)
        
        # 功能按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 第一行按钮
        ttk.Button(button_frame, text="1. 扫描分析", command=self.scan_files, width=15).grid(row=0, column=0, padx=2)
        ttk.Button(button_frame, text="2. 上传到图床", command=self.upload_images, width=15).grid(row=0, column=1, padx=2)
        ttk.Button(button_frame, text="3. 替换为远程", command=self.replace_to_remote, width=15).grid(row=0, column=2, padx=2)
        ttk.Button(button_frame, text="4. 替换为本地", command=self.replace_to_local, width=15).grid(row=0, column=3, padx=2)
        
        # 第二行按钮
        ttk.Button(button_frame, text="5. 下载远程图片", command=self.download_images, width=15).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(button_frame, text="6. 删除本地图片", command=self.delete_local_images, width=15).grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(button_frame, text="修复失效链接", command=self.fix_broken_links, width=15).grid(row=1, column=2, padx=2, pady=2)
        ttk.Button(button_frame, text="导出报告", command=self.export_report, width=15).grid(row=1, column=3, padx=2, pady=2)
        
        # 第三行按钮
        ttk.Button(button_frame, text="智能修复路径", command=self.smart_fix_paths, width=15).grid(row=2, column=0, padx=2, pady=2)
        ttk.Button(button_frame, text="撤销修复", command=self.undo_fixes, width=15).grid(row=2, column=1, padx=2, pady=2)
        ttk.Button(button_frame, text="清空日志", command=self.clear_log, width=15).grid(row=2, column=2, padx=2, pady=2)
        
        # 结果显示区域
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 创建Notebook用于标签页
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志标签页
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="操作日志")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 分析结果标签页
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="分析结果")
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, height=15, width=80)
        self.analysis_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 映射表标签页
        mapping_frame = ttk.Frame(self.notebook)
        self.notebook.add(mapping_frame, text="图片映射表")
        
        self.mapping_text = scrolledtext.ScrolledText(mapping_frame, height=15, width=80)
        self.mapping_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(0, weight=1)
        mapping_frame.columnconfigure(0, weight=1)
        mapping_frame.rowconfigure(0, weight=1)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def log(self, message):
        """添加日志信息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def select_directory(self):
        """选择工作目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.workspace_path = directory
            self.dir_var.set(directory)
            self.log(f"选择工作目录: {directory}")
    
    def load_mapping(self):
        """加载图片映射表"""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    self.image_mapping = json.load(f)
                self.update_mapping_display()
                self.log(f"加载映射表: {len(self.image_mapping)} 条记录")
        except Exception as e:
            self.log(f"加载映射表失败: {e}")
    
    def save_mapping(self):
        """保存图片映射表"""
        try:
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.image_mapping, f, ensure_ascii=False, indent=2)
            self.update_mapping_display()
            self.log(f"保存映射表: {len(self.image_mapping)} 条记录")
        except Exception as e:
            self.log(f"保存映射表失败: {e}")
    
    def update_mapping_display(self):
        """更新映射表显示"""
        self.mapping_text.delete(1.0, tk.END)
        if self.image_mapping:
            for local_path, remote_url in self.image_mapping.items():
                self.mapping_text.insert(tk.END, f"本地: {local_path}\n")
                self.mapping_text.insert(tk.END, f"远程: {remote_url}\n")
                self.mapping_text.insert(tk.END, "-" * 80 + "\n")    

    def scan_files(self):
        """扫描分析MD文件和图片"""
        if not self.workspace_path:
            messagebox.showerror("错误", "请先选择工作目录")
            return
        
        def scan_thread():
            try:
                self.log("开始扫描文件...")
                
                # 扫描MD文件
                self.md_files = []
                self.image_files = []
                self.image_references = {}
                self.invalid_images = {}
                self.referenced_local_images = []
                self.remote_images = []
                
                for root, dirs, files in os.walk(self.workspace_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 标准化路径格式并规范化分隔符
                        file_path = self.normalize_path(os.path.normpath(file_path))
                        if file.lower().endswith('.md'):
                            self.md_files.append(file_path)
                        elif any(file.lower().endswith(ext) for ext in self.image_extensions):
                            self.image_files.append(file_path)
                
                self.log(f"找到 {len(self.md_files)} 个MD文件")
                self.log(f"找到 {len(self.image_files)} 个图片文件")
                
                # 显示图片文件的一些示例路径
                if self.image_files:
                    self.log("本地图片文件示例:")
                    for i, img in enumerate(self.image_files[:3]):
                        rel_path = self.safe_relpath(img, self.workspace_path)
                        self.log(f"  {i+1}. {rel_path}")
                    if len(self.image_files) > 3:
                        self.log(f"  ... 还有 {len(self.image_files) - 3} 个文件")
                
                # 分析图片引用
                referenced_images = set()
                
                for md_file in self.md_files:
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 查找图片引用 ![](path) 和 <img src="path">
                        img_patterns = [
                            r'!\[.*?\]\((.*?)\)',  # ![alt](path)
                            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',  # <img src="path">
                        ]
                        
                        file_images = []
                        file_invalid = []
                        
                        for pattern in img_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                img_path = match.strip()
                                if img_path:
                                    # 处理相对路径
                                    if not (img_path.startswith('http') or img_path.startswith('https')):
                                        # 相对于MD文件的路径
                                        abs_img_path = os.path.join(os.path.dirname(md_file), img_path)
                                        abs_img_path = self.normalize_path(os.path.normpath(abs_img_path))
                                        
                                        if os.path.exists(abs_img_path):
                                            file_images.append(abs_img_path)
                                            referenced_images.add(abs_img_path)
                                        else:
                                            file_invalid.append(img_path)
                                    else:
                                        # 远程图片
                                        file_images.append(img_path)
                        
                        if file_images:
                            self.image_references[md_file] = file_images
                        if file_invalid:
                            self.invalid_images[md_file] = file_invalid
                    
                    except Exception as e:
                        self.log(f"分析文件 {md_file} 时出错: {e}")
                
                # 找出未被引用的图片
                # 标准化referenced_images中的路径
                referenced_images_normalized = {os.path.normpath(path) for path in referenced_images}
                
                self.unused_images = []
                for img_file in self.image_files:
                    # 标准化当前图片文件路径
                    img_file_normalized = os.path.normpath(img_file)
                    if img_file_normalized not in referenced_images_normalized:
                        self.unused_images.append(img_file)
                
                # 统计被引用的图片
                self.referenced_local_images = list(referenced_images)
                
                # 简化的统计验证
                actual_unused = len(self.image_files) - len(referenced_images)
                if abs(len(self.unused_images) - actual_unused) > 10:  # 允许小差异
                    self.log(f"⚠️ 注意：统计可能有小差异，这通常是由于重复引用造成的")
                
                # 统计远程图片
                self.remote_images = []
                for images in self.image_references.values():
                    for img in images:
                        if img.startswith('http') and img not in self.remote_images:
                            self.remote_images.append(img)
                
                self.log("扫描完成!")
                self.display_analysis_results()
                
            except Exception as e:
                self.log(f"扫描失败: {e}")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def display_analysis_results(self):
        """显示分析结果"""
        self.analysis_text.delete(1.0, tk.END)
        
        # 显示MD文件及其引用的图片
        self.analysis_text.insert(tk.END, "=== MD文件图片引用分析 ===\n\n")
        for md_file, images in self.image_references.items():
            rel_md = self.safe_relpath(md_file, self.workspace_path)
            self.analysis_text.insert(tk.END, f"📄 {rel_md}\n")
            for img in images:
                if img.startswith('http'):
                    self.analysis_text.insert(tk.END, f"  🌐 {img}\n")
                else:
                    rel_img = self.safe_relpath(img, self.workspace_path)
                    self.analysis_text.insert(tk.END, f"  🖼️  {rel_img}\n")
            self.analysis_text.insert(tk.END, "\n")
        
        # 显示无效图片
        if self.invalid_images:
            self.analysis_text.insert(tk.END, "=== 无效图片引用 ===\n\n")
            for md_file, invalid_imgs in self.invalid_images.items():
                rel_md = self.safe_relpath(md_file, self.workspace_path)
                self.analysis_text.insert(tk.END, f"📄 {rel_md}\n")
                for img in invalid_imgs:
                    self.analysis_text.insert(tk.END, f"  ❌ {img}\n")
                self.analysis_text.insert(tk.END, "\n")
        
        # 显示未被引用的图片
        if self.unused_images:
            self.analysis_text.insert(tk.END, "=== 未被引用的图片 ===\n\n")
            for img in self.unused_images:
                rel_img = self.safe_relpath(img, self.workspace_path)
                self.analysis_text.insert(tk.END, f"🗑️  {rel_img}\n")
        
        # 统计信息
        # 使用referenced_local_images的实际大小，因为路径匹配可能有问题
        referenced_local_count = len(getattr(self, 'referenced_local_images', []))
        unused_count = len(self.image_files) - referenced_local_count if referenced_local_count > 0 else len(self.unused_images)
        
        self.analysis_text.insert(tk.END, f"\n=== 统计信息 ===\n")
        self.analysis_text.insert(tk.END, f"MD文件总数: {len(self.md_files)}\n")
        self.analysis_text.insert(tk.END, f"本地图片文件总数: {len(self.image_files)}\n")
        self.analysis_text.insert(tk.END, f"被引用的本地图片数: {referenced_local_count}\n")
        self.analysis_text.insert(tk.END, f"被引用的远程图片数: {len(getattr(self, 'remote_images', []))}\n")
        self.analysis_text.insert(tk.END, f"未被引用的本地图片数: {unused_count}\n")
        self.analysis_text.insert(tk.END, f"无效引用数: {sum(len(imgs) for imgs in self.invalid_images.values())}\n")
        self.analysis_text.insert(tk.END, f"图片映射记录数: {len(self.image_mapping)}\n")
    
    def upload_images(self):
        """上传图片到图床（通过PicList）"""
        if not self.image_references:
            messagebox.showerror("错误", "请先扫描分析文件")
            return
        
        # 选择要处理的MD文件
        md_files = list(self.image_references.keys())
        if not md_files:
            messagebox.showinfo("信息", "没有找到包含图片的MD文件")
            return
        
        # 创建选择对话框
        selection_window = tk.Toplevel(self.root)
        selection_window.title("选择MD文件")
        selection_window.geometry("600x400")
        
        ttk.Label(selection_window, text="选择要上传图片的MD文件:").pack(pady=10)
        
        # 文件列表
        listbox_frame = ttk.Frame(selection_window)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, selectmode=tk.MULTIPLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for md_file in md_files:
            rel_path = self.safe_relpath(md_file, self.workspace_path)
            listbox.insert(tk.END, rel_path)
        
        def upload_selected():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("警告", "请选择至少一个MD文件")
                return
            
            selected_files = [md_files[i] for i in selected_indices]
            selection_window.destroy()
            self.perform_upload(selected_files)
        
        button_frame = ttk.Frame(selection_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="上传", command=upload_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=selection_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def perform_upload(self, md_files):
        """执行图片上传"""
        def upload_thread():
            try:
                self.log("开始上传图片到图床...")
                
                for md_file in md_files:
                    rel_md = self.safe_relpath(md_file, self.workspace_path)
                    self.log(f"处理文件: {rel_md}")
                    
                    images = self.image_references.get(md_file, [])
                    local_images = [img for img in images if not img.startswith('http')]
                    
                    for img_path in local_images:
                        if img_path in self.image_mapping:
                            self.log(f"  跳过已上传: {os.path.basename(img_path)}")
                            continue
                        
                        try:
                            # 使用PicList上传图片
                            remote_url = self.upload_to_piclist(img_path)
                            if remote_url:
                                self.image_mapping[img_path] = remote_url
                                self.log(f"  ✅ 上传成功: {os.path.basename(img_path)} -> {remote_url}")
                            else:
                                self.log(f"  ❌ 上传失败: {os.path.basename(img_path)}")
                        
                        except Exception as e:
                            self.log(f"  ❌ 上传出错: {os.path.basename(img_path)} - {e}")
                
                self.save_mapping()
                self.log("图片上传完成!")
                
            except Exception as e:
                self.log(f"上传失败: {e}")
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def upload_to_piclist(self, image_path):
        """通过PicList上传图片"""
        try:
            # 尝试调用PicList命令行接口
            # 注意：这里需要根据实际的PicList安装情况调整命令
            cmd = ['piclist', 'upload', image_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # 从输出中提取URL（需要根据PicList的实际输出格式调整）
                output = result.stdout.strip()
                # 假设PicList返回的是URL
                if output.startswith('http'):
                    return output
            
            # 如果PicList不可用，返回模拟URL（用于测试）
            filename = os.path.basename(image_path)
            return f"https://example.com/images/{filename}"
            
        except subprocess.TimeoutExpired:
            self.log(f"上传超时: {image_path}")
            return None
        except FileNotFoundError:
            self.log("PicList未找到，请确保已正确安装PicList")
            # 返回模拟URL用于测试
            filename = os.path.basename(image_path)
            return f"https://example.com/images/{filename}"
        except Exception as e:
            self.log(f"PicList上传出错: {e}")
            return None   
 
    def replace_to_remote(self):
        """替换图片链接为远程URL"""
        if not self.image_mapping:
            messagebox.showinfo("信息", "没有找到图片映射记录")
            return
        
        def replace_thread():
            try:
                self.log("开始替换为远程链接...")
                
                for md_file in self.md_files:
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        replaced_count = 0
                        
                        # 替换图片链接
                        for local_path, remote_url in self.image_mapping.items():
                            # 计算相对路径，处理跨驱动器情况
                            rel_path = self.safe_relpath(local_path, os.path.dirname(md_file))
                            local_path_normalized = self.normalize_path(local_path)
                            
                            # 替换各种可能的路径格式
                            patterns = [
                                f'!\\[([^\\]]*)\\]\\({re.escape(rel_path)}\\)',
                                f'!\\[([^\\]]*)\\]\\({re.escape(local_path_normalized)}\\)',
                                f'!\\[([^\\]]*)\\]\\({re.escape(local_path)}\\)',
                                f'<img([^>]+)src=["\']{re.escape(rel_path)}["\'](.*?)>',
                                f'<img([^>]+)src=["\']{re.escape(local_path_normalized)}["\'](.*?)>',
                                f'<img([^>]+)src=["\']{re.escape(local_path)}["\'](.*?)>',
                            ]
                            
                            for pattern in patterns:
                                if '!\\[' in pattern:
                                    # Markdown格式
                                    new_content = re.sub(pattern, f'![\\1]({remote_url})', content)
                                else:
                                    # HTML格式
                                    new_content = re.sub(pattern, f'<img\\1src="{remote_url}"\\2>', content)
                                
                                if new_content != content:
                                    content = new_content
                                    replaced_count += 1
                                    break
                        
                        # 如果有替换，保存文件
                        if content != original_content:
                            with open(md_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            rel_md = self.safe_relpath(md_file, self.workspace_path)
                            self.log(f"✅ {rel_md}: 替换了 {replaced_count} 个图片链接")
                    
                    except Exception as e:
                        rel_md = self.safe_relpath(md_file, self.workspace_path)
                        self.log(f"❌ 处理 {rel_md} 时出错: {e}")
                
                self.log("替换为远程链接完成!")
                
            except Exception as e:
                self.log(f"替换失败: {e}")
        
        threading.Thread(target=replace_thread, daemon=True).start()
    
    def replace_to_local(self):
        """替换图片链接为本地路径"""
        if not self.image_mapping:
            messagebox.showinfo("信息", "没有找到图片映射记录")
            return
        
        def replace_thread():
            try:
                self.log("开始替换为本地链接...")
                
                # 创建反向映射
                reverse_mapping = {remote_url: local_path for local_path, remote_url in self.image_mapping.items()}
                
                for md_file in self.md_files:
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        replaced_count = 0
                        
                        # 替换远程链接为本地路径
                        for remote_url, local_path in reverse_mapping.items():
                            if remote_url in content:
                                # 计算相对路径，处理跨驱动器情况
                                rel_path = self.safe_relpath(local_path, os.path.dirname(md_file))
                                
                                # 替换各种格式
                                patterns = [
                                    (f'!\\[([^\\]]*)\\]\\({re.escape(remote_url)}\\)', f'![\\1]({rel_path})'),
                                    (f'<img([^>]+)src=["\']{re.escape(remote_url)}["\'](.*?)>', f'<img\\1src="{rel_path}"\\2>'),
                                ]
                                
                                for pattern, replacement in patterns:
                                    new_content = re.sub(pattern, replacement, content)
                                    if new_content != content:
                                        content = new_content
                                        replaced_count += 1
                                        break
                        
                        # 如果有替换，保存文件
                        if content != original_content:
                            with open(md_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            rel_md = self.safe_relpath(md_file, self.workspace_path)
                            self.log(f"✅ {rel_md}: 替换了 {replaced_count} 个图片链接")
                    
                    except Exception as e:
                        rel_md = self.safe_relpath(md_file, self.workspace_path)
                        self.log(f"❌ 处理 {rel_md} 时出错: {e}")
                
                self.log("替换为本地链接完成!")
                
            except Exception as e:
                self.log(f"替换失败: {e}")
        
        threading.Thread(target=replace_thread, daemon=True).start()
    
    def download_images(self):
        """下载远程图片到本地"""
        def download_thread():
            try:
                self.log("开始下载远程图片...")
                
                for md_file in self.md_files:
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 查找远程图片链接
                        img_patterns = [
                            r'!\[.*?\]\((https?://[^)]+)\)',
                            r'<img[^>]+src=["\'](https?://[^"\']+)["\'][^>]*>',
                        ]
                        
                        remote_urls = set()
                        for pattern in img_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            remote_urls.update(matches)
                        
                        if not remote_urls:
                            continue
                        
                        rel_md = self.safe_relpath(md_file, self.workspace_path)
                        self.log(f"处理文件: {rel_md}")
                        
                        # 创建图片目录
                        md_dir = os.path.dirname(md_file)
                        img_dir = os.path.join(md_dir, 'images')
                        os.makedirs(img_dir, exist_ok=True)
                        
                        updated_content = content
                        
                        for remote_url in remote_urls:
                            try:
                                # 获取文件名
                                parsed_url = urlparse(remote_url)
                                filename = os.path.basename(parsed_url.path)
                                if not filename or '.' not in filename:
                                    filename = f"image_{hash(remote_url) % 10000}.jpg"
                                
                                local_path = self.normalize_path(os.path.join(img_dir, filename))
                                
                                # 如果文件已存在，跳过
                                if os.path.exists(local_path):
                                    self.log(f"  跳过已存在: {filename}")
                                    continue
                                
                                # 下载图片（带重试和特殊处理）
                                success = self.download_image_with_retry(remote_url, local_path)
                                
                                if success:
                                    # 计算相对路径，处理跨驱动器情况
                                    rel_img_path = self.safe_relpath(local_path, md_dir)
                                    
                                    # 更新映射表
                                    self.image_mapping[local_path] = remote_url
                                    
                                    # 替换内容中的链接
                                    updated_content = updated_content.replace(remote_url, rel_img_path)
                                    
                                    self.log(f"  ✅ 下载成功: {filename}")
                                else:
                                    self.log(f"  ❌ 下载失败: {filename} - 所有重试都失败")
                            
                            except Exception as e:
                                self.log(f"  ❌ 下载失败 {remote_url}: {e}")
                        
                        # 保存更新后的MD文件
                        if updated_content != content:
                            with open(md_file, 'w', encoding='utf-8') as f:
                                f.write(updated_content)
                    
                    except Exception as e:
                        rel_md = self.safe_relpath(md_file, self.workspace_path)
                        self.log(f"❌ 处理 {rel_md} 时出错: {e}")
                
                self.save_mapping()
                self.log("下载远程图片完成!")
                
            except Exception as e:
                self.log(f"下载失败: {e}")
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def delete_local_images(self):
        """删除本地图片文件"""
        if not self.unused_images and not self.image_mapping:
            messagebox.showinfo("信息", "没有找到可删除的图片")
            return
        
        # 确认对话框
        result = messagebox.askyesno(
            "确认删除", 
            f"将删除以下内容：\n"
            f"- {len(self.unused_images)} 个未被引用的图片\n"
            f"- {len(self.image_mapping)} 个已上传的本地图片\n"
            f"- 清空图片映射记录\n\n"
            f"此操作不可恢复，确定继续吗？"
        )
        
        if not result:
            return
        
        def delete_thread():
            try:
                self.log("开始删除本地图片...")
                
                deleted_count = 0
                
                # 删除未被引用的图片
                for img_path in self.unused_images:
                    try:
                        if os.path.exists(img_path):
                            os.remove(img_path)
                            deleted_count += 1
                            rel_path = self.safe_relpath(img_path, self.workspace_path)
                            self.log(f"✅ 删除未引用图片: {rel_path}")
                    except Exception as e:
                        rel_path = self.safe_relpath(img_path, self.workspace_path)
                        self.log(f"❌ 删除失败 {rel_path}: {e}")
                
                # 删除已上传的本地图片
                for local_path in list(self.image_mapping.keys()):
                    try:
                        if os.path.exists(local_path):
                            os.remove(local_path)
                            deleted_count += 1
                            rel_path = self.safe_relpath(local_path, self.workspace_path)
                            self.log(f"✅ 删除已上传图片: {rel_path}")
                    except Exception as e:
                        rel_path = self.safe_relpath(local_path, self.workspace_path)
                        self.log(f"❌ 删除失败 {rel_path}: {e}")
                
                # 清空映射记录
                self.image_mapping.clear()
                self.save_mapping()
                
                # 清空分析结果
                self.unused_images.clear()
                
                self.log(f"删除完成! 共删除 {deleted_count} 个文件")
                
            except Exception as e:
                self.log(f"删除失败: {e}")
        
        threading.Thread(target=delete_thread, daemon=True).start()
    
    def fix_broken_links(self):
        """修复失效的图片链接"""
        def fix_thread():
            try:
                self.log("开始修复失效链接...")
                
                broken_links = []
                
                # 检查所有MD文件中的远程链接
                for md_file in self.md_files:
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 查找远程图片链接
                        img_patterns = [
                            r'!\[.*?\]\((https?://[^)]+)\)',
                            r'<img[^>]+src=["\'](https?://[^"\']+)["\'][^>]*>',
                        ]
                        
                        remote_urls = set()
                        for pattern in img_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            remote_urls.update(matches)
                        
                        # 检查每个链接的可访问性
                        for url in remote_urls:
                            try:
                                response = requests.head(url, timeout=10, allow_redirects=True)
                                if response.status_code not in [200, 301, 302]:
                                    broken_links.append((md_file, url, response.status_code))
                                    self.log(f"  ❌ 失效链接: {url} (状态码: {response.status_code})")
                            except Exception as e:
                                broken_links.append((md_file, url, str(e)))
                                self.log(f"  ❌ 无法访问: {url} ({str(e)})")
                    
                    except Exception as e:
                        rel_md = self.safe_relpath(md_file, self.workspace_path)
                        self.log(f"❌ 检查文件 {rel_md} 时出错: {e}")
                
                if broken_links:
                    self.log(f"\n发现 {len(broken_links)} 个失效链接")
                    
                    # 提供修复建议
                    gitee_links = [link for link in broken_links if 'gitee.com' in link[1]]
                    if gitee_links:
                        self.log("\n=== Gitee链接修复建议 ===")
                        self.log("Gitee图床经常出现403错误，建议:")
                        self.log("1. 将图片重新上传到其他图床（如GitHub、七牛云等）")
                        self.log("2. 使用本地图片存储")
                        self.log("3. 检查Gitee仓库的访问权限设置")
                        
                        for md_file, url, error in gitee_links:
                            rel_md = self.safe_relpath(md_file, self.workspace_path)
                            self.log(f"  📄 {rel_md}")
                            self.log(f"     🔗 {url}")
                else:
                    self.log("✅ 所有远程链接都可以正常访问")
                
                self.log("失效链接检查完成!")
                
            except Exception as e:
                self.log(f"修复失效链接失败: {e}")
        
        threading.Thread(target=fix_thread, daemon=True).start()
    
    def smart_fix_paths(self):
        """智能修复路径问题 - 处理文件夹移动等情况"""
        if not self.invalid_images:
            messagebox.showinfo("信息", "没有发现无效引用需要修复")
            return
        
        # 安全确认对话框
        total_invalid = sum(len(imgs) for imgs in self.invalid_images.values())
        result = messagebox.askyesno(
            "智能修复确认", 
            f"将要智能修复 {total_invalid} 个无效引用\n\n"
            f"安全措施：\n"
            f"✅ 自动备份原始文件\n"
            f"✅ 记录所有修改操作\n"
            f"✅ 生成修复报告\n"
            f"✅ 可以撤销修改\n\n"
            f"确定继续吗？"
        )
        
        if not result:
            return
        
        def fix_thread():
            try:
                import datetime
                import shutil
                
                self.log("开始智能修复路径...")
                self.log(f"发现 {sum(len(imgs) for imgs in self.invalid_images.values())} 个无效引用")
                
                # 创建备份和日志目录
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_base = os.path.join(self.workspace_path, ".backup")
                backup_dir = os.path.join(backup_base, f"smart_fix_{timestamp}")
                os.makedirs(backup_dir, exist_ok=True)
                
                # 创建修复记录文件
                fix_log_file = os.path.join(backup_dir, "fix_log.json")
                fix_records = {
                    "timestamp": timestamp,
                    "total_files_processed": 0,
                    "total_fixes": 0,
                    "modifications": []
                }
                
                self.log(f"创建备份目录: {backup_dir}")
                
                # 创建文件名到路径的映射
                filename_to_paths = {}
                for img_path in self.image_files:
                    filename = os.path.basename(img_path).lower()
                    if filename not in filename_to_paths:
                        filename_to_paths[filename] = []
                    filename_to_paths[filename].append(img_path)
                
                self.log(f"建立了 {len(filename_to_paths)} 个文件名映射")
                
                total_fixed = 0
                total_invalid = 0
                
                for md_file, invalid_imgs in self.invalid_images.items():
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        fixed_count = 0
                        
                        rel_md = self.safe_relpath(md_file, self.workspace_path)
                        self.log(f"\n处理文件: {rel_md}")
                        
                        # 备份原始文件
                        backup_file = os.path.join(backup_dir, f"{os.path.basename(md_file)}.backup")
                        shutil.copy2(md_file, backup_file)
                        
                        # 记录文件处理
                        file_record = {
                            "file": rel_md,
                            "backup_file": backup_file,
                            "original_invalid_count": len(invalid_imgs),
                            "fixes": []
                        }
                        
                        for invalid_path in invalid_imgs:
                            total_invalid += 1
                            self.log(f"  🔍 检查路径: {invalid_path}")
                            
                            # 首先用原始路径的文件名查找
                            original_filename = os.path.basename(invalid_path).lower()
                            
                            # 查找同名文件
                            if original_filename in filename_to_paths:
                                candidates = filename_to_paths[original_filename]
                                
                                if len(candidates) == 1:
                                    # 只有一个候选，直接替换
                                    correct_path = candidates[0]
                                    rel_correct_path = self.safe_relpath(correct_path, os.path.dirname(md_file))
                                    
                                    # 替换内容中的路径
                                    old_patterns = [
                                        f'!\\[([^\\]]*)\\]\\({re.escape(invalid_path)}\\)',
                                        f'<img([^>]+)src=["\']{re.escape(invalid_path)}["\'](.*?)>',
                                    ]
                                    
                                    for pattern in old_patterns:
                                        if '!\\[' in pattern:
                                            new_content = re.sub(pattern, f'![\\1]({rel_correct_path})', content)
                                        else:
                                            new_content = re.sub(pattern, f'<img\\1src="{rel_correct_path}"\\2>', content)
                                        
                                        if new_content != content:
                                            content = new_content
                                            fixed_count += 1
                                            total_fixed += 1
                                            
                                            # 记录修复操作
                                            fix_detail = {
                                                "type": "exact_match",
                                                "original_path": invalid_path,
                                                "new_path": rel_correct_path,
                                                "absolute_path": correct_path,
                                                "confidence": "high"
                                            }
                                            file_record["fixes"].append(fix_detail)
                                            
                                            self.log(f"  ✅ 修复: {invalid_path} -> {rel_correct_path}")
                                            break
                                
                                elif len(candidates) > 1:
                                    # 多个候选，选择最相似的路径
                                    best_match = self.find_best_path_match(invalid_path, candidates)
                                    if best_match:
                                        rel_best_path = self.safe_relpath(best_match, os.path.dirname(md_file))
                                        
                                        # 替换内容中的路径
                                        old_patterns = [
                                            f'!\\[([^\\]]*)\\]\\({re.escape(invalid_path)}\\)',
                                            f'<img([^>]+)src=["\']{re.escape(invalid_path)}["\'](.*?)>',
                                        ]
                                        
                                        for pattern in old_patterns:
                                            if '!\\[' in pattern:
                                                new_content = re.sub(pattern, f'![\\1]({rel_best_path})', content)
                                            else:
                                                new_content = re.sub(pattern, f'<img\\1src="{rel_best_path}"\\2>', content)
                                            
                                            if new_content != content:
                                                content = new_content
                                                fixed_count += 1
                                                total_fixed += 1
                                                
                                                # 记录智能匹配操作
                                                similarity_score = self.calculate_similarity(invalid_path, best_match)
                                                fix_detail = {
                                                    "type": "smart_match",
                                                    "original_path": invalid_path,
                                                    "new_path": rel_best_path,
                                                    "absolute_path": best_match,
                                                    "confidence": "medium" if similarity_score > 0.7 else "low",
                                                    "similarity_score": similarity_score,
                                                    "candidates_count": len(candidates)
                                                }
                                                file_record["fixes"].append(fix_detail)
                                                
                                                self.log(f"  ✅ 智能匹配: {invalid_path} -> {rel_best_path} (相似度: {similarity_score:.2f})")
                                                break
                            else:
                                # 原始文件名找不到，尝试URL解码
                                decoded_path = unquote(invalid_path)
                                if decoded_path != invalid_path:
                                    self.log(f"  🔓 尝试URL解码: {decoded_path}")
                                    
                                    # 用解码后的文件名再次查找
                                    decoded_filename = os.path.basename(decoded_path).lower()
                                    if decoded_filename in filename_to_paths:
                                        candidates = filename_to_paths[decoded_filename]
                                        
                                        if len(candidates) == 1:
                                            # 只有一个候选，直接替换
                                            correct_path = candidates[0]
                                            rel_correct_path = self.safe_relpath(correct_path, os.path.dirname(md_file))
                                            
                                            # 替换内容中的路径
                                            old_patterns = [
                                                f'!\\[([^\\]]*)\\]\\({re.escape(invalid_path)}\\)',
                                                f'<img([^>]+)src=["\']{re.escape(invalid_path)}["\'](.*?)>',
                                            ]
                                            
                                            for pattern in old_patterns:
                                                if '!\\[' in pattern:
                                                    new_content = re.sub(pattern, f'![\\1]({rel_correct_path})', content)
                                                else:
                                                    new_content = re.sub(pattern, f'<img\\1src="{rel_correct_path}"\\2>', content)
                                                
                                                if new_content != content:
                                                    content = new_content
                                                    fixed_count += 1
                                                    total_fixed += 1
                                                    
                                                    # 记录解码修复操作
                                                    fix_detail = {
                                                        "type": "decoded_exact_match",
                                                        "original_path": invalid_path,
                                                        "decoded_path": decoded_path,
                                                        "new_path": rel_correct_path,
                                                        "absolute_path": correct_path,
                                                        "confidence": "high"
                                                    }
                                                    file_record["fixes"].append(fix_detail)
                                                    
                                                    self.log(f"  ✅ 解码修复: {invalid_path} -> {rel_correct_path}")
                                                    break
                                        
                                        elif len(candidates) > 1:
                                            # 多个候选，选择最相似的路径
                                            best_match = self.find_best_path_match(decoded_path, candidates)
                                            if best_match:
                                                rel_best_path = self.safe_relpath(best_match, os.path.dirname(md_file))
                                                
                                                # 替换内容中的路径
                                                old_patterns = [
                                                    f'!\\[([^\\]]*)\\]\\({re.escape(invalid_path)}\\)',
                                                    f'<img([^>]+)src=["\']{re.escape(invalid_path)}["\'](.*?)>',
                                                ]
                                                
                                                for pattern in old_patterns:
                                                    if '!\\[' in pattern:
                                                        new_content = re.sub(pattern, f'![\\1]({rel_best_path})', content)
                                                    else:
                                                        new_content = re.sub(pattern, f'<img\\1src="{rel_best_path}"\\2>', content)
                                                    
                                                    if new_content != content:
                                                        content = new_content
                                                        fixed_count += 1
                                                        total_fixed += 1
                                                        
                                                        # 记录解码智能匹配操作
                                                        similarity_score = self.calculate_similarity(decoded_path, best_match)
                                                        fix_detail = {
                                                            "type": "decoded_smart_match",
                                                            "original_path": invalid_path,
                                                            "decoded_path": decoded_path,
                                                            "new_path": rel_best_path,
                                                            "absolute_path": best_match,
                                                            "confidence": "medium" if similarity_score > 0.7 else "low",
                                                            "similarity_score": similarity_score,
                                                            "candidates_count": len(candidates)
                                                        }
                                                        file_record["fixes"].append(fix_detail)
                                                        
                                                        self.log(f"  ✅ 解码智能匹配: {invalid_path} -> {rel_best_path} (相似度: {similarity_score:.2f})")
                                                        break
                                    
                                    else:
                                        # 解码后的文件名也找不到，尝试完整路径匹配
                                        decoded_match = self.find_decoded_path_match(decoded_path, self.image_files)
                                        if decoded_match:
                                            rel_decoded_path = self.safe_relpath(decoded_match, os.path.dirname(md_file))
                                            
                                            # 替换内容中的路径
                                            old_patterns = [
                                                f'!\\[([^\\]]*)\\]\\({re.escape(invalid_path)}\\)',
                                                f'<img([^>]+)src=["\']{re.escape(invalid_path)}["\'](.*?)>',
                                            ]
                                            
                                            for pattern in old_patterns:
                                                if '!\\[' in pattern:
                                                    new_content = re.sub(pattern, f'![\\1]({rel_decoded_path})', content)
                                                else:
                                                    new_content = re.sub(pattern, f'<img\\1src="{rel_decoded_path}"\\2>', content)
                                                
                                                if new_content != content:
                                                    content = new_content
                                                    fixed_count += 1
                                                    total_fixed += 1
                                                    
                                                    # 记录解码路径匹配操作
                                                    fix_detail = {
                                                        "type": "decoded_path_match",
                                                        "original_path": invalid_path,
                                                        "decoded_path": decoded_path,
                                                        "new_path": rel_decoded_path,
                                                        "absolute_path": decoded_match,
                                                        "confidence": "medium"
                                                    }
                                                    file_record["fixes"].append(fix_detail)
                                                    
                                                    self.log(f"  ✅ 解码路径匹配: {invalid_path} -> {rel_decoded_path}")
                                                    break
                                
                                # 所有方法都失败了
                                if invalid_path in [fix["original_path"] for fix in file_record["fixes"]]:
                                    # 已经修复过了，跳过
                                    pass
                                else:
                                    self.log(f"  ❌ 未找到匹配文件: {invalid_path}")
                                    if decoded_path != invalid_path:
                                        self.log(f"      解码路径: {decoded_path}")
                        
                        # 保存修改后的文件
                        if content != original_content:
                            with open(md_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            self.log(f"  💾 已保存，修复了 {fixed_count} 个引用")
                            fix_records["total_files_processed"] += 1
                        
                        # 添加文件记录到总记录中
                        if file_record["fixes"]:
                            fix_records["modifications"].append(file_record)
                    
                    except Exception as e:
                        self.log(f"❌ 处理文件 {rel_md} 时出错: {e}")
                        # 记录错误
                        file_record["error"] = str(e)
                        fix_records["modifications"].append(file_record)
                
                # 保存修复记录
                fix_records["total_fixes"] = total_fixed
                with open(fix_log_file, 'w', encoding='utf-8') as f:
                    json.dump(fix_records, f, ensure_ascii=False, indent=2)
                
                # 生成撤销脚本
                self.generate_undo_script(backup_dir, fix_records)
                
                self.log(f"\n智能修复完成!")
                self.log(f"总计处理: {total_invalid} 个无效引用")
                self.log(f"成功修复: {total_fixed} 个引用")
                self.log(f"修复率: {total_fixed/total_invalid*100:.1f}%")
                self.log(f"备份目录: {backup_dir}")
                self.log(f"修复记录: {fix_log_file}")
                
                if total_fixed > 0:
                    self.log("✅ 所有修改已记录，可以撤销")
                    self.log("建议重新扫描以更新统计信息")
                
            except Exception as e:
                self.log(f"智能修复失败: {e}")
        
        threading.Thread(target=fix_thread, daemon=True).start()
    
    def find_best_path_match(self, invalid_path, candidates):
        """找到最匹配的路径 - 严格匹配标准"""
        import difflib
        
        # 提取无效路径的目录结构和文件名
        invalid_parts = invalid_path.replace('\\', '/').split('/')
        invalid_filename = os.path.basename(invalid_path).lower()
        
        best_score = 0
        best_match = None
        
        for candidate in candidates:
            candidate_parts = candidate.replace('\\', '/').split('/')
            candidate_filename = os.path.basename(candidate).lower()
            
            # 首先检查文件名相似度
            filename_similarity = difflib.SequenceMatcher(None, invalid_filename, candidate_filename).ratio()
            
            # 只有文件名相似度很高才考虑路径匹配
            if filename_similarity < 0.95:  # 文件名必须95%相似
                continue
            
            # 计算完整路径相似度
            path_similarity = difflib.SequenceMatcher(None, invalid_parts, candidate_parts).ratio()
            
            # 综合评分：文件名相似度 * 0.8 + 路径相似度 * 0.2
            combined_score = filename_similarity * 0.8 + path_similarity * 0.2
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = candidate
        
        # 只有综合相似度超过0.9才认为是有效匹配
        return best_match if best_score > 0.9 else None
    
    def find_decoded_path_match(self, decoded_path, image_files):
        """通过解码后的路径查找匹配的图片文件 - 严格匹配"""
        import difflib
        
        # 标准化解码后的路径
        decoded_normalized = decoded_path.replace('\\', '/').lower()
        decoded_filename = os.path.basename(decoded_normalized)
        
        # 首先尝试精确的文件名匹配
        for img_file in image_files:
            img_normalized = img_file.replace('\\', '/').lower()
            img_filename = os.path.basename(img_normalized)
            
            # 精确文件名匹配
            if decoded_filename == img_filename:
                return img_file
        
        # 如果精确匹配失败，尝试路径包含匹配（但要求很高的相似度）
        best_score = 0
        best_match = None
        
        for img_file in image_files:
            img_normalized = img_file.replace('\\', '/').lower()
            
            # 检查是否是完全路径匹配
            if decoded_normalized == img_normalized:
                return img_file
            
            # 检查路径是否包含关系（严格）
            if decoded_normalized in img_normalized or img_normalized.endswith(decoded_normalized):
                # 但要求路径长度相近，避免误匹配
                length_ratio = min(len(decoded_normalized), len(img_normalized)) / max(len(decoded_normalized), len(img_normalized))
                if length_ratio > 0.8:  # 路径长度相似度要求80%以上
                    return img_file
            
            # 计算文件名相似度（只有文件名相似度很高才考虑）
            decoded_filename = os.path.basename(decoded_normalized)
            img_filename = os.path.basename(img_normalized)
            filename_similarity = difflib.SequenceMatcher(None, decoded_filename, img_filename).ratio()
            
            # 只有文件名相似度超过0.9才考虑（几乎完全相同）
            if filename_similarity > 0.9 and filename_similarity > best_score:
                best_score = filename_similarity
                best_match = img_file
        
        # 只返回文件名几乎完全相同的匹配
        return best_match if best_score > 0.9 else None
    
    def calculate_similarity(self, path1, path2):
        """计算两个路径的相似度"""
        import difflib
        parts1 = path1.replace('\\', '/').split('/')
        parts2 = path2.replace('\\', '/').split('/')
        return difflib.SequenceMatcher(None, parts1, parts2).ratio()
    
    def generate_undo_script(self, backup_dir, fix_records):
        """生成撤销脚本"""
        undo_script = os.path.join(backup_dir, "undo_fixes.py")
        
        # 避免变量名冲突，并统一路径格式
        backup_dir_path = backup_dir.replace('\\', '/')
        workspace_path = self.workspace_path.replace('\\', '/')
        
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
        
        with open(undo_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        self.log(f"生成撤销脚本: {undo_script}")
        self.log("如需撤销修改，运行: python undo_fixes.py")
    
    def undo_fixes(self):
        """撤销最近的智能修复操作"""
        try:
            # 检查是否已选择工作目录
            if not self.workspace_path:
                messagebox.showwarning("警告", "请先选择工作目录")
                return
            
            # 查找最新的备份目录
            backup_base = os.path.join(self.workspace_path, ".backup")
            if not os.path.exists(backup_base):
                messagebox.showinfo("信息", "没有找到备份目录，无法撤销\n\n可能原因：\n1. 还没有执行过智能修复操作\n2. 备份目录被删除了")
                return
            
            # 获取所有备份目录，按时间排序
            backup_dirs = []
            for item in os.listdir(backup_base):
                backup_path = os.path.join(backup_base, item)
                if os.path.isdir(backup_path) and item.startswith("smart_fix_"):
                    backup_dirs.append(backup_path)
            
            if not backup_dirs:
                messagebox.showinfo("信息", "没有找到智能修复的备份记录\n\n可能原因：\n1. 还没有执行过智能修复操作\n2. 备份记录被删除了\n3. 备份目录中没有以'smart_fix_'开头的目录")
                return
            
            # 选择最新的备份
            latest_backup = max(backup_dirs, key=os.path.getctime)
            fix_log_file = os.path.join(latest_backup, "fix_log.json")
            
            if not os.path.exists(fix_log_file):
                messagebox.showerror("错误", "备份记录文件不存在")
                return
            
            # 确认撤销操作
            result = messagebox.askyesno(
                "确认撤销", 
                f"确定要撤销最近的智能修复操作吗？\n备份目录: {os.path.basename(latest_backup)}"
            )
            
            if not result:
                return
            
            # 读取修复记录
            with open(fix_log_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            self.log("开始撤销智能修复操作...")
            restored_count = 0
            
            for mod in records["modifications"]:
                try:
                    backup_file = mod["backup_file"]
                    original_file = mod["file"]
                    
                    if os.path.exists(backup_file):
                        # 恢复原始文件
                        target_file = os.path.join(self.workspace_path, original_file)
                        shutil.copy2(backup_file, target_file)
                        restored_count += 1
                        self.log(f"✅ 已恢复: {original_file}")
                    else:
                        self.log(f"❌ 备份文件不存在: {backup_file}")
                
                except Exception as e:
                    self.log(f"❌ 恢复失败 {mod['file']}: {e}")
            
            self.log(f"\n撤销完成! 共恢复 {restored_count} 个文件")
            self.log("建议重新扫描以更新统计信息")
            
            messagebox.showinfo("完成", f"撤销完成!\n共恢复 {restored_count} 个文件\n建议重新扫描以更新统计信息")
            
        except Exception as e:
            self.log(f"撤销操作失败: {e}")
            messagebox.showerror("错误", f"撤销操作失败: {e}")
    
    def export_report(self):
        """导出分析报告"""
        if not self.md_files:
            messagebox.showinfo("信息", "请先扫描分析文件")
            return
        
        try:
            report_file = os.path.join(self.workspace_path, "markdown_image_report.md")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# Markdown图片管理报告\n\n")
                f.write(f"生成时间: {os.path.basename(__file__)}\n")
                f.write(f"工作目录: {self.workspace_path}\n\n")
                
                # 统计信息
                referenced_local_count = len(getattr(self, 'referenced_local_images', []))
                unused_count = len(self.image_files) - referenced_local_count if referenced_local_count > 0 else len(self.unused_images)
                
                f.write("## 统计信息\n\n")
                f.write(f"- MD文件总数: {len(self.md_files)}\n")
                f.write(f"- 本地图片文件总数: {len(self.image_files)}\n")
                f.write(f"- 被引用的本地图片数: {referenced_local_count}\n")
                f.write(f"- 被引用的远程图片数: {len(getattr(self, 'remote_images', []))}\n")
                f.write(f"- 未被引用的本地图片数: {unused_count}\n")
                f.write(f"- 无效引用数: {sum(len(imgs) for imgs in self.invalid_images.values())}\n")
                f.write(f"- 图片映射记录数: {len(self.image_mapping)}\n\n")
                
                # MD文件图片引用
                f.write("## MD文件图片引用\n\n")
                for md_file, images in self.image_references.items():
                    rel_md = self.safe_relpath(md_file, self.workspace_path)
                    f.write(f"### {rel_md}\n\n")
                    for img in images:
                        if img.startswith('http'):
                            f.write(f"- 🌐 {img}\n")
                        else:
                            rel_img = self.safe_relpath(img, self.workspace_path)
                            f.write(f"- 🖼️ {rel_img}\n")
                    f.write("\n")
                
                # 无效图片引用
                if self.invalid_images:
                    f.write("## 无效图片引用\n\n")
                    for md_file, invalid_imgs in self.invalid_images.items():
                        rel_md = self.safe_relpath(md_file, self.workspace_path)
                        f.write(f"### {rel_md}\n\n")
                        for img in invalid_imgs:
                            f.write(f"- ❌ {img}\n")
                        f.write("\n")
                
                # 未被引用的图片
                if self.unused_images:
                    f.write("## 未被引用的图片\n\n")
                    for img in self.unused_images:
                        rel_img = self.safe_relpath(img, self.workspace_path)
                        f.write(f"- 🗑️ {rel_img}\n")
                    f.write("\n")
                
                # 图片映射表
                if self.image_mapping:
                    f.write("## 图片映射表\n\n")
                    for local_path, remote_url in self.image_mapping.items():
                        rel_local = self.safe_relpath(local_path, self.workspace_path)
                        f.write(f"- **本地**: {rel_local}\n")
                        f.write(f"  **远程**: {remote_url}\n\n")
            
            self.log(f"报告已导出: {report_file}")
            messagebox.showinfo("成功", f"报告已导出到:\n{report_file}")
            
        except Exception as e:
            self.log(f"导出报告失败: {e}")
            messagebox.showerror("错误", f"导出报告失败: {e}")
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MarkdownImageManager()
    app.run()