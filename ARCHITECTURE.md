# 🏗️ System Architecture

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │Dashboard │  │ AI Chat  │  │  Search  │  │ Profile  │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
└───────┼─────────────┼─────────────┼─────────────┼────────────── ┘
        │             │             │             │
┌───────┴─────────────┴─────────────┴─────────────┴──────────────┐
│                    FRONTEND (Next.js 15)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Components  │  Pages  │  API Routes  │  RAG  │  Utils   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬───────────────────────────────────┘
                             │ REST API / JSON
┌────────────────────────────┴───────────────────────────────────┐
│                  BACKEND (FastAPI + Python)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Intelligence │  │ Notifications│  │  Ingestion   │          │
│  │  - RAG       │  │  - Email     │  │  - Scraping  │          │
│  │  - Search    │  │  - SMS       │  │  - ETL       │          │
│  │  - Matching  │  │  - Push      │  │  - Pipeline  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐          │
│  │ Verification │  │   Security   │  │   Workflow   │          │
│  │  - OCR       │  │              │  │  - Engine    │          │
│  │              │  │  - Consent   │  │  - Tasks     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                        DATA LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │PostgreSQL│  │  Chroma  │  │ Supabase │  │  Redis   │        │
│  │(Relational│  │ (Vectors)│  │  (Auth)  │  │ (Cache)  │        │
│  │   Data)  │  │          │  │          │  │          │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │SendGrid  │  │  Twilio  │  │ Firebase │  │  Ollama  │        │
│  │ (Email)  │  │  (SMS)   │  │  (Push)  │  │  (LLM)   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. User Query Flow (RAG Chatbot)

```
User Query
    ↓
Frontend (Next.js)
    ↓
API Route (/api/chat)
    ↓
Vector Store Search
    ↓
Retrieve Top K Documents
    ↓
Build Context
    ↓
Ollama LLM
    ↓
Generate Response
    ↓
Return with Sources
    ↓
Display to User
```

### 2. Semantic Search Flow

```
User Search Query
    ↓
Frontend Search Page
    ↓
Backend API (/api/v1/search)
    ↓V
Embedding Generation
    ↓
ChromaDB Vector Search
    ↓
Similarity Scoring
    ↓
Filter & Rank Results
    ↓
Return Matches
    ↓
Display Results
```

### 3. Eligibility Matching Flow

```
Student Profile
    ↓
Get Opportunities
    ↓
For Each Opportunity:
    ├─> Check Category Match
    ├─> Check Income Criteria
    ├─> Check Location Match
    ├─> Check Academic Requirements
    ├─> Check Age Limits
    └─> Calculate Match Score
    ↓
Sort by Match Score
    ↓
Return Recommendations
```

### 4. Notification Flow

```
Trigger Event
(Deadline, Match, Status)
    ↓
Notification Orchestrator
    ↓
Check User Preferences
    ↓
Select Channels
    ├─> In-App → Database
    ├─> Email  → SendGrid API
    ├─> SMS    → Twilio API
    └─> Push   → Firebase FCM
    ↓
Log Delivery Status
    ↓
Store in History
```

---

## 🗄️ Database Schema

### Core Tables

