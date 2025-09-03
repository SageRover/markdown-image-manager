#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查代码重复问题
"""

import ast
import os

def find_duplicate_functions(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f'语法错误: {e}')
        return
    
    class FunctionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.functions = []
            self.scope_stack = []
        
        def visit_FunctionDef(self, node):
            scope = '.'.join(self.scope_stack) if self.scope_stack else 'global'
            full_name = f'{scope}.{node.name}' if scope != 'global' else node.name
            self.functions.append({
                'name': node.name,
                'full_name': full_name,
                'line': node.lineno,
                'scope': scope
            })
            
            # 进入函数作用域
            self.scope_stack.append(node.name)
            self.generic_visit(node)
            self.scope_stack.pop()
        
        def visit_ClassDef(self, node):
            # 进入类作用域
            self.scope_stack.append(node.name)
            self.generic_visit(node)
            self.scope_stack.pop()
    
    visitor = FunctionVisitor()
    visitor.visit(tree)
    
    # 按函数名分组
    function_groups = {}
    for func in visitor.functions:
        name = func['name']
        if name not in function_groups:
            function_groups[name] = []
        function_groups[name].append(func)
    
    print('函数定义分析:')
    duplicates_found = False
    
    for name, funcs in function_groups.items():
        if len(funcs) > 1:
            print(f'\n函数名 "{name}" 出现 {len(funcs)} 次:')
            for func in funcs:
                print(f'  行 {func["line"]}: {func["full_name"]} (作用域: {func["scope"]})')
            
            # 检查是否是真正的重复（同一作用域）
            scopes = [f['scope'] for f in funcs]
            if len(set(scopes)) < len(scopes):
                print(f'  ⚠️  警告: 在相同作用域中发现重复定义!')
                duplicates_found = True
            else:
                print(f'  ✅ 正常: 不同作用域中的同名函数')
    
    if not duplicates_found:
        print('\n✅ 没有发现真正的重复函数定义')
    
    return duplicates_found

if __name__ == "__main__":
    find_duplicate_functions('markdown_image_manager.py')