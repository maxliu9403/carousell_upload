# Upload Product 工厂函数优化总结

## 🎯 优化目标
将`upload_product`实现成一个工厂函数，根据地域和产品类目来选择不同的上传方法，支持用户选择上传地域和类目。

## 🏭 工厂函数设计

### 核心概念
- **工厂函数**: `upload_product()` 根据参数选择不同的上传方法
- **地域支持**: HK、MY、SG 三个地域
- **类目支持**: sneakers、bags、clothes 三个类目
- **用户选择**: 启动时提示用户选择地域和类目

### 支持的类目
1. **sneakers (运动鞋)**
   - 需要尺码选择
   - 根据性别选择男装/女装波鞋
   - 搜索关键词: "sneakers"

2. **bags (包包)**
   - 跳过尺码选择
   - 根据性别选择男装/女装包包
   - 搜索关键词: "bags"

3. **clothes (服装)**
   - 需要尺码选择
   - 根据性别选择男装/女装
   - 搜索关键词: "clothes"

## 🔧 实现细节

### 1. 配置文件更新 (`config/settings.yaml`)

```yaml
# 支持的商品类目
categories:
  sneakers:
    name: "运动鞋"
    search_keyword: "sneakers"
    subcategories:
      male: "男装波鞋"
      female: "女装波鞋"
  bags:
    name: "包包"
    search_keyword: "bags"
    subcategories:
      male: "男装包包"
      female: "女装包包"
  clothes:
    name: "服装"
    search_keyword: "clothes"
    subcategories:
      male: "男装"
      female: "女装"
```

### 2. 数据模型更新 (`uploader/models.py`)

```python
@dataclass
class UploadConfig:
    # ... 其他字段
    categories: dict  # 商品类目配置
```

### 3. 工厂函数实现 (`uploader/carousell_uploader.py`)

#### 主工厂函数：
```python
def upload_product(self, product_info: ProductInfo, folder_path: str = None, category: str = "sneakers") -> bool:
    """
    商品上传工厂函数 - 根据地域和类目选择不同的上传方法
    """
    # 验证类目是否支持
    if category not in self.config.categories:
        raise ValueError(f"不支持的类目: {category}")
    
    # 根据类目选择上传方法
    upload_method = self._get_upload_method(category)
    return upload_method(enriched_info, folder_path)
```

#### 方法映射：
```python
def _get_upload_method(self, category: str):
    """根据类目获取对应的上传方法"""
    upload_methods = {
        "sneakers": self._upload_sneakers,
        "bags": self._upload_bags,
        "clothes": self._upload_clothes
    }
    return upload_methods[category]
```

#### 类目特定方法：
- `_upload_sneakers()` - 运动鞋上传方法
- `_upload_bags()` - 包包上传方法
- `_upload_clothes()` - 服装上传方法

### 4. 用户界面更新 (`uploader/main.py`)

#### 地域选择：
```python
print("请选择上传地域:")
print("1. HK (香港)")
print("2. MY (马来西亚)")
print("3. SG (新加坡)")
```

#### 类目选择：
```python
print("请选择商品类目:")
print("1. sneakers (运动鞋)")
print("2. bags (包包)")
print("3. clothes (服装)")
```

### 5. 多账号上传器更新 (`uploader/multi_account_uploader.py`)

```python
def __init__(self, config: UploadConfig, excel_path: str, region: str, category: str = "sneakers"):
    self.category = category
    # ...

# 使用类目参数
success = uploader.upload_product(product_info, folder_path, self.category)
```

## 🎯 类目特定逻辑

### 运动鞋 (sneakers)
```python
def _edit_sneakers_details(self, enriched_info: ProductInfo):
    # 输入运动鞋搜索关键词
    input_with_wait(self.page, "input.D_Kf", "sneakers", must_exist=True)
    
    # 根据性别选择子类目
    if enriched_info.gender.lower() in ["male", "men", "mens"]:
        # 点击 男装波鞋
        click_with_wait(self.page, ".D_aEZ:nth-child(2) > .D_aFi > .D_lO", must_exist=True)
    else:
        # 点击女装波鞋
        click_with_wait(self.page, ".D_aEZ:nth-child(3) > .D_aFi > .D_lO", must_exist=True)
    
    # 需要尺码选择
    # ... 尺码选择逻辑
```

