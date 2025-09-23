"""
浏览器操作模块
包含浏览器控制和动作执行
"""

# 延迟导入，避免在模块级别导入时出现依赖问题
def get_browser_functions():
    from .browser import (
        start_browser,
        fetch_all_browser_windows,
        get_profile_id_by_browser_id,
        check_browser_api_health
    )
    return start_browser, fetch_all_browser_windows, get_profile_id_by_browser_id, check_browser_api_health

def get_action_functions():
    from .actions import (
        retry_action,
        click_with_wait,
        input_with_wait,
        wait_for_element,
        upload_folder_with_keyboard,
        human_delay,
        click_blank_area,
        click_center,
        smart_goto,
        smart_checkbox_click,
        smart_toggle_click,
        get_element_state
    )
    return (retry_action, click_with_wait, input_with_wait, wait_for_element, 
            upload_folder_with_keyboard, human_delay, click_blank_area, click_center,
            smart_goto, smart_checkbox_click, smart_toggle_click, get_element_state)

# 为了向后兼容，提供直接导入（如果依赖包可用）
try:
    from .browser import (
        start_browser,
        fetch_all_browser_windows,
        get_profile_id_by_browser_id,
        check_browser_api_health
    )
    from .actions import (
        retry_action,
        click_with_wait,
        input_with_wait,
        wait_for_element,
        upload_folder_with_keyboard,
        human_delay,
        click_blank_area,
        click_center,
        smart_goto,
        smart_checkbox_click,
        smart_toggle_click,
        get_element_state
    )
except ImportError:
    # 如果依赖包未安装，提供占位符
    start_browser = None
    fetch_all_browser_windows = None
    get_profile_id_by_browser_id = None
    check_browser_api_health = None
    retry_action = None
    click_with_wait = None
    input_with_wait = None
    wait_for_element = None
    upload_folder_with_keyboard = None
    human_delay = None
    click_blank_area = None
    click_center = None
    smart_goto = None
    smart_checkbox_click = None
    smart_toggle_click = None
    get_element_state = None

__all__ = [
    'get_browser_functions',
    'get_action_functions',
    'start_browser',
    'fetch_all_browser_windows',
    'get_profile_id_by_browser_id',
    'check_browser_api_health',
    'retry_action',
    'click_with_wait',
    'input_with_wait',
    'wait_for_element',
    'upload_folder_with_keyboard',
    'human_delay',
    'click_blank_area',
    'click_center',
    'smart_goto',
    'smart_checkbox_click',
    'smart_toggle_click',
    'get_element_state'
]
