# 내 상황을 아는 AI 비서

일반 ChatGPT는 사용자의 데이터를 모릅니다. 이 프로젝트는 **시계열 데이터를 요약**하고, 그 요약을 **시스템 프롬프트에 주입**해서 "내 데이터 기준"으로 답하는 AI 채팅 서비스입니다.

- 데이터 관리(CRUD): 날짜·값·메모 데이터를 추가/수정/삭제
- 데이터 요약: 기간, 개수, 합계/평균/최대/최소, 최근 추세(상승/하락/유지)
- 데이터 기반 AI 채팅: 요약을 프롬프트에 넣어 GPT가 맞춤형으로 답변
- 대화 기록: 대화 자동 저장, 목록 조회, 선택한 대화 메시지 다시 보기

## 배포 URL

| 구분 | URL |
|---|---|
| 프론트엔드 (Vercel) | https://your-app.vercel.app |
| 백엔드 API (Render) | https://your-api.onrender.com |
| Swagger UI | https://your-api.onrender.com/docs |

## 기술 스택

- Backend: Python 3.10+, FastAPI, Pydantic, Uvicorn
- Database: Firebase Firestore (firebase-admin)
- AI: OpenAI API (기본 모델 `gpt-4o-mini`)
- Frontend: HTML / CSS / JavaScript (프레임워크 없음)
- 배포: Render (백엔드), Vercel (프론트엔드)

## 프로젝트 구조

```
ai-secretary/
├── backend/
│   ├── main.py                  # FastAPI 앱, CORS, 라우터 등록
│   ├── config.py                # 환경 변수 로드
│   ├── db.py                    # Firebase 초기화, Firestore 클라이언트
│   ├── schemas.py               # Pydantic 모델 (요청/응답 검증)
│   ├── routers/                 # HTTP 엔드포인트만 담당
│   │   ├── data.py
│   │   ├── conversations.py
│   │   └── chat.py
│   ├── services/                # 비즈니스 로직 / DB 접근
│   │   ├── analysis.py          # 시계열 요약 계산
│   │   ├── data_service.py      # data 컬렉션 CRUD
│   │   ├── conversation_service.py  # conversations 컬렉션 CRUD
│   │   └── ai_service.py        # 프롬프트 구성 + GPT 호출
│   ├── scripts/seed_data.py     # 샘플/CSV 데이터 업로드
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html / style.css / app.js
    ├── config.js                # 로컬 개발용 API 주소
    ├── build.js                 # Vercel 빌드: API_BASE_URL 환경 변수 주입
    └── vercel.json
```

## 데이터 선정

- 기본 샘플: 2026-07-01부터 120일간의 일별 매출 (완만한 상승 + 주말 효과). `scripts/seed_data.py`로 생성합니다.
- 직접 데이터를 쓰려면 `date,value,memo` 헤더의 CSV를 만들어 업로드합니다. 최소 100개 이상의 데이터를 권장합니다.

```csv
date,value,memo
2026-07-01,2100000,화요일 매출
2026-07-02,2250000,
```

## API 목록

| Method | Endpoint | 설명 |
|---|---|---|
| POST | `/api/data` | 데이터 추가 |
| GET | `/api/data` | 데이터 목록 (날짜순) |
| PUT | `/api/data/{id}` | 데이터 수정 |
| DELETE | `/api/data/{id}` | 데이터 삭제 |
| GET | `/api/data/summary` | 요약 정보 (프롬프트 주입용) |
| POST | `/api/conversations` | 대화 저장 |
| GET | `/api/conversations` | 대화 목록 (messages 제외, `message_count`만 포함) |
| GET | `/api/conversations/{id}` | 특정 대화 전체 messages 조회 |
| DELETE | `/api/conversations/{id}` | 대화 삭제 |
| POST | `/api/chat` | AI 대화 (요약 주입 → GPT 호출 → 대화 자동 저장) |
| GET | `/health` | 서버 상태 확인 |

요약 응답 예시:

```json
{
  "period": "2026-07-01 ~ 2026-10-28",
  "count": 120,
  "metrics": { "total": 330000000, "average": 2750000, "max": 4100000, "min": 2000000 },
  "trend": "상승 (최근 30일 평균 +8.2% vs 직전 30일)",
  "latest": { "date": "2026-10-28", "value": 3200000 },
  "best": { "date": "2026-10-10", "value": 4100000 }
}
```

## Firestore 컬렉션 구조

- `data/{docId}`: `{ date: "YYYY-MM-DD", value: int, memo: str }`
- `conversations/{docId}`: `{ title, messages: [{role, content}], created_at, updated_at }`

## 로컬 실행 방법

