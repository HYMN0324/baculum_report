"""로깅 설정 모듈

애플리케이션 전체에서 사용할 로거 설정을 제공합니다.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(
    name: str = 'baculum',
    log_level: str = 'INFO',
    log_file: str = None,
    console: bool = True
) -> logging.Logger:
    """로거 설정

    파일 로깅과 콘솔 출력을 설정합니다.

    Args:
        name: 로거 이름
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로. None이면 기본 경로 사용
        console: 콘솔 출력 여부

    Returns:
        설정된 Logger 객체
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # 기존 핸들러 제거 (중복 방지)
    logger.handlers.clear()

    # 로그 포맷
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 파일 핸들러 설정
    if log_file is None:
        # 기본 로그 파일 경로
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        today = datetime.now().strftime('%Y%m%d')
        log_file = log_dir / f'app_{today}.log'

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 콘솔 핸들러 설정
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.info(f"로거 초기화 완료: {name}, 레벨={log_level}")

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """로거 가져오기

    이미 설정된 로거를 가져옵니다.
    설정되지 않았으면 기본 설정으로 생성합니다.

    Args:
        name: 로거 이름. None이면 'baculum' 사용

    Returns:
        Logger 객체
    """
    if name is None:
        name = 'baculum'

    logger = logging.getLogger(name)

    # 로거가 설정되지 않았으면 기본 설정 적용
    if not logger.handlers:
        return setup_logger(name)

    return logger
