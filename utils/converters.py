from typing import Union, Tuple
import re
import datetime
from typing import Optional


class PersianNumbersConverter:
    @staticmethod
    def to_persian(text: str) -> str:
        """تبدیل اعداد انگلیسی به فارسی"""
        numbers = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
        }
        return ''.join(numbers.get(c, c) for c in text)


class persian_numbers:
    @staticmethod
    def to_jalali(dt: Union[datetime.datetime, datetime.date, str, Tuple[int, int, int]]) -> str:
        """
        تبدیل تاریخ میلادی به شمسی
        پارامترهای ورودی:
        - datetime.datetime یا datetime.date
        - رشته به فرمت 'YYYY-MM-DD'
        - تاپل (سال, ماه, روز)

        خروجی: رشته تاریخ شمسی به فرمت 'YYYY/MM/DD'
        """
        # تبدیل انواع ورودی به سال، ماه، روز میلادی
        if isinstance(dt, (datetime.datetime, datetime.date)):
            year, month, day = dt.year, dt.month, dt.day
        elif isinstance(dt, str):
            m = re.match(r'^(\d{4})\D(\d{1,2})\D(\d{1,2})$', dt)
            if not m:
                raise ValueError("فرمت تاریخ نامعتبر. باید YYYY-MM-DD باشد")
            year, month, day = map(int, m.groups())
        elif isinstance(dt, tuple) and len(dt) == 3:
            year, month, day = dt
        else:
            raise TypeError("نوع ورودی نامعتبر")

        # اعتبارسنجی تاریخ میلادی
        try:
            datetime.datetime(year, month, day)
        except ValueError:
            raise ValueError("تاریخ میلادی نامعتبر")

        # الگوریتم تبدیل میلادی به شمسی
        d_4 = year % 4
        g_a = [0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        doy_g = g_a[month] + day
        if d_4 == 0 and month > 2:
            doy_g += 1

        d_33 = int(((year - 16) % 132) * 0.0305)
        a = 286 if (d_33 == 3 or d_33 < (d_4 - 1) or d_4 == 0) else 287
        if (d_33 == 1 or d_33 == 2) and (d_33 == d_4 or d_4 == 1):
            b = 78
        else:
            b = 80 if (d_33 == 3 and d_4 == 0) else 79

        if int((year - 10) / 63) == 30:
            a -= 1
            b += 1

        if doy_g > b:
            jy = year - 621
            doy_j = doy_g - b
        else:
            jy = year - 622
            doy_j = doy_g + a

        if doy_j < 187:
            jm = int((doy_j - 1) / 31)
            jd = doy_j - (31 * jm)
            jm += 1
        else:
            jm = int((doy_j - 187) / 30)
            jd = doy_j - 186 - (jm * 30)
            jm += 7

        return f"{jy}/{jm:02d}/{jd:02d}"

    @staticmethod
    def to_gregorian(jalali_date: Union[str, Tuple[int, int, int]]) -> datetime.date:
        """
        تبدیل تاریخ شمسی به میلادی
        پارامترهای ورودی:
        - رشته به فرمت 'YYYY/MM/DD'
        - تاپل (سال, ماه, روز)

        خروجی: شیء datetime.date
        """
        # تبدیل انواع ورودی به سال، ماه، روز شمسی
        if isinstance(jalali_date, str):
            m = re.match(r'^(\d{4})\D(\d{1,2})\D(\d{1,2})$', jalali_date)
            if not m:
                raise ValueError("فرمت تاریخ نامعتبر. باید YYYY/MM/DD باشد")
            year, month, day = map(int, m.groups())
        elif isinstance(jalali_date, tuple) and len(jalali_date) == 3:
            year, month, day = jalali_date
        else:
            raise TypeError("نوع ورودی نامعتبر")

        # اعتبارسنجی تاریخ شمسی
        if year < 1 or month < 1 or month > 12 or day < 1 or day > 31 or (month > 6 and day == 31):
            raise ValueError("تاریخ شمسی نامعتبر")

        # الگوریتم تبدیل شمسی به میلادی
        d_4 = (year + 1) % 4
        if month < 7:
            doy_j = ((month - 1) * 31) + day
        else:
            doy_j = ((month - 7) * 30) + day + 186

        d_33 = int(((year - 55) % 132) * 0.0305)
        a = 287 if (d_33 != 3 and d_4 <= d_33) else 286
        if (d_33 == 1 or d_33 == 2) and (d_33 == d_4 or d_4 == 1):
            b = 78
        else:
            b = 80 if (d_33 == 3 and d_4 == 0) else 79

        if int((year - 19) / 63) == 20:
            a -= 1
            b += 1

        if doy_j <= a:
            gy = year + 621
            gd = doy_j + b
        else:
            gy = year + 622
            gd = doy_j - a

        for gm, v in enumerate([0, 31, 29 if (gy % 4 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]):
            if gd <= v:
                break
            gd -= v

        return datetime.date(gy, gm, gd)

    @staticmethod
    def persian_numbers(text: str) -> str:
        """تبدیل اعداد انگلیسی به فارسی"""
        numbers = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
        }
        return ''.join(numbers.get(c, c) for c in text)

    @staticmethod
    def format_jalali(dt: datetime.datetime, with_time: bool = False) -> str:
        """
        قالب‌بندی تاریخ میلادی به شمسی زیبا
        مثال: ۱۴۰۳/۰۴/۱۵ -- ۱۴:۳۰
        """
        jalali_date = persian_numbers.to_jalali(dt)
        if with_time:
            time_part = f" -- {dt.hour:02d}:{dt.minute:02d}"
        else:
            time_part = ""
        return persian_numbers.persian_numbers(f"{jalali_date}{time_part}")
