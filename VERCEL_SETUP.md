# Vercel 배포 설정 가이드

## 환경변수 설정

Vercel 대시보드에서 다음 환경변수를 설정해야 합니다:

### 필수 환경변수

1. **CLIMATE_API_BASE_URL**
   - 값: `https://climate.gg.go.kr/ols/api/geoserver/wfs`
   - 설명: 경기기후플랫폼 API Base URL

2. **CLIMATE_API_KEY**
   - 값: `your_actual_api_key_here`
   - 설명: 경기기후플랫폼 API 키
   - ⚠️ 보안을 위해 절대 코드에 직접 입력하지 마세요!

### 선택적 환경변수

3. **DATABASE_URL**
   - 기본값: `sqlite:///./urban_cooling.db`
   - 프로덕션 환경에서는 PostgreSQL 사용 권장

4. **USE_MOCK_DATA**
   - 기본값: `False`
   - 테스트용으로 Mock 데이터 사용 시 `True`

## 설정 방법

### Vercel Dashboard에서 설정

1. Vercel 프로젝트 대시보드 접속
2. **Settings** > **Environment Variables** 메뉴 선택
3. 위의 환경변수들을 추가:
   - Name: 환경변수 이름 (예: `CLIMATE_API_KEY`)
   - Value: 실제 값
   - Environment: Production, Preview, Development 선택

### Vercel CLI로 설정

```bash
# 환경변수 추가
vercel env add CLIMATE_API_KEY

# 환경변수 확인
vercel env ls

# 환경변수 제거
vercel env rm CLIMATE_API_KEY
```

## 로컬 개발 환경

로컬 개발 시에는 `.env` 파일을 사용합니다:

```bash
# .env.example을 복사
cp .env.example .env

# .env 파일을 편집하여 실제 API 키 입력
# CLIMATE_API_KEY=your_actual_api_key_here
```

⚠️ **중요**: `.env` 파일은 절대 git에 커밋하지 마세요! (`.gitignore`에 이미 포함되어 있습니다)

## 배포

```bash
# 프로덕션 배포
vercel --prod

# 프리뷰 배포
vercel
```

## 보안 체크리스트

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] `vercel.json`에 API 키가 하드코딩되어 있지 않은지 확인
- [ ] Vercel Dashboard에 모든 환경변수가 설정되어 있는지 확인
- [ ] 소스 코드에 민감한 정보가 없는지 재확인
