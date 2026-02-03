# System Architecture

## 🏗️ High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USER BROWSER                         │
│                    http://localhost:3000                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP Requests
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    REACT FRONTEND                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Upload   │  │   Search   │  │    View    │            │
│  │    Tab     │  │     Tab    │  │     Tab    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                                                               │
│  • File Upload UI       • Search Interface                   │
│  • Presentation List    • Results Display                    │
│  • Slide Viewer         • Navigation                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Axios HTTP Requests
                           │ (JSON, multipart/form-data)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   FASTAPI BACKEND                            │
│                  http://localhost:8000                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              API ENDPOINTS                           │   │
│  │                                                       │   │
│  │  POST   /api/upload            - Upload PPT file    │   │
│  │  GET    /api/presentations     - List all           │   │
│  │  GET    /api/presentations/1   - Get details        │   │
│  │  GET    /api/search?q=text     - Search slides      │   │
│  │  DELETE /api/presentations/1   - Delete             │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                   │
│                           ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         BUSINESS LOGIC                               │   │
│  │                                                       │   │
│  │  • File validation                                   │   │
│  │  • PPT parsing (python-pptx)                        │   │
│  │  • Text extraction                                   │   │
│  │  • Database operations                               │   │
│  │  • Search logic                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   DATABASE   │  │   UPLOADS/   │  │   SLIDES/    │
│              │  │              │  │              │
│ SQLite DB    │  │  .pptx files │  │ Extracted    │
│              │  │              │  │ slide data   │
│ ┌──────────┐ │  │ Original     │  │              │
│ │Presenta- │ │  │ uploaded     │  │ (Future:     │
│ │tions     │ │  │ files        │  │  images)     │
│ └──────────┘ │  │              │  │              │
│ ┌──────────┐ │  └──────────────┘  └──────────────┘
│ │ Slides   │ │
│ └──────────┘ │
│              │
│ ppt_search.db│
└──────────────┘
```

## 📊 Data Flow

### 1. Upload Flow

```
User Selects File
       │
       ▼
Frontend: FileReader API
       │
       ▼
HTTP POST /api/upload
       │
       ▼
Backend: Validate file type
       │
       ▼
Save to ./uploads/
       │
       ▼
python-pptx: Parse PPT
       │
       ▼
Extract: Titles, Text, Notes
       │
       ▼
Create Presentation record (DB)
       │
       ▼
Create Slide records (DB)
       │
       ▼
Return: Success + metadata
       │
       ▼
Frontend: Show success message
       │
       ▼
Update presentations list
```

### 2. Search Flow

```
User Enters Query
       │
       ▼
Frontend: Capture input
       │
       ▼
HTTP GET /api/search?q=keyword
       │
       ▼
Backend: SQL LIKE query
       │
       ▼
Search in: title, text_content, notes
       │
       ▼
Fetch matching slides
       │
       ▼
Join with presentation data
       │
       ▼
Return: Results array (JSON)
       │
       ▼
Frontend: Display results
       │
       ▼
Show: Slide content + context
```

### 3. View Flow

```
User Clicks "View Slides"
       │
       ▼
HTTP GET /api/presentations/1
       │
       ▼
Backend: Fetch presentation
       │
       ▼
Fetch all related slides
       │
       ▼
Sort by slide_number
       │
       ▼
Return: Presentation + Slides (JSON)
       │
       ▼
Frontend: Render slide cards
       │
       ▼
Display: Titles, content, notes
```

## 🗄️ Database Schema

```sql
┌────────────────────────────────────┐
│         presentations              │
├────────────────────────────────────┤
│ id                 INTEGER (PK)    │
│ filename           VARCHAR         │
│ original_filename  VARCHAR         │
│ upload_date        DATETIME        │
│ slide_count        INTEGER         │
└──────────────┬─────────────────────┘
               │
               │ 1:N relationship
               │
┌──────────────▼─────────────────────┐
│             slides                 │
├────────────────────────────────────┤
│ id                 INTEGER (PK)    │
│ presentation_id    INTEGER (FK)    │
│ slide_number       INTEGER         │
│ title              VARCHAR         │
│ text_content       TEXT            │
│ notes              TEXT            │
│ image_path         VARCHAR         │
└────────────────────────────────────┘
```

## 🔧 Technology Stack Details

### Backend Stack

```
FastAPI (Web Framework)
    │
    ├── Uvicorn (ASGI Server)
    │   └── HTTP/WebSocket support
    │
    ├── Pydantic (Data Validation)
    │   └── Request/Response models
    │
    ├── SQLAlchemy (ORM)
    │   ├── Database Models
    │   ├── Query Builder
    │   └── Relationships
    │
    └── python-pptx (PPT Parser)
        ├── Slide extraction
        ├── Text parsing
        └── Notes extraction
```

### Frontend Stack

```
React 18
    │
    ├── JSX Components
    │   ├── App.js (Main component)
    │   ├── Upload UI
    │   ├── Search UI
    │   └── View UI
    │
    ├── Axios (HTTP Client)
    │   └── API calls
    │
    ├── CSS Modules
    │   ├── Gradients
    │   ├── Animations
    │   └── Responsive Grid
    │
    └── React Hooks
        ├── useState (State management)
        ├── useEffect (Side effects)
        └── Event handlers
```

## 🚀 Request/Response Flow

### Upload Request

```
POST /api/upload
Content-Type: multipart/form-data

┌─────────────────────────┐
│ FormData:               │
│   file: [Binary Data]   │
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│ Response (JSON):        │
│ {                       │
│   "success": true,      │
│   "presentation_id": 1, │
│   "filename": "...",    │
│   "slide_count": 10     │
│ }                       │
└─────────────────────────┘
```

### Search Request

```
GET /api/search?q=introduction

