"""커맨드 베이스 클래스

모든 커맨드가 상속받아야 하는 추상 베이스 클래스를 정의합니다.
"""

import logging
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import Optional

from src.utils.config import Config, ConfigError
from src.utils.logger import setup_logger


class BaseCommand(ABC):
    """커맨드 베이스 클래스

    모든 커맨드 클래스가 상속받아야 하는 추상 베이스 클래스입니다.
    공통 초기화 로직(로거, 설정 로드 등)을 제공합니다.

    Attributes:
        name: 커맨드 이름
        description: 커맨드 설명
        config: 애플리케이션 설정 객체
        logger: 로거 인스턴스
    """

    def __init__(self, name: str, description: str):
        """BaseCommand 초기화

        Args:
            name: 커맨드 이름
            description: 커맨드 설명
        """
        self.name = name
        self.description = description
        self.config: Optional[Config] = None
        self.logger: Optional[logging.Logger] = None

    def setup(self, args: Namespace) -> None:
        """커맨드 초기 설정

        로거 및 설정을 초기화합니다.

        Args:
            args: 파싱된 커맨드 라인 인자

        Raises:
            ConfigError: 설정 로드 실패 시
        """
        # 로그 레벨 설정
        log_level = 'DEBUG' if getattr(args, 'verbose', False) else 'INFO'

        # 로거 초기화
        self.logger = setup_logger('baculum', log_level=log_level)

        # 설정 로드
        try:
            self.config = Config()
            self.logger.info("✓ 설정 로드 완료")
        except ConfigError as e:
            self.logger.error(f"✗ 설정 로드 실패: {e}")
            raise

    @abstractmethod
    def setup_args(self, parser: ArgumentParser) -> None:
        """커맨드별 CLI 인자 설정

        각 커맨드에서 필요한 CLI 인자를 정의합니다.

        Args:
            parser: ArgumentParser 인스턴스
        """
        pass

    @abstractmethod
    def execute(self, args: Namespace) -> int:
        """커맨드 실행

        실제 커맨드 로직을 구현합니다.

        Args:
            args: 파싱된 커맨드 라인 인자

        Returns:
            종료 코드 (0: 성공, 1: 실패)
        """
        pass

    def run(self, args: Namespace) -> int:
        """커맨드 실행 워크플로우

        설정 초기화 → 커맨드 실행 순서로 진행합니다.

        Args:
            args: 파싱된 커맨드 라인 인자

        Returns:
            종료 코드 (0: 성공, 1: 실패)
        """
        try:
            # 초기 설정
            self.setup(args)

            # 커맨드 실행
            return self.execute(args)

        except KeyboardInterrupt:
            if self.logger:
                self.logger.warning("")
                self.logger.warning("사용자에 의해 중단되었습니다.")
            return 1
        except Exception as e:
            if self.logger:
                self.logger.error(f"예상치 못한 오류 발생: {e}", exc_info=True)
            return 1
