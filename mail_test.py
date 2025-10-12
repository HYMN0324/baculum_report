#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail SMTP 테스트 - 단일 파일 버전
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GmailSender:
    """Gmail SMTP를 이용한 메일 발송 클래스"""
    
    def __init__(self, email: str, app_password: str):
        self.email = email
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def send_simple_email(self, to_email: str, subject: str, body: str) -> bool:
        """간단한 텍스트 메일 발송"""
        try:
            # SMTP 서버 연결
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # 로그인
            server.login(self.email, self.app_password)
            
            # 메일 구성
            message = f"Subject: {subject}\n\n{body}"
            
            # 메일 발송
            server.sendmail(self.email, to_email, message.encode('utf-8'))
            server.quit()
            
            print(f"✅ 메일 발송 성공: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ 메일 발송 실패: {e}")
            return False


# ============================================
# 여기서부터 테스트 코드
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("Gmail SMTP 테스트")
    print("=" * 50)
    
    # ⚠️ 여기에 실제 값을 입력하세요
    GMAIL_USER = "qkrgyals41@gmail.com"       # 실제 Gmail 주소
    GMAIL_APP_PASSWORD = "fcnafqhizzilimix"   # 16자리 앱 비밀번호 (공백 제거)
    
    print(f"발신자: {GMAIL_USER}")
    print(f"앱 비밀번호 길이: {len(GMAIL_APP_PASSWORD)}자")
    
    # 앱 비밀번호 길이 검증
    if len(GMAIL_APP_PASSWORD) != 16:
        print("\n❌ 오류: 앱 비밀번호는 16자리여야 합니다!")
        print(f"   현재: {len(GMAIL_APP_PASSWORD)}자")
        print("   공백/하이픈을 제거했는지 확인하세요.")
        exit(1)
    
    # Gmail 발송 테스트
    sender = GmailSender(
        email=GMAIL_USER,
        app_password=GMAIL_APP_PASSWORD
    )
    
    print("\n📧 메일 발송 중...\n")
    
    # 메일 발송
    success = sender.send_simple_email(
        to_email="qkrgyals47@naver.com",
        subject="테스트 메일",
        body="Python에서 발송한 메일입니다!"
    )
    
    if success:
        print("\n" + "=" * 50)
        print("✅ 테스트 성공!")
        print("수신자 메일함을 확인하세요.")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ 테스트 실패")
        print("\n💡 문제 해결:")
        print("1. Gmail 2단계 인증 활성화 확인")
        print("2. 앱 비밀번호 재생성")
        print("3. 인터넷 연결 확인")
        print("=" * 50)