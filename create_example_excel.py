#!/usr/bin/env python3
"""
创建示例 Excel 文件的脚本
"""

import pandas as pd
import os

def create_example_excel():
    """创建示例 Excel 文件"""
    
    # 创建示例数据
    data = {
        'URL': [
            'https://example.com/product1', 
            'https://example.com/product2', 
            'https://example.com/product3',
            'https://example.com/product4',
            'https://example.com/product5'
        ],
        'SKU': 'SKU1',
        'BrowserID': ['1', '2', '1', '3', '2'],
        'ProductNameCn': [
            '耐克运动鞋', 
            '阿迪达斯跑鞋', 
            '新百伦休闲鞋',
            '匡威帆布鞋',
            '彪马运动鞋'
        ],
        'ProductNameEn': [
            'Nike Sneakers', 
            'Adidas Running Shoes', 
            'New Balance Casual Shoes',
            'Converse Canvas Shoes',
            'Puma Sports Shoes'
        ],
        'GenderCn': ['男', '女', '男', '女', '男'],
        'GenderEn': ['Male', 'Female', 'Male', 'Female', 'Male'],
        'HKPrice': ['500', '600', '450', '350', '400'],
        'SGPrice': ['80', '95', '70', '55', '65'],
        'MYPrice': ['250', '300', '220', '180', '200'],
        'Brand': ['Nike', 'Adidas', 'New Balance', 'Converse', 'Puma'],
        'folder': [
            '/Users/liuxiang/Desktop/nike_images',
            '/Users/liuxiang/Desktop/adidas_images', 
            '/Users/liuxiang/Desktop/nb_images',
            '/Users/liuxiang/Desktop/converse_images',
            '/Users/liuxiang/Desktop/puma_images'
        ]
    }
    
    # 创建 DataFrame
    df = pd.DataFrame(data)
    
    # 保存为 Excel 文件
    excel_path = 'example_products.xlsx'
    df.to_excel(excel_path, index=False)
    
    print(f"✅ 示例 Excel 文件已创建: {excel_path}")
    print("\n文件内容预览:")
    print(df.to_string(index=False))
    
    print(f"\n📋 Excel 文件列说明:")
    print("A列 = URL: 商品链接")
    print("B列 = SKU: 商品SKU")
    print("C列 = BrowserID: 浏览器ID")
    print("D列 = ProductNameCn: 中文商品名称")
    print("E列 = ProductNameEn: 英文商品名称")
    print("F列 = GenderCn: 中文性别")
    print("G列 = GenderEn: 英文性别")
    print("H列 = HKPrice: 香港价格")
    print("I列 = SGPrice: 新加坡价格")
    print("J列 = MYPrice: 马来西亚价格")
    print("K列 = Brand: 品牌")
    print("L列 = folder: 图片文件夹路径")

if __name__ == "__main__":
    create_example_excel()
