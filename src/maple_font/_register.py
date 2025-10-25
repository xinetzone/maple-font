import logging
import os
from pathlib import Path
from matplotlib import font_manager
from fontTools.ttLib import TTFont

# 配置日志记录
logger = logging.getLogger(__name__)


def is_ttf_supported(font_path: str) -> bool:
    """检查字体文件是否支持
    
    Args:
        font_path: 字体文件路径
    
    Returns:
        bool: 是否支持
    """
    try:
        TTFont(font_path)
        return True
    except Exception as e:
        # 使用日志而非print，并记录异常详情
        logger.warning(f"字体文件不兼容或损坏: {font_path}. 错误: {str(e)}")
        return False

# 支持的字体类型
SUPPORTED_FONT_TYPES = {'NF-CN', 'NF', 'TTF', 'TTF-AutoHint', 'Variable'}

# 缓存已注册的字体目录，避免重复注册
_registered_font_dirs = set()


def register_directory_fonts(font_dir: Path) -> int:
    """注册指定目录及其子目录中的所有字体文件
    
    Args:
        font_dir: 包含字体文件的目录路径
    
    Returns:
        int: 成功注册的字体数量
    """
    registered_count = 0
    try:
        # 确保font_dir是绝对路径
        font_dir_abs = font_dir.absolute()
        logger.debug(f"开始注册字体目录: {font_dir_abs}")
        
        for ext in ("*.ttf", "*.otf"):
            # 安全地获取字体文件，避免权限问题导致的崩溃
            try:
                font_files = list(font_dir_abs.rglob(ext))
                logger.debug(f"找到 {len(font_files)} 个{ext}文件")
                
                for fp in font_files:
                    try:
                        # 再次检查文件可读性
                        if os.access(str(fp), os.R_OK):
                            font_manager.fontManager.addfont(str(fp))
                            registered_count += 1
                            logger.debug(f"成功注册字体: {fp.name}")
                        else:
                            logger.warning(f"无权限读取字体文件: {fp.name}")
                    except Exception as e:
                        logger.warning(f"注册字体文件 {fp.name} 失败: {str(e)}")
            except PermissionError:
                logger.warning(f"无权限搜索 {ext} 文件在目录: {font_dir_abs}")
            except Exception as e:
                logger.warning(f"搜索 {ext} 文件时发生错误: {str(e)}")
        
        logger.debug(f"成功注册了 {registered_count} 个字体文件从目录: {font_dir_abs}")
        return registered_count
    except PermissionError:
        logger.error(f"无权限访问字体目录: {font_dir}")
        return 0
    except Exception as e:
        logger.error(f"注册字体目录 {font_dir} 时发生错误: {str(e)}")
        return 0

def _setup_logger(verbose: bool = False):
    """设置日志级别，避免重复配置"""
    # 只在根日志器未配置处理器时进行配置
    if not logging.root.handlers:
        if verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        # 只调整当前logger的级别
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    return logger