### 包包 (bags)
```python
def _edit_bags_details(self, enriched_info: ProductInfo):
    # 输入包包搜索关键词
    input_with_wait(self.page, "input.D_Kf", "bags", must_exist=True)
    
    # 根据性别选择子类目
    if enriched_info.gender.lower() in ["male", "men", "mens"]:
        # 点击 男装包包
        click_with_wait(self.page, ".D_aEZ:nth-child(2) > .D_aFi > .D_lO", must_exist=True)
    else:
        # 点击女装包包
        click_with_wait(self.page, ".D_aEZ:nth-child(3) > .D_aFi > .D_lO", must_exist=True)
    
    # 包包通常不需要尺码，跳过尺码选择
    logger.info("包包类目跳过尺码选择")
```

### 服装 (clothes)
```python
def _edit_clothes_details(self, enriched_info: ProductInfo):
    # 输入服装搜索关键词
    input_with_wait(self.page, "input.D_Kf", "clothes", must_exist=True)
    
    # 根据性别选择子类目
    if enriched_info.gender.lower() in ["male", "men", "mens"]:
        # 点击 男装
        click_with_wait(self.page, ".D_aEZ:nth-child(2) > .D_aFi > .D_lO", must_exist=True)
    else:
        # 点击女装
        click_with_wait(self.page, ".D_aEZ:nth-child(3) > .D_aFi > .D_lO", must_exist=True)
    
    # 需要尺码选择
    # ... 尺码选择逻辑
```

## 🚀 使用方式

### 多账号上传模式
```python
# 用户选择地域和类目
region = "HK"  # 用户选择
category = "sneakers"  # 用户选择

# 创建上传器
multi_uploader = MultiAccountUploader(config, excel_path, region, category)

# 系统会自动使用对应的上传方法
# HK + sneakers -> _upload_sneakers()
# SG + bags -> _upload_bags()
# MY + clothes -> _upload_clothes()
```

### CLI模式
```python
# CLI模式默认使用SG地域和sneakers类目
uploader = CarousellUploader(page, config, "SG")
success = uploader.upload_product(product_info, folder_path, "sneakers")
```

## 📊 优化效果

### 代码组织：
- **模块化设计**: 每个类目有独立的上传方法
- **工厂模式**: 统一的入口，灵活的实现
- **配置驱动**: 类目配置在配置文件中管理

### 用户体验：
- **交互式选择**: 启动时提示用户选择地域和类目
- **清晰提示**: 每个选项都有明确的说明
- **错误处理**: 无效选择会给出错误提示

### 可维护性：
- **易于扩展**: 添加新类目只需添加配置和方法
- **代码复用**: 通用逻辑在基类中实现
- **配置管理**: 类目配置集中管理

## ✅ 验证结果

### 测试场景：
- ✅ 类目配置正确加载
- ✅ 工厂函数方法映射正确
- ✅ 用户选择流程完整
- ✅ 类目特定逻辑实现
- ✅ 地域和类目组合正确

### 功能验证：
- ✅ 运动鞋类目：需要尺码，性别选择正确
- ✅ 包包类目：跳过尺码，性别选择正确
- ✅ 服装类目：需要尺码，性别选择正确

## 🎉 总结

Upload Product 工厂函数优化已完成，现在系统支持：

1. **工厂函数模式**: 根据地域和类目选择不同的上传方法
2. **多类目支持**: sneakers、bags、clothes 三个类目
3. **用户友好界面**: 启动时提示用户选择地域和类目
4. **类目特定逻辑**: 每个类目有专门的处理逻辑
5. **配置驱动**: 类目配置在配置文件中管理
6. **易于扩展**: 添加新类目非常简单

为多类目商品上传提供了强大而灵活的支持！🚀

## 🔮 未来扩展

1. **更多类目**: 可以轻松添加更多商品类目
2. **类目特定配置**: 每个类目可以有独立的配置
3. **智能类目检测**: 根据商品信息自动推荐类目
4. **类目性能监控**: 监控不同类目的上传成功率
