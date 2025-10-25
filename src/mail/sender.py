"""
이메일 발송 모듈.

Gmail SMTP를 통해 백업 리포트를 HTML 형식으로 발송합니다.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from premailer import transform


logger = logging.getLogger(__name__)


class EmailSendError(Exception):
    """이메일 발송 관련 예외."""
    pass


class EmailSender:
    """
    Gmail SMTP를 이용한 이메일 발송 클래스.

    Attributes:
        smtp_server: SMTP 서버 주소
        smtp_port: SMTP 포트 (587: STARTTLS)
        username: SMTP 인증 사용자명 (Gmail 주소)
        password: SMTP 인증 비밀번호 (Gmail 앱 비밀번호)
        from_email: 발신자 이메일 주소
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: Optional[str] = None
    ):
        """
        EmailSender 초기화.

        Args:
            smtp_server: SMTP 서버 주소 (예: smtp.gmail.com)
            smtp_port: SMTP 포트 (587 또는 465)
            username: SMTP 인증 사용자명
            password: SMTP 인증 비밀번호
            from_email: 발신자 이메일 (미지정 시 username 사용)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email or username

        logger.info(
            f"EmailSender 초기화: {self.smtp_server}:{self.smtp_port}"
        )

    def _connect(self) -> smtplib.SMTP:
        """
        SMTP 서버에 연결하고 인증합니다.

        Returns:
            연결된 SMTP 객체

        Raises:
            EmailSendError: 연결 또는 인증 실패 시
        """
        try:
            logger.debug(
                f"SMTP 서버 연결 중: {self.smtp_server}:{self.smtp_port}"
            )
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.starttls()

            logger.debug(f"SMTP 인증 중: {self.username}")
            server.login(self.username, self.password)

            logger.info("SMTP 서버 연결 및 인증 성공")
            return server

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP 인증 실패: {e}"
            logger.error(error_msg)
            raise EmailSendError(error_msg) from e
        except smtplib.SMTPException as e:
            error_msg = f"SMTP 연결 실패: {e}"
            logger.error(error_msg)
            raise EmailSendError(error_msg) from e
        except Exception as e:
            error_msg = f"SMTP 연결 중 예상치 못한 오류: {e}"
            logger.error(error_msg)
            raise EmailSendError(error_msg) from e

    def _transform_css_to_inline(self, html_content: str) -> str:
        """
        HTML의 CSS를 인라인 스타일로 변환합니다.

        premailer의 cssutils 로깅을 억제하여 CSS 파싱 경고를 방지합니다.

        Args:
            html_content: 변환할 HTML 내용

        Returns:
            CSS가 인라인으로 변환된 HTML 문자열
        """
        # cssutils 로깅 레벨을 CRITICAL로 설정하여 경고 억제
        cssutils_logger = logging.getLogger('cssutils')
        original_level = cssutils_logger.level
        cssutils_logger.setLevel(logging.CRITICAL)

        try:
            # CSS를 인라인 스타일로 변환
            transformed_html = transform(html_content)
            return transformed_html
        finally:
            # 원래 로깅 레벨로 복원
            cssutils_logger.setLevel(original_level)

    def _build_html_message(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> MIMEMultipart:
        """
        HTML 이메일 메시지를 구성합니다.

        Args:
            to_email: 수신자 이메일 주소
            subject: 메일 제목
            html_content: HTML 본문 내용

        Returns:
            구성된 MIME 메시지 객체
        """
        message = MIMEMultipart('alternative')
        message['From'] = self.from_email
        message['To'] = to_email
        message['Subject'] = subject

        # HTML 파트 추가
        html_part = MIMEText(html_content, 'html', 'utf-8')
        message.attach(html_part)

        return message

    def send_html_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        max_retries: int = 3
    ) -> bool:
        """
        HTML 형식의 이메일을 발송합니다.

        Args:
            to_email: 수신자 이메일 주소
            subject: 메일 제목
            html_content: HTML 본문 내용
            max_retries: 최대 재시도 횟수 (기본값: 3)

        Returns:
            발송 성공 여부

        Raises:
            EmailSendError: 최대 재시도 후에도 발송 실패 시
        """
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"메일 발송 시도 {attempt}/{max_retries}: {to_email}"
                )

                # SMTP 서버 연결
                server = self._connect()

                # 메시지 구성
                message = self._build_html_message(
                    to_email, subject, html_content
                )

                # 메일 발송
                server.send_message(message)
                server.quit()

                logger.info(f"메일 발송 성공: {to_email}")
                return True

            except EmailSendError as e:
                logger.warning(f"시도 {attempt} 실패: {e}")
                if attempt == max_retries:
                    raise
            except Exception as e:
                error_msg = f"메일 발송 중 예상치 못한 오류: {e}"
                logger.error(error_msg)
                if attempt == max_retries:
                    raise EmailSendError(error_msg) from e

        return False

    def send_report_email(
        self,
        to_email: str,
        report_path,
        report_date: str
    ) -> bool:
        """
        백업 리포트 HTML 파일을 이메일로 발송합니다.

        Args:
            to_email: 수신자 이메일 주소
            report_path: HTML 리포트 파일 경로 (str 또는 Path)
            report_date: 리포트 날짜 (예: 2024-01-15)

        Returns:
            발송 성공 여부

        Raises:
            EmailSendError: 파일 읽기 또는 발송 실패 시
        """
        try:
            # 문자열을 Path 객체로 변환
            if isinstance(report_path, str):
                report_path = Path(report_path)

            # HTML 파일 읽기
            logger.info(f"리포트 파일 읽기: {report_path}")
            if not report_path.exists():
                error_msg = f"리포트 파일이 존재하지 않습니다: {report_path}"
                raise EmailSendError(error_msg)

            html_content = report_path.read_text(encoding='utf-8')

            # CSS를 인라인 스타일로 변환 (이메일 클라이언트 호환성)
            logger.info("CSS를 인라인 스타일로 변환 중...")
            html_content = self._transform_css_to_inline(html_content)
            logger.info("CSS 변환 완료")

            # 메일 제목 구성
            subject = f"[Bacula] 백업 리포트 - {report_date}"

            # 메일 발송
            return self.send_html_email(to_email, subject, html_content)

        except EmailSendError:
            raise
        except Exception as e:
            error_msg = f"리포트 메일 발송 실패: {e}"
            logger.error(error_msg)
            raise EmailSendError(error_msg) from e
