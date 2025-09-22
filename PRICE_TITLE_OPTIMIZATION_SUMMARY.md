# Price和Title地域优化总结

## 🎯 优化目标
优化`ProductInfo`中的`price`和`title`字段，让它们能够根据地域来选择对应的Excel列数据。

## 📋 字段映射规则

| 地域 | 价格字段 | 标题字段 | 说明 |
|------|----------|----------|------|
| **HK** (香港) | `HKPrice` | `ProductNameCn` | 香港使用中文标题 |
| **SG** (新加坡) | `SGPrice` | `ProductNameEn` | 新加坡使用英文标题 |
| **MY** (马来西亚) | `MYPrice` | `ProductNameEn` | 马来西亚使用英文标题 |

## 🔧 实现细节

### 1. Excel解析器优化 (`uploader/excel_parser.py`)

#### 新增方法：`_get_title_by_region()`
```python
def _get_title_by_region(self, product_data: Dict[str, Any]) -> str:
    """根据地域获取对应的商品标题"""
    region = product_data['region']
    
    if region == 'HK':
        # HK地域使用中文标题
        title = product_data['product_name_cn'] or product_data['product_name_en']
    elif region == 'SG':
        # SG地域使用英文标题
        title = product_data['product_name_en'] or product_data['product_name_cn']
    elif region == 'MY':
        # MY地域使用英文标题
        title = product_data['product_name_en'] or product_data['product_name_cn']
    else:
        # 默认使用英文标题
        title = product_data['product_name_en'] or product_data['product_name_cn']
    
    return title
```

#### 优化方法：`create_product_info()`
```python
# 根据地域选择商品名称
title = self._get_title_by_region(product_data)
```

### 2. 价格映射逻辑 (已存在)
```python
def _get_price_column(self, region: str) -> str:
    """根据地域获取对应的价格列名"""
    price_mapping = {
        'HK': 'HKPrice',
        'MY': 'MYPrice', 
        'SG': 'SGPrice'
    }
    return price_mapping[region]
```

## 🚀 使用方式

### 多账号上传模式
```python
# 系统会自动根据地域选择对应的字段
uploader = CarousellUploader(page, config, "HK")  # 使用香港地域

# 创建ProductInfo时会自动选择：
# - 价格: HKPrice列的数据
# - 标题: ProductNameCn列的数据
product_info = parser.create_product_info(product_data)
```

### 字段选择逻辑
```python
# 价格选择
if region == 'HK':
    price = row['HKPrice']
elif region == 'SG':
    price = row['SGPrice']
elif region == 'MY':
    price = row['MYPrice']

# 标题选择
if region == 'HK':
    title = row['ProductNameCn']  # 中文标题
else:  # SG, MY
    title = row['ProductNameEn']  # 英文标题
```

## 📊 优化效果

### 优化前：
- 所有地域使用相同的字段选择逻辑
- 标题选择不够灵活

### 优化后：
- 根据地域智能选择对应的价格字段
- 根据地域智能选择对应的标题字段
- 支持中文/英文标题的地域化选择

## 🛡️ 容错机制

- 如果主要字段为空，会自动回退到备用字段
- 例如：HK地域优先使用`ProductNameCn`，如果为空则使用`ProductNameEn`
- 保持向后兼容，现有代码无需修改

## ✅ 验证结果

### 测试数据示例：
```python
# Excel数据
{
    'ProductNameCn': '测试商品中文',
    'ProductNameEn': 'Test Product English',
    'HKPrice': '100',
    'SGPrice': '120',
    'MYPrice': '90'
}
```

### 测试结果：
- ✅ HK地域: 价格=100 (HKPrice), 标题="测试商品中文" (ProductNameCn)
- ✅ SG地域: 价格=120 (SGPrice), 标题="Test Product English" (ProductNameEn)
- ✅ MY地域: 价格=90 (MYPrice), 标题="Test Product English" (ProductNameEn)

## 🎉 总结

Price和Title地域优化已完成，现在系统支持：

1. **智能价格选择**: 根据地域自动选择对应的价格字段
2. **智能标题选择**: 根据地域自动选择对应的标题字段
3. **地域化内容**: HK使用中文标题，SG/MY使用英文标题
4. **完善容错**: 主字段为空时自动回退到备用字段
5. **向后兼容**: 现有代码无需修改即可正常工作

为多地域Carousell平台的内容本地化提供了强大的支持！🌍