```sql
-- Users (managed by Supabase Auth)
users (
    id UUID PRIMARY KEY,
    email VARCHAR,
    created_at TIMESTAMP
)

-- Student Profiles
student_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    full_name VARCHAR,
    date_of_birth DATE,
    category VARCHAR,
    income_annual INTEGER,
    state VARCHAR,
    district VARCHAR,
    college VARCHAR,
    degree VARCHAR,
    cgpa DECIMAL,
    skills JSONB,
    created_at TIMESTAMP
)

-- Opportunities
opportunities (
    id UUID PRIMARY KEY,
    source VARCHAR,
    category VARCHAR,
    title VARCHAR,
    description TEXT,
    amount_min INTEGER,
    amount_max INTEGER,
    deadline DATE,
    eligibility_rules JSONB,
    documents_required JSONB,
    application_url VARCHAR,
    state_filter JSONB,
    tags JSONB,
    created_at TIMESTAMP
)

-- Applications
applications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    opportunity_id UUID REFERENCES opportunities(id),
    state VARCHAR,
    match_score DECIMAL,
    checklist JSONB,
    progress_pct INTEGER,
    saved BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Notifications
notifications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR,
    body TEXT,
    channel VARCHAR,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
)

-- Notification Preferences
notification_preferences (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    email_enabled BOOLEAN,
    sms_enabled BOOLEAN,
    push_enabled BOOLEAN,
    deadline_reminders BOOLEAN,
    new_matches BOOLEAN,
    status_updates BOOLEAN
)

-- Notification History
notification_history (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    notification_type VARCHAR,
    channel VARCHAR,
    recipient VARCHAR,
    success BOOLEAN,
    error TEXT,
    sent_at TIMESTAMP
)

-- Documents
documents (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    document_type VARCHAR,
    file_path VARCHAR,
    verification_status VARCHAR,
    extracted_fields JSONB,
    confidence_score DECIMAL,
    uploaded_at TIMESTAMP
)

-- Feedback
feedback (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    opportunity_id UUID REFERENCES opportunities(id),
    feedback_type VARCHAR,
    comment TEXT,
    submitted_at TIMESTAMP
)

-- Consent Records
consent_records (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    purpose VARCHAR,
    granted BOOLEAN,
    granted_at TIMESTAMP,
    revoked_at TIMESTAMP
)

-- Audit Logs
audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID,
    action VARCHAR,
    resource VARCHAR,
    details JSONB,
    ip_address VARCHAR,
    timestamp TIMESTAMP
)
```

---


## 🔐 Security Architecture

### Authentication Flow

```
User Login Request
    ↓
Supabase Auth
    ↓
JWT Token Generated
    ↓
Token Stored (HttpOnly Cookie)
    ↓
Include in API Requests
    ↓
Backend Validates Token
    ↓
Extract User Context
    ↓
Check RBAC Permissions
    ↓
Process Request
```

### Authorization Layers

1. **Authentication** - Supabase JWT tokens
2. **API Gateway** - Rate limiting, CORS
3. **RBAC** - Role-based access control
4. **Row-Level Security** - Supabase RLS policies
5. **Data Encryption** - At rest and in transit
6. **Audit Logging** - All sensitive operations

---

## 🚀 Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────────────┐
│          Load Balancer (Cloudflare)         │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
┌───────▼──────┐  ┌──▼────────────┐
│   Frontend   │  │    Backend    │
│   (Vercel)   │  │  (Railway)    │
│              │  │               │
│  - Next.js   │  │  - FastAPI    │
│  - CDN       │  │  - Uvicorn    │
│  - Edge      │  │  - Workers    │
└──────┬───────┘  └───┬───────────┘
       │              │
       │     ┌────────┴────────┐
       │     │                 │
    ┌──▼─────▼──┐   ┌─────────▼──────┐
    │  Supabase │   │   PostgreSQL   │
    │           │   │   (Managed)    │
    │  - Auth   │   │                │
    │  - Storage│   │   - Primary DB │
    └───────────┘   └────────────────┘
                            │
              ┌─────────────┴────────┐
              │                      │
       ┌──────▼──────┐    ┌─────────▼────┐
       │   ChromaDB  │    │    Redis     │
       │  (Vectors)  │    │   (Cache)    │
       └─────────────┘    └──────────────┘
```

---

## 📊 Performance Considerations

### Frontend Optimization
- Server-side rendering (SSR)
- Static generation for landing pages
- Image optimization (Next.js Image)
- Code splitting
- Lazy loading components
- CDN for static assets

### Backend Optimization
- Database connection pooling
- Redis caching
- Query optimization
- Async/await for I/O operations
- Background tasks (Celery)
- API response compression

### Database Optimization
- Proper indexing
- Query optimization
- Connection pooling
- Read replicas
- Materialized views
- Partitioning large tables

---

## 🔍 Monitoring & Observability

### Metrics to Track
- API response times
- Database query performance
- Error rates
- User engagement
- Notification delivery rates
- LLM response times

### Logging Strategy
- Application logs (Winston/Python logging)
- Access logs (Nginx)
- Database query logs
- Audit logs (user actions)
- Error tracking (Sentry)

### Health Checks
- Frontend: `/health`
- Backend: `/health`
- Database: Connection test
- Redis: Ping test
- External services: Status checks

---

**This architecture is designed for scalability, security, and maintainability.** 🚀
