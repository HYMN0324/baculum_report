# Task Active: 향후 확장 (메일 발송)

**Phase**: Phase 8
**상태**: ⏸️ 보류 (메일 서버 구축 후 진행)
**시작일**: TBD

---

## 📋 작업 개요

백업 리포트 자동 메일 발송 기능 추가 (현재 단계에서는 보류)

**브랜치**: `git checkout -b phase-8-mail` (작업 시작 시 생성)

---

## 8.1 메일 발송 모듈 준비

### SMTP 라이브러리 선택
- [ ] SMTP 라이브러리 선택 (`smtplib` or `yagmail`)
  - `smtplib`: Python 표준 라이브러리 (추가 설치 불필요)
  - `yagmail`: 간단한 API, Gmail 최적화
- [ ] 선택한 라이브러리 설치 및 `requirements.txt` 업데이트

### 메일 발송 함수 설계
- [ ] `src/mail/` 디렉토리 생성
- [ ] `src/mail/__init__.py` 생성
- [ ] `src/mail/email_sender.py` 생성
  - EmailSender 클래스 설계
  - `__init__`: SMTP 서버 정보, 인증 정보 초기화
  - `send_report()`: 리포트 메일 발송
  - `_connect()`: SMTP 서버 연결
  - `_build_message()`: 메일 메시지 구성

### 메일 내용 구성
- [ ] 메일 제목 설정
  - 예: `[Bacula] 백업 리포트 - YYYY-MM-DD`
- [ ] 메일 본문 구성
  - 간단한 요약 (성공/실패 건수)
  - 상세 리포트는 첨부 파일 또는 본문에 HTML 삽입
- [ ] 첨부 파일 처리 (선택사항)
  - HTML 리포트 파일을 첨부

### 환경 변수 설정
- [ ] `.env`에 메일 관련 설정 추가
  ```
  SMTP_SERVER=smtp.example.com
  SMTP_PORT=587
  SMTP_USERNAME=...
  SMTP_PASSWORD=...
  MAIL_FROM=bacula@example.com
  MAIL_TO=admin@example.com
  ```
- [ ] `.env.example` 업데이트

---

## 8.2 메인 프로그램 통합

### main.py 수정
- [ ] 메일 발송 옵션 추가 (`--send-mail` 플래그)
- [ ] 리포트 생성 후 메일 발송 로직 추가
- [ ] 메일 발송 성공/실패 로깅

### 에러 처리
- [ ] SMTP 연결 실패 처리
- [ ] 메일 발송 실패 시 재시도 로직
- [ ] 메일 발송 실패해도 리포트 생성은 성공으로 처리

---

## 8.3 테스트

### 단위 테스트
- [ ] `tests/test_mail.py` 생성
- [ ] 메일 메시지 구성 테스트
- [ ] SMTP 연결 테스트 (mock 사용)

### 통합 테스트
- [ ] **실제 메일 서버 연결 테스트** (테스트 계정 사용)
- [ ] 테스트 메일 발송 성공 확인
- [ ] 수신 메일 확인 (제목, 본문, 첨부 파일)

---

## 8.4 문서화

### 사용자 문서 업데이트
- [ ] README.md 업데이트 (메일 발송 기능 추가)
- [ ] 메일 설정 가이드 추가
- [ ] 예제 메일 스크린샷 추가 (선택사항)

### Phase 완료
- [ ] Phase 8 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-8-mail --no-ff -m "Phase 8: 메일 발송 기능 추가"
  git tag v1.1.0
  ```

---

## 📝 작업 전제조건

메일 발송 기능을 구현하기 전에 다음 사항이 준비되어야 합니다:

1. **메일 서버 구축 완료**
   - SMTP 서버 주소 및 포트 확인
   - 인증 정보 (사용자명, 비밀번호) 확보

2. **메일 발송 정책 확인**
   - 발송 빈도 제한 확인
   - 수신자 목록 확정

3. **보안 검토**
   - 메일 인증 정보 안전한 관리 방안
   - TLS/SSL 암호화 사용 여부

---

## 🔗 관련 문서

- [프로젝트 요구사항](./project.md)
- [개발 가이드](./dev.md)
- [이전 태스크](./tasks/)

---

## 💡 참고 사항

현재 시스템은 HTML 리포트 생성까지 완료되어 있으므로, 메일 발송 기능은 별도 모듈로 추가하는 것이 권장됩니다. 메일 서버 준비가 완료되면 이 파일을 기반으로 작업을 진행하세요.
