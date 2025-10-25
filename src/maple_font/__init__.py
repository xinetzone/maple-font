from pathlib import Path
from typing import List, Dict, Set
from ._builder import build_maple
from ._register import register_directory_fonts, enhanced_register_fonts
import logging

logger = logging.getLogger(__name__)

FONTS_DIR = Path(__file__).parent / "data" / "fonts"

# 用于跟踪已注册的字体类型，避免重复注册
def _get_registered_fonts_store() -> Set[str]:
    """获取用于跟踪已注册字体类型的集合（使用闭包避免全局变量）"""
    _registered_fonts: Set[str] = set()
    return _registered_fonts

_registered_fonts = _get_registered_fonts_store()
_fonts_initialized = False

# 首次导入时自动构建并注册字体
def _initialize_fonts() -> None:
    """初始化字体环境，构建并注册字体"""
    global _fonts_initialized
    if not _fonts_initialized:
        # 首次导入时自动构建字体
        if not any(FONTS_DIR.rglob("*.ttf")):
            logger.info("[maple-font] 首次使用，开始构建 Maple Mono 字体...")
            build_maple()
        
        # 注册字体
        register_directory_fonts(FONTS_DIR)
        _registered_fonts.add("all")  # 标记所有字体已注册
        _fonts_initialized = True

# 初始化字体环境
_initialize_fonts()

def fonts_dir() -> str:
    """获取字体目录的绝对路径
    
    Returns:
        str: 字体目录的绝对路径字符串
    """
    return str(FONTS_DIR)

def get_font_path(name: str) -> str:
    """获取指定字体文件的绝对路径
    
    Args:
        name: 字体文件名或相对于字体目录的路径
        
    Returns:
        str: 字体文件的绝对路径字符串
    """
    return str(FONTS_DIR / name)

def ensure_latest(verbose: bool = False) -> bool:
    """确保使用最新版本的字体，重新构建并注册字体
    
    Args:
        verbose: 是否输出详细信息
    
    Returns:
        bool: 是否成功更新到最新字体
    
    此函数会强制执行以下操作：
    1. 重新构建字体文件
    2. 重新注册所有字体文件
    3. 重置注册状态
    """
    global _fonts_initialized
    try:
        # 强制重新构建字体
        build_success = build_maple(force_rebuild=True, verbose=verbose)
        
        if build_success:
            # 清空已注册字体记录
            _registered_fonts.clear()
            
            # 重新注册所有字体
            register_directory_fonts(FONTS_DIR)
            _registered_fonts.add("all")
            _fonts_initialized = True
            
            if verbose:
                logger.debug("[maple-font] 已更新到最新字体并重新注册")
            return True
        else:
            if verbose:
                logger.debug("[maple-font] 字体构建失败，无法更新到最新版本")
            return False
    except Exception as e:
        if verbose:
            logger.debug(f"[maple-font] 更新字体时发生错误: {str(e)}")
        return False

def register_fonts(silent: bool = False):
    """注册字体到Matplotlib/Pillow，该函数确保字体只被注册一次
    
    Args:
        silent: 是否静默执行，不打印提示信息
    """
    if "all" not in _registered_fonts:
        register_directory_fonts(FONTS_DIR)
        _registered_fonts.add("all")
    else: # 已注册过字体，则静默返回
        if not silent:
            logger.debug("[maple-font] 字体已注册，无需重复注册")

def get_font_family_name(font_type: str = "NF-CN") -> str:
    """获取指定字体类型的Matplotlib字体族名称
    
    Args:
        font_type: 字体类型，可选值为 'NF-CN', 'NF', 'TTF', 'TTF-AutoHint', 'Variable'
        
    Returns:
        str: Matplotlib中应该使用的字体族名称
    """
    # 定义字体类型到字体族名称的映射
    font_name_map: Dict[str, str] = {
        'NF-CN': 'Maple Mono NF CN',
        'NF': 'Maple Mono NF',
        'TTF': 'Maple Mono',
        'TTF-AutoHint': 'Maple Mono',
        'Variable': 'Maple Mono'
    }
    
    # 确保font_type是字符串并去除空白
    if not isinstance(font_type, str):
        font_type = str(font_type)
    font_type = font_type.strip()
    
    # 返回对应的字体族名称，如果不存在则返回默认值
    return font_name_map.get(font_type, 'Maple Mono')

