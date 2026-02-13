Here’s a clean set of **endpoints + JSON structs** you can use to connect **frontend ↔ backend** for your CityTrip app.

## Base

`/api/v1`

---

## 1) Categories (for filters)

### GET `/categories`

**Response**

```json
{
  "items": [
    { "id": "bar", "label": "Bar" },
    { "id": "restaurant", "label": "Restaurant" },
    { "id": "event", "label": "Event" },
    { "id": "cafe", "label": "Café" }
  ]
}
```

---

## 2) List places/events for map + cards

### GET `/spots?city=Berlin&lat=52.52&lng=13.405&radiusKm=20&category=bar&from=2026-02-13&to=2026-02-20`

* `lat/lng/radiusKm` optional (for “near me”)
* `from/to` optional (especially for events)
* `category` optional

**Response**

```json
{
  "meta": {
    "city": "Berlin",
    "radiusKm": 20,
    "count": 2
  },
  "items": [
    {
      "id": "sp_1001",
      "type": "restaurant",
      "name": "Trattoria Roma",
      "shortDescription": "Italian food, good for groups.",
      "category": "restaurant",
      "tags": ["pizza", "pasta"],
      "location": {
        "address": "Example Street 12",
        "city": "Berlin",
        "country": "DE",
        "lat": 52.5208,
        "lng": 13.4095
      },
      "openingHours": {
        "mon": "12:00-22:00",
        "tue": "12:00-22:00"
      },
      "priceLevel": 2,
      "rating": { "avg": 4.4, "count": 128 },
      "media": {
        "coverUrl": "https://example.com/img/trattoria.jpg"
      },
      "createdAt": "2026-02-01T10:00:00Z",
      "updatedAt": "2026-02-10T18:20:00Z"
    },
    {
      "id": "ev_2001",
      "type": "event",
      "name": "Live Jazz Night",
      "shortDescription": "Jazz band + drinks.",
      "category": "event",
      "tags": ["music", "jazz"],
      "location": {
        "address": "Music Hall 3",
        "city": "Berlin",
        "country": "DE",
        "lat": 52.517,
        "lng": 13.4
      },
      "event": {
        "startAt": "2026-02-15T19:00:00Z",
        "endAt": "2026-02-15T23:00:00Z",
        "ticketUrl": "https://example.com/tickets"
      },
      "priceLevel": 1,
      "media": {
        "coverUrl": "https://example.com/img/jazz.jpg"
      },
      "createdAt": "2026-02-05T12:00:00Z",
      "updatedAt": "2026-02-05T12:00:00Z"
    }
  ]
}
```

---

## 3) Spot details page

### GET `/spots/{id}`

**Response**

```json
{
  "id": "sp_1001",
  "type": "restaurant",
  "name": "Trattoria Roma",
  "description": "Longer description text...",
  "category": "restaurant",
  "tags": ["pizza", "pasta", "family"],
  "contact": {
    "phone": "+49 30 123456",
    "website": "https://trattoria.example",
    "instagram": "https://instagram.com/trattoria"
  },
  "location": {
    "address": "Example Street 12",
    "zip": "10115",
    "city": "Berlin",
    "country": "DE",
    "lat": 52.5208,
    "lng": 13.4095
  },
  "openingHours": {
    "mon": "12:00-22:00",
    "tue": "12:00-22:00",
    "wed": "12:00-22:00"
  },
  "priceLevel": 2,
  "media": {
    "coverUrl": "https://example.com/img/cover.jpg",
    "gallery": [
      "https://example.com/img/1.jpg",
      "https://example.com/img/2.jpg"
    ]
  },
  "owner": {
    "id": "u_9001",
    "displayName": "Max M."
  },
  "createdAt": "2026-02-01T10:00:00Z",
  "updatedAt": "2026-02-10T18:20:00Z"
}
```

---

## 4) Create new spot (for owners)

### POST `/spots`

**Request**

```json
{
  "type": "bar",
  "name": "Neon Bar",
  "shortDescription": "Cocktails and good music.",
  "description": "More details...",
  "category": "bar",
  "tags": ["cocktails", "music"],
  "location": {
    "address": "Night Street 7",
    "zip": "10117",
    "city": "Berlin",
    "country": "DE",
    "lat": 52.5212,
    "lng": 13.4011
  },
  "openingHours": {
    "fri": "18:00-03:00",
    "sat": "18:00-03:00"
  },
  "contact": {
    "website": "https://neonbar.example"
  },
  "priceLevel": 2,
  "media": {
    "coverUrl": "https://example.com/neon.jpg"
  }
}
```

**Response**

```json
{
  "id": "sp_1234",
  "createdAt": "2026-02-13T08:30:00Z"
}
```

---

## 5) Update / delete (owner)

### PATCH `/spots/{id}`

**Request**

```json
{
  "shortDescription": "New short text",
  "tags": ["cocktails", "dj"]
}
```

### DELETE `/spots/{id}`

**Response**

```json
{ "deleted": true }
```

---

## 6) Reviews (optional but nice)

### GET `/spots/{id}/reviews`

**Response**

```json
{
  "items": [
    {
      "id": "r_1",
      "spotId": "sp_1001",
      "rating": 5,
      "comment": "Great food!",
      "author": { "displayName": "Lisa" },
      "createdAt": "2026-02-11T20:00:00Z"
    }
  ]
}
```

### POST `/spots/{id}/reviews`

**Request**

```json
{
  "rating": 4,
  "comment": "Nice place."
}
```

---

## 7) Auth (simple version)

### POST `/auth/register`

```json
{
  "email": "owner@example.com",
  "password": "secret123",
  "role": "owner",
  "displayName": "Neon Bar Owner"
}
```

### POST `/auth/login`

```json
{
  "email": "owner@example.com",
  "password": "secret123"
}
```

**Response**

```json
{
  "token": "jwt_or_session_token",
  "user": { "id": "u_9001", "role": "owner", "displayName": "Neon Bar Owner" }
}
```