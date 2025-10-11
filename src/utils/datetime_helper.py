"""날짜/시간 관련 유틸리티 모듈

백업 작업 조회 기간 계산 및 타임스탬프 포맷팅 기능을 제공합니다.
"""

from datetime import datetime, timedelta
from typing import Tuple


def get_test_period() -> Tuple[datetime, datetime]:
    """테스트 모드 조회 기간 계산

    1주일 전부터 현재까지의 시간 범위를 반환합니다.

    Returns:
        (시작 시간, 종료 시간) 튜플
    """
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    return start_time, end_time


def get_production_period() -> Tuple[datetime, datetime]:
    """프로덕션 모드 조회 기간 계산

    전일 22시부터 현재까지의 시간 범위를 반환합니다.

    Returns:
        (시작 시간, 종료 시간) 튜플
    """
    end_time = datetime.now()
    yesterday = end_time - timedelta(days=1)
    start_time = yesterday.replace(hour=22, minute=0, second=0, microsecond=0)
    return start_time, end_time


def format_timestamp(dt: datetime = None) -> str:
    """타임스탬프를 리포트 파일명 형식으로 변환

    YYYYMMDDHHMMSS 형식의 문자열을 반환합니다.

    Args:
        dt: 변환할 datetime 객체. None이면 현재 시간 사용

    Returns:
        YYYYMMDDHHMMSS 형식의 문자열

    Example:
        >>> format_timestamp(datetime(2025, 10, 11, 14, 30, 45))
        '20251011143045'
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y%m%d%H%M%S')


def format_datetime_display(dt: datetime) -> str:
    """날짜/시간을 화면 표시용 형식으로 변환

    YYYY-MM-DD HH:MM:SS 형식의 문자열을 반환합니다.

    Args:
        dt: 변환할 datetime 객체

    Returns:
        YYYY-MM-DD HH:MM:SS 형식의 문자열

    Example:
        >>> format_datetime_display(datetime(2025, 10, 11, 14, 30, 45))
        '2025-10-11 14:30:45'
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def parse_datetime(datetime_str: str) -> datetime:
    """문자열을 datetime 객체로 변환

    여러 날짜/시간 형식을 지원합니다.

    Args:
        datetime_str: 날짜/시간 문자열

    Returns:
        datetime 객체

    Raises:
        ValueError: 지원하지 않는 형식인 경우
    """
    # 시도할 형식 목록
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue

    raise ValueError(
        f"지원하지 않는 날짜/시간 형식: {datetime_str}. "
        f"지원 형식: {', '.join(formats)}"
    )
