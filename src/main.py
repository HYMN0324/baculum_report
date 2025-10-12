"""Bacula 백업 리포트 생성 메인 프로그램

백업 작업 정보를 조회하여 HTML 리포트를 생성합니다.
"""

import sys
import argparse
import time
from datetime import datetime
from typing import List

from src.api.bacula_client import BaculaClient, BaculaAPIError
from src.models.backup_job import BackupJob
from src.report.report_generator import ReportGenerator, ReportGeneratorError
from src.mail.email_sender import EmailSender, EmailSendError
from src.utils.config import Config, ConfigError
from src.utils.logger import setup_logger
from src.utils.datetime_helper import (
    get_test_period,
    get_production_period,
    format_datetime_display
)


def parse_arguments() -> argparse.Namespace:
    """커맨드 라인 인자 파싱

    Returns:
        파싱된 인자 객체
    """
    parser = argparse.ArgumentParser(
        description='Bacula 백업 리포트 생성 프로그램',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
사용 예시:
  # 테스트 모드 (최근 1주일 데이터)
  python src/main.py --mode test

  # 프로덕션 모드 (전일 22시 ~ 현재)
  python src/main.py --mode production

  # 상세 로그 출력
  python src/main.py --mode test --verbose
        '''
    )

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

    return parser.parse_args()


def main() -> int:
    """메인 실행 함수

    Returns:
        종료 코드 (0: 성공, 1: 실패)
    """
    # 커맨드 라인 인자 파싱
    args = parse_arguments()

    # 로그 레벨 설정
    log_level = 'DEBUG' if args.verbose else 'INFO'

    # 로거 초기화
    logger = setup_logger('baculum', log_level=log_level)

    try:
        logger.info("=" * 60)
        logger.info("Bacula 백업 리포트 생성 시작")
        logger.info("=" * 60)
        logger.info(f"실행 모드: {args.mode}")
        logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        start_time = time.time()

        # 1. 설정 로드
        logger.info("")
        logger.info("[1/4] 설정 로드 중...")
        try:
            config = Config()
            logger.info("✓ 설정 로드 완료")
        except ConfigError as e:
            logger.error(f"✗ 설정 로드 실패: {e}")
            return 1

        # 2. API 연결 및 데이터 수집
        logger.info("")
        logger.info("[2/4] Bacula API 연결 및 데이터 수집 중...")
        try:
            # BaculaClient 생성
            client = BaculaClient(**config.get_baculum_client_config())

            # API 연결 테스트
            client.connect()
            logger.info("✓ API 연결 성공")

            # 조회 기간 설정
            if args.mode == 'test':
                start_period, end_period = get_test_period()
                logger.info("테스트 모드: 최근 1주일 데이터 조회")
            else:
                start_period, end_period = get_production_period()
                logger.info("프로덕션 모드: 전일 22시 ~ 현재 데이터 조회")

            logger.info(
                f"조회 기간: {format_datetime_display(start_period)} ~ "
                f"{format_datetime_display(end_period)}"
            )

            # 백업 작업 조회 - 레벨별로 나누어 조회
            api_start = time.time()

            logger.info("백업 레벨별 작업 조회 중...")

            # Full 백업 조회
            full_jobs_data = client.get_jobs(
                start_period, end_period, level='F', type='B'
            )
            logger.info(f"  Full 백업: {len(full_jobs_data)}건")

            # Incremental 백업 조회
            incremental_jobs_data = client.get_jobs(
                start_period, end_period, level='I', type='B'
            )
            logger.info(f"  Incremental 백업: {len(incremental_jobs_data)}건")

            # Differential 백업 조회
            differential_jobs_data = client.get_jobs(
                start_period, end_period, level='D', type='B'
            )
            logger.info(f"  Differential 백업: {len(differential_jobs_data)}건")

            # 모든 작업 합치기
            jobs_data = full_jobs_data + incremental_jobs_data + differential_jobs_data
            api_elapsed = time.time() - api_start

            logger.info(f"✓ 백업 작업 총 {len(jobs_data)}건 조회 완료")
            logger.info(f"  API 호출 시간: {api_elapsed:.2f}초")

            if api_elapsed > 10:
                logger.warning(
                    f"⚠ API 호출 시간이 10초를 초과했습니다: {api_elapsed:.2f}초"
                )

        except BaculaAPIError as e:
            logger.error(f"✗ API 오류: {e}")
            return 1
        except Exception as e:
            logger.error(f"✗ 데이터 수집 실패: {e}", exc_info=True)
            return 1

        # 3. 데이터 가공
        logger.info("")
        logger.info("[3/4] 데이터 가공 중...")
        try:
            jobs: List[BackupJob] = []
            parse_errors = 0

            for job_data in jobs_data:
                try:
                    job = BackupJob.from_api_response(job_data)
                    jobs.append(job)
                except ValueError as e:
                    logger.warning(f"작업 데이터 파싱 실패: {e}")
                    parse_errors += 1

            logger.info(f"✓ 데이터 가공 완료: {len(jobs)}건")
            if parse_errors > 0:
                logger.warning(f"  파싱 실패: {parse_errors}건")

            # 통계 출력
            success_count = sum(1 for job in jobs if job.is_success)
            failed_count = sum(1 for job in jobs if job.is_failed)
            running_count = sum(1 for job in jobs if job.is_running)
            canceled_count = sum(1 for job in jobs if job.is_canceled)

            logger.info(f"  성공: {success_count}건")
            logger.info(f"  실패: {failed_count}건")
            logger.info(f"  실행 중: {running_count}건")
            logger.info(f"  취소됨: {canceled_count}건")

        except Exception as e:
            logger.error(f"✗ 데이터 가공 실패: {e}", exc_info=True)
            return 1

        # 4. 리포트 생성
        logger.info("")
        logger.info("[4/5] HTML 리포트 생성 중..." if args.send_mail else "[4/4] HTML 리포트 생성 중...")
        try:
            generator = ReportGenerator()
            report_path = generator.generate_report(
                jobs=jobs,
                start_period=start_period,
                end_period=end_period,
                filename=args.output
            )
            logger.info("✓ 리포트 생성 완료")
            logger.info(f"  파일 경로: {report_path}")

        except ReportGeneratorError as e:
            logger.error(f"✗ 리포트 생성 실패: {e}")
            return 1
        except Exception as e:
            logger.error(f"✗ 리포트 생성 실패: {e}", exc_info=True)
            return 1

        # 5. 메일 발송 (옵션)
        if args.send_mail:
            logger.info("")
            logger.info("[5/5] 이메일 발송 중...")
            try:
                # 메일 설정 확인
                if not config.has_mail_config():
                    logger.warning("⚠ 메일 설정이 불완전합니다. 이메일 발송을 건너뜁니다.")
                    logger.warning("  .env 파일에서 SMTP 관련 설정을 확인하세요.")
                else:
                    # EmailSender 생성
                    email_sender = EmailSender(**config.get_email_sender_config())

                    # 리포트 날짜 (파일명에서 추출 또는 현재 날짜)
                    report_date = end_period.strftime('%Y-%m-%d')

                    # 메일 발송
                    email_sender.send_report_email(
                        to_email=config.mail_to,
                        report_path=report_path,
                        report_date=report_date
                    )
                    logger.info("✓ 이메일 발송 완료")
                    logger.info(f"  수신자: {config.mail_to}")

            except EmailSendError as e:
                logger.error(f"✗ 이메일 발송 실패: {e}")
                logger.warning("  리포트는 생성되었지만 이메일 발송에 실패했습니다.")
                # 메일 발송 실패해도 프로그램은 성공으로 처리
            except Exception as e:
                logger.error(f"✗ 이메일 발송 중 예상치 못한 오류: {e}", exc_info=True)
                logger.warning("  리포트는 생성되었지만 이메일 발송에 실패했습니다.")

        # 실행 시간 출력
        elapsed = time.time() - start_time
        logger.info("")
        logger.info("=" * 60)
        logger.info("백업 리포트 생성 완료!")
        if args.send_mail and config.has_mail_config():
            logger.info("이메일 발송 완료!")
        logger.info(f"총 실행 시간: {elapsed:.2f}초")
        logger.info("=" * 60)

        return 0

    except KeyboardInterrupt:
        logger.warning("")
        logger.warning("사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
