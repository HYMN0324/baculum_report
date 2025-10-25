"""리포트 생성 커맨드

백업 리포트를 생성하고 선택적으로 이메일로 발송하는 커맨드입니다.
"""

import time
from argparse import ArgumentParser, Namespace
from datetime import datetime
from typing import List

from src.commands.base import BaseCommand
from src.api.client import BaculaClient, BaculaAPIError
from src.services.backup import BackupService
from src.models.backup_job import BackupJob
from src.report.generator import ReportGenerator, ReportGeneratorError
from src.mail.sender import EmailSender, EmailSendError


class ReportCommand(BaseCommand):
    """리포트 생성 커맨드

    백업 작업 정보를 조회하여 HTML 리포트를 생성하고,
    선택적으로 이메일로 발송합니다.
    """

    def __init__(self):
        """ReportCommand 초기화"""
        super().__init__(
            name='report',
            description='백업 리포트를 생성하고 선택적으로 이메일로 발송합니다.'
        )

    def setup_args(self, parser: ArgumentParser) -> None:
        """리포트 커맨드 CLI 인자 설정

        Args:
            parser: ArgumentParser 인스턴스
        """
        parser.add_argument(
            '--mode',
            choices=['test', 'production'],
            default='test',
            help='실행 모드 (test: 1주일 데이터, production: 전일 22시~현재)'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='상세 로그 출력 (DEBUG 레벨)'
        )

        parser.add_argument(
            '--output',
            help='출력 파일명 (지정하지 않으면 자동 생성: mail_YYYYMMDDHHMMSS.html)'
        )

        parser.add_argument(
            '--send-mail',
            action='store_true',
            help='리포트를 이메일로 발송 (.env에 메일 설정 필요)'
        )

    def execute(self, args: Namespace) -> int:
        """리포트 생성 실행

        Args:
            args: 파싱된 커맨드 라인 인자

        Returns:
            종료 코드 (0: 성공, 1: 실패)
        """
        self.logger.info("=" * 60)
        self.logger.info("Bacula 백업 리포트 생성 시작")
        self.logger.info("=" * 60)
        self.logger.info(f"실행 모드: {args.mode}")
        self.logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        start_time = time.time()

        # 1. API 연결 및 데이터 수집
        self.logger.info("")
        self.logger.info("[1/3] Bacula API 연결 및 데이터 수집 중..." if not args.send_mail
                         else "[1/4] Bacula API 연결 및 데이터 수집 중...")

        try:
            # BaculaClient 및 BackupService 생성
            client = BaculaClient(**self.config.get_baculum_client_config())
            client.connect()
            self.logger.info("✓ API 연결 성공")

            backup_service = BackupService(client)

            # 백업 작업 조회 (서비스 레이어 사용)
            jobs, start_period, end_period = backup_service.get_jobs_by_period(args.mode)

        except BaculaAPIError as e:
            self.logger.error(f"✗ API 오류: {e}")
            return 1
        except Exception as e:
            self.logger.error(f"✗ 데이터 수집 실패: {e}", exc_info=True)
            return 1

        # 2. 리포트 생성
        self.logger.info("")
        self.logger.info("[2/3] HTML 리포트 생성 중..." if not args.send_mail
                         else "[2/4] HTML 리포트 생성 중...")

        try:
            report_path = self._generate_report(jobs, start_period, end_period, args.output)
        except ReportGeneratorError as e:
            self.logger.error(f"✗ 리포트 생성 실패: {e}")
            return 1
        except Exception as e:
            self.logger.error(f"✗ 리포트 생성 실패: {e}", exc_info=True)
            return 1

        # 3. 메일 발송 (옵션)
        if args.send_mail:
            self.logger.info("")
            self.logger.info("[3/4] 이메일 발송 중...")

            try:
                self._send_email(report_path, end_period)
            except EmailSendError as e:
                self.logger.error(f"✗ 이메일 발송 실패: {e}")
                self.logger.warning("  리포트는 생성되었지만 이메일 발송에 실패했습니다.")
            except Exception as e:
                self.logger.error(f"✗ 이메일 발송 중 예상치 못한 오류: {e}", exc_info=True)
                self.logger.warning("  리포트는 생성되었지만 이메일 발송에 실패했습니다.")

        # 실행 시간 출력
        elapsed = time.time() - start_time
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("백업 리포트 생성 완료!")
        if args.send_mail and self.config.has_mail_config():
            self.logger.info("이메일 발송 완료!")
        self.logger.info(f"총 실행 시간: {elapsed:.2f}초")
        self.logger.info("=" * 60)

        return 0

    def _generate_report(
        self,
        jobs: List[BackupJob],
        start_period: datetime,
        end_period: datetime,
        filename: str = None
    ) -> str:
        """리포트 생성

        Args:
            jobs: 백업 작업 리스트
            start_period: 조회 시작 시간
            end_period: 조회 종료 시간
            filename: 출력 파일명

        Returns:
            생성된 리포트 파일 경로

        Raises:
            ReportGeneratorError: 리포트 생성 실패 시
        """
        generator = ReportGenerator(config=self.config)
        report_path = generator.generate_report(
            jobs=jobs,
            start_period=start_period,
            end_period=end_period,
            filename=filename
        )
        self.logger.info("✓ 리포트 생성 완료")
        self.logger.info(f"  파일 경로: {report_path}")

        return report_path

    def _send_email(self, report_path: str, end_period: datetime) -> None:
        """이메일 발송

        Args:
            report_path: 리포트 파일 경로
            end_period: 리포트 종료 날짜

        Raises:
            EmailSendError: 이메일 발송 실패 시
        """
        # 메일 설정 확인
        if not self.config.has_mail_config():
            self.logger.warning("⚠ 메일 설정이 불완전합니다. 이메일 발송을 건너뜁니다.")
            self.logger.warning("  .env 파일에서 SMTP 관련 설정을 확인하세요.")
            return

        # EmailSender 생성
        email_sender = EmailSender(**self.config.get_email_sender_config())

        # 리포트 날짜
        report_date = end_period.strftime('%Y-%m-%d')

        # 메일 발송
        email_sender.send_report_email(
            to_email=self.config.mail_to,
            report_path=report_path,
            report_date=report_date
        )
        self.logger.info("✓ 이메일 발송 완료")
        self.logger.info(f"  수신자: {self.config.mail_to}")
