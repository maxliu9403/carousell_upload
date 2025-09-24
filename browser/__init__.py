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
        check_browser_api_health,
        close_browser_by_profile_id
    )
    return start_browser, fetch_all_browser_windows, get_profile_id_by_browser_id, check_browser_api_health, close_browser_by_profile_id

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
        # 原有接口（保持向后兼容）
        start_browser,
        fetch_all_browser_windows,
        get_profile_id_by_browser_id,
        check_browser_api_health,
        close_browser_by_profile_id,
        # 新的统一接口
        initialize_browser_interface,
        check_browser_health,
        start_browser_unified,
        close_browser_unified,
        get_browser_windows_unified,
        get_profile_id_by_browser_id_unified
    )
    from .browser_selector import (
        select_browser_type,
        interactive_browser_setup,
        validate_browser_config
    )
    from .browser_factory import BrowserFactory
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
    close_browser_by_profile_id = None
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
    # 原有接口（保持向后兼容）
    'start_browser',
    'fetch_all_browser_windows',
    'get_profile_id_by_browser_id',
    'check_browser_api_health',
    'close_browser_by_profile_id',
        # 新的统一接口
        'initialize_browser_interface',
        'check_browser_health',
        'start_browser_unified',
        'close_browser_unified',
        'get_browser_windows_unified',
        'get_profile_id_by_browser_id_unified',
        # 浏览器管理
        'get_current_browser_type',
    # 浏览器选择器
    'select_browser_type',
    'interactive_browser_setup',
    'validate_browser_config',
    # 浏览器工厂
    'BrowserFactory',
    # 动作函数
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
