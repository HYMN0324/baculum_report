# Task 004: 메인 실행 로직

**Phase**: Phase 4
**상태**: ✅ 완료
**완료일**: 2025-10-12

---

## 📋 작업 개요

전체 프로세스를 통합하는 메인 프로그램 및 유틸리티 함수 구현

**브랜치**: `git checkout -b phase-4-main`

---

## 4.1 메인 프로그램 작성

### main.py 구현
- [x] `src/main.py` 구현
- [x] 커맨드 라인 인자 처리 (테스트/운영 모드 선택)
- [x] 전체 프로세스 오케스트레이션
  1. API 연결
  2. 데이터 수집
  3. 데이터 가공
  4. 리포트 생성
- [x] 실행 시간 측정 및 출력
- [x] 에러 핸들링 및 종료 코드 설정

---

## 4.2 유틸리티 함수

### Logger (로깅 시스템)
- [x] `src/utils/__init__.py` 생성
- [x] `src/utils/logger.py` - 로깅 설정
  - 파일 로깅 (logs/app.log - 일별 로테이션)
  - 콘솔 출력 (INFO 레벨)
  - 포맷: `[YYYY-MM-DD HH:MM:SS] [LEVEL] message`

### Config (설정 관리)
- [x] `src/utils/config.py` - 설정 관리
  - .env 로드
  - 기본값 설정
  - 설정 검증 (필수 값 확인)

### DateTime Helper (시간 계산)
- [x] `src/utils/datetime_helper.py` - 시간 계산 유틸리티
  - `get_test_period()`: 1주일 전 ~ 현재
  - `get_production_period()`: 전일 22시 ~ 현재
  - `format_timestamp()`: 리포트 파일명용 (YYYYMMDDHHMMSS)

### Phase 완료
- [x] Phase 4 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-4-main --no-ff -m "Phase 4: 메인 실행 로직 완료"
  git tag v0.4-phase4
  ```

---

## 📝 작업 결과

- 메인 실행 로직 구현 완료
- 로깅 시스템 구축 (파일 + 콘솔)
- 설정 관리 모듈 구현
- 시간 계산 유틸리티 구현
- 테스트/프로덕션 모드 분리

---

## 🚀 실행 방법

```bash
# 테스트 모드 (1주일 전 ~ 현재)
python src/main.py --mode test

# 프로덕션 모드 (전일 22시 ~ 현재)
python src/main.py --mode production
```

---

## 🔗 관련 문서

- [프로젝트 요구사항](../project.md)
- [개발 가이드](../dev.md)
