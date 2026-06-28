"""
校历服务：根据日期智能识别教学周数
"""

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional, Union

CALENDAR_PATH = Path(__file__).resolve().parent.parent / "data" / "school_calendar.json"

_calendar_cache: Optional[dict] = None


def _load_calendar() -> dict:
    global _calendar_cache
    if _calendar_cache is None:
        with open(CALENDAR_PATH, encoding="utf-8") as f:
            _calendar_cache = json.load(f)
    return _calendar_cache


def parse_date(value: str) -> Optional[date]:
    """解析 YYYY-MM-DD 或 M.D 格式日期"""
    if not value:
        return None
    value = value.strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", value)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"^(\d{1,2})[.\-/](\d{1,2})$", value)
    if m:
        cal = _load_calendar()
        year = date.fromisoformat(cal["semester_start"]).year
        return date(year, int(m.group(1)), int(m.group(2)))
    return None


def get_week_number(date_value: Union[str, date]) -> Optional[int]:
    """
    根据校历计算教学周数。
    以学期起始周的周一为第1周，遇节假日不顺延（与教务系统周次一致）。
    """
    cal = _load_calendar()
    semester_start = date.fromisoformat(cal["semester_start"])
    max_weeks = cal.get("max_weeks", 20)

    if isinstance(date_value, str):
        dt = parse_date(date_value)
    else:
        dt = date_value

    if dt is None:
        return None

    if dt < semester_start:
        return None

    days = (dt - semester_start).days
    week = days // 7 + 1
    return min(week, max_weeks) if week >= 1 else None


def get_week_date_range(week_number: int) -> tuple[Optional[date], Optional[date]]:
    """返回指定教学周的起止日期（周一至周日）"""
    cal = _load_calendar()
    semester_start = date.fromisoformat(cal["semester_start"])
    if week_number < 1:
        return None, None
    week_start = semester_start + timedelta(days=(week_number - 1) * 7)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def get_calendar_info() -> dict:
    """返回校历元信息"""
    cal = _load_calendar()
    return {
        "name": cal.get("name", ""),
        "semester_start": cal.get("semester_start", ""),
        "max_weeks": cal.get("max_weeks", 20),
    }
