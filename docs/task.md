# Bacula Backup Report System - 작업 계획서

## 📋 프로젝트 개요
**목적**: Bacula API로 백업 현황 조회 → HTML 리포트 자동 생성
**현재 범위**: API 조회 + HTML 생성 (메일 발송은 추후)

**기술 환경**:
- OS: Rocky Linux 9.6
- Python: 3.12 (.venv 환경, python명령어로 실행.)
- 필수 라이브러리: requests, jinja2, python-dotenv, flake8

---

## 🎯 핵심 요구사항
- **API 호출 시간**: 10초 이하
- **오류율**: 0.1% 이하
- **리포트 파일명**: `mail_YYYYMMDDHHMMSS.html`
- **조회 기간**:
  - 테스트: 1주일 전 ~ 현재
  - 프로덕션: 전일 22시 ~ 실행 시점
- **개발 규칙**: dev.md 파일 참조

---

## 📂 Phase 1: 프로젝트 초기 설정

### 1.1 환경 설정
- [x] Git 저장소 확인 및 초기화
  - `git status` 실행해서 저장소 상태 확인
  - "fatal: not a git repository" 에러 발생 시에만 `git init` 실행
  - 이미 git 저장소면 스킵
- [x] main 브랜치 확인 (기본 브랜치 설정)
- [x] Phase 1 작업 브랜치 생성: `git checkout -b phase-1-setup`
- [x] `.gitignore` 설정
  ```
  # Python
  __pycache__/
  *.py[cod]
  *$py.class
  *.so
  .venv/
  venv/

  # Environment
  .env

  # Output
  reports/*.html
  logs/*.log

  # IDE
  .vscode/
  .idea/
  *.swp
  ```
- [x] Python 3.12 가상환경 확인/생성 (`.venv`)
- [x] 가상환경 활성화 확인 (`source .venv/bin/activate`)
- [x] pip 업그레이드 (`pip install --upgrade pip`)
- [x] 필수 패키지 설치 (`requests`, `jinja2`, `python-dotenv`, `flake8`, `pytest`)
- [x] `requirements.txt` 생성
  - 파일이 없으면: `pip freeze > requirements.txt`
  - 파일이 있으면: 내용 확인 후 업데이트 여부 결정
- [x] `.env.example` 템플릿 생성 (실제 값 없이 키만)
- [x] `.env` 파일 확인
  - 파일이 있으면: 내용 확인 (필수 키 존재 여부)
  - 파일이 없으면: `.env.example` 복사 후 실제 값 입력
- [x] `.flake8` 설정 파일 생성
  ```ini
  [flake8]
  max-line-length = 100
  exclude = .venv,__pycache__,.git
  ignore = E203,W503
  ```
- [x] 초기 커밋 (phase-1-setup 브랜치에서)
  ```bash
  git add .gitignore .flake8 requirements.txt .env.example
  git commit -m "init: 프로젝트 초기 설정"
  ```
  ⚠️ `.env` 파일은 절대 커밋하지 않음

### 1.2 프로젝트 구조 설계
- [x] 디렉토리 구조 생성
  ```
  baculum/
  ├── src/
  │   ├── api/
  │   │   ├── __init__.py
  │   │   └── bacula_client.py
  │   ├── report/
  │   │   ├── __init__.py
  │   │   └── report_generator.py
  │   ├── models/
  │   │   ├── __init__.py
  │   │   └── backup_job.py
  │   ├── utils/
  │   │   ├── __init__.py
  │   │   ├── logger.py
  │   │   ├── config.py
  │   │   └── datetime_helper.py
  │   └── main.py
  ├── templates/
  │   └── report_template.html
  ├── reports/          # .gitkeep 파일만
  ├── logs/             # 애플리케이션 로그
  ├── tests/
  │   ├── __init__.py
  │   ├── fixtures/
  │   │   └── api_response_sample.json
  │   ├── test_api.py
  │   ├── test_report.py
  │   └── test_utils.py
  ├── docs/
  │   ├── project.md
  │   ├── task.md
  │   └── task_log/
  ├── .env
  ├── .env.example
  ├── .gitignore
  ├── .flake8
  ├── requirements.txt
  └── README.md
  ```
