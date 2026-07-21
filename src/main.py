import sys

import flet as ft

from ui.layout import Layout
from utils.error_log import logger, setup_global_exception_handler

setup_global_exception_handler()


def main(page: ft.Page):
    try:
        page.title = "阿星的小助手"
        page.window.width = 900
        page.window.height = 700
        page.add(Layout())
        page.update()

    except KeyboardInterrupt:
        logger.warning("用户手动中断程序 (Ctrl+C)")
        sys.exit(0)
    except Exception:
        logger.exception("💥 程序发生未捕获的致命异常")
        sys.exit(1)


if __name__ == "__main__":
    ft.run(main)
