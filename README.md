# EduPilot - Student Success AI Copilot

**Comprehensive Technical Documentation**

> A multi-agent AI system for Indian students providing scholarship discovery, eligibility checks, document verification, internship/hackathon tracking, and career guidance through conversational AI.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Complete Workflow Diagram](#complete-workflow-diagram)
6. [Feature-by-Feature Documentation](#feature-by-feature-documentation)
7. [Installation & Setup](#installation--setup)
8. [Testing](#testing)
9. [AI Quality Metrics & Evaluation](#ai-quality-metrics--evaluation)
10. [API Endpoints](#api-endpoints)
11. [Database Schema](#database-schema)

---

## Project Overview

**EduPilot** is an agentic AI platform designed specifically for Indian students to:

- **Discover** scholarships, internships, and hackathons from 847+ sources
- **Verify** eligibility automatically using AI-powered rule engines
- **Process** documents (marksheets, income certificates, Aadhaar) using OCR + TEE
- **Recommend** personalized opportunities using two-stage hybrid RAG
- **Notify** students about deadlines via Email, SMS, Push, and Voice calls
- **Chat** with an AI assistant powered by Groq + LangChain + LangGraph
- **Track** application workflows with state machines
- **Evaluate** AI quality continuously with Ragas framework (67.65% overall score)
- **Experiment** using A/B testing framework for continuous improvement


---

## Tech Stack

### Frontend (Next.js 15)
- **Framework**: Next.js 15.3.3 (App Router)
- **Language**: TypeScript 5
- **UI Library**: React 19.2.4
- **Styling**: TailwindCSS 4 + PostCSS
- **Authentication**: Supabase Auth (@supabase/ssr, @supabase/supabase-js)
- **Icons**: Lucide React 1.26.0
- **Theme**: next-themes (dark/light mode)

### Backend (Python FastAPI)
- **Framework**: FastAPI 0.115+
- **Server**: Uvicorn (ASGI)
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL (pgvector) + SQLite (fallback)
- **Vector DB**: ChromaDB 0.5+ (persistent)
- **Task Queue**: Celery 5.4 + Redis 5.2
- **Validation**: Pydantic 2.8+

### AI & ML Stack
- **LLM**: Groq Cloud API (llama-3.3-70b-versatile) - 10x faster than local inference
- **Framework**: LangChain 0.3+ + LangGraph 0.2+ (agentic workflows)
- **Embeddings**: sentence-transformers 2.2+
- **RAG**: Two-stage hybrid search (brief lists → detailed responses)
- **Evaluation**: Ragas framework with gemma4:cloud judge model
- **OCR**: Tesseract (pytesseract 0.3+)

### External Services
- **Email**: SendGrid 6.11+
- **SMS/Voice**: Twilio 9.0+
- **Push Notifications**: Firebase Admin 6.5+
- **Web Scraping**: Playwright 1.40+ + BeautifulSoup4 4.12+

### Security & Compliance
- **Encryption**: cryptography 41.0+ (AES-256-GCM, Fernet)
- **TEE**: AWS Nitro Enclaves / Azure Confidential (mock mode available)
- **Auth**: python-jose 3.3+ (JWT)
- **Phone Validation**: phonenumbers 8.13+


---

## Architecture

**EduPilot** follows a **microservices-inspired monolith** architecture:

- **Frontend**: Next.js 15 (SSR + Client Components) → API Gateway
- **Backend**: FastAPI (RESTful API) → Business Logic
- **Database**: PostgreSQL (relational) + ChromaDB (vector embeddings)
- **Cache/Queue**: Redis (Celery broker + caching)
- **AI Engine**: Groq Cloud API (llama-3.3-70b-versatile) + LangChain/LangGraph (agents)

### Key Design Patterns

1. **Agent-Based Architecture**: Specialized agents for scholarships, internships, hackathons, documents, chat
2. **Hybrid RAG**: Combines semantic vector search (ChromaDB) with structured SQL queries
3. **State Machine Workflows**: Application lifecycle managed via FSM (discovered → verified → submitted)
4. **A/B Testing Framework**: Built-in experimentation service for recommendation algorithms
5. **Multi-Channel Notifications**: Orchestrator pattern for Email/SMS/Push/Voice
6. **TEE-Protected Document Processing**: Encrypted at rest + in-flight with audit logs
7. **Consent-First Data Access**: DPDP Act compliant with consent checks before decryption

---

## Project Structure

### Total Files (Excluding Dependencies)
- **Python Files**: 122 (.py)
- **TypeScript/TSX**: 51 (.tsx, .ts)
- **Markdown Docs**: 14 (.md)
- **JSON Configs**: 11 (.json)
- **CSV Data**: 11 (.csv)
- **SQL Scripts**: 2 (.sql)


### Directory Structure

```
student-ai-copilot/
├── app/                          # Frontend (Next.js 15)
│   ├── app/                      # Next.js App Router
│   │   ├── auth/                 # Authentication pages (login, signup, callback)
│   │   ├── components/           # React components (home, dashboard)
│   │   ├── dashboard/            # Protected dashboard pages
│   │   │   ├── admin/            # Admin panel
│   │   │   ├── chat/             # AI chatbot interface
│   │   │   ├── scholarships/     # Scholarship browser
│   │   │   ├── internships/      # Internship listings
│   │   │   ├── hackathons/       # Hackathon finder
│   │   │   ├── profile/          # Student profile editor
│   │   │   ├── documents/        # Document upload/verification
│   │   │   ├── notifications/    # Notification preferences
│   │   │   └── search/           # Semantic search interface
│   │   └── lib/                  # Utility functions (API client, Supabase)
│   ├── api/                      # API route handlers (Next.js API routes)
│   ├── data/                     # Static JSON data (schemes)
│   ├── public/                   # Static assets (logos, icons)
│   └── package.json              # Frontend dependencies
│
├── services/                     # Backend (Python FastAPI)
│   ├── app/
│   │   ├── agents/               # AI Agents (chatbot, scholarship, internship, hackathon, document)
│   │   ├── analytics/            # A/B testing + metrics
│   │   ├── api/
│   │   │   ├── middleware/       # Experiment context injection
│   │   │   └── routes/           # FastAPI endpoints (17 route modules)
│   │   ├── db/                   # Database models + session management
│   │   ├── ingestion/            # Data connectors (NSP, MahaDBT, Internshala, etc.)
│   │   ├── intelligence/         # Eligibility, embeddings, recommendations, vector search
│   │   ├── knowledge/            # Hybrid RAG implementation
│   │   ├── notifications/        # Email, SMS, Push, Voice, Orchestrator, Deadline Monitor
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── security/             # Document encryption, TEE, RBAC, consent
│   │   ├── verification/         # OCR, parsers, gov API verification, auto-verification engine
│   │   └── workflow/             # State machine for application tracking
│   ├── eval/                     # Evaluation (Ragas, DeepEval) + golden datasets
│   ├── tests/                    # Pytest test suite (19 test modules)
│   ├── requirements.txt          # Backend dependencies
│   └── .env                      # Environment variables
│
├── chroma_data/                  # ChromaDB vector store (persistent)
├── secure_documents/             # Encrypted document storage
├── docker-compose.yml            # Multi-container setup (postgres, redis, api, worker)
└── README.md                     # This file
```


---

## Complete Workflow Diagram

```mermaid
graph TB
    subgraph "User Entry Points"
        A[Student Browser] --> B[Next.js Frontend]
        C[Mobile App] --> B
    end

    subgraph "Frontend Layer - Next.js 15"
        B --> D[Landing Page]
        B --> E[Auth Pages<br/>Login/Signup]
        B --> F[Dashboard<br/>Protected Routes]
        
        E --> G[Supabase Auth]
        G --> H[JWT Token]
        
        F --> I[Profile Editor]
        F --> J[Scholarship Browser]
        F --> K[Internship Listings]
        F --> L[Hackathon Finder]
        F --> M[AI Chat Interface]
        F --> N[Document Upload]
        F --> O[Semantic Search]
        F --> P[Notification Prefs]
    end

    subgraph "API Gateway"
        H --> Q[FastAPI Backend<br/>Port 8000]
        Q --> R[CORS Middleware]
        R --> S[Experiment Context<br/>Middleware]
        S --> T[Route Handlers]
    end

    subgraph "Backend Services - Python FastAPI"
        T --> U[Profile API<br/>/api/v1/profile]
        T --> V[Scholarships API<br/>/api/v1/scholarships]
        T --> W[Internships API<br/>/api/v1/internships]
        T --> X[Hackathons API<br/>/api/v1/hackathons]
        T --> Y[Chat API<br/>/api/v1/chat]
        T --> Z[Documents API<br/>/api/v1/documents]
        T --> AA[Workflow API<br/>/api/v1/workflow]
        T --> AB[Notifications API<br/>/api/v1/notifications]
        T --> AC[Admin API<br/>/api/v1/admin]
        T --> AD[Experiments API<br/>/api/v1/experiments]
        T --> AE[Feedback API<br/>/api/v1/feedback]
        T --> AF[Consent API<br/>/api/v1/consent]
        T --> AG[Search API<br/>/api/v1/search]
    end


    subgraph "AI Agent Layer"
        Y --> AH[Chatbot Agent<br/>LangGraph + Ollama]
        V --> AI[Scholarship Agent]
        W --> AJ[Internship Agent]
        X --> AK[Hackathon Agent]
        Z --> AL[Document Identifier Agent]
        
        AH --> AM[Hybrid RAG<br/>ChromaDB + SQL]
        AI --> AM
        AJ --> AM
        AK --> AM
    end

    subgraph "Intelligence Services"
        AM --> AN[Vector Search<br/>ChromaDB Semantic]
        AM --> AO[Eligibility Engine<br/>Rule-based]
        AM --> AP[Recommendation Engine<br/>Scoring + Ranking]
        AL --> AQ[OCR Service<br/>Tesseract]
        AL --> AR[Document Parser<br/>Field Extraction]
        AL --> AS[Gov API Verification<br/>Aadhaar, Income]
        AL --> AT[Auto-Verification Engine<br/>Confidence Scoring]
    end

    subgraph "Security Layer"
        Z --> AU[TEE Service<br/>Secure Enclave]
        Z --> AV[Document Store<br/>AES-256-GCM Encryption]
        AV --> AW[Consent Check<br/>Before Decrypt]
        AW --> AX[Audit Log<br/>Write-Only]
    end

    subgraph "Data Ingestion Pipeline"
        AY[Celery Worker<br/>Beat Scheduler] --> AZ[Connector Registry]
        AZ --> BA[NSP Connector]
        AZ --> BB[MahaDBT Connector]
        AZ --> BC[MyScheme Connector]
        AZ --> BD[AICTE Connector]
        AZ --> BE[Internshala Scraper<br/>Playwright]
        AZ --> BF[Unstop Connector<br/>Hackathons]
        
        BA --> BG[Normalizer<br/>Unified Schema]
        BB --> BG
        BC --> BG
        BD --> BG
        BE --> BG
        BF --> BG
        
        BG --> BH[(PostgreSQL<br/>Opportunities Table)]
        BG --> AN
    end

    subgraph "Notification System"
        AB --> BI[Notification Orchestrator<br/>Multi-Channel]
        BI --> BJ[Email Service<br/>SendGrid]
        BI --> BK[SMS Service<br/>Twilio]
        BI --> BL[Voice Service<br/>Twilio Calls]
        BI --> BM[Push Service<br/>Firebase FCM]
        
        BN[Deadline Monitor<br/>Celery Task] --> BI
    end


    subgraph "Data Persistence"
        BH --> BO[(Users Table)]
        BH --> BP[(Student Profiles)]
        BH --> BQ[(Applications FSM)]
        BH --> BR[(Notifications)]
        BH --> BS[(Documents Encrypted)]
        BH --> BT[(Consent Records)]
        BH --> BU[(Audit Logs)]
        BH --> BV[(Experiments<br/>Variants + Assignments)]
        BH --> BW[(Feedback)]
        BH --> BX[(User Events Analytics)]
        BH --> BY[(Chat Threads + Messages)]
        BH --> BZ[(User Memories<br/>Long-term)]
        
        AN --> CA[(ChromaDB<br/>Vector Embeddings)]
    end

    subgraph "Analytics & Experimentation"
        AD --> CB[Experiment Service<br/>A/B Testing]
        CB --> CC[User Assignment<br/>Consistent Hashing]
        CC --> BV
        
        AE --> CD[Feedback Collector]
        CD --> BW
        
        CE[Metrics Calculator] --> BW
        CE --> BX
        CE --> CF[Accuracy Metrics<br/>FP/FN Tracking]
    end

    subgraph "Workflow State Machine"
        AA --> CG[Workflow Engine<br/>FSM]
        CG --> CH[States:<br/>discovered → eligibility_check<br/>→ document_validation<br/>→ human_review<br/>→ submitted → tracking]
        CH --> BQ
    end

    subgraph "External Integrations"
        BJ --> CI[SendGrid API]
        BK --> CJ[Twilio SMS API]
        BL --> CK[Twilio Voice API]
        BM --> CL[Firebase Cloud Messaging]
        AS --> CM[UIDAI Aadhaar API]
        AS --> CN[Income Certificate API]
    end

    %% Request/Response Flow
    I -.Profile Update.-> U
    U -.Save.-> BP
    
    J -.Get Scholarships.-> V
    V -.Query.-> AM
    AM -.Vector Search.-> CA
    AM -.Eligibility.-> AO
    AM -.Results.-> V
    V -.Response.-> J
    
    M -.Chat Message.-> Y
    Y -.RAG.-> AM
    Y -.LLM.-> AH
    AH -.Response.-> M
    
    N -.Upload.-> Z
    Z -.OCR.-> AQ
    Z -.Encrypt.-> AV
    AV -.Store.-> BS
```

---

## Complete End-to-End Feature Integration Workflow

This diagram shows how all major features are interconnected in a real-world user journey from login to scholarship application completion.

```mermaid
graph TB
    %% User Journey Start
    START([Student Visits EduPilot]) --> AUTH{Authenticated?}
    AUTH -->|No| LOGIN[Login/Signup Page]
    LOGIN --> SUPABASE[Supabase Auth]
    SUPABASE --> JWT[JWT Token Generated]
    AUTH -->|Yes| DASHBOARD[Dashboard Home]
    JWT --> DASHBOARD

    %% Feature 1: Profile Setup (Foundation for all other features)
    DASHBOARD --> PROFILE_CHECK{Profile<br/>Complete?}
    PROFILE_CHECK -->|No| PROFILE_FORM[Fill Profile Form]
    PROFILE_FORM --> PROFILE_SAVE[Save Profile to DB]
    PROFILE_SAVE --> READINESS[Calculate Readiness Score]
    READINESS --> PROFILE_CHECK
    PROFILE_CHECK -->|Yes| FEATURE_SELECT[Choose Feature]

    %% Feature Selection
    FEATURE_SELECT --> F1[Browse Scholarships]
    FEATURE_SELECT --> F2[Chat with AI]
    FEATURE_SELECT --> F3[Upload Documents]
    FEATURE_SELECT --> F4[Search Opportunities]
    FEATURE_SELECT --> F5[Track Applications]

    %% FEATURE 1: Browse Scholarships (RAG + Eligibility)
    F1 --> FETCH_SCHOLARSHIPS[GET /api/v1/scholarships]
    FETCH_SCHOLARSHIPS --> HYBRID_RAG1[Hybrid RAG Engine]
    HYBRID_RAG1 --> VECTOR_SEARCH1[ChromaDB Semantic Search<br/>25 candidates]
    VECTOR_SEARCH1 --> LOAD_OPPS1[Load Full Opportunities<br/>from PostgreSQL]
    LOAD_OPPS1 --> ELIGIBILITY_CHECK1[Run Eligibility Rules<br/>for Student Profile]
    ELIGIBILITY_CHECK1 --> RANK1[Rank by Eligibility<br/>+ Relevance Score]
    RANK1 --> DISPLAY_SCHOLARSHIPS[Display Top 8 Matches]
    
    DISPLAY_SCHOLARSHIPS --> USER_ACTION1{User Action}
    USER_ACTION1 -->|Save| SAVE_APP[Create Application<br/>state=discovered]
    USER_ACTION1 -->|Apply| START_WORKFLOW[Trigger Workflow]
    USER_ACTION1 -->|Feedback| SUBMIT_FEEDBACK[POST /api/v1/feedback<br/>relevant/not_relevant]
    
    SUBMIT_FEEDBACK --> LOG_EVENT1[Log UserEvent<br/>for A/B Testing]
    LOG_EVENT1 --> METRICS_CALC[MetricsCalculator<br/>Update Precision/Recall]

    %% FEATURE 2: AI Chat (LangGraph + Memory)
    F2 --> CHAT_INTERFACE[Chat Interface]
    CHAT_INTERFACE --> SEND_MSG[POST /api/v1/chat]
    SEND_MSG --> CHATBOT_AGENT[Chatbot Agent<br/>LangGraph]
    
    CHATBOT_AGENT --> THREAD_MGT[Get/Create Thread<br/>Load Last 12 Messages]
    THREAD_MGT --> MEMORY_LOAD[Load Long-Term Memory<br/>UserMemory Table]
    MEMORY_LOAD --> DETECT_INTENT{Needs<br/>Opportunity<br/>Data?}
    
    DETECT_INTENT -->|No| DIRECT_LLM[Ollama LLM<br/>Direct Response]
    DETECT_INTENT -->|Yes| HYBRID_RAG2[Hybrid RAG<br/>Retrieve 8 Docs]
    HYBRID_RAG2 --> VECTOR_SEARCH2[Semantic Search]
    VECTOR_SEARCH2 --> ELIGIBILITY_CHECK2[Filter by Eligibility]
    ELIGIBILITY_CHECK2 --> FORMAT_CONTEXT[Format Context<br/>amounts, deadlines, docs]
    FORMAT_CONTEXT --> LLM_WITH_CONTEXT[Ollama LLM<br/>Context + Profile + Memory]
    
    LLM_WITH_CONTEXT --> STREAM_RESPONSE[Stream Tokens]
    DIRECT_LLM --> STREAM_RESPONSE
    STREAM_RESPONSE --> SAVE_THREAD[Save to ChatThread<br/>+ ChatMessageRecord]
    SAVE_THREAD --> EXTRACT_MEMORY{User said<br/>'remember'?}
    EXTRACT_MEMORY -->|Yes| SAVE_MEMORY[Save to UserMemory]
    EXTRACT_MEMORY -->|No| CHAT_DONE[Display Response]
    SAVE_MEMORY --> CHAT_DONE
    
    CHAT_DONE --> USER_ACTION2{Continue?}
    USER_ACTION2 -->|Ask More| SEND_MSG
    USER_ACTION2 -->|Save Scholarship| SAVE_APP
    USER_ACTION2 -->|Upload Doc| F3

    %% FEATURE 3: Document Upload & Verification (OCR + TEE + Auto-Verify)
    F3 --> DOC_UPLOAD[Upload Document Image]
    DOC_UPLOAD --> POST_DOC[POST /api/v1/documents/upload]
    POST_DOC --> TEE_PROCESS[TEE Service<br/>Encrypt in Enclave]
    TEE_PROCESS --> OCR_EXTRACT[OCR Service<br/>Tesseract Extract Text]
    OCR_EXTRACT --> DOC_PARSER[Document Parser<br/>Extract Fields]
    DOC_PARSER --> DOC_TYPE{Document<br/>Type?}
    
    DOC_TYPE -->|Aadhaar| GOV_VERIFY_AADHAAR[UIDAI API<br/>Verify Aadhaar]
    DOC_TYPE -->|Income Cert| GOV_VERIFY_INCOME[State Portal API<br/>Verify Income]
    DOC_TYPE -->|Marksheet| SKIP_GOV[No Gov API]
    
    GOV_VERIFY_AADHAAR --> CALC_CONFIDENCE[Calculate Confidence<br/>OCR + Gov API]
    GOV_VERIFY_INCOME --> CALC_CONFIDENCE
    SKIP_GOV --> CALC_CONFIDENCE
    
    CALC_CONFIDENCE --> VERIFY_STATUS{Confidence<br/>Score?}
    VERIFY_STATUS -->|≥ 0.85| AUTO_APPROVE[Status: auto_approved]
    VERIFY_STATUS -->|0.60-0.85| NEEDS_REVIEW[Status: needs_review]
    VERIFY_STATUS -->|< 0.60| REJECT_DOC[Status: rejected]
    
    AUTO_APPROVE --> ENCRYPT_STORE[Encrypt Document<br/>AES-256-GCM]
    NEEDS_REVIEW --> ENCRYPT_STORE
    REJECT_DOC --> ENCRYPT_STORE
    
    ENCRYPT_STORE --> SAVE_DOC_DB[Save to Document Table<br/>+ Audit Log]
    SAVE_DOC_DB --> ATTACH_PROFILE{Attach to<br/>Profile?}
    ATTACH_PROFILE -->|Yes| UPDATE_PROFILE[Update StudentProfile<br/>documents JSON]
    ATTACH_PROFILE -->|No| DOC_DONE[Document Processed]
    UPDATE_PROFILE --> DOC_DONE
    
    DOC_DONE --> NOTIFY_USER1[Send Notification<br/>'Document Verified']

    %% FEATURE 4: Semantic Search (Hybrid RAG)
    F4 --> SEARCH_INTERFACE[Search Interface]
    SEARCH_INTERFACE --> SEARCH_QUERY[POST /api/v1/search/semantic]
    SEARCH_QUERY --> HYBRID_RAG3[Hybrid RAG Engine]
    HYBRID_RAG3 --> VECTOR_SEARCH3[ChromaDB Query<br/>Top 25 by Relevance]
    VECTOR_SEARCH3 --> LOAD_OPPS2[Load from PostgreSQL]
    LOAD_OPPS2 --> ELIGIBILITY_CHECK3[Filter Eligible Only]
    ELIGIBILITY_CHECK3 --> RANK2[Rank by Combined Score]
    RANK2 --> SEARCH_RESULTS[Display Results]
    SEARCH_RESULTS --> USER_ACTION1

    %% FEATURE 5: Application Workflow (State Machine)
    START_WORKFLOW --> WORKFLOW_ENGINE[Workflow Engine]
    SAVE_APP --> WORKFLOW_ENGINE
    
    WORKFLOW_ENGINE --> STATE_DISCOVERED[State: discovered]
    STATE_DISCOVERED --> AUTO_TRANSITION1[Auto-check Eligibility]
    AUTO_TRANSITION1 --> STATE_ELIGIBLE[State: eligibility_check]
    STATE_ELIGIBLE --> CHECK_DOCS{Documents<br/>Uploaded?}
    
    CHECK_DOCS -->|No| PROMPT_UPLOAD[Notify: Upload Docs]
    CHECK_DOCS -->|Yes| STATE_DOC_VAL[State: document_validation]
    PROMPT_UPLOAD --> NOTIFY_USER2[Email/SMS/Push<br/>Notification]
    
    STATE_DOC_VAL --> CHECK_VERIFY{All Docs<br/>auto_approved?}
    CHECK_VERIFY -->|Yes| STATE_SUBMIT[State: submitted]
    CHECK_VERIFY -->|No| STATE_REVIEW[State: human_review]
    
    STATE_REVIEW --> REVIEWER_QUEUE[Add to Reviewer Queue]
    REVIEWER_QUEUE --> REVIEWER_ACTION{Reviewer<br/>Decision}
    REVIEWER_ACTION -->|Approve| STATE_SUBMIT
    REVIEWER_ACTION -->|Reject| STATE_REJECT[State: rejected]
    
    STATE_SUBMIT --> NOTIFY_USER3[Notify: Ready to Submit]
    STATE_REJECT --> NOTIFY_USER4[Notify: Rejected + Reason]
    
    STATE_SUBMIT --> TRACK_DEADLINE[Deadline Monitor<br/>Celery Task]

    %% FEATURE 6: Multi-Channel Notifications (Orchestrator)
    NOTIFY_USER1 --> NOTIF_ORCHESTRATOR[Notification Orchestrator]
    NOTIFY_USER2 --> NOTIF_ORCHESTRATOR
    NOTIFY_USER3 --> NOTIF_ORCHESTRATOR
    NOTIFY_USER4 --> NOTIF_ORCHESTRATOR
    TRACK_DEADLINE --> DEADLINE_CHECK{Days Until<br/>Deadline?}
    
    DEADLINE_CHECK -->|7 days| NOTIF_7DAY[Send 7-Day Reminder]
    DEADLINE_CHECK -->|2 days| NOTIF_2DAY[Send 2-Day Reminder<br/>+ Voice Call]
    NOTIF_7DAY --> NOTIF_ORCHESTRATOR
    NOTIF_2DAY --> NOTIF_ORCHESTRATOR
    
    NOTIF_ORCHESTRATOR --> GET_PREFS[Get NotificationPreference]
    GET_PREFS --> SELECT_CHANNELS{Select<br/>Channels}
    
    SELECT_CHANNELS -->|Email Enabled| SEND_EMAIL[SendGrid API]
    SELECT_CHANNELS -->|SMS Enabled| SEND_SMS[Twilio SMS]
    SELECT_CHANNELS -->|Push Enabled| SEND_PUSH[Firebase FCM]
    SELECT_CHANNELS -->|Urgent| SEND_VOICE[Twilio Voice Call]
    
    SEND_EMAIL --> LOG_HISTORY[Log to NotificationHistory]
    SEND_SMS --> LOG_HISTORY
    SEND_PUSH --> LOG_HISTORY
    SEND_VOICE --> LOG_HISTORY
    
    LOG_HISTORY --> NOTIF_DONE[Notification Sent]

    %% FEATURE 7: Data Ingestion (Background Celery Task)
    CELERY_BEAT[Celery Beat<br/>Daily Schedule] --> TRIGGER_INGESTION[Run Ingestion Pipeline]
    TRIGGER_INGESTION --> CONNECTOR_LOOP[For Each Connector]
    
    CONNECTOR_LOOP --> NSP_CONN[NSP Connector<br/>Fetch Scholarships]
    CONNECTOR_LOOP --> MAHADBT_CONN[MahaDBT Connector]
    CONNECTOR_LOOP --> INTERNSHALA_CONN[Internshala Scraper<br/>Playwright]
    CONNECTOR_LOOP --> UNSTOP_CONN[Unstop Hackathons]
    
    NSP_CONN --> NORMALIZE[Normalizer<br/>Unified Schema]
    MAHADBT_CONN --> NORMALIZE
    INTERNSHALA_CONN --> NORMALIZE
    UNSTOP_CONN --> NORMALIZE
    
    NORMALIZE --> DEDUP[Deduplication<br/>by source + external_id]
    DEDUP --> UPSERT[Upsert to Opportunity]
    UPSERT --> INDEX_VECTOR[Index in ChromaDB<br/>Generate Embedding]
    INDEX_VECTOR --> UPDATE_STATUS[Update ConnectorStatus]
    UPDATE_STATUS --> INGESTION_DONE[Ingestion Complete]
    
    INGESTION_DONE -.New Data.-> VECTOR_SEARCH1
    INGESTION_DONE -.New Data.-> VECTOR_SEARCH2
    INGESTION_DONE -.New Data.-> VECTOR_SEARCH3

    %% FEATURE 8: A/B Testing (Experiment Framework)
    LOG_EVENT1 --> EXPERIMENT_MIDDLEWARE[Experiment Middleware]
    EXPERIMENT_MIDDLEWARE --> CHECK_ASSIGNMENT{User Assigned<br/>to Experiment?}
    
    CHECK_ASSIGNMENT -->|No| HASH_ASSIGN[Hash user_id<br/>Consistent Assignment]
    CHECK_ASSIGNMENT -->|Yes| GET_VARIANT[Get Assigned Variant]
    HASH_ASSIGN --> SAVE_ASSIGNMENT[Save to UserExperiment]
    SAVE_ASSIGNMENT --> GET_VARIANT
    
    GET_VARIANT --> INJECT_CONFIG[Inject Variant Config<br/>into Request State]
    INJECT_CONFIG --> USE_VARIANT[Use Variant Logic<br/>in Recommendation]
    USE_VARIANT --> LOG_EVENT2[Log UserEvent<br/>with variant info]
    LOG_EVENT2 --> METRICS_CALC
    
    METRICS_CALC --> AGGREGATE[Aggregate Metrics<br/>by Variant]
    AGGREGATE --> COMPARE{Control vs<br/>Treatment<br/>Winner?}
    COMPARE -->|Yes| PROMOTE[Promote to Default]
    COMPARE -->|No| CONTINUE_EXP[Continue Experiment]

    %% Cross-Feature Integrations
    DISPLAY_SCHOLARSHIPS -.Click Details.-> CHAT_INTERFACE
    CHAT_DONE -.Mentioned Doc.-> DOC_UPLOAD
    SEARCH_RESULTS -.Save.-> SAVE_APP
    DOC_DONE -.Auto-link.-> STATE_DOC_VAL
    
    %% Analytics & Feedback Loop
    METRICS_CALC --> IMPROVE_ALGO[Improve Eligibility<br/>& Ranking Algorithms]
    IMPROVE_ALGO -.Deploy.-> ELIGIBILITY_CHECK1
    IMPROVE_ALGO -.Deploy.-> ELIGIBILITY_CHECK2
    IMPROVE_ALGO -.Deploy.-> ELIGIBILITY_CHECK3

    style START fill:#4CAF50,stroke:#2E7D32,color:#fff
    style DASHBOARD fill:#2196F3,stroke:#1565C0,color:#fff
    style HYBRID_RAG1 fill:#FF9800,stroke:#E65100,color:#fff
    style HYBRID_RAG2 fill:#FF9800,stroke:#E65100,color:#fff
    style HYBRID_RAG3 fill:#FF9800,stroke:#E65100,color:#fff
    style CHATBOT_AGENT fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style TEE_PROCESS fill:#F44336,stroke:#C62828,color:#fff
    style NOTIF_ORCHESTRATOR fill:#00BCD4,stroke:#00838F,color:#fff
    style WORKFLOW_ENGINE fill:#795548,stroke:#4E342E,color:#fff
    style EXPERIMENT_MIDDLEWARE fill:#607D8B,stroke:#37474F,color:#fff
```

### Key Integration Points Shown in Diagram:

1. **Profile → All Features**: Student profile drives eligibility checks across scholarships, chat RAG, and search
2. **RAG → Multiple Entry Points**: Hybrid RAG powers scholarship browse, AI chat, and semantic search
3. **Document Verification → Workflow**: Auto-verified docs automatically progress application states
4. **Workflow → Notifications**: State transitions trigger multi-channel notifications
5. **Chat → Other Features**: Chat can redirect to document upload or save scholarships
6. **Ingestion → Search**: Background data pipeline continuously updates vector search
7. **A/B Testing → Recommendations**: Experiments inject variant logic into eligibility/ranking
8. **Feedback Loop**: User feedback → metrics → algorithm improvements → better recommendations

---

## Feature-by-Feature Documentation

### Feature 1: AI Chatbot (Conversational Assistant)

#### What It Does
A conversational AI assistant powered by local Ollama LLMs that helps students discover scholarships, answer eligibility questions, and provide guidance through natural language chat.

#### How It Works Internally
1. **User sends message** via `/api/v1/chat` endpoint
2. **Thread Management**: Get or create conversation thread (persistent history)
3. **Context Retrieval** (RAG):
   - Check if message needs opportunity retrieval (keyword detection)
   - If yes: semantic search in ChromaDB (8 results)
   - Filter by eligibility rules for student profile
   - Format context with amounts, deadlines, descriptions
4. **LLM Generation**:
   - Build system prompt with profile + context + long-term memory
   - Load last 12 messages from thread
   - Call Ollama (llama3.2:3b) via LangChain
   - Stream tokens back to client
5. **Persistence**:
   - Save user message + assistant response to ChatMessageRecord
   - Extract explicit preferences ("remember that...") → UserMemory
   - Update thread timestamp
6. **Response**: Return full response + retrieved docs + thread_id

#### Key Files
- `services/app/agents/chatbot.py` - ChatbotAgent (LangGraph state machine)
- `services/app/api/routes/chat.py` - FastAPI endpoints (POST /chat, POST /stream, GET /history)
- `services/app/knowledge/hybrid_rag.py` - HybridRAG (semantic + structured search)
- `services/app/db/models.py` - ChatThread, ChatMessageRecord, UserMemory

#### Inputs & Outputs
**Input**:
```json
{
  "message": "Show me engineering scholarships",
  "thread_id": "optional-uuid",
  "user_profile": {"stream": "Engineering", "cgpa": 8.5}
}
```

**Output**:
```json
{
  "response": "Here are 3 scholarships for engineering students...",
  "thread_id": "uuid",
  "retrieved_docs": [{"title": "AICTE Pragati", "amount": 50000, ...}],
  "message_count": 8
}
```

#### Dependencies
- Ollama server running on port 11434
- ChromaDB vector store indexed with opportunities
- PostgreSQL (chat threads, messages, memories)


---

### Feature 2: Hybrid RAG (Retrieval-Augmented Generation)

#### What It Does
Combines semantic vector search (ChromaDB) with structured SQL queries to find relevant scholarships/internships/hackathons based on natural language queries AND student eligibility rules.

#### How It Works Internally
1. **Indexing Phase** (during data ingestion):
   - Build rich text representation: title + description + amount + eligibility rules + tags
   - Generate embedding using ChromaDB's default model
   - Store in `opportunities` collection with metadata
   - Update Opportunity.embedding_id in PostgreSQL

2. **Retrieval Phase** (during search/chat):
   - **Semantic Search**: Query ChromaDB with user message → get 25 candidates
   - **Structured Filtering**: Load full Opportunity objects from PostgreSQL
   - **Eligibility Check**: For each candidate, run rule engine (category, gender, income, CGPA, etc.)
   - **Scoring & Ranking**: Combine relevance_score + eligibility_score
   - **Return Top N**: Default 8 results, sorted by (eligibility, relevance)

3. **Eligibility Rules Engine**:
   ```python
   # Example rule check
   if rules.get("max_income") and profile.income_annual > rules["max_income"]:
       return {"eligible": False, "reason": "Income exceeds limit"}
   ```

#### Key Files
- `services/app/knowledge/hybrid_rag.py` - HybridRAG class (index_opportunity, semantic_search, retrieve_for_profile)
- `services/app/intelligence/eligibility.py` - evaluate_eligibility() function
- `services/app/intelligence/vector_search.py` - Vector search utilities
- `services/app/intelligence/embeddings.py` - Embedding generation

#### Inputs & Outputs
**Input**:
```python
rag.retrieve_for_profile(
    db, 
    query="engineering scholarship for girls", 
    profile=student_profile,  # StudentProfile object
    limit=8
)
```

**Output**:
```python
[
    {
        "opportunity_id": "uuid",
        "title": "AICTE Pragati Scholarship for Girls",
        "relevance_score": 0.89,
        "eligibility_score": 0.95,
        "eligible": True,
        "amount": 50000,
        "deadline": "2024-12-31"
    },
    ...
]
```

#### Dependencies
- ChromaDB (persistent vector store)
- PostgreSQL (Opportunity table with eligibility_rules JSON)
- sentence-transformers (for embedding generation)


---

### Feature 3: Document Verification (OCR + Auto-Verification)

#### What It Does
Automatically extracts text from uploaded documents (Aadhaar, marksheets, income certificates) using OCR, verifies fields against government APIs, calculates confidence scores, and assigns verification status (auto_approved / needs_review / rejected).

#### How It Works Internally
1. **Upload**: User uploads image via `/api/v1/documents/upload`
2. **TEE Processing**: Image bytes encrypted and processed in Trusted Execution Environment
3. **OCR Extraction**: Tesseract extracts raw text + confidence scores
4. **Field Parsing**: Document-specific parser extracts structured fields:
   - **Aadhaar**: Number, name, DOB, gender, address
   - **Income Certificate**: Income amount, issuing authority, validity
   - **Marksheet**: Marks, CGPA, percentage, institution
5. **Gov API Verification** (if applicable):
   - Aadhaar: UIDAI API verification
   - Income: State portal API (mock in dev)
6. **Confidence Scoring**:
   - `overall_confidence = avg(field_confidences)`
   - Boost if gov_verified = True
7. **Status Assignment**:
   - `≥ 0.85` → `auto_approved`
   - `0.60-0.85` → `needs_review`
   - `< 0.60` → `rejected`
8. **Encryption at Rest**: Document stored encrypted (AES-256-GCM)
9. **Audit Log**: All decryption events logged with user_id, timestamp

#### Key Files
- `services/app/verification/engine.py` - AutoVerificationEngine (orchestrates pipeline)
- `services/app/verification/ocr_service.py` - OCRService (Tesseract wrapper)
- `services/app/verification/parsers.py` - parse_document() for each doc type
- `services/app/verification/gov_api.py` - GovAPIService (Aadhaar, Income verification)
- `services/app/security/document_store.py` - DocumentStore (encryption/decryption)
- `services/app/security/tee.py` - TEE service (mock/AWS/Azure)
- `services/app/api/routes/documents_api.py` - Upload/verify endpoints

#### Inputs & Outputs
**Input**:
```python
await engine.verify_document(
    user_id="uuid",
    document_type="aadhaar",
    image_bytes=b"...image data...",
    application_id="optional-uuid"
)
```

**Output**:
```json
{
  "document_type": "aadhaar",
  "verification_status": "auto_approved",
  "confidence_score": 0.92,
  "extracted_fields": {
    "aadhaar_number": "XXXX-XXXX-1234",
    "name": "John Doe",
    "dob": "1995-05-15"
  },
  "gov_api_verified": true,
  "tee_processed": true
}
```

#### Dependencies
- Tesseract OCR engine installed
- UIDAI API credentials (production) or mock mode
- PostgreSQL (Document, AuditLog tables)
- Cryptography library (Fernet for AES-256)


---

### Feature 4: Multi-Channel Notifications (Email, SMS, Push, Voice)

#### What It Does
Sends deadline reminders, new match alerts, and status updates to students via their preferred channels: Email (SendGrid), SMS (Twilio), Push (Firebase), and Voice calls (Twilio).

#### How It Works Internally
1. **Trigger**: Deadline monitor (Celery beat task) or API call
2. **User Preferences**: Query NotificationPreference table
   - Defaults: Email + In-App enabled
   - User can enable SMS, Push, Voice
3. **Channel Selection**:
   ```python
   channels = []
   if pref.email_enabled: channels.append(EMAIL)
   if pref.sms_enabled: channels.append(SMS)
   if pref.push_enabled: channels.append(PUSH)
   if urgent and notification_type == DEADLINE_REMINDER:
       channels.append(VOICE)  # Auto-enable for 2-day deadlines
   ```
4. **Send via Services**:
   - **Email**: SendGrid API (subject + HTML body)
   - **SMS**: Twilio SMS API (body text)
   - **Voice**: Twilio Voice API (TTS: "Hello! This is EduPilot calling...")
   - **Push**: Firebase FCM (title + body + data payload)
5. **History Logging**: Record each attempt in NotificationHistory table
6. **Failure Handling**: Log error messages for debugging

#### Key Files
- `services/app/notifications/orchestrator.py` - NotificationOrchestrator (multi-channel coordinator)
- `services/app/notifications/email.py` - EmailNotificationService
- `services/app/notifications/sms.py` - SMSNotificationService
- `services/app/notifications/voice.py` - VoiceNotificationService
- `services/app/notifications/push.py` - PushNotificationService
- `services/app/notifications/deadline_monitor.py` - Celery task (7-day, 2-day reminders)
- `services/app/api/routes/notifications.py` - Preference management endpoints

#### Inputs & Outputs
**Input**:
```python
await orchestrator.send_notification(
    user_id="uuid",
    notification_type=NotificationType.DEADLINE_REMINDER,
    title="Scholarship Deadline Approaching",
    body="AICTE Pragati deadline is in 2 days!",
    metadata={"opportunity_id": "uuid"}
)
```

**Output**:
```json
{
  "user_id": "uuid",
  "notification_type": "deadline_reminder",
  "channels_attempted": ["email", "sms", "voice"],
  "channel_results": {
    "email": {"success": true, "message_id": "abc123"},
    "sms": {"success": true, "sid": "SM123"},
    "voice": {"success": true, "call_sid": "CA123"}
  },
  "timestamp": "2024-12-20T10:30:00Z"
}
```

#### Dependencies
- SendGrid API key (SENDGRID_API_KEY)
- Twilio credentials (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_PHONE)
- Firebase Admin SDK credentials (FIREBASE_CREDENTIALS_PATH)
- Celery + Redis (for scheduled deadline monitoring)


---

### Feature 5: Data Ingestion Pipeline (Scholarship/Internship/Hackathon Connectors)

#### What It Does
Automatically fetches opportunity data from 847+ sources (NSP, MahaDBT, MyScheme, AICTE, Internshala, Unstop, etc.), normalizes to unified schema, deduplicates, and syncs to database + vector store.

#### How It Works Internally
1. **Scheduled Execution**: Celery beat runs daily/weekly
2. **Connector Registry**: Load enabled connectors from config
3. **For Each Connector**:
   - **Fetch**: Call connector.fetch() → returns raw JSON list
   - **Normalize**: Convert to standard schema (title, amount, deadline, eligibility_rules, etc.)
   - **Deduplication**: Check existing by (source, external_id) or source_url
   - **Upsert**: Insert new or update existing Opportunity
   - **Vector Indexing**: Call rag.index_opportunity() → ChromaDB embedding
   - **Stats Tracking**: Count inserted/updated/errors per source
4. **Connector Types**:
   - **API-based**: NSP, AICTE (HTTP JSON APIs)
   - **Web Scraping**: Internshala (Playwright live scraper), MahaDBT (BeautifulSoup)
   - **Static/Dummy**: Unstop, Indeed, Naukri (pre-seeded data for demo)
5. **Error Handling**: Rollback on failure, log error to ConnectorStatus table

#### Key Files
- `services/app/ingestion/pipeline.py` - run_ingestion() orchestrator
- `services/app/ingestion/connectors.py` - Scholarship connectors (NSP, MahaDBT, MyScheme, AICTE)
- `services/app/ingestion/connectors/internshala_sync.py` - Playwright scraper
- `services/app/ingestion/hackathon_pipeline.py` - Hackathon ingestion (Unstop)
- `services/app/ingestion/normalizer.py` - normalize(), normalize_internship(), upsert_opportunity()
- `services/app/ingestion/base.py` - BaseConnector abstract class
- `services/app/ingestion/connector_registry.py` - Dynamic connector loading
- `services/app/tasks.py` - Celery task definitions

#### Inputs & Outputs
**Input**: Celery task trigger or manual API call
```bash
# Trigger via Celery
celery -A app.tasks beat -l info

# Or API endpoint
POST /api/v1/admin/run-ingestion
```

**Output**:
```json
{
  "inserted": 245,
  "updated": 102,
  "errors": 3,
  "sources": {
    "nsp": {"fetched": 120, "synced": 118},
    "mahadbt": {"fetched": 85, "synced": 82},
    "internshala": {"fetched": 150, "synced": 147},
    "unstop_hackathons": {"error": "timeout"}
  },
  "completed_at": "2024-12-20T15:30:00Z"
}
```

#### Dependencies
- Playwright (for web scraping)
- BeautifulSoup4 + lxml (HTML parsing)
- httpx (async HTTP requests)
- Celery + Redis (task scheduling)
- PostgreSQL (Opportunity, ConnectorStatus tables)
- ChromaDB (vector indexing)


---

### Feature 6: A/B Testing Framework (Experiments)

#### What It Does
Enables data-driven optimization by running A/B experiments on recommendation algorithms, UI variations, and notification strategies. Automatically assigns users to variants using consistent hashing and tracks metrics.

#### How It Works Internally
1. **Experiment Setup** (via admin API):
   ```python
   experiment_service.create_experiment(
       "recommendation_algo_v2",
       variants=[
           {"name": "control", "config": {"algo": "baseline"}},
           {"name": "treatment_a", "config": {"algo": "ml_enhanced"}}
       ]
   )
   ```

2. **User Assignment** (automatic via middleware):
   - Hash user_id + experiment_name using SHA-256
   - Modulo hash by variant count → deterministic variant selection
   - Store in UserExperiment table (user always gets same variant)

3. **Variant Injection** (middleware):
   - ExperimentContextMiddleware runs on every request
   - Checks if active experiments exist
   - Assigns user if not already assigned
   - Injects variant config into request.state

4. **Metric Tracking**:
   - UserEvents table records: recommendation_viewed, saved, applied, dismissed
   - Feedback table records: relevant, not_relevant, ineligible
   - AccuracyMetric table tracks false positives/negatives
   - MetricsCalculator computes precision, recall, CTR per variant

5. **Analysis & Graduation**:
   - Compare metrics across variants (control vs treatment_a)
   - Promote winning variant to default using `promote_variant_to_default()`

#### Key Files
- `services/app/analytics/experiment_service.py` - ExperimentService (create, assign, track)
- `services/app/analytics/metrics_calculator.py` - MetricsCalculator (precision, recall, CTR)
- `services/app/analytics/event_service.py` - Event logging utilities
- `services/app/api/middleware/experiment_context.py` - ExperimentContextMiddleware
- `services/app/api/routes/experiments.py` - Admin API for experiment management
- `services/app/db/models.py` - ExperimentVariant, UserExperiment, UserEvent, Feedback

#### Inputs & Outputs
**Create Experiment**:
```python
POST /api/v1/experiments
{
  "name": "recommendation_algo_v2",
  "variants": [
    {"name": "control", "config": {"algo": "baseline"}},
    {"name": "treatment_a", "config": {"algo": "ml_enhanced"}}
  ]
}
```

**User Assignment** (automatic):
```python
# Middleware injects into request.state
request.state.experiments = {
    "recommendation_algo_v2": {
        "variant": "treatment_a",
        "config": {"algo": "ml_enhanced"}
    }
}
```

**Metrics Query**:
```python
GET /api/v1/experiments/recommendation_algo_v2/metrics
# Returns precision, recall, CTR by variant
```

#### Dependencies
- PostgreSQL (experiment tables)
- Middleware (FastAPI dependency injection)
- hashlib (SHA-256 for consistent hashing)


---

### Feature 7: Application Workflow State Machine

#### What It Does
Tracks the lifecycle of scholarship/internship applications through a finite state machine with states: discovered → eligibility_check → document_validation → human_review → submitted → tracking → completed/rejected.

#### How It Works Internally
1. **State Definition** (enum):
   ```python
   class ApplicationState(str, enum.Enum):
       DISCOVERED = "discovered"
       ELIGIBILITY_CHECK = "eligibility_check"
       DOCUMENT_VALIDATION = "document_validation"
       HUMAN_REVIEW = "human_review"
       SUBMITTED = "submitted"
       TRACKING = "tracking"
       COMPLETED = "completed"
       REJECTED = "rejected"
   ```

2. **Transition Rules**:
   - `discovered → eligibility_check` (automatic after eligibility scoring)
   - `eligibility_check → document_validation` (if eligible)
   - `document_validation → human_review` (if confidence < 0.85)
   - `document_validation → submitted` (if auto_approved)
   - `human_review → submitted` (after reviewer approval)
   - `submitted → tracking` (confirmation received)
   - `tracking → completed` (result announced)

3. **Event Logging**: WorkflowEvent records each transition
   ```python
   WorkflowEvent(
       application_id="uuid",
       from_state="eligibility_check",
       to_state="document_validation",
       actor_id="system",
       notes="Auto-transitioned after eligibility pass"
   )
   ```

4. **API Operations**:
   - `POST /api/v1/workflow/transition` - Manually trigger transition
   - `GET /api/v1/workflow/application/{id}` - Get current state + history
   - `POST /api/v1/workflow/auto-progress` - Batch auto-progress eligible apps

#### Key Files
- `services/app/workflow/engine.py` - WorkflowEngine (transition logic)
- `services/app/api/routes/workflow.py` - Workflow API endpoints
- `services/app/db/models.py` - Application, ApplicationState enum, WorkflowEvent

#### Inputs & Outputs
**Transition Request**:
```json
POST /api/v1/workflow/transition
{
  "application_id": "uuid",
  "to_state": "submitted",
  "notes": "Documents verified, submitting to portal"
}
```

**Application State Response**:
```json
{
  "application_id": "uuid",
  "current_state": "document_validation",
  "progress_pct": 60,
  "history": [
    {"from": "discovered", "to": "eligibility_check", "timestamp": "2024-12-15T10:00:00Z"},
    {"from": "eligibility_check", "to": "document_validation", "timestamp": "2024-12-16T14:30:00Z"}
  ]
}
```

#### Dependencies
- PostgreSQL (Application, WorkflowEvent tables)
- Enum validation (Pydantic)


---

### Feature 8: Security & Encryption (TEE + Document Store)

#### What It Does
Protects sensitive student documents (Aadhaar, income certificates, marksheets) using AES-256-GCM encryption at rest, Trusted Execution Environment processing, and consent-based decryption with audit logging.

#### How It Works Internally
1. **Encryption at Rest**:
   - **Key Derivation**: PBKDF2-HMAC-SHA256 with 100,000 iterations
   - **Per-Document Keys**: `master_key + salt + document_id` → unique AES key
   - **Cipher**: Fernet (AES-128-CBC + HMAC-SHA256)
   - **Storage**: Encrypted bytes saved to `secure_documents/{document_id}.enc`

2. **TEE Processing**:
   - **Mock Mode** (dev): Simulates enclave processing
   - **AWS Nitro** (prod): Runs in AWS Nitro Enclave
   - **Azure Confidential** (prod): Runs in Azure Confidential VM
   - Operations: `encrypt_sensitive`, `decrypt_sensitive`, `validate_hash`

3. **Consent-Based Decryption**:
   ```python
   def decrypt_document(user_id, document_id, encrypted_data):
       # 1. Check consent
       consent = db.query(ConsentRecord).filter_by(
           user_id=user_id, revoked_at=None
       ).first()
       if not consent:
           raise PermissionError("Consent required")
       
       # 2. Decrypt
       decrypted = fernet.decrypt(encrypted_data)
       
       # 3. Audit log
       db.add(AuditLog(action="document_decryption_access", ...))
       
       return decrypted
   ```

4. **Audit Trail**:
   - Write-only logs (no deletion)
   - Fields: user_id, action, resource_type, resource_id, timestamp, ip_address
   - Retention: 3 years (DPDP Act compliance)

#### Key Files
- `services/app/security/document_store.py` - DocumentStore (encryption/decryption)
- `services/app/security/tee.py` - TEE service (mock/AWS/Azure implementations)
- `services/app/security/consent.py` - Consent management
- `services/app/security/rbac.py` - Role-based access control
- `services/app/db/models.py` - Document, ConsentRecord, AuditLog

#### Inputs & Outputs
**Encrypt & Store**:
```python
store.store_encrypted_document(
    document_id="doc-abc123",
    raw_data=b"...PDF bytes..."
)
# Returns: "secure_documents/doc-abc123.enc"
```

**Decrypt with Consent**:
```python
decrypted = store.decrypt_document(
    user_id="user-uuid",
    document_id="doc-abc123",
    encrypted_data=encrypted_bytes
)
# Audit log created automatically
```

#### Dependencies
- cryptography library (Fernet, PBKDF2)
- PostgreSQL (Document, ConsentRecord, AuditLog tables)
- TEE environment (AWS Nitro / Azure Confidential in production)


---

## Installation & Setup

### Prerequisites
- **Node.js 20+** (for Next.js frontend)
- **Python 3.11+** (for FastAPI backend)
- **PostgreSQL 16+** with pgvector extension
- **Redis 7+** (for Celery task queue)
- **Ollama** (for local LLM inference)
- **Tesseract OCR** (for document processing)

### Backend Setup (Python FastAPI)

1. **Clone Repository**:
   ```bash
   git clone <repo-url>
   cd student-ai-copilot/services
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment** (`.env` file):
   ```env
   # Database
   DATABASE_URL=sqlite:///./edupilot.db  # Or PostgreSQL URL
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=edupilot
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=yourpassword

   # Redis
   REDIS_URL=redis://localhost:6379/0

   # Ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2:3b

   # Notification Services
   SENDGRID_API_KEY=your_sendgrid_key
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_FROM_PHONE=+1234567890

   # Security
   ENCRYPTION_KEY_MASTER=base64_encoded_32byte_key
   TEE_MODE=mock  # mock | aws_nitro | azure_confidential
   ```

5. **Install Ollama**:
   ```bash
   # Download from https://ollama.ai
   ollama pull llama3.2:3b
   ollama serve  # Run in separate terminal
   ```

6. **Install Tesseract OCR**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr

   # macOS
   brew install tesseract

   # Windows: Download installer from GitHub
   ```

7. **Initialize Database**:
   ```bash
   python -c "from app.db.session import init_db; init_db()"
   ```

8. **Index Sample Data** (optional):
   ```bash
   python index_scholarships_now.py
   ```

9. **Start Backend Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

10. **Start Celery Worker** (separate terminal):
    ```bash
    celery -A app.tasks worker -B -l info
    ```


### Frontend Setup (Next.js 15)

1. **Navigate to Frontend**:
   ```bash
   cd ../app
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Configure Environment** (`.env` file):
   ```env
   # Supabase (for authentication)
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

   # Backend API
   NEXT_API_URL=http://localhost:8000
   ```

4. **Start Development Server**:
   ```bash
   npm run dev
   ```

5. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Docker Setup (All Services)

1. **Start All Services**:
   ```bash
   docker-compose up -d
   ```

   This starts:
   - PostgreSQL (port 5433)
   - Redis (port 6379)
   - FastAPI Backend (port 8000)
   - Celery Worker

2. **Access Logs**:
   ```bash
   docker-compose logs -f api
   ```

3. **Stop Services**:
   ```bash
   docker-compose down
   ```

---

## Testing

### Backend Tests (Pytest)

**Run All Tests**:
```bash
cd services
pytest
```

**Run Specific Test Module**:
```bash
pytest tests/test_notification_service.py -v
```

**Run with Coverage**:
```bash
pytest --cov=app --cov-report=html
```

### Pre-Hackathon Test Suite

**Comprehensive System Check**:
```bash
cd services
python test_everything.py
```

This tests:
- ✅ Ollama LLM connectivity
- ✅ Database connection + data
- ✅ RAG index functionality
- ✅ Chatbot end-to-end
- ✅ Notification configuration (Email, SMS, Voice)

**Expected Output**:
```
🚀 EDUPILOT PRE-HACKATHON TEST SUITE
✅ Ollama
✅ Database
✅ RAG Index
✅ Chatbot
⚠️  Notifications (SMS not configured)

TOTAL: 4/5 systems ready (80%)
```

### Notification Feature Tests

**Test Email/SMS/Voice**:
```bash
python test_notifications.py
```

**Test Chatbot RAG**:
```bash
python test_all_chatbot_features.py
```


---

## AI Quality Metrics & Evaluation

EduPilot uses **Ragas** (RAG Assessment) to continuously evaluate and improve the AI chatbot's performance. We track 4 critical metrics that measure how well our RAG system retrieves relevant information and generates accurate, helpful responses.

### Overview

Our evaluation pipeline:
1. **Golden Dataset**: 76 real student questions with expected answers
2. **Automated Testing**: Run `python eval/ragas_eval.py` to evaluate
3. **Continuous Monitoring**: Track metrics over time to measure improvements
4. **Iterative Refinement**: Use results to optimize retrieval and generation

### The 4 Core Metrics

---

#### 1. **Faithfulness** 📊
**What it measures**: How factually accurate the AI's answer is based on the retrieved context (no hallucination).

**Scale**: 0.0 (complete hallucination) to 1.0 (perfectly faithful)

**Why it matters**: 
- Prevents the AI from making up scholarship amounts, deadlines, or eligibility criteria
- Ensures students get reliable information they can trust
- Critical for decision-making (applying to wrong scholarships wastes time)

**Example**:

❌ **Low Faithfulness (0.2)**:
```
Context: "AICTE Pragati offers ₹50,000 per year for girl students"
AI Response: "AICTE Pragati provides ₹1,00,000 per year"
❌ Hallucinated the amount (₹1L vs ₹50K)
```

✅ **High Faithfulness (0.9)**:
```
Context: "AICTE Pragati offers ₹50,000 per year for girl students"
AI Response: "According to the data, AICTE Pragati provides ₹50,000 annually"
✅ Accurately reflects the context
```

**How we calculate it**:
- AI judges compare each statement in the answer against the retrieved context
- Count how many statements are supported by evidence
- Formula: `faithful_statements / total_statements`

**Current Performance**: 
- **Overall Quality**: 67.65% (up from 59.35%)
- **Target**: ≥70% (good) | ≥85% (excellent)

**Improvement Status**:
- ✅ **Context Recall**: 58% → 76% (+18%) - Major improvement in retrieval completeness
- ✅ **Answer Relevancy**: 69% → 76% (+7%) - Better on-topic responses
- ✅ **Context Precision**: 55% → 64% (+9%) - Improved retrieval accuracy
- ⚠️ **Faithfulness**: 45% → 55% (+10%) - Still needs work to reduce hallucinations

**What we're doing to improve**:
- ✅ Two-stage RAG (brief list first, details on demand)
- ✅ Strict system prompts emphasizing "only use available data"
- ✅ Reduced context size to minimize confusion
- 🔄 Adding citation links to source documents

---

#### 2. **Answer Relevancy** 🎯
**What it measures**: How well the AI's answer actually addresses the user's question (not going off-topic).

**Scale**: 0.0 (completely irrelevant) to 1.0 (perfectly relevant)

**Why it matters**:
- Users ask specific questions and expect focused answers
- Prevents verbose, rambling responses that waste time
- Improves user satisfaction and trust

**Example**:

❌ **Low Relevancy (0.3)**:
```
Question: "What documents do I need for AICTE Pragati?"
AI Response: "AICTE offers many scholarships including Pragati, Saksham, and Swanath. These are great opportunities for students. You should check eligibility carefully..."
❌ Talks about other scholarships instead of answering the question
```

✅ **High Relevancy (0.9)**:
```
Question: "What documents do I need for AICTE Pragati?"
AI Response: "For AICTE Pragati, you need: 1) Income certificate, 2) 10th & 12th marksheets, 3) College admission letter, 4) Aadhaar card"
✅ Directly answers the specific question asked
```

**How we calculate it**:
- AI generates multiple question variations from the answer
- Compares similarity between original question and generated questions
- High similarity = answer stayed on topic

**Current Performance**:
- **Overall**: 76% (excellent - exceeds target)
- **Target**: ≥0.80 (good)

**What we're doing to improve**:
- ✅ Query intent detection (list vs detail vs comparison)
- ✅ Progressive disclosure (show summary first)
- 🔄 Answer formatting guidelines in system prompt

---

#### 3. **Context Precision** 🔍
**What it measures**: How many of the retrieved documents are actually relevant to the question (retrieval quality).

**Scale**: 0.0 (all retrieved docs are irrelevant) to 1.0 (all retrieved docs are relevant)

**Why it matters**:
- Better retrieval = better answers
- Reduces noise in the context given to the LLM
- Prevents the AI from getting confused by irrelevant information

**Example**:

❌ **Low Precision (0.4)**:
```
Question: "Engineering scholarships for girls"
Retrieved: 
  1. ✅ AICTE Pragati (girl students, engineering) - RELEVANT
  2. ❌ Medical fellowship (irrelevant stream)
  3. ❌ Sports scholarship (irrelevant category)
  4. ✅ Tata scholarship (engineering) - RELEVANT
  5. ❌ Post-matric SC scholarship (not specific to engineering)

Only 2/5 docs are relevant → Precision = 0.4
```

✅ **High Precision (0.8)**:
```
Question: "Engineering scholarships for girls"
Retrieved:
  1. ✅ AICTE Pragati (girl students, engineering)
  2. ✅ Reliance Foundation (UG engineering)
  3. ✅ Google WomenTechmakers (tech scholarships)
  4. ✅ ONGC scholarship (engineering students)
  5. ❌ General merit scholarship (not gender-specific)

4/5 docs are relevant → Precision = 0.8
```

**How we calculate it**:
- AI judge evaluates if each retrieved document is relevant to the question
- Counts relevant docs at each position (weighted by rank)
- Formula: `sum(relevance[i] * precision_at_i) / total_relevant`

**Current Performance**:
- **Overall**: 64% (moderate - approaching target)
- **Target**: ≥0.70 (good)

**What we're doing to improve**:
- ✅ Hybrid search (semantic + structured filters)
- ✅ Eligibility pre-filtering before retrieval
- 🔄 Query expansion with synonyms
- 🔄 Re-ranking retrieved results

---

#### 4. **Context Recall** 📚
**What it measures**: How much of the necessary information from the dataset was actually retrieved (coverage).

**Scale**: 0.0 (missed all relevant info) to 1.0 (retrieved all relevant info)

**Why it matters**:
- Ensures we don't miss important scholarships
- Complete answers require complete context
- Prevents "I don't know" when the info exists in our database

**Example**:

❌ **Low Recall (0.4)**:
```
Question: "Scholarships for SC category engineering students"

Ground Truth (what exists in DB):
  - AICTE Pragati ✓
  - Post-Matric SC Scholarship ✓
  - Sitaram Jindal Scholarship ✓
  - INSPIRE Fellowship ✓
  - State Merit Scholarship ✓

Retrieved (what we actually fetched):
  - AICTE Pragati ✓
  - Post-Matric SC Scholarship ✓
  
Only 2/5 relevant scholarships retrieved → Recall = 0.4
```

✅ **High Recall (0.8)**:
```
Question: "Scholarships for SC category engineering students"

Ground Truth: 5 relevant scholarships
Retrieved: 4 out of those 5

4/5 = 0.8 recall (missed only 1)
```

**How we calculate it**:
- AI judge identifies which context chunks are needed to answer
- Compares against what was actually retrieved
- Formula: `retrieved_relevant / total_relevant_available`

**Current Performance**:
- **Before optimization**: 58% (moderate)
- **After optimization**: 76% (excellent - significant improvement)
- **Target**: ≥75% (good)

**What we're doing to improve**:
- ✅ Increased retrieval limit (5 → 8 docs)
- ✅ Multi-query retrieval for complex questions
- 🔄 Diversity-aware re-ranking

---

### Metric Relationships & Trade-offs

```
┌─────────────────────────────────────────────────────────┐
│                   RAG Pipeline Flow                     │
└─────────────────────────────────────────────────────────┘

User Question
     ↓
┌────────────────────────────────────┐
│   Context Precision + Recall       │  ← Retrieval Quality
│   (Are we getting the right docs?) │
└────────────────────────────────────┘
     ↓
Retrieved Documents (Context)
     ↓
┌────────────────────────────────────┐
│   LLM Generation                   │
└────────────────────────────────────┘
     ↓
AI Answer
     ↓
┌────────────────────────────────────┐
│   Faithfulness + Relevancy         │  ← Generation Quality
│   (Is the answer accurate & on-topic?)│
└────────────────────────────────────┘
```

**Key Trade-offs**:

1. **Precision vs Recall**:
   - High precision (fewer docs) → Better faithfulness but lower recall
   - High recall (more docs) → Better coverage but lower precision
   - **Our choice**: Moderate (8 docs) - balance both

2. **Context Size vs Faithfulness**:
   - More context → Higher recall but more confusion (lower faithfulness)
   - Less context → Higher faithfulness but might miss info (lower recall)
   - **Our choice**: Two-stage RAG (brief list first, details on demand)

3. **Strictness vs Helpfulness**:
   - Very strict prompts → High faithfulness but robotic answers
   - Flexible prompts → Natural conversation but more hallucination risk
   - **Our choice**: Balanced prompts with clear guidelines

---

### Current Performance Summary

| Metric | Score | Grade | Status |
|--------|-------|-------|--------|
| **Faithfulness** | 55% | 🟡 C+ | Improving (was 45%) |
| **Answer Relevancy** | 76% | 🟢 B+ | Excellent (exceeds target) |
| **Context Precision** | 64% | 🟡 C+ | Moderate (improving) |
| **Context Recall** | 76% | 🟢 A- | Excellent (exceeds target) |

**Overall RAG Health**: 🟢 **Good** - 67.65% overall (up from 59%)

---

### How to Run Evaluation

#### Step 1: Setup
```bash
cd services
pip install ragas datasets langchain-huggingface
```

#### Step 2: Run Evaluation
```bash
python eval/ragas_eval.py
```

#### Step 3: View Results
Results are saved in `eval/results/ragas_results_TIMESTAMP.csv`:
```csv
question,answer,contexts,ground_truth,faithfulness,answer_relevancy,context_precision,context_recall
"Which scholarships am I eligible for?","Based on your profile...",["AICTE Pragati..."],"You are eligible for...",0.45,0.78,0.62,0.70
```

#### Step 4: Analyze Trends
```bash
# Compare multiple runs
python eval/analyze_trends.py
```

---

### Improvement Roadmap

#### ✅ Completed (v1.0)
- Two-stage RAG system (brief list → full details)
- Strict system prompts for faithfulness
- Hybrid search (semantic + structured)
- Social message detection (avoid retrieval for "hi")
- Query intent classification

#### 🔄 In Progress (v1.1)
- Citation links in responses
- Re-ranking with cross-encoder
- Query expansion for better recall
- Confidence scores displayed to user

#### 📋 Planned (v2.0)
- Multi-query retrieval for complex questions
- Self-reflective RAG (critique & refine answers)
- User feedback loop (upvote/downvote → retrain)
- A/B testing different RAG strategies

---

### Monitoring & Alerts

We track metrics daily and alert if:
- **Faithfulness drops below 0.40** → Critical (too much hallucination)
- **Answer Relevancy drops below 0.70** → Warning (going off-topic)
- **Context Precision drops below 0.50** → Warning (poor retrieval)
- **Context Recall drops below 0.60** → Warning (missing relevant info)

**Dashboard**: `/api/v1/admin/rag-metrics` (admin only)

---

### Best Practices for RAG Quality

1. **Golden Dataset Maintenance**:
   - Add real user questions monthly
   - Include edge cases and tricky queries
   - Validate ground truth answers with domain experts

2. **Iterative Optimization**:
   - Change ONE thing at a time
   - Run evaluation before & after
   - Keep what works, revert what doesn't

3. **Human-in-the-Loop**:
   - Manual review of low-scoring answers
   - Collect user feedback (helpful/not helpful)
   - Use feedback to refine prompts & retrieval

4. **Context Quality over Quantity**:
   - Better to retrieve 3 highly relevant docs than 10 mixed docs
   - Filter by eligibility BEFORE semantic search
   - Use structured data (amounts, deadlines) directly when available

---


## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login with email/password
- `GET /auth/callback` - OAuth callback (Supabase)

### Profile Management
- `GET /api/v1/profile` - Get student profile
- `PUT /api/v1/profile` - Update profile
- `POST /api/v1/profile/calculate-readiness` - Calculate profile completeness score

### Opportunities (Scholarships, Internships, Hackathons)
- `GET /api/v1/scholarships` - List scholarships (filtered by profile)
- `GET /api/v1/scholarships/{id}` - Get scholarship details
- `GET /api/v1/internships` - List internships
- `GET /api/v1/hackathons` - List hackathons
- `GET /api/v1/hackathons/live` - Live hackathons (registration open)

### Search
- `POST /api/v1/search/semantic` - Semantic search (vector + eligibility)
- `GET /api/v1/search/filters` - Available filter options

### Chat (AI Assistant)
- `POST /api/v1/chat` - Send message (blocking response)
- `POST /api/v1/chat/stream` - Send message (streaming response)
- `POST /api/v1/chat/upload` - Upload document in chat
- `GET /api/v1/chat/history/{thread_id}` - Get conversation history
- `DELETE /api/v1/chat/history/{thread_id}` - Clear conversation
- `GET /api/v1/chat/threads` - List user threads
- `GET /api/v1/chat/health` - Chat service health check

### Documents
- `POST /api/v1/documents/upload` - Upload document for verification
- `GET /api/v1/documents` - List user documents
- `GET /api/v1/documents/{id}` - Get document details
- `POST /api/v1/documents/{id}/verify` - Trigger manual verification

### Workflow (Application Tracking)
- `GET /api/v1/workflow/application/{id}` - Get application state
- `POST /api/v1/workflow/transition` - Transition application state
- `GET /api/v1/workflow/applications` - List user applications

### Notifications
- `GET /api/v1/notifications/preferences` - Get notification preferences
- `PUT /api/v1/notifications/preferences` - Update preferences
- `GET /api/v1/notifications/history` - Get notification history

### Consent
- `POST /api/v1/consent/grant` - Grant consent
- `POST /api/v1/consent/revoke` - Revoke consent
- `GET /api/v1/consent/status` - Check consent status

### Experiments (A/B Testing)
- `POST /api/v1/experiments` - Create experiment (admin)
- `GET /api/v1/experiments` - List active experiments
- `GET /api/v1/experiments/{name}/metrics` - Get experiment metrics

### Feedback
- `POST /api/v1/feedback` - Submit feedback on recommendation
- `GET /api/v1/feedback/stats` - Get feedback statistics

### Admin
- `POST /api/v1/admin/run-ingestion` - Trigger data ingestion
- `GET /api/v1/admin/connector-status` - Get connector health
- `GET /api/v1/admin/analytics` - System analytics dashboard

### Health Check
- `GET /health` - API health status


---

## Database Schema

### Core Tables

#### users
```sql
- id: VARCHAR(36) PRIMARY KEY
- email: VARCHAR(255) UNIQUE
- phone_number: VARCHAR(20)
- role: ENUM(student, reviewer, admin)
- created_at: TIMESTAMP
```

#### student_profiles
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- full_name: VARCHAR(255)
- date_of_birth: DATE
- gender: VARCHAR(32)
- state: VARCHAR(64)
- category: VARCHAR(32)  # SC/ST/OBC/General
- income_annual: FLOAT
- college: VARCHAR(255)
- stream: VARCHAR(128)
- cgpa: FLOAT
- percentage_12th: FLOAT
- skills: JSON
- documents: JSON
- readiness_score: FLOAT
```

#### opportunities
```sql
- id: VARCHAR(36) PRIMARY KEY
- external_id: VARCHAR(128)
- source: VARCHAR(64)
- source_url: VARCHAR(1024) UNIQUE
- category: ENUM(scholarship, internship, placement, hackathon)
- title: VARCHAR(512)
- description: TEXT
- amount_min: FLOAT
- amount_max: FLOAT
- deadline: DATE
- eligibility_rules: JSON
- documents_required: JSON
- tags: JSON
- embedding_id: VARCHAR(128)
- is_active: BOOLEAN
- UNIQUE(source, external_id)
```

#### applications
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- opportunity_id: VARCHAR(36) FK → opportunities.id
- state: ENUM(discovered, eligibility_check, document_validation, ...)
- match_score: FLOAT
- eligibility_result: JSON
- checklist: JSON
- progress_pct: INTEGER
- saved: BOOLEAN
```

#### documents
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- document_type: VARCHAR(64)  # aadhaar, income_certificate, marksheet
- file_path: VARCHAR(512)  # Encrypted file location
- encryption_key_id: VARCHAR(128)
- verification_status: VARCHAR(32)
- extracted_fields: JSON
- overall_confidence: FLOAT
- gov_verification_status: VARCHAR(32)
```


### Notification Tables

#### notification_preferences
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id UNIQUE
- email_enabled: BOOLEAN DEFAULT TRUE
- sms_enabled: BOOLEAN DEFAULT FALSE
- push_enabled: BOOLEAN DEFAULT TRUE
- deadline_reminders: BOOLEAN DEFAULT TRUE
- phone_verified: BOOLEAN DEFAULT FALSE
```

#### notification_history
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- notification_type: VARCHAR(64)
- channel: VARCHAR(32)  # email, sms, push, voice
- recipient: VARCHAR(255)
- success: BOOLEAN
- error: TEXT
- message_id: VARCHAR(128)
- sent_at: TIMESTAMP
```

#### deadline_reminders
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- opportunity_id: VARCHAR(36) FK → opportunities.id
- reminder_type: VARCHAR(32)  # 7_day, 2_day
- sent_at: TIMESTAMP
- UNIQUE(user_id, opportunity_id, reminder_type)
```

### Chat Tables

#### chat_threads
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- title: VARCHAR(255)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### chat_messages
```sql
- id: VARCHAR(36) PRIMARY KEY
- thread_id: VARCHAR(36) FK → chat_threads.id
- role: VARCHAR(16)  # user, assistant
- content: TEXT
- created_at: TIMESTAMP
```

#### user_memories
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- content: TEXT
- source: VARCHAR(32)  # chat, profile
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### Security Tables

#### consent_records
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- purpose: VARCHAR(128)
- granted: BOOLEAN
- granted_at: TIMESTAMP
- revoked_at: TIMESTAMP
- ip_address: VARCHAR(64)
- UNIQUE(user_id, purpose)
```

#### audit_logs
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- action: VARCHAR(128)  # document_decryption_access, etc.
- resource_type: VARCHAR(64)
- resource_id: VARCHAR(36)
- details: JSON
- ip_address: VARCHAR(64)
- consent_id: VARCHAR(36)
- created_at: TIMESTAMP (indexed)
```


### Experiment Tables

#### experiment_variants
```sql
- id: VARCHAR(36) PRIMARY KEY
- experiment_name: VARCHAR(128)
- variant_name: VARCHAR(64)  # control, treatment_a, etc.
- is_active: BOOLEAN
- config: JSON
- created_at: TIMESTAMP
- UNIQUE(experiment_name, variant_name)
```

#### user_experiments
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- experiment_name: VARCHAR(128)
- variant_name: VARCHAR(64)
- assigned_at: TIMESTAMP
- UNIQUE(user_id, experiment_name)
```

#### user_events (Analytics)
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- event_type: VARCHAR(64)  # recommendation_viewed, saved, applied, etc.
- opportunity_id: VARCHAR(36) FK → opportunities.id
- application_id: VARCHAR(36) FK → applications.id
- experiment_name: VARCHAR(128)
- variant_name: VARCHAR(64)
- match_score: FLOAT
- event_metadata: JSON
- session_id: VARCHAR(128)
- created_at: TIMESTAMP
```

#### feedback
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- opportunity_id: VARCHAR(36) FK → opportunities.id
- feedback_type: VARCHAR(32)  # relevant, not_relevant, ineligible, applied
- comment: TEXT
- experiment_name: VARCHAR(128)
- variant_name: VARCHAR(64)
- created_at: TIMESTAMP
```

#### accuracy_metrics
```sql
- id: VARCHAR(36) PRIMARY KEY
- user_id: VARCHAR(36) FK → users.id
- opportunity_id: VARCHAR(36) FK → opportunities.id
- metric_type: VARCHAR(32)  # false_positive, false_negative
- predicted_eligible: BOOLEAN
- actual_eligible: BOOLEAN
- rule_context: JSON
- created_at: TIMESTAMP
```

### Workflow Tables

#### workflow_events
```sql
- id: VARCHAR(36) PRIMARY KEY
- application_id: VARCHAR(36) FK → applications.id
- from_state: VARCHAR(64)
- to_state: VARCHAR(64)
- actor_id: VARCHAR(36)
- actor_role: VARCHAR(32)
- notes: TEXT
- created_at: TIMESTAMP
```

### Connector Tracking

#### connector_status
```sql
- id: VARCHAR(36) PRIMARY KEY
- name: VARCHAR(64) UNIQUE
- last_run: TIMESTAMP
- last_success: TIMESTAMP
- last_error: TEXT
- records_processed: INTEGER
- is_stale: BOOLEAN
```

---


## Environment Variables Reference

### Backend (.env)

```env
# Application
APP_NAME=Student Success Copilot API
DEBUG=true
DEV_MODE=true

# Database - SQLite (default)
DATABASE_URL=sqlite:///./edupilot.db

# Database - PostgreSQL (production)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=edupilot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=15

# Redis
REDIS_URL=redis://localhost:6379/0

# ChromaDB Vector Store
CHROMA_PATH=./chroma_data

# Ollama LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TEMPERATURE=0.7

# CORS (Frontend URLs)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Authentication (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_JWT_SECRET=your_jwt_secret

# Notification Services
SENDGRID_API_KEY=SG.your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@edupilot.local
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_PHONE=+1234567890
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-adminsdk.json

# Document Verification
TESSERACT_CMD=/usr/bin/tesseract  # Or C:\Program Files\Tesseract-OCR\tesseract.exe
UIDAI_API_KEY=your_uidai_api_key
UIDAI_API_URL=https://api.uidai.gov.in

# Security & Encryption
ENCRYPTION_KEY_MASTER=base64_encoded_32byte_key_here
TEE_MODE=mock  # mock | aws_nitro | azure_confidential
AUDIT_LOG_RETENTION_DAYS=1095

# Data Connectors
ENABLED_CONNECTORS=unstop,internshala
UNSTOP_API_KEY=your_unstop_api_key

# Auto-verification Thresholds
AUTO_APPROVAL_THRESHOLD=0.85
REVIEW_THRESHOLD=0.60
```

### Frontend (.env)

```env
# Supabase Authentication
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend API
NEXT_API_URL=http://localhost:8000
```

---


## Key Implementation Details

### 1. Hybrid RAG Architecture

**Problem**: Pure semantic search returns irrelevant results when eligibility rules aren't met (e.g., showing ₹8L/year income limit scholarship to ₹10L/year student).

**Solution**: Two-stage retrieval
1. **Semantic Stage**: ChromaDB vector search (cosine similarity) returns 25 candidates
2. **Eligibility Stage**: Rule engine filters candidates by student profile
3. **Ranking**: Combine `relevance_score` + `eligibility_score` → top 8 results

**Code**: `services/app/knowledge/hybrid_rag.py::retrieve_for_profile()`

### 2. Consistent Hashing for A/B Testing

**Problem**: Users must always get the same variant across sessions.

**Solution**: Deterministic assignment
```python
hash_input = f"{user_id}:{experiment_name}"
hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()
variant_index = int(hash_digest[:8], 16) % len(variants)
```

**Benefits**:
- Reproducible: Same user → same variant
- Isolated: Different experiments → different assignments
- Balanced: Even distribution across variants

**Code**: `services/app/analytics/experiment_service.py::_hash_user_to_variant()`

### 3. TEE-Protected Document Processing

**Problem**: Sensitive documents (Aadhaar, income certificates) must never be exposed in plaintext.

**Solution**: End-to-end encryption + enclave processing
1. **Upload**: Encrypt client-side (future) or server-side immediately
2. **TEE Enclave**: Process in isolated environment (AWS Nitro / Azure Confidential)
3. **OCR**: Extract text inside enclave
4. **Storage**: Save encrypted bytes only
5. **Decryption**: Only after consent check + audit log

**Code**: 
- `services/app/security/tee.py` (TEE service)
- `services/app/security/document_store.py` (encryption)
- `services/app/verification/engine.py` (orchestration)

### 4. Multi-Channel Notification Orchestrator

**Problem**: Different users prefer different channels (email vs SMS vs push).

**Solution**: Preference-based dispatch
1. **Check Preferences**: Query NotificationPreference table
2. **Select Channels**: Build list based on enabled flags
3. **Send Parallel**: Fire requests to all services simultaneously
4. **Log History**: Record success/failure per channel
5. **Auto-Enable Voice**: For urgent 2-day deadline reminders

**Code**: `services/app/notifications/orchestrator.py::send_notification()`

### 5. LangGraph-Based Chatbot

**Problem**: Simple prompt engineering doesn't handle complex RAG workflows.

**Solution**: State machine with nodes
```
START → retrieve_context → generate_response → END
```

**Benefits**:
- **Modularity**: Separate retrieval from generation
- **Debuggability**: Inspect state at each node
- **Extensibility**: Add nodes for memory, tool use, etc.

**Code**: `services/app/agents/chatbot.py::_build_graph()`


---

## Performance & Scalability

### Current Capacity
- **Database**: SQLite (dev) / PostgreSQL (prod) handles 100K+ opportunities
- **Vector Store**: ChromaDB supports millions of embeddings
- **Concurrent Users**: FastAPI async handles 1000+ req/sec
- **LLM Inference**: Ollama local (10-30 tokens/sec on CPU, 100+ on GPU)
- **Task Queue**: Celery + Redis scales horizontally

### Optimization Strategies
1. **Database Indexing**: 
   - Composite indexes on (source, external_id), (user_id, opportunity_id)
   - BTREE index on deadline for fast deadline queries
   
2. **Vector Search Caching**:
   - Cache frequently queried embeddings in Redis
   - TTL: 1 hour for hot queries
   
3. **RAG Optimization**:
   - Limit retrieval to 25 candidates (not full DB scan)
   - Batch eligibility checks (vectorized operations)
   
4. **Connection Pooling**:
   - PostgreSQL: pool_size=5, max_overflow=15
   - Redis: connection pool with health checks

5. **Async Operations**:
   - All I/O operations (DB, HTTP, LLM) are async
   - Concurrent document processing in TEE

---

## Compliance & Data Privacy

### DPDP Act Compliance (India)

1. **Consent Management**:
   - Explicit consent required before data processing
   - ConsentRecord table tracks grants/revocations
   - Decryption blocked without active consent

2. **Audit Logging**:
   - Write-only logs (no deletion)
   - 3-year retention (DPDP requirement)
   - Tracks: who, what, when, IP address

3. **Right to Erasure**:
   - User can request data deletion via API
   - Cascade deletes: profile → documents → applications
   - Encrypted documents purged from storage

4. **Data Minimization**:
   - Only collect necessary fields
   - Auto-delete old notifications after 90 days
   - Profile readiness score guides minimal data collection

5. **Encryption at Rest**:
   - All sensitive documents encrypted (AES-256-GCM)
   - Per-document key derivation (PBKDF2)
   - Master key rotated quarterly

### Security Best Practices

1. **JWT Authentication**: Supabase Auth with short-lived tokens
2. **RBAC**: Role-based access (student, reviewer, admin)
3. **Rate Limiting**: 100 req/min per user (via middleware)
4. **SQL Injection Prevention**: SQLAlchemy ORM + parameterized queries
5. **CORS**: Whitelist frontend origins only
6. **HTTPS**: TLS 1.3 in production
7. **Secret Management**: Environment variables + Azure Key Vault (prod)

---


## Data Sources (847+ Integrated)

### Scholarship Sources
1. **National Scholarship Portal (NSP)** - 150+ schemes
2. **MahaDBT (Maharashtra)** - State scholarships
3. **MyScheme (govt.in)** - Central + state schemes
4. **AICTE** - Technical education scholarships
5. **UGC** - University Grants Commission
6. **MHRD** - Ministry of HRD schemes
7. **Devnarayan Foundation** - Rajasthan scholarships
8. **Inspire (DST)** - Science scholarships

### Internship Sources
1. **Internshala** - Live scraper (Playwright)
2. **Indeed** - Dummy data (demo)
3. **Naukri** - Dummy data (demo)
4. **Wellfound (AngelList)** - Dummy data (demo)
5. **Unstop (formerly Dare2Compete)** - API connector

### Hackathon Sources
1. **Unstop** - Live + past hackathons
2. **Devpost** - Global hackathons
3. **MLH (Major League Hacking)** - Student hackathons
4. **HackerEarth** - Corporate + community hackathons

### Future Integrations
- PMRF (Prime Minister's Research Fellowship)
- Buddy4Study
- Scholarships.com (international)
- LinkedIn Jobs
- Glassdoor

---

## Monitoring & Observability

### Logging
- **Format**: Structured JSON logs
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Outputs**: Console (dev), File + Sentry (prod)

### Metrics
- **Request Latency**: p50, p95, p99 via FastAPI middleware
- **DB Query Performance**: SQLAlchemy slow query log
- **LLM Response Time**: Ollama inference duration
- **Notification Delivery Rate**: Success % per channel
- **RAG Relevance Score**: Avg relevance score per query

### Health Checks
- `GET /health` - API status
- `GET /api/v1/chat/health` - Chatbot + Ollama status
- `GET /api/v1/admin/connector-status` - Data ingestion health

### Error Tracking
- **Sentry**: Exception tracking + stack traces
- **Custom Alerts**: Slack notifications for critical errors
- **Audit Logs**: Security event monitoring

---

## Development Workflow

### Code Structure
```
services/app/
├── agents/          # AI agents (modular, testable)
├── api/             # FastAPI routes (thin controllers)
├── intelligence/    # Business logic (eligibility, recommendations)
├── knowledge/       # RAG implementation
├── security/        # Encryption, TEE, consent
├── verification/    # OCR, parsers, gov APIs
├── notifications/   # Multi-channel orchestrator
├── analytics/       # A/B testing, metrics
└── db/              # SQLAlchemy models
```

### Coding Standards
- **Python**: PEP 8, Black formatter, isort
- **TypeScript**: ESLint + Prettier
- **Docstrings**: Google style
- **Tests**: Pytest with >80% coverage target
- **Type Hints**: Enforced via mypy

### Git Workflow
1. Feature branches: `feature/chatbot-memory`
2. Pull requests with review required
3. CI/CD: GitHub Actions (test → lint → build → deploy)

---


## Troubleshooting

### Common Issues

#### 1. Ollama Connection Error
**Error**: `ChatOllama connection failed`

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull model if missing
ollama pull llama3.2:3b
```

#### 2. ChromaDB Empty Results
**Error**: `RAG retrieval returns 0 documents`

**Solution**:
```bash
# Reindex scholarships
cd services
python index_scholarships_now.py

# Verify indexing
python -c "from app.knowledge.hybrid_rag import HybridRAG; \
           rag = HybridRAG(); \
           print(rag.semantic_search('engineering', limit=5))"
```

#### 3. PostgreSQL Connection Refused
**Error**: `psycopg2.OperationalError: could not connect`

**Solution**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS

# Verify connection
psql -U postgres -d edupilot -c "SELECT 1;"
```

#### 4. Celery Worker Not Picking Tasks
**Error**: Tasks stay in "pending" state

**Solution**:
```bash
# Check Redis connection
redis-cli ping

# Restart Celery worker
celery -A app.tasks worker -B -l info --purge

# Verify task queue
celery -A app.tasks inspect active
```

#### 5. Tesseract OCR Not Found
**Error**: `TesseractNotFoundError`

**Solution**:
```bash
# Install Tesseract
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows: Download installer from GitHub
# Then set TESSERACT_CMD in .env
```

#### 6. Frontend 404 on API Calls
**Error**: `Failed to fetch from /api/v1/...`

**Solution**:
1. Check backend is running: http://localhost:8000/health
2. Verify CORS origins in `.env`:
   ```env
   CORS_ORIGINS=http://localhost:3000
   ```
3. Check Next.js API URL:
   ```env
   NEXT_API_URL=http://localhost:8000
   ```

---

## Roadmap

### Q1 2025
- [ ] Mobile app (React Native)
- [ ] Voice interface (WhatsApp bot)
- [ ] Regional language support (Hindi, Tamil, Telugu)
- [ ] Aadhaar e-KYC integration

### Q2 2025
- [ ] Career guidance agent (skill gap analysis)
- [ ] Interview prep chatbot (mock interviews)
- [ ] Scholarship application tracking (portal scraping)
- [ ] Peer comparison dashboard

### Q3 2025
- [ ] Blockchain-verified credentials (NFT certificates)
- [ ] Personalized learning paths
- [ ] Alumni mentor matching
- [ ] Corporate scholarship partnerships

---


## Contributing

We welcome contributions! Here's how you can help:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Write tests**: Ensure >80% coverage
5. **Run tests**: `pytest` (backend), `npm test` (frontend)
6. **Commit**: Use conventional commits (e.g., `feat: add voice notifications`)
7. **Push**: `git push origin feature/your-feature-name`
8. **Open Pull Request**: Describe changes clearly

### Areas We Need Help

- **Data Connectors**: Add more scholarship/internship sources
- **Regional Languages**: Hindi, Tamil, Telugu UI translations
- **Documentation**: Improve guides, add tutorials
- **Testing**: Write integration tests, improve coverage
- **UI/UX**: Enhance dashboard, mobile responsiveness

### Code Review Process

1. Automated checks (CI): lint, test, build
2. Manual review by maintainers
3. Address feedback
4. Merge to `main` after approval

---

## License

**MIT License**

Copyright (c) 2024 EduPilot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Contact & Support

- **GitHub Issues**: https://github.com/your-repo/issues
- **Email**: support@edupilot.local
- **Discord**: [Join our community](#)
- **Documentation**: [docs.edupilot.local](#)

---

## Acknowledgments

Built with ❤️ for Indian students by the EduPilot team.

Special thanks to:
- **Ollama** for local LLM inference
- **LangChain/LangGraph** for agent frameworks
- **FastAPI** for async Python web framework
- **Next.js** for React framework
- **Supabase** for authentication infrastructure
- **ChromaDB** for vector database
- **Twilio** & **SendGrid** for communication APIs

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: ✅ Production Ready

