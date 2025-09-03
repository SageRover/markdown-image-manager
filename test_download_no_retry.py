#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试下载功能不重试的修改效果
"""

import time
import tempfile
import os

def test_download_behavior():
    """测试下载行为"""
    
    print("🧪 测试下载功能修改效果")
    print("=" * 50)
    
    # 模拟修改后的下载函数
    def download_image_no_retry(url, local_path, max_retries=1):
        """模拟修改后的下载函数"""
        import requests
        
        print(f"📥 开始下载: {url}")
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                print(f"    下载: {os.path.basename(local_path)}")
                
                # 模拟网络请求
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    
                    end_time = time.time()
                    print(f"    ✅ 下载成功 ({end_time - start_time:.2f}秒)")
                    return True
                else:
                    print(f"    ❌ HTTP {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"    ❌ 下载超时")
            except requests.exceptions.ConnectionError:
                print(f"    ❌ 连接错误")
            except Exception as e:
                print(f"    ❌ 下载错误: {str(e)}")
            
            # 不重试，直接退出循环
            break
        
        end_time = time.time()
        print(f"    ❌ 下载失败 ({end_time - start_time:.2f}秒)")
        return False
    
    # 测试用例
    test_cases = [
        {
            "name": "有效图片URL",
            "url": "https://httpbin.org/image/png",
            "expected": "成功"
        },
        {
            "name": "无效URL",
            "url": "https://httpbin.org/status/404",
            "expected": "失败"
        },
        {
            "name": "超时URL",
            "url": "https://httpbin.org/delay/15",  # 15秒延迟，会超时
            "expected": "超时"
        }
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 测试目录: {temp_dir}")
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{i}. 测试 {case['name']}")
            print(f"   URL: {case['url']}")
            print(f"   预期: {case['expected']}")
            
            local_path = os.path.join(temp_dir, f"test_{i}.png")
            
            # 记录开始时间
            test_start = time.time()
            
            # 执行下载测试
            try:
                success = download_image_no_retry(case['url'], local_path)
                test_end = time.time()
                
                print(f"   结果: {'成功' if success else '失败'}")
                print(f"   耗时: {test_end - test_start:.2f}秒")
                
                # 检查文件是否存在
                if success and os.path.exists(local_path):
                    file_size = os.path.getsize(local_path)
                    print(f"   文件大小: {file_size} 字节")
                
            except Exception as e:
                test_end = time.time()
                print(f"   异常: {e}")
                print(f"   耗时: {test_end - test_start:.2f}秒")

def compare_old_vs_new():
    """对比修改前后的行为"""
    
    print(f"\n📊 修改前后对比")
    print("=" * 50)
    
    print("修改前 (max_retries=3):")
    print("  - 失败时会重试3次")
    print("  - 每次重试间隔: 1秒, 2秒, 4秒 (指数退避)")
    print("  - 总耗时: 可能超过30秒")
    print("  - 日志: '尝试下载 (第1次)', '尝试下载 (第2次)', ...")
    
    print("\n修改后 (max_retries=1):")
    print("  - 只尝试1次，不重试")
    print("  - 无重试间隔")
    print("  - 总耗时: 最多10-30秒 (取决于timeout)")
    print("  - 日志: '下载: filename.png'")
    
    print("\n🎯 优势:")
    print("  ✅ 更快的失败反馈")
    print("  ✅ 减少不必要的网络请求")
    print("  ✅ 降低服务器压力")
    print("  ✅ 更简洁的日志输出")
    print("  ✅ 更好的用户体验")

def simulate_batch_download():
    """模拟批量下载场景"""
    
    print(f"\n🚀 批量下载场景模拟")
    print("=" * 50)
    
    # 模拟100个图片的下载场景
    total_images = 100
    failed_images = 20  # 假设20个失败
    
    print(f"场景: 下载 {total_images} 个图片，其中 {failed_images} 个失败")
    
    # 修改前的时间计算
    success_time_old = (total_images - failed_images) * 2  # 成功的平均2秒
    failed_time_old = failed_images * 15  # 失败的平均15秒 (3次重试)
    total_time_old = success_time_old + failed_time_old
    
    # 修改后的时间计算  
    success_time_new = (total_images - failed_images) * 2  # 成功的平均2秒
    failed_time_new = failed_images * 5  # 失败的平均5秒 (1次尝试)
    total_time_new = success_time_new + failed_time_new
    
    print(f"\n修改前:")
    print(f"  成功图片耗时: {success_time_old} 秒")
    print(f"  失败图片耗时: {failed_time_old} 秒")
    print(f"  总耗时: {total_time_old} 秒 ({total_time_old/60:.1f} 分钟)")
    
    print(f"\n修改后:")
    print(f"  成功图片耗时: {success_time_new} 秒")
    print(f"  失败图片耗时: {failed_time_new} 秒")
    print(f"  总耗时: {total_time_new} 秒 ({total_time_new/60:.1f} 分钟)")
    
    time_saved = total_time_old - total_time_new
    print(f"\n💰 节省时间: {time_saved} 秒 ({time_saved/60:.1f} 分钟)")
    print(f"📈 效率提升: {(time_saved/total_time_old)*100:.1f}%")

if __name__ == "__main__":
    test_download_behavior()
    compare_old_vs_new()
    simulate_batch_download()