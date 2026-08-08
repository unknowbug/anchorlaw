"""Out-of-line anchor registrations for tools/ scripts (§6.2 registry interop).

验证载体：check_encoding.py 每次被运行即产生可公共观测结论
（`python tools/check_encoding.py`，退出码 0/1 + 逐文件 UTF-8 判定）。
"""

from anchorlaw_scanner import register_anchored_function

# 直接字符串调用形式——scanner 的 registry 互操作（§6.2）按此正则加载
register_anchored_function("collect_targets")  # 路径收集：纯逻辑，全量运行验证
register_anchored_function("check_file")  # UTF-8 解码检查：I/O 函数，脚本自验证（退出码即结论）
register_anchored_function("main")  # 入口：I/O 编排，一次运行给出确定性结论（v0.9 终止门禁 B）
