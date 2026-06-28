"""
节次格式化工具
吉利学院一天11节课：上午5节、下午4节、晚上2节
标准表示：1-2、3-4、5-6、6-7、7-8、8-9、10-11 等
"""

import re

# 上午5节(1-5)、下午4节(6-9)、晚上2节(10-11) 的常见配对
STANDARD_PAIRS = ("1-2", "3-4", "5-6", "6-7", "7-8", "8-9", "10-11")


def normalize_period(period: str) -> str:
    """将节次统一为 X-Y 格式（如 1-2、6-7）"""
    if not period:
        return ""

    s = period.strip().replace("节", "").replace(" ", "")
    s = re.sub(r"[一—–~～至]", "-", s)

    # 已是 X-Y 或 X-Y-Z 范围
    if re.match(r"^\d+-\d+(-\d+)?$", s):
        return s

    # 单个数字 → 匹配标准节次对
    if re.match(r"^\d+$", s):
        n = int(s)
        for pair in STANDARD_PAIRS:
            start, end = pair.split("-")
            if n == int(start) or n == int(end):
                return pair
        if n % 2 == 1 and n < 11:
            return f"{n}-{n + 1}"
        if n == 5:
            return "5-6"
        if n == 11:
            return "10-11"

    return s
