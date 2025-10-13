# Task Active: 메일 발송 기능

**Phase**: Phase 8
**상태**: ✅ 완료
**시작일**: 2025-10-12
**완료일**: 2025-10-13

---

## 📋 작업 개요

백업 리포트 자동 메일 발송 기능 추가 (현재 단계에서는 보류)

**브랜치**: `git checkout -b phase-8-mail` (작업 시작 시 생성)

---

## 8.1 메일 발송 모듈 준비

### SMTP 라이브러리 선택
- [x] SMTP 라이브러리 선택: `smtplib` (Python 표준 라이브러리)
  - 추가 설치 불필요
  - `mail_test.py` 참고하여 구현

### 메일 발송 함수 설계
- [x] `src/mail/` 디렉토리 생성
- [x] `src/mail/__init__.py` 생성
- [x] `src/mail/email_sender.py` 생성
  - EmailSender 클래스 구현
  - `__init__`: SMTP 서버 정보, 인증 정보 초기화
  - `send_html_email()`: HTML 메일 발송
  - `send_report_email()`: 백업 리포트 메일 발송
  - `_connect()`: SMTP 서버 연결 및 인증
  - `_build_html_message()`: HTML 메일 메시지 구성
  - 재시도 로직 구현 (최대 3회)
  - 상세한 에러 처리 및 로깅

### 메일 내용 구성
- [x] 메일 제목 설정: `[Bacula] 백업 리포트 - YYYY-MM-DD`
- [x] 메일 본문 구성: HTML 리포트 파일을 그대로 본문에 삽입
- [x] MIME Multipart 사용하여 HTML 이메일 구성

### 환경 변수 설정
- [x] `.env.example`에 메일 관련 설정 추가
  ```
  SMTP_SERVER=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USERNAME=your_gmail_address@gmail.com
  SMTP_PASSWORD=your_16_digit_app_password
  MAIL_FROM=your_gmail_address@gmail.com
  MAIL_TO=recipient@example.com
  ```
- [x] Gmail SMTP 사용 (smtp.gmail.com:587)
- [x] 앱 비밀번호 인증 방식

---

## 8.2 설정 모듈 업데이트

### config.py 수정
- [x] 메일 관련 프로퍼티 추가
  - `smtp_server`, `smtp_port`, `smtp_username`, `smtp_password`
  - `mail_from`, `mail_to`
- [x] `has_mail_config()` 메서드: 메일 설정 완전성 확인
- [x] `get_email_sender_config()` 메서드: EmailSender 초기화용 설정 반환
- [x] 메일 설정은 선택사항 (필수 검증에 포함하지 않음)

## 8.3 메인 프로그램 통합

### main.py 수정
- [x] 메일 발송 옵션 추가 (`--send-mail` 플래그)
- [x] 리포트 생성 후 메일 발송 로직 추가 ([5/5] 단계)
- [x] 메일 발송 성공/실패 로깅
- [x] 메일 설정 확인 후 발송

### 에러 처리
- [x] SMTP 연결 실패 처리
- [x] EmailSender에서 재시도 로직 구현 (최대 3회)
- [x] 메일 발송 실패해도 리포트 생성은 성공으로 처리
- [x] 메일 설정 불완전 시 경고 메시지 출력 후 건너뛰기

---

## 8.4 코드 품질 검증

### flake8 검증
- [x] 새로 작성한 코드 flake8 검증
  - `src/mail/email_sender.py`
  - `src/utils/config.py`
  - `src/main.py`
- [x] 모든 코드 스타일 검사 통과

## 8.5 테스트 (사용자 직접 수행 필요)

### 테스트 준비사항
1. `.env` 파일에 Gmail 설정 추가
   - Gmail 계정의 2단계 인증 활성화
   - 앱 비밀번호 생성 (16자리)
   - SMTP 설정 입력
2. 테스트 수신자 이메일 주소 설정

### 통합 테스트 방법
```bash
# 메일 발송 없이 리포트만 생성
python -m src.main --mode test

# 메일 발송 포함
python -m src.main --mode test --send-mail

# 상세 로그 포함
python -m src.main --mode test --send-mail --verbose
```

### 확인 사항
- [x] **실제 메일 발송 테스트** (테스트 계정 사용)
- [x] 테스트 메일 발송 성공 확인
- [x] 수신 메일함에서 메일 확인
  - 제목: `[Bacula] 백업 리포트 - YYYY-MM-DD`
  - 본문: HTML 리포트 정상 렌더링
  - 모든 스타일 및 레이아웃 정상 표시

---

## 8.6 추가 개선 사항

