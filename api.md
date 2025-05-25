# TripMind API 문서

## 1. 개요

TripMind API는 여행 일정 생성, 장소 검색, 캘린더 연동, 일정 공유 등의 기능을 제공하는 RESTful API입니다.

## 2. 기본 정보

- **Base URL**: `http://localhost:8000/api/v1`
- **인증**: JWT 토큰 기반 인증
- **응답 형식**: JSON

## 3. API 엔드포인트

### 3.1 여행 일정 API

#### 일정 생성

```http
POST /itineraries/
```

**요청 본문**:

```json
{
  "title": "제주도 여행",
  "start_date": "2024-04-01",
  "end_date": "2024-04-03",
  "preferences": {
    "budget": "중간",
    "style": "자연",
    "activities": ["관광", "맛집"]
  }
}
```

**응답**:

```json
{
  "id": 1,
  "title": "제주도 여행",
  "start_date": "2024-04-01",
  "end_date": "2024-04-03",
  "status": "created",
  "created_at": "2024-03-20T10:00:00Z"
}
```

#### 일정 조회

```http
GET /itineraries/{id}/
```

**응답**:

```json
{
  "id": 1,
  "title": "제주도 여행",
  "start_date": "2024-04-01",
  "end_date": "2024-04-03",
  "activities": [
    {
      "day": 1,
      "place": "성산일출봉",
      "time": "06:00",
      "description": "일출 관람"
    }
  ],
  "status": "completed",
  "created_at": "2024-03-20T10:00:00Z"
}
```

### 3.2 장소 검색 API

#### 키워드 검색

```http
GET /places/search/
```

**쿼리 파라미터**:

- `keyword`: 검색어
- `category`: 카테고리 (선택)
- `page`: 페이지 번호 (기본값: 1)
- `size`: 페이지 크기 (기본값: 10)

**응답**:

```json
{
  "total": 100,
  "page": 1,
  "size": 10,
  "places": [
    {
      "id": "1234567890",
      "name": "성산일출봉",
      "category": "관광지",
      "address": "제주시 성산읍",
      "coordinates": {
        "lat": 33.4583,
        "lng": 126.9422
      }
    }
  ]
}
```

### 3.3 캘린더 API

#### 일정 등록

```http
POST /calendar/events/
```

**요청 본문**:

```json
{
  "itinerary_id": 1,
  "calendar_id": "primary",
  "notify_before": "1h"
}
```

**응답**:

```json
{
  "id": "event_123",
  "calendar_id": "primary",
  "status": "scheduled",
  "created_at": "2024-03-20T10:00:00Z"
}
```

### 3.4 공유 API

#### 공유 링크 생성

```http
POST /sharing/links/
```

**요청 본문**:

```json
{
  "itinerary_id": 1,
  "expires_in": "7d",
  "permissions": ["view"]
}
```

**응답**:

```json
{
  "id": "link_123",
  "url": "https://tripmind.com/s/abc123",
  "expires_at": "2024-03-27T10:00:00Z",
  "created_at": "2024-03-20T10:00:00Z"
}
```

## 4. 에러 처리

### 4.1 에러 응답 형식

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "잘못된 요청입니다.",
    "details": {
      "field": "title",
      "reason": "필수 항목입니다."
    }
  }
}
```

### 4.2 주요 에러 코드

- `INVALID_REQUEST`: 잘못된 요청
- `UNAUTHORIZED`: 인증 실패
- `FORBIDDEN`: 권한 없음
- `NOT_FOUND`: 리소스 없음
- `INTERNAL_ERROR`: 서버 내부 오류

## 5. 인증

### 5.1 토큰 발급

```http
POST /auth/token/
```

**요청 본문**:

```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**응답**:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 3600
}
```

### 5.2 토큰 갱신

```http
POST /auth/token/refresh/
```

**요청 본문**:

```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 6. 요청 제한

- **Rate Limit**: 1000 요청/시간
- **최대 요청 크기**: 1MB
- **최대 응답 크기**: 10MB

## 7. 버전 관리

- API 버전은 URL에 포함 (`/api/v1/`)
- 주요 변경사항은 새로운 버전으로 릴리스
- 이전 버전은 1년간 지원

## 8. 웹소켓 API

### 8.1 실시간 업데이트

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/updates/");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("업데이트:", data);
};
```

### 8.2 이벤트 타입

- `itinerary_updated`: 일정 업데이트
- `place_added`: 장소 추가
- `calendar_synced`: 캘린더 동기화
- `share_created`: 공유 생성
