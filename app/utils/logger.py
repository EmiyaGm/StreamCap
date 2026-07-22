import os
import sys

from loguru import logger

script_path = os.path.split(os.path.realpath(sys.argv[0]))[0]

# 临时：全项目只输出与自定义脚本相关的日志。恢复全部日志时删掉此过滤，并还原下方 handlers。
_CUSTOM_SCRIPT_FUNCTIONS = frozenset(
    {
        "custom_script_execute",
        "run_script_sync",
        "run_script_async",
        "_log_script_stream",
        "_post_recording_processing",
    }
)
_CUSTOM_SCRIPT_KEYWORDS = (
    "custom script",
    "[custom_script]",
    "script execution",
    "script command",
    "script has no execution",
    "#!/bin/bash",
    "adding script execution",
)


def _allow_custom_script_only(record) -> bool:
    if record["function"] in _CUSTOM_SCRIPT_FUNCTIONS:
        return True
    message = str(record["message"]).lower()
    return any(keyword in message for keyword in _CUSTOM_SCRIPT_KEYWORDS)


logger.remove()
logger.level("STREAM", no=22, color="<blue>")

_CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
_FILE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"

logger.add(
    sys.stderr,
    level="DEBUG",
    format=_CONSOLE_FORMAT,
    filter=_allow_custom_script_only,
    enqueue=True,
)

logger.add(
    f"{script_path}/logs/streamget.log",
    level="DEBUG",
    format=_FILE_FORMAT,
    filter=lambda record: record["level"].name != "STREAM" and _allow_custom_script_only(record),
    serialize=False,
    enqueue=True,
    retention=3,
    rotation="3 MB",
    encoding="utf-8",
)

# play_url / STREAM 日志在仅看自定义脚本时关闭
# logger.add(
#     f"{script_path}/logs/play_url.log",
#     level="STREAM",
#     format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}",
#     filter=lambda i: i["level"].name == "STREAM",
#     serialize=False,
#     enqueue=True,
#     retention=1,
#     rotation="500 KB",
#     encoding="utf-8",
# )
