"""리포트 생성 모듈

HTML 백업 리포트를 생성하는 기능을 제공합니다.
"""

import logging
from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from datetime import datetime

from ..models.backup_job import BackupJob
from ..models.report_stats import ReportStats
from ..utils.config import Config
from ..utils.datetime_helper import format_timestamp


logger = logging.getLogger(__name__)


class ReportGeneratorError(Exception):
    """리포트 생성 관련 예외"""
    pass


class ReportGenerator:
    """백업 리포트 생성기

    백업 작업 데이터를 HTML 리포트로 생성합니다.

    Attributes:
        config: 애플리케이션 설정 객체
        template_dir: 템플릿 디렉토리 경로
        output_dir: 리포트 출력 디렉토리 경로
        jinja_env: Jinja2 환경 객체
    """

    def __init__(
        self,
        config: Config,
        template_dir: str = None,
        output_dir: str = None
    ):
        """ReportGenerator 초기화

        Args:
            config: 애플리케이션 설정 객체
            template_dir: 템플릿 디렉토리 경로. None이면 기본 경로 사용
            output_dir: 출력 디렉토리 경로. None이면 기본 경로 사용
        """
        self.config = config
        # 프로젝트 루트 기준 경로 설정
        project_root = Path(__file__).parent.parent.parent

        if template_dir is None:
            self.template_dir = project_root / 'templates'
        else:
            self.template_dir = Path(template_dir)

        if output_dir is None:
            self.output_dir = project_root / 'reports'
        else:
            self.output_dir = Path(output_dir)

        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Jinja2 환경 설정
        try:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=True
            )
            logger.info(
                f"ReportGenerator 초기화: "
                f"template={self.template_dir}, "
                f"output={self.output_dir}"
            )
        except Exception as e:
            raise ReportGeneratorError(f"Jinja2 환경 초기화 실패: {e}")

    def generate_report(
        self,
        jobs: List[BackupJob],
        start_period: datetime,
        end_period: datetime,
        filename: str = None
    ) -> str:
        """백업 리포트 생성

        백업 작업 리스트를 받아 HTML 리포트를 생성합니다.

        Args:
            jobs: 백업 작업 리스트
            start_period: 조회 시작 시간
            end_period: 조회 종료 시간
            filename: 출력 파일명. None이면 자동 생성

        Returns:
            생성된 리포트 파일의 절대 경로

        Raises:
            ReportGeneratorError: 리포트 생성 실패 시
        """
        try:
            logger.info(f"리포트 생성 시작: {len(jobs)}개 작업")

            # 통계 생성
            stats = ReportStats.from_jobs(jobs, start_period, end_period)
            logger.debug(f"통계 생성 완료: {stats}")

            # 작업 분류 (type='B'인 Backup 작업만 포함, Restore 작업 제외)
            success_jobs = [
                job for job in jobs
                if job.is_success and job.is_backup
            ]
            failed_jobs = [job for job in jobs if job.is_failed]
            running_jobs = [job for job in jobs if job.is_running]
            canceled_jobs = [job for job in jobs if job.is_canceled]

            logger.debug(
                f"작업 분류: success={len(success_jobs)}, "
                f"failed={len(failed_jobs)}, "
                f"running={len(running_jobs)}, "
                f"canceled={len(canceled_jobs)}"
            )

            # 템플릿 렌더링
            html_content = self._render_template(
                stats=stats,
                success_jobs=success_jobs,
                failed_jobs=failed_jobs,
                running_jobs=running_jobs,
                canceled_jobs=canceled_jobs
            )

            # 파일명 생성
            if filename is None:
                timestamp = format_timestamp()
                filename = f"mail_{timestamp}.html"

            # 파일 저장
            output_path = self.output_dir / filename
            self._save_report(output_path, html_content)

            logger.info(f"리포트 생성 완료: {output_path}")
            return str(output_path.absolute())

        except Exception as e:
            logger.error(f"리포트 생성 실패: {e}", exc_info=True)
            raise ReportGeneratorError(f"리포트 생성 실패: {e}")

    def _render_template(
        self,
        stats: ReportStats,
        success_jobs: List[BackupJob],
        failed_jobs: List[BackupJob],
        running_jobs: List[BackupJob],
        canceled_jobs: List[BackupJob]
    ) -> str:
        """템플릿 렌더링

        Args:
            stats: 통계 객체
            success_jobs: 성공한 작업 리스트
            failed_jobs: 실패한 작업 리스트
            running_jobs: 실행 중인 작업 리스트
            canceled_jobs: 취소된 작업 리스트

        Returns:
            렌더링된 HTML 문자열

        Raises:
            ReportGeneratorError: 템플릿 로드 또는 렌더링 실패 시
        """
        try:
            template = self.jinja_env.get_template('report_template.html')

            # Baculum 웹 URL 구성 (설정이 있는 경우에만)
            baculum_web_url = None
            if self.config.has_baculum_web_config():
                baculum_web_url = (
                    f"http://{self.config.baculum_web_host}:"
                    f"{self.config.baculum_web_port}"
                )

            html_content = template.render(
                stats=stats,
                success_jobs=success_jobs,
                failed_jobs=failed_jobs,
                running_jobs=running_jobs,
                canceled_jobs=canceled_jobs,
                baculum_web_url=baculum_web_url
            )

            logger.debug("템플릿 렌더링 완료")
            return html_content

        except TemplateNotFound as e:
            raise ReportGeneratorError(
                f"템플릿 파일을 찾을 수 없습니다: {e}. "
                f"템플릿 디렉토리: {self.template_dir}"
            )
        except Exception as e:
            raise ReportGeneratorError(f"템플릿 렌더링 실패: {e}")

    def _save_report(self, file_path: Path, content: str) -> None:
        """리포트 파일 저장

        Args:
            file_path: 저장할 파일 경로
            content: 저장할 내용

        Raises:
            ReportGeneratorError: 파일 저장 실패 시
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"파일 저장 완료: {file_path}")
        except IOError as e:
            raise ReportGeneratorError(f"파일 저장 실패: {e}")

    def get_latest_report(self) -> str:
        """최신 리포트 파일 경로 조회

        Returns:
            최신 리포트 파일의 절대 경로. 없으면 None

        Raises:
            ReportGeneratorError: 디렉토리 접근 실패 시
        """
        try:
            report_files = list(self.output_dir.glob('mail_*.html'))
            if not report_files:
                return None

            # 파일명의 타임스탬프로 정렬 (최신순)
            latest_file = sorted(
                report_files,
                key=lambda f: f.name,
                reverse=True
            )[0]

            return str(latest_file.absolute())

        except Exception as e:
            raise ReportGeneratorError(
                f"최신 리포트 조회 실패: {e}"
            )

    def list_reports(self, limit: int = 10) -> List[str]:
        """리포트 파일 목록 조회

        Args:
            limit: 조회할 최대 개수

        Returns:
            리포트 파일 경로 리스트 (최신순)

        Raises:
            ReportGeneratorError: 디렉토리 접근 실패 시
        """
        try:
            report_files = list(self.output_dir.glob('mail_*.html'))

            # 파일명의 타임스탬프로 정렬 (최신순)
            sorted_files = sorted(
                report_files,
                key=lambda f: f.name,
                reverse=True
            )[:limit]

            return [str(f.absolute()) for f in sorted_files]

        except Exception as e:
            raise ReportGeneratorError(f"리포트 목록 조회 실패: {e}")
