from typing import Literal


def format_number(number: int | float, decimal_values=2, seperator=True, local_us=False) -> str:
    sep = ',' if seperator else ''
    negative = number < 0
    major, minor = [str(v) for v in str(float(number)).split('.')]
    major = int(major)
    str_number = f"{'-' if negative and not major else ''}{major}"
    if minor and int(str(minor)[:decimal_values] or 0):
        str_number += f'.{minor[:decimal_values]}'
        str_number = f"{float(str_number):{sep}}"
    else:
        if not major:
            return "0"
        str_number = f"{int(str_number):{sep}}"
    if local_us:
        return str_number
    return str_number.replace(',', '?').replace('.', ',').replace('?', '.')


def format_second(seconds: int, short=True) -> str:
    time_units = {
        "w": ("week", "week"),
        "d": ("day", "day"),
        "h": ("hour", "hour"),
        "m": ("min", "minute"),
        "s": ("sec", "second"),
    }
    units = [("w", 7 * 24 * 3600), ("d", 24 * 3600), ("h", 3600), ("m", 60), ("s", 1)]
    parts = []
    for unit, divisor in units:
        value, seconds = divmod(seconds, divisor)
        if value:
            idx = 0 if short else 1
            plural_s = "s" if value > 1 else ""
            unit_name = time_units[unit][idx] + plural_s
            parts.append(f"{value}{unit_name}")
    return " ".join(parts) if parts else "now"


_TimestampType = Literal["t", "T", "d", "D", "f", "F", "R"]


def format_timestamp(seconds: int, key: _TimestampType = 'R') -> str:
    """
    Format a timestamp based on the specified key.
    - 't': "short time"
    - 'T': "long time"
    - 'd': "short date"
    - 'D': "long date"
    - 'f': "long date with short time"
    - 'F': "long date with day of the week and short time"
    - 'R': "relative"
    """
    return f"<t:{seconds}:{key}>"
