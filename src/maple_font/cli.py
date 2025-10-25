#!/usr/bin/env python3
"""Maple Mono字体管理工具命令行接口"""

import sys
from pathlib import Path
import logging
import argparse
from typing import Set

# 配置日志
logging.basicConfig(level=logging.INFO, format='[maple-font-cli] %(message)s')
logger = logging.getLogger(__name__)

# 支持的字体类型
SUPPORTED_FONT_TYPES: Set[str] = {'NF-CN', 'NF', 'TTF', 'TTF-AutoHint', 'Variable'}

# 常量定义
DEFAULT_FONT_TYPE: str = 'NF-CN'
MAX_DISPLAY_GLYPHS: int = 50

FONTS_DIR: Path = Path(__file__).parent / "data" / "fonts"


def setup_logger(verbose: bool) -> None:
    """设置日志级别"""
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format='[maple-font-cli] [%(levelname)s] %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='[maple-font-cli] %(message)s')


def validate_font_type(font_type: str) -> str:
    """验证字体类型参数"""
    if not isinstance(font_type, str):
        font_type = str(font_type)
        logger.warning(f"字体类型被转换为字符串: {font_type}")
    
    if font_type not in SUPPORTED_FONT_TYPES:
        logger.error(f"不支持的字体类型: {font_type}，支持的类型为: {', '.join(SUPPORTED_FONT_TYPES)}")
        sys.exit(1)
    
    return font_type


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Maple Mono字体管理工具",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # 添加全局参数
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="显示详细信息"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # build 命令
    build_parser = subparsers.add_parser(
        "build", 
        help="构建Maple Mono字体"
    )
    build_parser.add_argument(
        "--force", 
        action="store_true", 
        help="强制重新构建，即使已存在字体文件"
    )
    build_parser.add_argument(
        "--full", 
        action="store_true", 
        help="构建完整版本字体，包含所有样式"
    )
    build_parser.add_argument(
        "--args", 
        nargs="*", 
        help="传递给build.py的额外参数"
    )
    
    # register 命令
    register_parser = subparsers.add_parser(
        "register", 
        help="注册字体到Matplotlib/Pillow"
    )
    register_parser.add_argument(
        "--font-type", 
        default=DEFAULT_FONT_TYPE, 
        choices=list(SUPPORTED_FONT_TYPES),
        help=f"字体类型，默认为 {DEFAULT_FONT_TYPE}"
    )
    register_parser.add_argument(
        "--silent", 
        action="store_true", 
        help="静默执行，不显示提示信息"
    )
    register_parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="显示详细的注册信息"
    )
    
    # set-font 命令
    set_font_parser = subparsers.add_parser(
        "set-font", 
        help="一键设置Matplotlib使用Maple Mono字体"
    )
    set_font_parser.add_argument(
        "--font-type", 
        default=DEFAULT_FONT_TYPE, 
        choices=list(SUPPORTED_FONT_TYPES),
        help=f"字体类型，默认为 {DEFAULT_FONT_TYPE}"
    )
    
    # check 命令
    check_parser = subparsers.add_parser(
        "check", 
        help="检查字体安装状态"
    )
    check_parser.add_argument(
        "--font-type", 
        default=None, 
        choices=list(SUPPORTED_FONT_TYPES),
        help="指定要检查的字体类型"
    )
    
    # glyph 命令组
    glyph_parser = subparsers.add_parser(
        "glyph", 
        help="管理字体中的glyphs"
    )
    glyph_subparsers = glyph_parser.add_subparsers(dest="glyph_command", help="glyph相关命令")
    
    # glyph list 命令
    glyph_list_parser = glyph_subparsers.add_parser(
        "list", 
        help="列出字体中的所有glyphs"
    )
    glyph_list_parser.add_argument(
        "--font-type", 
        default=DEFAULT_FONT_TYPE, 
        choices=list(SUPPORTED_FONT_TYPES),
        help=f"字体类型，默认为 {DEFAULT_FONT_TYPE}"
    )
    glyph_list_parser.add_argument(
        "--max-display", 
        type=int, 
        default=MAX_DISPLAY_GLYPHS, 
        help=f"最多显示的glyph数量，默认为 {MAX_DISPLAY_GLYPHS}"
    )
    
    # glyph check 命令
    glyph_check_parser = glyph_subparsers.add_parser(
        "check", 
        help="检查指定的glyph是否存在"
    )
    glyph_check_parser.add_argument(
        "glyph_name", 
        help="要检查的glyph名称"
    )
    glyph_check_parser.add_argument(
        "--font-type", 
        default=DEFAULT_FONT_TYPE, 
        choices=list(SUPPORTED_FONT_TYPES),
        help=f"字体类型，默认为 {DEFAULT_FONT_TYPE}"
    )
    
    # build-with-glyphs 命令
    build_with_glyphs_parser = subparsers.add_parser(
        "build-with-glyphs", 
        help="构建包含自定义glyphs的字体"
    )
    build_with_glyphs_parser.add_argument(
        "--glyphs", 
        nargs="*", 
        help="要包含的自定义glyphs列表"
    )
    build_with_glyphs_parser.add_argument(
        "--force", 
        action="store_true", 
        help="强制重新构建，即使已存在字体文件"
    )
    
    return parser