### 이메일 호환성 개선
- [x] CSS 경고 억제 기능 추가 (`_transform_css_to_inline` 메서드)
  - cssutils 로깅 레벨을 CRITICAL로 조정
  - CSS 파싱 경고 완전 제거
- [x] HTML 템플릿 이메일 호환 CSS 변환
  - CSS Grid → Table 레이아웃으로 변경
  - 모던 CSS 속성 제거 (transition, transform, gap)
  - CSS Level 2.1 호환 (Outlook, Gmail 지원)

### 백업 작업 처리 개선
- [x] 진행 중인 백업 작업 처리
  - BackupJob.end_time을 Optional[datetime]으로 변경
  - 진행 중인 작업은 현재 시간 기준으로 duration 계산
  - TypeError 해결

### HTML 레이아웃 개선
- [x] 백업 현황 요약 레이아웃 재설계
  - 기존: 전체/Full/Incremental/Differential/실행중
  - 변경: 전체/성공/실패/실행중 + 각각에 Full/Incremental 세부 표시
  - ReportStats에 running_full, running_incremental, running_differential 속성 추가

### Phase 완료
- [x] 실제 메일 발송 테스트 완료
- [x] main 브랜치에 커밋 완료 (d20613c)
  ```bash
  git commit -m "Phase 8: 메일 발송 기능 구현 및 이메일 호환성 개선"
  ```

---

## 📝 작업 결과

### 구현 완료 항목
1. **EmailSender 클래스** (`src/mail/email_sender.py`)
   - Gmail SMTP 기반 메일 발송
   - HTML 메일 지원
   - 재시도 로직 (최대 3회)
   - 상세한 에러 처리 및 로깅
   - **CSS 경고 억제 기능** (`_transform_css_to_inline` 메서드)
   - **PEP 8 100% 준수**

2. **Config 클래스 확장** (`src/utils/config.py`)
   - 메일 관련 설정 프로퍼티 추가
   - 메일 설정 완전성 검증 메서드
   - 선택적 메일 설정 지원

3. **메인 프로그램 통합** (`src/main.py`)
   - `--send-mail` 플래그 추가
   - 메일 발송 로직 통합 ([5/5] 단계)
   - 메일 발송 실패해도 프로그램 정상 종료

4. **환경 설정** (`.env.example`)
   - Gmail SMTP 설정 추가
   - 앱 비밀번호 사용 방식

5. **HTML 템플릿 이메일 호환성** (`templates/report_template.html`)
   - CSS Grid → Table 레이아웃 변환
   - CSS Level 2.1 호환 (Outlook, Gmail 지원)
   - 백업 현황 요약 레이아웃 재설계 (전체/성공/실패/실행중)

6. **BackupJob 모델 개선** (`src/models/backup_job.py`)
   - end_time을 Optional[datetime]으로 변경
   - 진행 중인 백업 작업 처리

7. **ReportStats 모델 확장** (`src/models/report_stats.py`)
   - running_full, running_incremental, running_differential 속성 추가
   - 실행 중인 백업의 레벨별 통계 지원

### 사용 방법
```bash
# 리포트 생성만
python -m src.main --mode test

# 리포트 생성 + 메일 발송
python -m src.main --mode test --send-mail

# 프로덕션 모드 + 메일 발송
python -m src.main --mode production --send-mail
```

### ⚠️ 중요 사항

1. **Gmail 앱 비밀번호 필요**
   - Gmail 계정에서 2단계 인증 활성화
   - 앱 비밀번호 생성 (16자리)
   - .env 파일에 설정

2. **메일 발송 실패 처리**
   - 메일 발송 실패해도 리포트는 정상 생성됨
   - 메일 설정이 없으면 경고만 출력하고 건너뜀

3. **보안**
   - .env 파일은 git에 커밋 금지
   - 앱 비밀번호는 안전하게 보관
   - mail_test.py의 하드코딩된 정보 삭제 권장

---

## 🔗 관련 문서

- [프로젝트 요구사항](./project.md)
- [개발 가이드](./dev.md)
- [이전 태스크](./tasks/)

---

## 💡 완료 요약

Phase 8이 성공적으로 완료되었습니다:
- ✅ 메일 발송 기능 구현 및 테스트 완료
- ✅ 이메일 호환성 개선 (CSS 경고 제거, HTML 호환 레이아웃)
- ✅ 진행 중인 백업 작업 처리
- ✅ HTML 리포트 레이아웃 개선
- ✅ 모든 코드 PEP 8 준수
- ✅ Git 커밋 완료 (d20613c)

다음 단계: 필요시 추가 기능 또는 개선 작업
