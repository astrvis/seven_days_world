import logging
import sys
import threading

logger = logging.getLogger("ConfigManager")


def setup_global_exception_handler(log_file: str = "error.log"):
    """初始化全局异常钩子，必须在程序入口处最先调用"""

    if not logger.handlers:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
        )
        logger.addHandler(fh)
        # ========== 新增：控制台输出处理器 ==========
        sh = logging.StreamHandler(stream=sys.stdout)
        # 控制台可以用精简格式，和文件区分
        sh.setFormatter(logging.Formatter("%(levelname)-8s | %(message)s"))
        logger.addHandler(sh)
        # ==========================================
        logger.setLevel(logging.DEBUG)

    def global_exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        try:
            logger.critical(
                "🔴 未捕获的全局异常: %s",
                exc_value,
                exc_info=(exc_type, exc_value, exc_traceback),
            )
        except Exception as log_err:
            print(f"[FATAL] 日志写入失败: {log_err}", file=sys.stderr)
            print(
                f"[FATAL] 原始异常: {exc_type.__name__}: {exc_value}", file=sys.stderr
            )

    def thread_exception_handler(args):
        try:
            logger.critical(
                "🧵 线程 [%s] 未捕获异常: %s",
                args.thread.name,
                args.exc_value,
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
            )
        except Exception as log_err:
            print(f"[FATAL] 线程日志写入失败: {log_err}", file=sys.stderr)
            print(
                f"[FATAL] 原始异常: {args.exc_type.__name__}: {args.exc_value}",
                file=sys.stderr,
            )

    sys.excepthook = global_exception_handler
    if hasattr(threading, "excepthook"):
        threading.excepthook = thread_exception_handler