def set_font(font_type: str = "NF-CN", silent: bool = False) -> bool:
    """一键设置Matplotlib使用指定的Maple Mono字体
    
    Args:
        font_type: 要使用的字体类型，可选值为 'NF-CN', 'NF', 'TTF', 'TTF-AutoHint', 'Variable'
        silent: 是否静默执行，不打印提示信息
        
    Returns:
        bool: 是否成功设置字体
    """
    # 验证字体类型
    valid_font_types = ['NF-CN', 'NF', 'TTF', 'TTF-AutoHint', 'Variable']
    if font_type not in valid_font_types:
        if not silent:
            logger.debug(f"[maple-font] 无效的字体类型: {font_type}，可选值为: {', '.join(valid_font_types)}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        
        # 检查字体是否已注册，避免重复注册
        if font_type not in _registered_fonts:
            success = enhanced_register_fonts(font_type=font_type, silent=silent)
            if success:
                _registered_fonts.add(font_type)
        else:
            success = True  # 字体已注册
        
        if success:
            # 设置字体 - 将字体族名称作为列表设置，符合Matplotlib的要求
            font_family = get_font_family_name(font_type)
            plt.rcParams["font.family"] = [font_family]
            if not silent:
                logger.debug(f"[maple-font] 已设置Matplotlib使用 '{font_family}' 字体")
        
        return success
    except ImportError:
        if not silent:
            logger.debug("[maple-font] 未找到Matplotlib库，请先安装")
        return False
    except Exception as e:
        if not silent:
            logger.debug(f"[maple-font] 设置字体时发生错误: {str(e)}")
        return False

# 用于缓存已加载的glyph列表，提高性能
def _get_glyph_cache() -> Dict[str, List[str]]:
    """获取用于缓存glyph列表的字典"""
    _glyph_cache: Dict[str, List[str]] = {}
    return _glyph_cache

glyph_cache = _get_glyph_cache()

def get_available_glyphs(font_type: str = "NF-CN") -> List[str]:
    """获取指定字体类型中可用的glyph名称列表
    
    Args:
        font_type: 字体类型，可选值为 'NF-CN', 'NF', 'TTF', 'TTF-AutoHint', 'Variable'
        
    Returns:
        List[str]: 可用glyph名称的列表
    """
    # 检查缓存中是否已有结果
    if font_type in glyph_cache:
        return glyph_cache[font_type]
    
    try:
        from fontTools.ttLib import TTFont
        
        # 获取字体文件路径
        font_dir = FONTS_DIR / font_type
        if not font_dir.exists():
            logger.debug(f"[maple-font] 未找到字体目录: {font_dir}")
            return []
        
        # 获取第一个字体文件
        font_files = list(font_dir.glob("*.ttf"))
        if not font_files:
            logger.debug(f"[maple-font] 在目录 {font_dir} 中未找到字体文件")
            return []
        
        # 加载字体并获取glyph名称
        font = TTFont(font_files[0])
        glyph_names = font.getGlyphNames()
        font.close()
        
        # 缓存结果
        glyph_cache[font_type] = glyph_names
        
        return glyph_names
    except ImportError:
        logger.debug("[maple-font] 未找到fontTools库，请先安装")
        return []
    except Exception as e:
        logger.debug(f"[maple-font] 获取glyph列表时发生错误: {str(e)}")
        return []

def check_glyph_exists(glyph_name: str, font_type: str = "NF-CN") -> bool:
    """检查指定的glyph是否存在于字体中
    
    Args:
        glyph_name: 要检查的glyph名称
        font_type: 字体类型，可选值为 'NF-CN', 'NF', 'TTF', 'TTF-AutoHint', 'Variable'
        
    Returns:
        bool: glyph是否存在
    """
    # 验证输入参数
    if not isinstance(glyph_name, str):
        return False
    
    # 利用缓存的glyph列表提高性能
    available_glyphs = get_available_glyphs(font_type)
    return glyph_name in available_glyphs

def build_with_custom_glyphs(
    glyphs: List[str], 
    force_rebuild: bool = False, 
    verbose: bool = False
) -> bool:
    """构建包含自定义glyphs的字体
    
    Args:
        glyphs: 要包含的自定义glyphs列表
        force_rebuild: 是否强制重新构建字体
        verbose: 是否输出详细的构建信息
        
    Returns:
        bool: 构建是否成功
    """
    # 验证输入参数
    if not isinstance(glyphs, list):
        if verbose:
            logger.debug("[maple-font] 无效的glyphs参数，必须是字符串列表")
        return False
    
    # 确保glyphs列表中的元素都是字符串
    valid_glyphs = []
    for glyph in glyphs:
        if isinstance(glyph, str):
            valid_glyphs.append(glyph)
        else:
            if verbose:
                logger.debug(f"[maple-font] 忽略非字符串类型的glyph: {glyph}")
    
    if not valid_glyphs:
        if verbose:
            logger.debug("[maple-font] 没有有效的glyphs来构建字体")
        return False
    
    try:
        # 调用构建函数，并传递自定义glyphs参数
        args = ["--ttf-only", "--nf", "--cn", "--least-styles"]
        
        # 构建字体
        success = build_maple(
            force_rebuild=force_rebuild, 
            verbose=verbose, 
            args=args,
            custom_glyphs=valid_glyphs
        )
        
        # 如果构建成功，清空缓存以反映新的字体变化
        if success:
            glyph_cache.clear()
            _registered_fonts.clear()
            
        return success
    except Exception as e:
        if verbose:
            logger.debug(f"[maple-font] 构建自定义glyphs字体时发生错误: {str(e)}")
        return False