- [x] 각 모듈에 `__init__.py` 생성 (Python 패키지 인식)
- [x] `reports/.gitkeep` 생성 (빈 디렉토리 보존)
- [x] `logs/` 디렉토리 생성 (애플리케이션 로그용)
- [ ] Phase 1 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-1-setup --no-ff -m "Phase 1: 프로젝트 초기 설정 완료"
  git tag v0.1-phase1
  ```

---

## 📂 Phase 2: Bacula API 연동

**브랜치 생성**: `git checkout -b phase-2-api`

### 2.1 API 클라이언트 구현
- [x] Bacula REST API 문서 검토 (https://bacula.org/downloads/baculum/baculum-api-v1)
- [x] `test.py` 코드 분석 - API 호출 방식, 인증 방법, 응답 구조 파악
- [x] `src/api/__init__.py` 생성
- [x] `src/api/bacula_client.py` 생성
  - BaculaClient 클래스 설계
  - `__init__`: API URL, 인증 정보 초기화
  - `connect()`: API 연결 테스트
  - `get_jobs()`: 백업 작업 목록 조회
  - `_request()`: 공통 HTTP 요청 처리 (타임아웃, 재시도)
- [x] `.env`에서 설정 로드 (python-dotenv 사용)
  ```python
  BACULUM_API_HOST='172.16.1.0'
  BACULUM_API_PORT='9096'
  BACULUM_API_USERNAME=...
  BACULUM_API_PASSWORD=...
  ```
- [x] 타임아웃 설정 (requests timeout=10)
- [x] 재시도 로직 추가 (최대 3회, 지수 백오프)
- [x] 커스텀 예외 클래스 정의 (BaculaAPIError, ConnectionError, TimeoutError)
- [x] 상세 로깅 추가 (요청/응답, 에러 정보)

### 2.2 데이터 수집 로직
- [x] 시간 범위 설정 함수 구현
  - 테스트 모드: 1주일 전 ~ 현재
  - 프로덕션 모드: 전일 22시 ~ 실행 시점
- [x] API 응답 데이터 파싱 함수 구현
- [x] 백업 상태 분류 로직 (성공/실패/진행중)
- [x] **실패한 백업의 에러 로그 추출** (필수 - 강조 표시)

### 2.3 API 테스트
- [x] **실제 API 호출 테스트** (실제 Bacula 시스템 대상)
  - API 연결 확인
  - 응답 데이터 구조 파악 및 저장 (JSON 샘플)
  - API 호출 시간 측정 (10초 이하 확인)
- [x] 응답 데이터 기반으로 파싱 로직 구현
- [x] 파싱 로직 단위 테스트 작성 (실제 응답 샘플 사용)
- [ ] Phase 2 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-2-api --no-ff -m "Phase 2: Bacula API 연동 완료"
  git tag v0.2-phase2
  ```

---

## 📂 Phase 3: 리포트 생성 시스템

**브랜치 생성**: `git checkout -b phase-3-report`

### 3.1 데이터 모델 설계
- [ ] `src/models/__init__.py` 생성
- [ ] `src/models/backup_job.py` - 백업 작업 데이터 클래스
  ```python
  @dataclass
  class BackupJob:
      job_id: int
      server_name: str
      status: str  # 'success', 'failed', 'running'
      start_time: datetime
      end_time: Optional[datetime]
      backup_size: Optional[int]
      error_message: Optional[str]

      @property
      def is_success(self) -> bool
      @property
      def is_failed(self) -> bool
      @property
      def is_running(self) -> bool
  ```
- [ ] `src/models/report_stats.py` - 리포트 통계 클래스
  ```python
  @dataclass
  class ReportStats:
      total_servers: int
      success_count: int
      failed_count: int
      running_count: int
      start_period: datetime
      end_period: datetime
  ```

### 3.2 HTML 템플릿 작성
- [ ] Jinja2 템플릿 파일 생성 (`templates/report_template.html`)
- [ ] 리포트 헤더 섹션 (제목, 생성 시간, 조회 기간)
- [ ] **백업 현황 요약** 섹션
  - 전체 서버 수
  - 성공 건수
  - 실패 건수
  - 진행중 건수
- [ ] **성공한 백업 목록** 테이블
  - 서버명, 완료시간, 백업 크기 등
- [ ] **실패한 백업 상세** 섹션 (⚠️ 강조 표시)
  - 서버명, 실패시간
  - **에러 로그 표시** (필수)
- [ ] **진행 중인 백업** 목록
  - 서버명, 시작시간
