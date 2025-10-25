import shutil
from pathlib import Path
import subprocess
import sys
import logging
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='[maple-font-builder] %(message)s')
logger = logging.getLogger(__name__)

# 确保日志记录器的级别正确设置
def _setup_logger(verbose: bool) -> None:
    """根据verbose标志设置日志级别"""
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

PKG_DIR = Path(__file__).parent
ROOT_DIR = PKG_DIR.parent.parent  # 正确指向 maple-font 根目录
FONTS_DIR = PKG_DIR / "data" / "fonts"

def build_maple(force_rebuild: bool = False, verbose: bool = False, args=None, custom_glyphs=None) -> bool:
    """构建Maple字体
    
    Args:
        force_rebuild: 是否强制重新构建字体，即使已存在字体文件
        verbose: 是否输出详细的构建信息
        args: 传递给build.py的参数列表
        custom_glyphs: 自定义glyphs列表，用于构建包含特定glyph的字体
        
    Returns:
        bool: 字体构建是否成功
    """
    # 设置日志级别
    _setup_logger(verbose)
    
    try:
        # 检查是否已存在字体文件且不需要强制重建
        if not force_rebuild and list(FONTS_DIR.glob("**/*.ttf")):
            if verbose:
                logger.debug("字体文件已存在，跳过构建")
            return True
        
        # 创建字体目录
        FONTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 设置默认参数
        if args is None:
            args = ["--ttf-only", "--nf", "--cn", "--least-styles"]
        elif not isinstance(args, list):
            logger.error("参数args必须是列表类型")
            return False
        
        # 处理自定义glyphs参数
        if custom_glyphs:
            if not isinstance(custom_glyphs, list):
                logger.error("参数custom_glyphs必须是列表类型")
                return False
                
            # 添加自定义glyphs相关参数
            if verbose:
                logger.debug(f"将包含自定义glyphs: {custom_glyphs}")
            
            # 将glyphs列表转换为逗号分隔的字符串并添加到参数中
            try:
                glyphs_str = ",".join(custom_glyphs)
                args.extend(["--feat", glyphs_str])
            except TypeError as e:
                logger.error(f"自定义glyphs列表中包含非字符串元素: {str(e)}")
                return False
        
        # 调用官方build.py构建字体
        build_script = ROOT_DIR / "build.py"
        if build_script.exists():
            if verbose:
                logger.debug(f"正在调用构建脚本: {build_script}，参数: {args}")
            
            # 执行构建命令
            try:
                result = subprocess.run(
                    [sys.executable, str(build_script), *args], 
                    cwd=str(ROOT_DIR),
                    capture_output=not verbose,  # 非verbose模式下捕获输出
                    text=True,
                    timeout=3600  # 设置1小时超时
                )
            except subprocess.TimeoutExpired:
                logger.error("字体构建超时，已超过1小时")
                return False
            
            # 检查构建是否成功
            if result.returncode != 0:
                logger.error(f"字体构建失败: {result.stderr}")
                return False
            
            # 复制字体文件
            copy_success = _copy_fonts_to_target(verbose=verbose)
            return copy_success
        else:
            logger.error(f"未找到build.py脚本: {build_script}")
            return False
    except PermissionError as e:
        logger.error(f"权限错误: {str(e)}")
        return False
    except OSError as e:
        logger.error(f"操作系统错误: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"构建字体时发生异常: {str(e)}")
        return False


def _copy_fonts_to_target(verbose: bool = False) -> bool:
    """将构建的字体文件复制到目标目录
    
    Args:
        verbose: 是否输出详细的复制信息
        
    Returns:
        bool: 字体文件复制是否成功
    """
    # 设置日志级别
    _setup_logger(verbose)
    
    try:
        source_dir = ROOT_DIR / "fonts"
        if not source_dir.exists():
            logger.error(f"源字体目录不存在: {source_dir}")
            return False
        
        # 检查源目录是否有字体文件
        source_fonts = list(source_dir.glob("**/*.ttf")) + list(source_dir.glob("**/*.otf"))
        if not source_fonts:
            logger.warning(f"源字体目录为空: {source_dir}")
            return False
        
        # 清理目标目录
        if verbose:
            logger.debug(f"正在清理目标目录: {FONTS_DIR}")
        
        # 记录清理失败的文件数
        failed_cleanup_count = 0
        for item in FONTS_DIR.glob("*"):
            try:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=False)
                else:
                    item.unlink()
            except PermissionError as e:
                logger.warning(f"清理目标目录项时权限不足 ({item}): {str(e)}")
                failed_cleanup_count += 1
            except Exception as e:
                logger.warning(f"清理目标目录项时出错 ({item}): {str(e)}")
                failed_cleanup_count += 1
                # 继续清理其他项目，不中断流程
        
        # 如果有太多清理失败，可能会影响复制，发出警告
        if failed_cleanup_count > 10:
            logger.warning(f"有{failed_cleanup_count}个文件清理失败，可能会影响字体复制")
        
        # 复制字体文件
        if verbose:
            logger.debug(f"正在将字体文件从 {source_dir} 复制到 {FONTS_DIR}")
        
        # 记录成功和失败的复制数
        copied_count = 0
        failed_copy_count = 0
        
        for item in source_dir.iterdir():
            try:
                target_path = FONTS_DIR / item.name
                if item.is_dir():
                    # 确保目标目录不存在
                    if target_path.exists():
                        if verbose:
                            logger.debug(f"目标目录已存在，将被覆盖: {target_path}")
                        shutil.rmtree(target_path, ignore_errors=True)
                    shutil.copytree(item, target_path)
                else:
                    shutil.copy2(item, target_path)
                
                copied_count += 1
                if verbose:
                    logger.debug(f"已复制: {item.name}")
            except PermissionError as e:
                logger.warning(f"复制文件时权限不足 ({item}): {str(e)}")
                failed_copy_count += 1
            except Exception as e:
                logger.warning(f"复制文件时出错 ({item}): {str(e)}")
                failed_copy_count += 1
                # 继续复制其他文件，不中断流程
        
        # 验证复制是否成功
        target_fonts = list(FONTS_DIR.glob("**/*.ttf"))
        if target_fonts:
            if verbose:
                logger.debug(f"字体文件复制成功，共复制 {copied_count} 个文件，失败 {failed_copy_count} 个")
            return True
        else:
            logger.error("字体文件复制失败，目标目录中没有找到字体文件")
            return False
            
    except PermissionError as e:
        logger.error(f"权限错误: {str(e)}")
        return False
    except OSError as e:
        logger.error(f"操作系统错误: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"复制字体文件时发生异常: {str(e)}")
        return False


def check_fonts_exist(font_type: Optional[str] = None) -> bool:
    """检查指定类型的字体文件是否存在
    
    Args:
        font_type: 字体类型，如 'NF-CN', 'NF' 等。如果为None，则检查所有字体
        
    Returns:
        bool: 字体文件是否存在
    """
    try:
        # 验证FONTS_DIR是否存在
        if not FONTS_DIR.exists():
            logger.debug(f"字体根目录不存在: {FONTS_DIR}")
            return False
        
        if font_type:
            # 确保font_type是字符串
            if not isinstance(font_type, str):
                font_type = str(font_type)
                logger.warning(f"字体类型被转换为字符串: {font_type}")
            
            target_dir = FONTS_DIR / font_type
            if not target_dir.exists():
                logger.debug(f"指定的字体类型目录不存在: {target_dir}")
                return False
            
            # 检查是否存在TTF文件
            has_ttf = any(target_dir.glob("*.ttf"))
            if not has_ttf:
                logger.debug(f"在{target_dir}中未找到TTF字体文件")
            return has_ttf
        else:
            # 检查所有字体
            has_any_font = any(FONTS_DIR.glob("**/*.ttf"))
            if not has_any_font:
                logger.debug(f"在{FONTS_DIR}中未找到任何TTF字体文件")
            return has_any_font
    except Exception as e:
        logger.error(f"检查字体是否存在时发生错误: {str(e)}")
        return False
