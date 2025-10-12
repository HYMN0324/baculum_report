# Task 003: 리포트 생성 시스템

**Phase**: Phase 3
**상태**: ✅ 완료
**완료일**: 2025-10-12

---

## 📋 작업 개요

HTML 리포트 생성 기능 구현 (Jinja2 템플릿 활용)

**브랜치**: `git checkout -b phase-3-report`

---

## 3.1 데이터 모델 설계

### BackupJob 모델
- [x] `src/models/__init__.py` 생성
- [x] `src/models/backup_job.py` - 백업 작업 데이터 클래스
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

### ReportStats 모델
- [x] `src/models/report_stats.py` - 리포트 통계 클래스
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

---

## 3.2 HTML 템플릿 작성

### 템플릿 구조
- [x] Jinja2 템플릿 파일 생성 (`templates/report_template.html`)
- [x] 리포트 헤더 섹션 (제목, 생성 시간, 조회 기간)

### 리포트 섹션
- [x] **백업 현황 요약** 섹션
  - 전체 서버 수
  - 성공 건수
  - 실패 건수
  - 진행중 건수
- [x] **성공한 백업 목록** 테이블
  - 서버명, 완료시간, 백업 크기 등
- [x] **실패한 백업 상세** 섹션 (⚠️ 강조 표시)
  - 서버명, 실패시간
  - **에러 로그 표시** (필수)
- [x] **진행 중인 백업** 목록
  - 서버명, 시작시간

### 스타일링
- [x] CSS 스타일링 (가독성 향상, 실패 항목 강조)

---

## 3.3 리포트 생성 모듈

### ReportGenerator 구현
- [x] `src/report/report_generator.py` 생성
- [x] Jinja2 환경 설정
- [x] 템플릿 렌더링 함수 구현
- [x] 리포트 파일명 생성 (타임스탬프 포함)
- [x] `reports/` 디렉토리에 HTML 파일 저장
- [x] 파일 생성 성공/실패 로깅

### Phase 완료
- [x] Phase 3 완료 후 main에 병합
  ```bash
  git checkout main
  git merge phase-3-report --no-ff -m "Phase 3: 리포트 생성 시스템 완료"
  git tag v0.3-phase3
  ```

---

## 📝 작업 결과

- 백업 작업 및 통계 데이터 모델 설계 완료
- Jinja2 기반 HTML 템플릿 작성 완료
- 리포트 생성 모듈 구현 완료
- 리포트 파일명 형식: `mail_YYYYMMDDHHMMSS.html`

---

## 🔗 관련 문서

- [프로젝트 요구사항](../project.md)
- [개발 가이드](../dev.md)