- [ ] CSS 스타일링 (가독성 향상, 실패 항목 강조)

### 3.3 리포트 생성 모듈
- [ ] `src/report/report_generator.py` 생성
- [ ] Jinja2 환경 설정
- [ ] 템플릿 렌더링 함수 구현
- [ ] 리포트 파일명 생성 (타임스탬프 포함)
- [ ] `reports/` 디렉토리에 HTML 파일 저장
- [ ] 파일 생성 성공/실패 로깅
- [ ] Phase 3 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-3-report --no-ff -m "Phase 3: 리포트 생성 시스템 완료"
  git tag v0.3-phase3
  ```

---

## 📂 Phase 4: 메인 실행 로직

**브랜치 생성**: `git checkout -b phase-4-main`

### 4.1 메인 프로그램 작성
- [ ] `src/main.py` 구현
- [ ] 커맨드 라인 인자 처리 (테스트/운영 모드 선택)
- [ ] 전체 프로세스 오케스트레이션
  1. API 연결
  2. 데이터 수집
  3. 데이터 가공
  4. 리포트 생성
- [ ] 실행 시간 측정 및 출력
- [ ] 에러 핸들링 및 종료 코드 설정

### 4.2 유틸리티 함수
- [ ] `src/utils/__init__.py` 생성
- [ ] `src/utils/logger.py` - 로깅 설정
  - 파일 로깅 (logs/app.log - 일별 로테이션)
  - 콘솔 출력 (INFO 레벨)
  - 포맷: `[YYYY-MM-DD HH:MM:SS] [LEVEL] message`
- [ ] `src/utils/config.py` - 설정 관리
  - .env 로드
  - 기본값 설정
  - 설정 검증 (필수 값 확인)
- [ ] `src/utils/datetime_helper.py` - 시간 계산 유틸리티
  - `get_test_period()`: 1주일 전 ~ 현재
  - `get_production_period()`: 전일 22시 ~ 현재
  - `format_timestamp()`: 리포트 파일명용 (YYYYMMDDHHMMSS)
- [ ] Phase 4 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-4-main --no-ff -m "Phase 4: 메인 실행 로직 완료"
  git tag v0.4-phase4
  ```

---

## 📂 Phase 5: 테스트 및 검증

**브랜치 생성**: `git checkout -b phase-5-test`

### 5.1 단위 테스트 (pytest 사용)
- [ ] pytest 관련 패키지 설치 (`pytest`, `pytest-cov`, `pytest-mock`)
- [ ] `tests/__init__.py` 생성
- [ ] `tests/fixtures/` 디렉토리 생성
  - Phase 2.3에서 수집한 실제 API 응답 샘플 저장
  - `api_response_sample.json` (정상 응답)
  - `api_response_failed.json` (실패 케이스)
- [ ] `tests/test_api.py` - API 클라이언트 테스트
  - **실제 응답 샘플 사용** (fixtures/api_response_sample.json)
  - 응답 파싱 로직 테스트
  - 데이터 변환 테스트
  - 에러 응답 처리 테스트
- [ ] `tests/test_models.py` - 데이터 모델 테스트
  - BackupJob 프로퍼티 테스트
  - 상태 분류 테스트
- [ ] `tests/test_report.py` - 리포트 생성 테스트
  - 템플릿 렌더링 테스트
  - 파일 생성 테스트
- [ ] `tests/test_utils.py` - 유틸리티 테스트
  - 시간 계산 로직 테스트
  - 설정 로드 테스트
- [ ] pytest 설정 파일 생성 (`pytest.ini`)
- [ ] 테스트 실행 및 커버리지 확인 (`pytest -v --cov=src`)

### 5.2 통합 테스트 (실제 API 사용)
- [ ] **실제 Bacula API 연결** (.env 설정 사용)
- [ ] 1주일 전 데이터로 전체 프로세스 테스트
- [ ] 생성된 HTML 파일 검증
- [ ] 다양한 시나리오 테스트
  - 모든 백업 성공
  - 일부 백업 실패
  - 진행 중 백업 있음
  - API 오류 상황 (가능하면)

