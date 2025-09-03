#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gitee图片链接修复工具
专门处理Gitee图床的403 Forbidden问题
"""

import re
import requests
import os
from urllib.parse import urlparse

class GiteeImageFixer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://gitee.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def fix_gitee_url(self, url):
        """修复Gitee URL的常见问题"""
        fixes = []
        
        # 1. 修复双斜杠问题
        if '//img/' in url:
            fixed_url = url.replace('//img/', '/img/')
            fixes.append(('双斜杠修复', fixed_url))
        
        # 2. 尝试不同的分支名
        if '/raw/master/' in url:
            fixed_url = url.replace('/raw/master/', '/raw/main/')
            fixes.append(('主分支修复', fixed_url))
        
        # 3. 去掉raw参数
        if '/raw/' in url:
            fixed_url = url.replace('/raw/master/', '/master/').replace('/raw/main/', '/main/')
            fixes.append(('去掉raw', fixed_url))
        
        # 4. 使用CDN加速
        if 'gitee.com' in url:
            cdn_url = url.replace('gitee.com', 'gitee.io')
            fixes.append(('CDN加速', cdn_url))
        
        return fixes
    
    def test_url(self, url):
        """测试URL是否可访问"""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def find_working_url(self, original_url):
        """找到可用的URL"""
        # 首先测试原始URL
        if self.test_url(original_url):
            return original_url
        
        # 尝试各种修复方案
        fixes = self.fix_gitee_url(original_url)
        for fix_name, fixed_url in fixes:
            if self.test_url(fixed_url):
                return fixed_url
        
        return None
    
    def download_image(self, url, local_path):
        """下载图片"""
        working_url = self.find_working_url(url)
        if not working_url:
            return False, "找不到可用的URL"
        
        try:
            response = self.session.get(working_url, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return True, f"成功下载: {working_url}"
        except Exception as e:
            return False, str(e)

def main():
    """命令行工具"""
    import sys
    
    if len(sys.argv) != 3:
        print("用法: python gitee_image_fixer.py <gitee_url> <local_path>")
        return
    
    url = sys.argv[1]
    local_path = sys.argv[2]
    
    fixer = GiteeImageFixer()
    success, message = fixer.download_image(url, local_path)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ 下载失败: {message}")

if __name__ == "__main__":
    main()