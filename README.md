# 동작SN 네이버 플레이스 순위 추적기

동작에스엔재활의학과의원의 네이버 플레이스 노출 순위를 **매일 자동으로 기록·시각화**하는 도구입니다.
(원본: [goaldeer/naver-place-rank-tracker](https://github.com/goaldeer/naver-place-rank-tracker) 를 병원 키워드로 커스터마이징)

## 추적 대상 (세팅 완료)

- **업체**: 동작에스엔재활의학과의원
- **키워드 8종**

| # | 키워드 | 구분 |
|---|--------|------|
| 1 | 동작구 정형외과 | 지역(구) × 진료과 |
| 2 | 동작구 도수치료 | 지역(구) × 치료 |
| 3 | 상도동 도수치료 | 지역(동) × 치료 |
| 4 | 신대방삼거리 도수치료 | 역세권 × 치료 |
| 5 | 신대방삼거리 정형외과 | 역세권 × 진료과 |
| 6 | 상도동 정형외과 | 지역(동) × 진료과 |
| 7 | 도수치료 | 광역(경쟁 심함) |
| 8 | 정형외과 | 광역(경쟁 심함) |

## 사용 방법 (10분 세팅)

### 1) GitHub 저장소 만들기
1. GitHub에서 **Private 저장소** 새로 생성 (예: `sn-place-rank`)
2. 이 폴더 전체를 업로드(push)

```bash
cd sn-place-rank-tracker
git init && git add . && git commit -m "초기 세팅"
git branch -M main
git remote add origin https://github.com/<내계정>/sn-place-rank.git
git push -u origin main
```

### 2) 자동 실행 확인
- `.github/workflows/daily_update.yml` 이 **매일 오전 10시(KST)** 에 자동 실행되어
  `data/search_results.csv` 에 순위가 한 줄씩 쌓입니다.
- 저장소 → **Actions 탭 → "SN Daily Place Rank Update" → Run workflow** 로 즉시 수동 실행도 가능합니다.
- Settings → Actions → General → Workflow permissions 를 **Read and write** 로 설정해야 결과가 커밋됩니다.

### 3) 대시보드 보기 (선택)
```bash
pip install -r requirements.txt
streamlit run app.py
```
- 또는 [Streamlit Cloud](https://streamlit.io/cloud) 무료 배포로 팀원 누구나 브라우저에서 확인

## 순위 데이터 읽는 법

- `rank` 값 = 광고 제외 오가닉 순위
- `rank = -1` = **미노출** (해당 키워드 목록에서 병원이 발견되지 않음)
  - 특히 7·8번 광역 키워드와 "정형외과" 계열은 초기에 -1이 정상입니다.
    -1 → 숫자로 바뀌는 시점이 스마트플레이스 최적화의 성과 지표입니다.

## 주의사항

- 네이버 페이지 구조가 바뀌면 파싱이 실패할 수 있습니다 (`modules/search_engine.py`의 CSS 선택자 수정 필요). 월 1회 Actions 로그 확인 권장.
- 하루 1회 실행 유지 (과도한 자동 조회는 차단 위험).
- 키워드 추가는 `data/keywords.csv` 에 행 추가 후 push.