### 5.3 성능 테스트
- [ ] API 호출 시간 측정 (10초 이하 확인)
- [ ] 대량 데이터 처리 성능 검증
- [ ] 메모리 사용량 확인
- [ ] Phase 5 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-5-test --no-ff -m "Phase 5: 테스트 및 검증 완료"
  git tag v0.5-phase5
  ```

---

## 📂 Phase 6: 문서화 및 배포 준비

**브랜치 생성**: `git checkout -b phase-6-docs`

### 6.1 문서 작성
- [ ] `README.md` 작성
  - 프로젝트 설명
  - 설치 방법
  - 사용 방법
  - 설정 가이드
- [ ] 코드 주석 및 docstring 추가

### 6.2 코드 품질 검증 및 리팩토링
- [ ] **flake8 실행 및 코드 컨벤션 준수 확인**
- [ ] flake8 경고/에러 수정
- [ ] 코드 스타일 통일 (PEP 8)
- [ ] 불필요한 코드 제거
- [ ] 에러 처리 강화
- [ ] 로깅 레벨 조정
- [ ] 성능 최적화

### 6.3 배포 준비
- [ ] 실행 스크립트 작성 (`run.sh`)
  ```bash
  #!/bin/bash
  cd /path/to/baculum
  source .venv/bin/activate
  python src/main.py --mode production
  ```
- [ ] 실행 권한 부여 (`chmod +x run.sh`)
- [ ] 실행 가이드 작성 (`docs/deployment.md`)
  - 수동 실행 방법
  - 설정 확인 사항
  - 로그 확인 방법
- [ ] Phase 6 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-6-docs --no-ff -m "Phase 6: 문서화 및 배포 준비 완료"
  git tag v0.6-phase6
  ```

---

## 📂 Phase 7: 최종 검증

**브랜치**: main (최종 검증은 main에서 수행)

### 7.1 최종 검증
- [ ] 모든 요구사항 충족 확인
- [ ] 성능 기준 달성 확인 (API 10초 이하, 오류율 0.1% 이하)
- [ ] 문서 최종 검토
- [ ] Git 커밋 이력 검토 (`git log --oneline` 확인)
- [ ] 코드 정리 및 최종 flake8 검증

### 7.2 인수인계 준비
- [ ] README.md 최종 업데이트
- [ ] 배포 가이드 확인 (`docs/deployment.md`)
- [ ] 트러블슈팅 가이드 작성 (자주 발생할 수 있는 문제)
- [ ] 인수인계 문서 작성 (운영자용)
- [ ] 최종 릴리즈 태그 생성
  ```bash
  git tag v1.0.0 -m "Release: Bacula Backup Report System v1.0.0"
  ```

---

## 📂 Phase 8: 향후 확장 (메일 발송)

### 8.1 메일 발송 모듈 준비 (현재 단계에서는 보류)
- [ ] SMTP 라이브러리 선택 (`smtplib` or `yagmail`)
- [ ] 메일 발송 함수 설계
- [ ] 메일 제목/본문 구성
- [ ] 첨부 파일 처리 (선택사항)
- [ ] 메일 서버 구축 후 통합 테스트

---

## ✅ 작업 진행 규칙

### 안전한 개발을 위한 Git 브랜치 전략

**주요 원칙**: 각 Phase마다 별도 브랜치에서 작업, 완료 후 main에 병합

```bash
# Phase 시작 전
git checkout -b phase-1-setup    # Phase 1용 브랜치 생성
git checkout -b phase-2-api      # Phase 2용 브랜치 생성
# ...

# Phase 완료 후
git checkout main
git merge phase-1-setup          # 검증 완료 후 병합
git tag v0.1-phase1              # 태그로 마일스톤 표시
```

### 작업 진행 절차

1. **Phase 시작 시**:
   - 새 브랜치 생성: `git checkout -b phase-N-작업명`
   - 브랜치명 예시: `phase-1-setup`, `phase-2-api`, `phase-3-report`

2. **각 작업 시작 시**:
   - 작업 로그 파일 생성: `docs/task_log/YYYYMMDD_HHMMSS_작업명.md`
   - 로그에 작업 내용, 진행 과정, 결과 기록

3. **각 작업 완료 시**:
   - 체크박스를 [x]로 변경
   - 작업 로그에 최종 결과 및 이슈 기록
   - 현재 브랜치에 커밋:
     ```bash
     git add [변경된 파일들]
     git commit -m "task: [작업명] 완료"
     ```
   - 작업 로그 파일도 함께 커밋