def enhanced_register_fonts(font_type: str = "NF-CN", silent: bool = False, verbose: bool = False) -> bool:
    """增强的字体注册函数，提供自动搜索和错误处理
    
    Args:
        font_type: 要注册的字体类型，可选值为 'NF-CN', 'NF', 'TTF', 'TTF-AutoHint', 'Variable'
        silent: 是否静默执行，不打印提示信息
        verbose: 是否输出详细日志
    
    Returns:
        bool: 字体是否成功注册
    """
    # 设置日志级别
    _setup_logger(verbose)
    
    # 验证字体类型
    if not isinstance(font_type, str):
        font_type = str(font_type)
        logger.warning(f"字体类型被转换为字符串: {font_type}")
    
    if font_type not in SUPPORTED_FONT_TYPES:
        logger.warning(f"不支持的字体类型: {font_type}，支持的类型为: {SUPPORTED_FONT_TYPES}")
    
    def _show_message(message):
        """内部函数：显示消息或记录日志"""
        if not silent:
            logger.debug(message)
    
    try:
        # 获取包的安装路径
        from . import __file__ as package_file
        package_dir = Path(package_file).parent.absolute()
        logger.debug(f"包安装路径: {package_dir}")
        
        # 定义可能的字体目录路径列表
        possible_font_dirs = [
            package_dir / "data" / "fonts" / font_type,
        ]
        
        # 尝试添加FONTS_DIR路径（如果可用）
        try:
            from . import FONTS_DIR as package_fonts_dir
            if package_fonts_dir:
                possible_font_dirs.append(Path(package_fonts_dir).absolute() / font_type)
                logger.debug(f"添加FONTS_DIR路径: {possible_font_dirs[-1]}")
        except (ImportError, AttributeError):
            logger.debug("无法导入或使用FONTS_DIR常量")
        
        # 遍历所有可能的字体目录，找到第一个存在且可读的目录
        font_dir = None
        for candidate_dir in possible_font_dirs:
            if candidate_dir.exists() and os.access(str(candidate_dir), os.R_OK):
                font_dir = candidate_dir
                logger.debug(f"找到有效的字体目录: {font_dir}")
                break
        
        # 如果没有找到有效的字体目录
        if font_dir is None:
            logger.error(f"无法找到有效的字体目录 (类型: {font_type})")
            _show_message(f"提示: Maple Mono {font_type} 字体文件未找到或无法访问，将使用系统默认字体")
            return False
        
        # 检查字体目录是否已注册（避免重复注册）
        font_dir_str = str(font_dir)
        if font_dir_str in _registered_font_dirs:
            logger.debug(f"字体目录已注册，跳过: {font_dir}")
            return True
        
        # 尝试查找字体文件
        try:
            font_files = list(font_dir.glob("*.ttf"))
            logger.debug(f"在目录 {font_dir} 中找到 {len(font_files)} 个TTF文件")
            
            if not font_files:
                logger.warning(f"字体目录存在但未找到TTF文件: {font_dir}")
                _show_message(f"提示: Maple Mono {font_type} 字体文件存在但为空，将使用系统默认字体")
                return False
            
            # 过滤有效字体文件
            valid_font_files = [f for f in font_files if is_ttf_supported(str(f))]
            logger.debug(f"过滤后有效字体文件数: {len(valid_font_files)}")
            
            if not valid_font_files:
                logger.warning(f"所有字体文件均不兼容: {font_dir}")
                _show_message(f"提示: Maple Mono {font_type} 字体文件不兼容，将使用系统默认字体")
                return False
            
            # 注册字体文件
            registered_count = register_directory_fonts(font_dir)
            
            if registered_count > 0:
                # 注册成功，添加到已注册目录缓存
                _registered_font_dirs.add(font_dir_str)
                logger.debug(f"成功注册了 {registered_count} 个{font_type}类型字体文件")
                return True
            else:
                logger.warning(f"未能注册任何字体文件从目录: {font_dir}")
                _show_message(f"提示: 未能注册任何 Maple Mono {font_type} 字体文件，将使用系统默认字体")
                return False
        except PermissionError as e:
            logger.error(f"访问字体文件时权限不足: {str(e)}")
            _show_message("提示: 访问字体文件时权限不足，将使用系统默认字体")
            return False
        except FileNotFoundError as e:
            logger.error(f"找不到必要的字体文件: {str(e)}")
            _show_message("提示: 找不到必要的字体文件，将使用系统默认字体")
            return False
        except Exception as e:
            logger.error(f"字体注册过程中发生错误: {str(e)}")
            _show_message(f"提示: 字体注册过程中发生错误 ({str(e)})，将使用系统默认字体")
            return False
    except Exception as e:
        # 捕获所有其他未预见的异常
        logger.error(f"增强字体注册过程中发生未预期的错误: {str(e)}")
        _show_message(f"提示: 字体注册过程中发生未预期错误，将使用系统默认字体")
        return False