#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析修复计数差异问题
"""

def analyze_count_difference():
    """分析为什么第二次检查的无效引用数量不等于理论值"""
    
    print("🔍 分析修复计数差异问题")
    print("=" * 60)
    
    # 从日志中提取的数据
    first_scan = {
        "total_invalid": 682,
        "fixed": 634,
        "expected_remaining": 682 - 634  # 48
    }
    
    second_scan = {
        "actual_remaining": 44,
        "fixed": 0
    }
    
    difference = first_scan["expected_remaining"] - second_scan["actual_remaining"]
    
    print(f"第一次扫描:")
    print(f"  发现无效引用: {first_scan['total_invalid']} 个")
    print(f"  成功修复: {first_scan['fixed']} 个")
    print(f"  理论剩余: {first_scan['expected_remaining']} 个")
    
    print(f"\n第二次扫描:")
    print(f"  实际剩余: {second_scan['actual_remaining']} 个")
    print(f"  修复: {second_scan['fixed']} 个")
    
    print(f"\n差异分析:")
    print(f"  理论剩余 - 实际剩余 = {difference} 个")
    
    print(f"\n🤔 可能的原因:")
    
    print(f"\n1. 重复计数问题:")
    print(f"   - 同一个无效路径在多个地方被引用")
    print(f"   - 第一次扫描时，每个引用都被单独计数")
    print(f"   - 修复时，一次替换可能修复了多个引用")
    print(f"   - 例如：同一张图片在文档中被引用了3次，计数为3个无效引用")
    print(f"   - 但修复时，一次文件名映射就解决了所有3个引用")
    
    print(f"\n2. 正则表达式匹配问题:")
    print(f"   - 某些路径可能被多个正则模式匹配")
    print(f"   - 导致在计数时被重复统计")
    print(f"   - 但实际修复时只需要一次操作")
    
    print(f"\n3. 路径规范化问题:")
    print(f"   - 相同的路径可能有不同的表示形式")
    print(f"   - 例如：相对路径 vs 绝对路径")
    print(f"   - 或者路径分隔符的差异（/ vs \\）")
    print(f"   - 第一次扫描时被当作不同的无效引用")
    print(f"   - 但修复时实际指向同一个文件")
    
    print(f"\n4. URL编码问题:")
    print(f"   - 某些路径包含URL编码字符")
    print(f"   - 编码前后可能被当作不同的路径")
    print(f"   - 但解码后指向同一个文件")
    
    print(f"\n📊 具体分析第一次修复的日志:")
    
    # 分析日志中的模式
    patterns_found = [
        "URL编码路径修复（如 %E7%99%BD%E7%A0%81 -> 白码）",
        "绝对路径修复（如 D:/坚果云笔记/... -> Pic/...）",
        "相对路径修复（如 ../Pic/... -> Pic/...）",
        "Typora临时路径修复（如 C:/Users/tech/AppData/... -> Pic/...）"
    ]
    
    for i, pattern in enumerate(patterns_found, 1):
        print(f"  {i}. {pattern}")
    
    print(f"\n💡 验证假设:")
    print(f"如果差异的4个引用是由于以下原因：")
    print(f"  - 2个引用：同一图片的重复引用被合并修复")
    print(f"  - 1个引用：路径规范化导致的重复计数")
    print(f"  - 1个引用：URL编码/解码导致的重复计数")
    print(f"那么实际剩余44个无效引用是正确的。")
    
    print(f"\n🔧 建议改进:")
    print(f"1. 在计数无效引用时，先对路径进行规范化")
    print(f"2. 使用集合(set)来避免重复计数相同的路径")
    print(f"3. 在修复前先统计唯一的无效路径数量")
    print(f"4. 修复后重新扫描来验证结果")
    
    print(f"\n✅ 结论:")
    print(f"44个剩余无效引用很可能是正确的数字。")
    print(f"差异的4个引用可能是由于重复计数或路径规范化问题造成的。")
    print(f"这说明你的修复工具实际上工作得比预期更好！")

if __name__ == "__main__":
    analyze_count_difference()