┌─────────────────────────┐
│ Query Params:           │
│   q = "introduction"    │
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│ Response (JSON):        │
│ {                       │
│   "query": "intro...",  │
│   "count": 5,           │
│   "results": [          │
│     {                   │
│       "slide": {...},   │
│       "presentation": {│
│         ...             │
│       }                 │
│     }                   │
│   ]                     │
│ }                       │
└─────────────────────────┘
```

## 🔐 Security Architecture

```
┌──────────────────────────┐
│   Security Layers        │
├──────────────────────────┤
│                          │
│  1. CORS Protection      │
│     └─ Origin validation │
│                          │
│  2. File Validation      │
│     ├─ Type check        │
│     ├─ Extension check   │
│     └─ (Future: Size)    │
│                          │
│  3. Input Sanitization   │
│     └─ SQLAlchemy ORM    │
│                          │
│  4. Error Handling       │
│     ├─ Try/Catch blocks  │
│     └─ HTTP exceptions   │
│                          │
│  5. File Storage         │
│     ├─ Unique names      │
│     └─ Organized dirs    │
└──────────────────────────┘
```

## 📦 Deployment Architecture

### Docker Container Structure

```
┌─────────────────────────────────────┐
│      Docker Container               │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   Python Runtime              │ │
│  │   + Dependencies              │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   Backend Application         │ │
│  │   (FastAPI + Uvicorn)         │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   Built Frontend              │ │
│  │   (Static files)              │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   Volume Mounts:              │ │
│  │   • ./uploads → /app/uploads  │ │
│  │   • ./slides → /app/slides    │ │
│  │   • ppt_search.db             │ │
│  └───────────────────────────────┘ │
│                                     │
│         Port 8000 exposed          │
└─────────────────────────────────────┘
```

## 🎯 Component Interaction

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Upload    │      │  Database   │      │  PPT Parser │
│  Component  │      │   Module    │      │   Module    │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                     │
       │ 1. Send file       │                     │
       ├────────────────────┼────────────────────▶│
       │                    │                     │
       │                    │    2. Parse slides  │
       │                    │◀────────────────────┤
       │                    │                     │
       │    3. Save to DB   │                     │
       │───────────────────▶│                     │
       │                    │                     │
       │◀───────────────────┤ 4. Return metadata  │
       │                    │                     │

┌─────────────┐      ┌─────────────┐
│   Search    │      │  Database   │
│  Component  │      │   Module    │
└──────┬──────┘      └──────┬──────┘
       │                    │
       │ 1. Search query    │
       ├───────────────────▶│
       │                    │
       │                    │ 2. SQL LIKE query
       │                    │
       │◀───────────────────┤ 3. Return results
       │                    │
       │ 4. Display         │
       │                    │
```

## 🔄 State Management

### Frontend State Flow

```
App Component State:
├── presentations[]        - List of all presentations
├── selectedPresentation   - Currently viewed presentation
├── searchQuery            - Current search text
├── searchResults[]        - Search results
├── uploading              - Upload in progress flag
├── activeTab              - Current tab name
└── message                - Toast notification

State Updates:
• File Upload      → uploading: true → presentations: updated
• Presentation Click → selectedPresentation: data → activeTab: 'view'
• Search Submit     → searchResults: updated
• Tab Click         → activeTab: changed
```

## 🎨 UI Component Tree

```
<App>
  │
  ├── <Header>
  │   ├── Title
  │   └── Description
  │
  ├── <Message> (conditional)
  │   └── Toast notification
  │
  ├── <Tabs>
  │   ├── Upload button
  │   ├── Presentations button
  │   ├── Search button
  │   └── View button (conditional)
  │
  └── <Content>
      │
      ├── <UploadSection> (if activeTab === 'upload')
      │   ├── <UploadCard>
      │   └── <FileInput>
      │
      ├── <PresentationsSection> (if activeTab === 'presentations')
      │   └── <PresentationCard>[]
      │       ├── Title
      │       ├── Metadata
      │       ├── View button
      │       └── Delete button
      │
      ├── <SearchSection> (if activeTab === 'search')
      │   ├── <SearchForm>
      │   └── <SearchResults>
      │       └── <ResultCard>[]
      │
      └── <ViewSection> (if activeTab === 'view')
          ├── <ViewHeader>
          └── <SlideCard>[]
              ├── Slide number
              ├── Title
              ├── Content
              └── Notes
```

## 📈 Performance Considerations

### Backend Optimization
- Connection pooling (SQLAlchemy)
- Efficient query patterns
- File streaming for uploads
- Lazy loading of related data

### Frontend Optimization
- Single-page application (SPA)
- Component-based rendering
- CSS animations (GPU-accelerated)
- Conditional rendering
- Optimized re-renders

### Database Optimization
- Indexed columns (id, presentation_id)
- LIKE queries with indexes
- Relationship loading strategies
- Query result caching (future)

## 🔮 Extension Points

### Easy to Add:
1. **Authentication** - Add middleware in main.py
2. **Authorization** - Add user_id to tables
3. **Caching** - Add Redis layer
4. **File Storage** - Switch to S3/Cloud Storage
5. **Database** - Change SQLite to PostgreSQL
6. **Analytics** - Add tracking middleware
7. **Webhooks** - Add event system
8. **API Keys** - Add authentication layer

---

**This architecture provides a solid foundation for a scalable, maintainable PowerPoint search platform.**