### 0. 사전 준비
1. **Firebase**: 프로젝트 생성 → Firestore Database 생성(테스트 모드 가능) → 프로젝트 설정 > 서비스 계정 > 새 비공개 키 생성(JSON 다운로드)
2. **OpenAI**: API 키 발급 (과금이 발생할 수 있으니 사용량 한도를 설정하세요)

### 1. 백엔드
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # 값 채우기
# 다운받은 서비스 계정 JSON을 backend/serviceAccountKey.json 으로 저장

python scripts/seed_data.py       # 샘플 데이터 업로드 (또는 CSV 경로 지정)
uvicorn main:app --reload
```
- 확인: http://127.0.0.1:8000/docs

### 2. 프론트엔드
```bash
cd frontend
python -m http.server 5500
```
- 확인: http://localhost:5500
- `.env`의 `ALLOWED_ORIGINS`에 `http://localhost:5500`이 포함되어 있어야 합니다.

## 환경 변수

| 변수 | 위치 | 설명 |
|---|---|---|
| `OPENAI_API_KEY` | 백엔드 | OpenAI API 키 (필수) |
| `OPENAI_MODEL` | 백엔드 | 사용할 모델 (기본 `gpt-4o-mini`) |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | 백엔드(Render) | 서비스 계정 JSON 내용 전체 (배포용) |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | 백엔드(로컬) | 서비스 계정 JSON 파일 경로 (로컬용) |
| `ALLOWED_ORIGINS` | 백엔드 | CORS 허용 도메인 목록, 쉼표 구분 |
| `API_BASE_URL` | 프론트(Vercel) | 백엔드 Render 주소 (예: `https://your-api.onrender.com`) |

> 키 파일과 `.env`는 `.gitignore`에 포함되어 있어 GitHub에 올라가지 않습니다. 키는 코드에 직접 쓰지 마세요.

## 배포 방법

### 백엔드 (Render)
1. GitHub에 저장소 푸시 (`backend/` 기준)
2. Render → New → Web Service → 저장소 연결
3. 설정
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Environment에 `OPENAI_API_KEY`, `FIREBASE_SERVICE_ACCOUNT_JSON`(한 줄), `ALLOWED_ORIGINS` 입력
5. 배포 후 `https://…onrender.com/docs` 접속 확인

> 무료 티어는 일정 시간 요청이 없으면 잠들고, 첫 요청에 30초~1분이 걸릴 수 있습니다. 이 앱은 접속 시 자동으로 서버를 깨우고 안내 문구를 보여줍니다.

### 프론트엔드 (Vercel)
1. Vercel → New Project → 같은 저장소 연결
2. Root Directory: `frontend`
3. Environment Variables: `API_BASE_URL` = Render 백엔드 주소
4. Deploy 후 발급된 주소를 백엔드 `ALLOWED_ORIGINS`에 추가하고 Render를 재배포

## 설계 포인트 (과제 학습 목표 대응)

- **시계열 요약 흐름**: `analysis.py`가 원본 데이터를 기간/개수/통계/추세로 압축합니다. 전체 데이터를 프롬프트에 넣는 대신 요약만 넣으므로 토큰 비용이 줄고 답변이 핵심에 집중됩니다.
- **라우터/서비스 분리**: `routers/`는 HTTP 입출력만, `services/`는 DB와 계산을 담당합니다. DB 구조가 바뀌어도 라우터 코드는 그대로 둘 수 있습니다.
- **Pydantic 검증**: `schemas.py`에서 날짜 형식, 값의 0 이상 정수, 메모 길이, 메시지 role 등을 검증합니다. 잘못된 요청은 FastAPI가 자동으로 422 응답을 돌려줍니다.
- **Firestore CRUD**: `document()`로 ID를 만들고 `set`/`get`/`update`/`delete`로 다룹니다. 대화 목록은 `updated_at` 역순 정렬을 사용합니다.
- **컨텍스트 주입**: `build_system_prompt()`가 요약을 시스템 프롬프트에 넣고, 최근 대화 10개를 함께 보내 맥락을 이어갑니다. 모델은 이 데이터 범위 안에서 답하도록 지시받습니다.
- **CORS / 환경 변수 / 키 관리**: 브라우저는 다른 도메인(Vercel→Render) 요청을 CORS 정책으로 제한하므로 `ALLOWED_ORIGINS`에 프론트 주소를 넣어야 합니다. 키는 환경 변수로만 전달해 저장소 노출을 막습니다.

## 제출 스크린샷

- [ ] 데이터 요약이 보이는 채팅 화면 (질문 + 답변 포함): `docs/chat.png`
- [ ] 데이터 관리 화면 (추가/수정/삭제 중 1개 동작): `docs/data.png`
- [ ] 대화 기록 화면 (대화 불러오기 동작): `docs/history.png`