4. **Phase 완료 시**:
   - 해당 Phase의 모든 체크박스 확인
   - 통합 테스트 수행
   - Phase 브랜치에서 최종 커밋
   - main 브랜치로 병합:
     ```bash
     git checkout main
     git merge phase-N-작업명 --no-ff  # 병합 커밋 생성
     git tag v0.N-phaseN              # 마일스톤 태그
     ```

5. **문제 발생 시 되돌리기**:
   ```bash
   # 방법 1: 특정 커밋으로 되돌리기 (커밋 유지)
   git revert <commit-hash>

   # 방법 2: 브랜치 삭제 후 다시 시작
   git checkout main
   git branch -D phase-N-작업명
   git checkout -b phase-N-작업명

   # 방법 3: 태그로 되돌리기
   git checkout v0.N-phaseN
   git checkout -b phase-N-fix
   ```

6. **정기 백업** (중요 작업 전):
   ```bash
   # 현재 상태 백업
   git branch backup-YYYYMMDD-HHMMSS

   # 또는 원격 저장소 푸시 (설정된 경우)
   git push origin phase-N-작업명
   ```

4. **작업 로그 형식**:
   ```markdown
   # [작업명]

   ## 작업 정보
   - 시작 시간: YYYY-MM-DD HH:MM:SS
   - 담당: [이름]
   - 관련 Phase: Phase X.Y

   ## 작업 내용
   [수행한 작업 설명]

   ## 진행 과정
   - [단계별 진행 내용]

   ## 이슈 및 해결
   - [발생한 문제와 해결 방법]

   ## 결과
   - 완료 시간: YYYY-MM-DD HH:MM:SS
   - 결과물: [생성된 파일, 코드 등]
   - 테스트 결과: [통과/실패]
   ```

---

## 📊 진행 상황 요약

| Phase | 제목 | 진행률 |
|-------|------|--------|
| 1 | 프로젝트 초기 설정 | 0% |
| 2 | Bacula API 연동 | 0% |
| 3 | 리포트 생성 시스템 | 0% |
| 4 | 메인 실행 로직 | 0% |
| 5 | 테스트 및 검증 | 0% |
| 6 | 문서화 및 배포 준비 | 0% |
| 7 | 운영 테스트 및 최종 검증 | 0% |
| 8 | 향후 확장 (보류) | 0% |

---

## 🔗 참고 자료
- **프로젝트 문서**: `docs/project.md` - 프로젝트 요구사항 (PRD)
- **API 문서**: https://bacula.org/downloads/baculum/baculum-api-v1
- **API 호출 예시**: `test.py` - API 호출 방식 참고
- **API 접속 정보**: `.env` - API 인증 정보 (git 커밋 금지)

## ⚠️ 제약사항 및 주의사항
1. **보안**:
   - `.env` 파일은 절대 git에 커밋하지 않음
   - API 인증 정보 하드코딩 금지
   - 로그에 민감 정보 출력 금지
2. **에러 처리**:
   - API 연결 실패 시 재시도 로직 필수 (최대 3회)
   - 모든 예외는 로깅 후 적절히 처리
   - 사용자에게 명확한 에러 메시지 제공
3. **필수 표시**:
   - 실패한 백업의 에러 로그는 반드시 HTML에 표시
   - 리포트에 생성 시간 및 조회 기간 명시
4. **코드 품질**:
   - flake8 규칙 준수 (배포 전 검증 필수)
   - 모든 함수에 docstring 작성
   - 타입 힌트 사용 권장
5. **성능**:
   - API 타임아웃 10초 엄수
   - 대량 데이터 처리 시 메모리 효율 고려
6. **테스트**:
   - 핵심 로직은 반드시 단위 테스트 작성
   - 배포 전 통합 테스트 필수

## 🚀 개발 시작 가이드

### 준비사항 확인
- [ ] `.env` 파일 존재 여부 확인 (API 접속 정보)
- [ ] `test.py` 파일 확인 (API 호출 참고용)
- [ ] Python 3.12 설치 확인

### 개발 시작
**task.md의 Phase 1.1부터 순차적으로 진행하세요.**

각 Phase의 체크박스를 확인하면서 단계별로 작업하면 됩니다.

### 개발 완료 후 실행 방법
```bash
# 가상환경 활성화
source .venv/bin/activate

# 테스트 실행
pytest -v

# 프로그램 실행 (테스트 모드)
python src/main.py --mode test

# 프로그램 실행 (프로덕션 모드)
python src/main.py --mode production
```
