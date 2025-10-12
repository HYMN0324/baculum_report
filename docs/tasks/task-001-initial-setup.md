# Task 001: 프로젝트 초기 설정

**Phase**: Phase 1
**상태**: ✅ 완료
**완료일**: 2025-10-12

---

## 📋 작업 개요

프로젝트의 기본 환경 구축 및 디렉토리 구조 설계

---

## 1.1 환경 설정

### Git 저장소 설정
- [x] Git 저장소 확인 및 초기화
  - `git status` 실행해서 저장소 상태 확인
  - "fatal: not a git repository" 에러 발생 시에만 `git init` 실행
  - 이미 git 저장소면 스킵
- [x] main 브랜치 확인 (기본 브랜치 설정)
- [x] Phase 1 작업 브랜치 생성: `git checkout -b phase-1-setup`

### 환경 파일 설정
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
- [x] `.flake8` 설정 파일 생성
  ```ini
  [flake8]
  max-line-length = 100
  exclude = .venv,__pycache__,.git
  ignore = E203,W503
  ```

### Python 환경 설정
- [x] Python 3.12 가상환경 확인/생성 (`.venv`)
- [x] 가상환경 활성화 확인 (`source .venv/bin/activate`)
- [x] pip 업그레이드 (`pip install --upgrade pip`)
- [x] 필수 패키지 설치 (`requests`, `jinja2`, `python-dotenv`, `flake8`, `pytest`)
- [x] `requirements.txt` 생성
  - 파일이 없으면: `pip freeze > requirements.txt`
  - 파일이 있으면: 내용 확인 후 업데이트 여부 결정

### 환경 변수 설정
- [x] `.env.example` 템플릿 생성 (실제 값 없이 키만)
- [x] `.env` 파일 확인
  - 파일이 있으면: 내용 확인 (필수 키 존재 여부)
  - 파일이 없으면: `.env.example` 복사 후 실제 값 입력

### 초기 커밋
- [x] 초기 커밋 (phase-1-setup 브랜치에서)
  ```bash
  git add .gitignore .flake8 requirements.txt .env.example
  git commit -m "init: 프로젝트 초기 설정"
  ```
  ⚠️ `.env` 파일은 절대 커밋하지 않음

---

## 1.2 프로젝트 구조 설계

### 디렉토리 구조
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

### Phase 완료
- [x] Phase 1 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-1-setup --no-ff -m "Phase 1: 프로젝트 초기 설정 완료"
  git tag v0.1-phase1
  ```

---

## 📝 작업 결과

- 프로젝트 기본 구조 설정 완료
- Python 가상환경 및 필수 패키지 설치 완료
- Git 브랜치 전략 수립 및 초기 커밋 완료
- 코드 품질 검증 도구(flake8) 설정 완료

---

## 🔗 관련 문서

- [프로젝트 요구사항](../project.md)
- [개발 가이드](../dev.md)
