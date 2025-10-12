"""메일 발송 모듈.

Gmail SMTP를 통한 이메일 발송 기능을 제공합니다.
"""

from .email_sender import EmailSender, EmailSendError

__all__ = ['EmailSender', 'EmailSendError']
