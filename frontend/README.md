# FeedbackForge AI

> **Tagline:** Turn Customer Feedback into Product Decisions.  
> **Product Intelligence Workspace**

FeedbackForge AI is an AI-powered Product Intelligence Workspace that takes customer feedback, analyzes it using an AI/Python backend, stores the analyzed results in MongoDB, and presents actionable insights to product teams.

---

## Tech Stack

- **ReactJS** (v18)
- **Vite**
- **JavaScript**
- **Tailwind CSS**
- **React Router** (v6)
- **Lucide React** (icons)
- **Axios** (API communication)
- **Recharts** (focused metric visualizations)

---

## Design System & Principles

- **Human-Designed & Professional:** Clean hierarchy, comfortable spacing, consistent typography, subtle borders, and moderate corner radii.
- **Palette:**
  - Base: Warm off-white (`#F8FAFC`, `#FFFFFF`)
  - Typography: Slate / Charcoal (`#0F172A`, `#334155`, `#64748B`)
  - Primary Accent: Emerald (`#059669`)
  - Warning / Priority: Amber (`#F59E0B`)
  - Negative / Error: Rose (`#E11D48`)
  - AI Secondary Highlights: Violet (`#7C3AED`)
- **Restraint:** No excessive gradients, no glowing effects, no emojis as UI icons, and no fake production statistics.

---

## Directory Structure

```text
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── EmptyState.jsx
│   │   │   ├── LoadingState.jsx
│   │   │   ├── ErrorState.jsx
│   │   │   └── StatusBadge.jsx
│   │   ├── layout/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Header.jsx
│   │   │   └── MainLayout.jsx
│   │   ├── feedback/
│   │   │   ├── FeedbackForm.jsx
│   │   │   ├── FeedbackTable.jsx
│   │   │   └── FeedbackCard.jsx
│   │   ├── insights/
│   │   │   ├── InsightMetric.jsx
│   │   │   ├── IssueTable.jsx
│   │   │   ├── FeatureRequestTable.jsx
│   │   │   ├── ThemeList.jsx
│   │   │   └── PriorityList.jsx
│   │   └── planning/
│   │       ├── PlanningCard.jsx
│   │       └── PriorityBadge.jsx
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── CustomerFeedback.jsx
│   │   ├── Insights.jsx
│   │   ├── Planning.jsx
│   │   ├── Requirements.jsx
│   │   └── NotFound.jsx
│   ├── routes/
│   │   └── AppRoutes.jsx
│   ├── services/
│   │   ├── api.js
│   │   ├── authService.js
│   │   ├── feedbackService.js
│   │   ├── insightsService.js
│   │   └── planningService.js
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── utils/
│   │   ├── formatters.js
│   │   └── validators.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── .env
├── .env.example
├── package.json
├── vite.config.js
└── README.md
```

---

## Getting Started

### 1. Install Dependencies
```bash
npm install
# or from root workspace:
npm --prefix frontend install
```

### 2. Environment Configuration
Create `.env` from `.env.example`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Run Development Server
```bash
npm run dev
# or from root workspace:
npm run dev
```

### 4. Build for Production
```bash
npm run build
```

---

## FastAPI Backend Contract

The frontend communicates with FastAPI endpoints:
- `POST /auth/register` — User account registration
- `POST /auth/login` — Authentication & JWT bearer token issuance
- `GET /auth/me` — Authenticated profile verification
- `GET /feedback` — Retrieve ingested feedback items
- `POST /feedback` — Submit raw customer feedback text
- `POST /feedback/upload` — Multipart upload for `.csv`, `.txt`, `.pdf`, `.doc`, `.docx`
- `POST /feedback/analyze` — Trigger AI batch processing
- `GET /insights` — Ingested feedback metrics, AI executive summary, issues, feature requests, common themes, and priority opportunities
- `POST /insights/generate` — On-demand recomputation of feedback insights
- `GET /planning` & `POST /planning` — Product planning initiatives
- `GET /requirements` & `POST /requirements/generate` — Technical product requirements & acceptance criteria
