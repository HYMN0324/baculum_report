"""설정 관리 모듈

.env 파일에서 설정을 로드하고 검증하는 기능을 제공합니다.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    """설정 관련 예외"""
    pass


class Config:
    """애플리케이션 설정 클래스

    .env 파일에서 설정을 로드하고 필수 값을 검증합니다.
    """

    def __init__(self, env_file: Optional[str] = None):
        """Config 초기화

        Args:
            env_file: .env 파일 경로. None이면 프로젝트 루트의 .env 사용
        """
        if env_file is None:
            # 프로젝트 루트 디렉토리의 .env 파일 사용
            project_root = Path(__file__).parent.parent.parent
            env_file = project_root / '.env'

        # .env 파일 로드
        if not Path(env_file).exists():
            raise ConfigError(
                f".env 파일을 찾을 수 없습니다: {env_file}. "
                f".env.example을 참고하여 .env 파일을 생성하세요."
            )

        load_dotenv(env_file)

        # 필수 설정 검증
        self._validate_required_settings()

    def _validate_required_settings(self):
        """필수 설정 항목 검증

        Raises:
            ConfigError: 필수 설정이 없거나 잘못된 경우
        """
        required_settings = [
            'BACULUM_API_HOST',
            'BACULUM_API_PORT',
            'BACULUM_API_USERNAME',
            'BACULUM_API_PASSWORD',
        ]

        missing = []
        for setting in required_settings:
            value = os.getenv(setting)
            if not value:
                missing.append(setting)

        if missing:
            raise ConfigError(
                f"필수 설정이 누락되었습니다: {', '.join(missing)}. "
                f".env 파일을 확인하세요."
            )

        # 포트 번호 검증
        try:
            port = int(os.getenv('BACULUM_API_PORT'))
            if port < 1 or port > 65535:
                raise ValueError
        except (TypeError, ValueError):
            raise ConfigError(
                "BACULUM_API_PORT는 1-65535 사이의 정수여야 합니다."
            )

    @property
    def api_host(self) -> str:
        """API 호스트 주소"""
        return os.getenv('BACULUM_API_HOST')

    @property
    def api_port(self) -> int:
        """API 포트 번호"""
        return int(os.getenv('BACULUM_API_PORT'))

    @property
    def api_username(self) -> str:
        """API 사용자명"""
        return os.getenv('BACULUM_API_USERNAME')

    @property
    def api_password(self) -> str:
        """API 비밀번호"""
        return os.getenv('BACULUM_API_PASSWORD')

    @property
    def api_timeout(self) -> int:
        """API 타임아웃 (초)"""
        return int(os.getenv('BACULUM_API_TIMEOUT', '10'))

    @property
    def api_max_retries(self) -> int:
        """API 최대 재시도 횟수"""
        return int(os.getenv('BACULUM_API_MAX_RETRIES', '3'))

    @property
    def log_level(self) -> str:
        """로그 레벨"""
        return os.getenv('LOG_LEVEL', 'INFO').upper()

    def get_baculum_client_config(self) -> dict:
        """BaculaClient 초기화에 필요한 설정 딕셔너리 반환

        Returns:
            BaculaClient 생성자에 전달할 설정 딕셔너리
        """
        return {
            'api_host': self.api_host,
            'api_port': self.api_port,
            'username': self.api_username,
            'password': self.api_password,
            'timeout': self.api_timeout,
            'max_retries': self.api_max_retries,
        }
