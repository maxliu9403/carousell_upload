"""
图片匹配点击器 - 基于OpenCV的图像识别和点击
专门用于处理AI文案相关按钮
"""

import os
import cv2
import numpy as np
import time
from pathlib import Path
from typing import Optional, Tuple, List
from playwright.sync_api import Page
from core.logger import logger
from browser.actions import human_delay


class ImageClicker:
    """图片匹配点击器"""
    
    def __init__(self, page: Page, templates_dir: str = "templates", threshold_delay: float = 1.0):
        """
        初始化图片匹配点击器
        
        Args:
            page: Playwright页面对象
            templates_dir: 图片模板目录
            threshold_delay: 阈值切换延迟时间（秒）
        """
        self.page = page
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        self.threshold_delay = threshold_delay
        
        # 创建AI文案模板目录
        self.ai_templates_dir = self.templates_dir / "ai_writing"
        self.ai_templates_dir.mkdir(exist_ok=True)
        
        logger.info(f"图片匹配点击器初始化完成，模板目录: {self.templates_dir}, 阈值延迟: {self.threshold_delay}秒")
    
    def capture_page_screenshot(self, filename: str = None) -> str:
        """
        截取页面截图
        
        Args:
            filename: 截图文件名
            
        Returns:
            str: 截图文件路径
        """
        if filename is None:
            filename = f"screenshot_{int(time.time())}.png"
        
        screenshot_path = self.templates_dir / filename
        self.page.screenshot(path=str(screenshot_path), full_page=True)
        
        logger.debug(f"页面截图已保存: {screenshot_path}")
        return str(screenshot_path)
    
    def find_image_on_page(self, template_path: str, threshold: float = 0.8) -> Optional[Tuple[int, int, int, int]]:
        """
        在页面截图中查找模板图片
        
        Args:
            template_path: 模板图片路径
            threshold: 匹配阈值 (0-1)
            
        Returns:
            Optional[Tuple[int, int, int, int]]: 找到的位置 (x, y, width, height)
        """
        try:
            # 截取页面截图
            screenshot_path = self.capture_page_screenshot()
            
            # 读取截图和模板
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)
            
            if screenshot is None:
                logger.error(f"无法读取截图: {screenshot_path}")
                return None
            
            if template is None:
                logger.error(f"无法读取模板: {template_path}")
                return None
            
            # 模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            
            # 找到最佳匹配位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                # 计算实际位置
                template_h, template_w = template.shape[:2]
                x = max_loc[0]
                y = max_loc[1]
                
                logger.info(f"找到匹配图片: {template_path}, 置信度: {max_val:.3f}, 位置: ({x}, {y})")
                return (x, y, template_w, template_h)
            else:
                logger.debug(f"未找到匹配图片: {template_path}, 最高置信度: {max_val:.3f}")
                return None
                
        except Exception as e:
            logger.error(f"图片匹配失败: {template_path}, 错误: {e}")
            return None
    
    def click_image(self, template_path: str, threshold: float = 0.8) -> bool:
        """
        点击图片匹配的位置
        
        Args:
            template_path: 模板图片路径
            threshold: 匹配阈值
            
        Returns:
            bool: 是否成功点击
        """
        try:
            # 查找图片位置
            match_result = self.find_image_on_page(template_path, threshold)
            
            if match_result:
                x, y, w, h = match_result
                
                # 智能选择点击位置
                click_x, click_y = self._find_smart_click_position(x, y, w, h)
                
                logger.info(f"点击图片位置: ({click_x}, {click_y})")
                
                # 执行点击
                self.page.mouse.click(click_x, click_y)
                human_delay(0.5, 1.0)
                
                logger.info(f"成功点击图片: {template_path}")
                return True
            else:
                logger.info(f"未找到可点击的图片: {template_path}")
                return False
                
        except Exception as e:
            logger.error(f"点击图片失败: {template_path}, 错误: {e}")
            return False
    
    def click_ai_writing_button(self, region: str = "all") -> bool:
        """
        点击AI文案相关按钮
        
        Args:
            region: 地域 (HK, SG, all)
            
        Returns:
            bool: 是否成功点击
        """
        try:
            logger.info(f"开始查找AI文案按钮 (地域: {region})")
            
            # 获取模板列表
            templates = self._get_ai_templates(region)
            
            if not templates:
                logger.warning("没有找到AI文案模板")
                return False
            
            # 尝试不同的阈值
            thresholds = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3]
            for i, threshold in enumerate(thresholds):
                logger.info(f"尝试匹配阈值: {threshold}")
                
                # 按优先级尝试模板
                for template_path in templates:
                    logger.info(f"尝试模板: {Path(template_path).name}")
                    
                    if self.click_image(template_path, threshold):
                        logger.info(f"成功点击AI文案按钮: {Path(template_path).name}")
                        return True
                    else:
                        logger.info(f"模板 {Path(template_path).name} 阈值 {threshold} 未找到匹配")
                
                # 在尝试下一个阈值前等待
                if i < len(thresholds) - 1:  # 不是最后一个阈值
                    logger.info(f"等待{self.threshold_delay}秒后尝试下一个阈值...")
                    time.sleep(self.threshold_delay)
            
            logger.info("所有AI文案模板都未找到匹配")
            return False
            
        except Exception as e:
            logger.error(f"点击AI文案按钮失败: {e}")
            return False
    
    def _get_ai_templates(self, region: str) -> List[str]:
        """
        获取AI文案模板列表
        
        Args:
            region: 地域
            
        Returns:
            List[str]: 模板文件路径列表
        """
        templates = []
        
        # 检查模板目录是否存在
        if not self.ai_templates_dir.exists():
            logger.info(f"模板目录不存在，创建目录: {self.ai_templates_dir}")
            self.ai_templates_dir.mkdir(parents=True, exist_ok=True)
            return templates
        
        # 根据地域选择模板
        template_patterns = []
        if region == "HK":
            template_patterns = [
                "ai_writing_cancel_hk.png",
            ]
        elif region == "SG":
            template_patterns = [
                "ai_writing_cancel_sg.png",
            ]
        
        # 通用模板
        template_patterns.extend([
            "ai_writing_cancel_hk.png",
        ])
        
        # 查找存在的模板
        for pattern in template_patterns:
            template_path = self.ai_templates_dir / pattern
            if template_path.exists():
                templates.append(str(template_path))
                logger.debug(f"找到模板: {template_path}")
        
        # 如果没有找到特定模板，查找所有PNG文件
        if not templates:
            all_templates = list(self.ai_templates_dir.glob("*.png"))
            templates = [str(t) for t in all_templates]
            logger.info(f"找到通用模板: {len(templates)} 个")
        
        return templates
    
    def create_template_from_screenshot(self, template_name: str, x: int, y: int, w: int, h: int) -> bool:
        """
        从页面截图中创建模板
        
        Args:
            template_name: 模板名称
            x, y, w, h: 截图区域坐标
            
        Returns:
            bool: 是否成功创建
        """
        try:
            # 截取页面截图
            screenshot_path = self.capture_page_screenshot()
            screenshot = cv2.imread(screenshot_path)
            
            if screenshot is None:
                logger.error(f"无法读取截图: {screenshot_path}")
                return False
            
            # 裁剪模板区域
            template = screenshot[y:y+h, x:x+w]
            
            # 保存模板
            template_path = self.ai_templates_dir / f"{template_name}.png"
            cv2.imwrite(str(template_path), template)
            
            logger.info(f"模板已创建: {template_path}, 区域: ({x}, {y}, {w}, {h})")
            return True
            
        except Exception as e:
            logger.error(f"创建模板失败: {template_name}, 错误: {e}")
            return False
    
    def find_multiple_images(self, template_candidates: List[str], 
                           thresholds: List[float] = None,
                           templates_dir: Path = None) -> Optional[Tuple[str, float, Tuple[int, int, int, int]]]:
        """
        多张图片匹配 - 通用方法
        
        Args:
            template_candidates: 模板候选文件名列表
            thresholds: 匹配阈值列表，默认 [0.8, 0.7, 0.6]
            templates_dir: 模板目录，默认使用 ai_templates_dir
            
        Returns:
            Optional[Tuple[str, float, Tuple[int, int, int, int]]]: 
            (匹配的模板文件名, 匹配阈值, 位置坐标) 或 None
        """
        if thresholds is None:
            thresholds = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3]
        
        if templates_dir is None:
            templates_dir = self.ai_templates_dir
        
        # 收集所有存在的模板文件
        existing_templates = []
        for candidate in template_candidates:
            candidate_path = templates_dir / candidate
            if candidate_path.exists():
                existing_templates.append(candidate_path)
                logger.debug(f"找到模板文件: {candidate}")
        
        if not existing_templates:
            logger.warning(f"未找到任何模板文件，候选: {template_candidates}")
            logger.warning(f"模板目录: {templates_dir}")
            logger.warning(f"请检查模板文件是否存在")
            return None
        
        logger.info(f"开始匹配 {len(existing_templates)} 张模板")
        
        # 尝试不同的匹配阈值
        for i, threshold in enumerate(thresholds):
            logger.info(f"尝试匹配阈值: {threshold}")
            
            # 遍历所有模板文件
            for template_path in existing_templates:
                logger.debug(f"匹配模板: {template_path.name}")
                
                # 查找图片位置
                match_result = self.find_image_on_page(str(template_path), threshold)
                
                if match_result:
                    logger.info(f"✅ 找到匹配 - 模板: {template_path.name}, 阈值: {threshold}")
                    return (template_path.name, threshold, match_result)
                else:
                    logger.info(f"❌ 模板 {template_path.name} 阈值 {threshold} 未找到匹配")
            
            # 在尝试下一个阈值前等待
            if i < len(thresholds) - 1:  # 不是最后一个阈值
                logger.info(f"等待{self.threshold_delay}秒后尝试下一个阈值...")
                time.sleep(self.threshold_delay)
        
        logger.info("所有模板都未找到匹配")
        return None
    
    def _find_smart_click_position(self, x: int, y: int, w: int, h: int) -> Tuple[int, int]:
        """
        智能选择点击位置，避免无效区域
        
        Args:
            x, y, w, h: 匹配区域的坐标和尺寸
            
        Returns:
            Tuple[int, int]: 优化后的点击坐标
        """
        try:
            # 截取匹配区域
            screenshot_path = self.capture_page_screenshot()
            screenshot = cv2.imread(screenshot_path)
            
            if screenshot is None:
                logger.warning("无法读取截图，使用默认中心点")
                return (x + w // 2, y + h // 2)
            
            # 提取匹配区域
            region = screenshot[y:y+h, x:x+w]
            
            # 转换为灰度图
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            
            # 使用边缘检测找到有效区域
            edges = cv2.Canny(gray, 50, 150)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 找到最大的轮廓
                largest_contour = max(contours, key=cv2.contourArea)
                
                # 计算轮廓的质心
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # 转换为全局坐标
                    global_x = x + cx
                    global_y = y + cy
                    
                    logger.info(f"智能点击位置: ({global_x}, {global_y}) (基于轮廓质心)")
                    return (global_x, global_y)
            
            # 如果轮廓检测失败，尝试寻找非白色区域
            # 将白色区域（接近255）设为0，其他区域设为1
            mask = (gray < 240).astype(np.uint8) * 255
            
            # 查找非零像素
            non_zero = cv2.findNonZero(mask)
            if non_zero is not None and len(non_zero) > 0:
                # 计算非零像素的中心
                mean_x = int(np.mean(non_zero[:, 0, 0]))
                mean_y = int(np.mean(non_zero[:, 0, 1]))
                
                # 转换为全局坐标
                global_x = x + mean_x
                global_y = y + mean_y
                
                logger.info(f"智能点击位置: ({global_x}, {global_y}) (基于非白色区域)")
                return (global_x, global_y)
            
            # 如果所有方法都失败，使用默认中心点
            logger.info("使用默认中心点作为点击位置")
            return (x + w // 2, y + h // 2)
            
        except Exception as e:
            logger.warning(f"智能点击位置计算失败: {e}，使用默认中心点")
            return (x + w // 2, y + h // 2)

    def click_multiple_images(self, template_candidates: List[str],
                            thresholds: List[float] = None,
                            templates_dir: Path = None) -> bool:
        """
        多张图片匹配并点击 - 通用方法
        
        Args:
            template_candidates: 模板候选文件名列表
            thresholds: 匹配阈值列表，默认 [0.8, 0.7, 0.6]
            templates_dir: 模板目录，默认使用 ai_templates_dir
            
        Returns:
            bool: 是否成功点击
        """
        try:
            # 查找匹配的图片
            match_result = self.find_multiple_images(template_candidates, thresholds, templates_dir)
            
            if match_result:
                template_name, threshold, (x, y, w, h) = match_result
                
                # 智能选择点击位置
                click_x, click_y = self._find_smart_click_position(x, y, w, h)
                
                logger.info(f"点击图片位置: ({click_x}, {click_y})")
                
                # 执行点击
                self.page.mouse.click(click_x, click_y)
                human_delay(0.5, 1.0)
                
                logger.info(f"成功点击图片: {template_name} (阈值: {threshold})")
                return True
            else:
                logger.info("未找到可点击的图片")
                return False
                
        except Exception as e:
            logger.error(f"多张图片点击失败: {e}")
            return False  

def click_ai_writing_button_with_image(page: Page, region: str = "all", 
                                      templates_dir: str = "templates") -> bool:
    """
    使用图片匹配点击AI文案按钮
    
    Args:
        page: Playwright页面对象
        region: 地域 (HK, SG, all)
        templates_dir: 模板目录
        
    Returns:
        bool: 是否成功点击
    """
    try:
        image_clicker = ImageClicker(page, templates_dir)
        return image_clicker.click_ai_writing_button(region)
    except Exception as e:
        logger.error(f"图片匹配点击失败: {e}")
        return False


# 全局实例管理
_image_clicker_instance = None

def get_image_clicker(page: Page, threshold_delay: float = 3.0) -> ImageClicker:
    """获取图片点击器实例"""
    global _image_clicker_instance
    if _image_clicker_instance is None:
        _image_clicker_instance = ImageClicker(page, threshold_delay=threshold_delay)
    return _image_clicker_instance