def main() -> None:
    """主函数，处理命令行参数并执行相应的命令"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 设置日志级别
    setup_logger(args.verbose)
    
    # 执行相应的命令
    # 如果没有指定命令，显示帮助信息
    if not args.command:
        parser.print_help()
        sys.exit(1)
    elif args.command == "build":
        from ._builder import build_maple
        
        build_args = args.args
        
        # 如果没有提供额外参数但指定了full选项，使用完整参数集
        if not build_args and args.full:
            build_args = ["--ttf-only", "--nf", "--cn"]
        elif not build_args:
            build_args = ["--ttf-only", "--nf", "--cn", "--least-styles"]
        
        # 验证build_args是列表类型
        if not isinstance(build_args, list):
            logger.error("build参数必须是列表类型")
            sys.exit(1)
        
        try:
            success = build_maple(
                force_rebuild=args.force,
                verbose=args.verbose,
                args=build_args
            )
            
            if success:
                logger.debug("字体构建成功")
                sys.exit(0)
            else:
                logger.error("字体构建失败")
                sys.exit(1)
        except Exception as e:
            logger.error(f"构建过程中发生错误: {str(e)}")
            sys.exit(1)
        
    elif args.command == "register":
        from ._register import enhanced_register_fonts
        
        # 验证字体类型
        font_type = validate_font_type(args.font_type)
        
        try:
            success = enhanced_register_fonts(
                font_type=font_type,
                silent=args.silent,
                verbose=args.verbose
            )
            
            if success and not args.silent:
                logger.debug(f"已成功注册 {font_type} 字体")
            elif not success and not args.silent:
                logger.warning(f"注册 {font_type} 字体失败")
                sys.exit(1)
        except Exception as e:
            logger.error(f"注册过程中发生错误: {str(e)}")
            sys.exit(1)
        
    elif args.command == "set-font":
        from .__init__ import set_font
        
        # 验证字体类型
        font_type = validate_font_type(args.font_type)
        
        try:
            success = set_font(
                font_type=font_type,
                silent=not args.verbose
            )
            
            if not success:
                logger.error(f"设置 {font_type} 字体失败")
                sys.exit(1)
        except Exception as e:
            logger.error(f"设置字体过程中发生错误: {str(e)}")
            sys.exit(1)
        
    elif args.command == "check":
        from ._builder import check_fonts_exist
        
        # 验证字体类型
        font_type = args.font_type
        if font_type:
            font_type = validate_font_type(font_type)
        
        try:
            fonts_exist = check_fonts_exist(font_type=font_type)
            
            if font_type:
                if fonts_exist:
                    logger.debug(f"{font_type} 字体文件存在")
                else:
                    logger.warning(f"未找到 {font_type} 字体文件")
            else:
                if fonts_exist:
                    logger.debug("Maple Mono 字体文件已安装")
                else:
                    logger.warning("未找到任何 Maple Mono 字体文件")
                    logger.debug("请使用 'maple-font build' 命令构建字体")
            
            # 根据检查结果设置退出码
            sys.exit(0 if fonts_exist else 1)
        except Exception as e:
            logger.error(f"检查过程中发生错误: {str(e)}")
            sys.exit(1)
        
    # 处理glyph命令
    elif args.command == "glyph":
        if args.glyph_command == "list":
            from .__init__ import get_available_glyphs
            
            # 验证字体类型
            font_type = validate_font_type(args.font_type)
            
            try:
                max_display = max(1, min(args.max_display, 1000))  # 限制在1-1000之间
                
                glyphs = get_available_glyphs(font_type=font_type)
                logger.debug(f"字体 {font_type} 中包含 {len(glyphs)} 个glyphs")
                if len(glyphs) > 0:
                    # 显示指定数量的glyphs
                    logger.debug(f"前{min(len(glyphs), max_display)}个glyphs：")
                    for glyph in glyphs[:max_display]:
                        logger.debug(f"  {glyph}")
                    if len(glyphs) > max_display:
                        logger.debug(f"  ... 还有 {len(glyphs) - max_display} 个glyphs未显示")
                        logger.debug(f"  使用 --max-display {len(glyphs)} 参数查看所有glyphs")
                sys.exit(0)
            except ImportError:
                logger.error("需要安装fontTools库来查看glyphs。使用 pip install fontTools 安装。")
                sys.exit(1)
            except Exception as e:
                logger.error(f"获取glyph列表过程中发生错误: {str(e)}")
                sys.exit(1)
        elif args.glyph_command == "check":
            from .__init__ import check_glyph_exists
            
            # 验证字体类型
            font_type = validate_font_type(args.font_type)
            
            try:
                # 验证glyph_name是字符串
                if not isinstance(args.glyph_name, str):
                    args.glyph_name = str(args.glyph_name)
                    logger.warning(f"glyph名称被转换为字符串: {args.glyph_name}")
                
                exists = check_glyph_exists(glyph_name=args.glyph_name, font_type=font_type)
                if exists:
                    logger.debug(f"Glyph '{args.glyph_name}' 在字体 {font_type} 中存在")
                    sys.exit(0)
                else:
                    logger.error(f"Glyph '{args.glyph_name}' 在字体 {font_type} 中不存在")
                    sys.exit(1)
            except ImportError:
                logger.error("需要安装fontTools库来检查glyphs。使用 pip install fontTools 安装。")
                sys.exit(1)
            except Exception as e:
                logger.error(f"检查glyph过程中发生错误: {str(e)}")
                sys.exit(1)
        else:
            parser.print_help()
            sys.exit(1)
    
    # 处理build-with-glyphs命令
    elif args.command == "build-with-glyphs":
        from .__init__ import build_with_custom_glyphs
        
        try:
            success = build_with_custom_glyphs(
                glyphs=args.glyphs or [],
                force_rebuild=args.force,
                verbose=args.verbose
            )
            if success:
                logger.debug("包含自定义glyphs的字体构建成功")
                sys.exit(0)
            else:
                logger.error("包含自定义glyphs的字体构建失败")
                sys.exit(1)
        except Exception as e:
            logger.error(f"构建包含自定义glyphs的字体过程中发生错误: {str(e)}")
            sys.exit(1)
        
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()