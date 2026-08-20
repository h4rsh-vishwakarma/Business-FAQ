# Business FAQ & Lead-Capture Chatbot

FastAPI-based FAQ and lead-capture chatbot demo for a small business. This implementation uses a restaurant niche, `Maple & Thyme Bistro`, so the product feels like a real client-facing solution instead of a generic support bot.

## What it includes

- FAQ chatbot with fuzzy matching against a JSON knowledge base
- Lead capture flow for bookings, catering, callbacks, and general inquiries
- SQLite persistence for chat sessions, conversation logs, and leads
- Basic admin dashboard at `/admin/leads`
- Embeddable chat widget served from `/api/embed.js`
- Demo landing page served from `/`
- API tests for health, FAQ response, and lead capture flow

## Project structure

```text
app/
  config.py
  database.py
  main.py
  models.py
  schemas.py
  services/
data/
  faqs.json
static/
  index.html
  admin.html
  admin.js
  styles.css
  widget.js
tests/
  test_api.py
main.py
requirements.txt
```

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- Demo site: `http://127.0.0.1:8000/`
- Health check: `http://127.0.0.1:8000/health`
- Leads API: `http://127.0.0.1:8000/api/leads`
- Admin dashboard: `http://127.0.0.1:8000/admin/leads`

Default admin credentials:

- Username: `admin`
- Password: `admin123`

## Environment variables

```env
DATABASE_URL=sqlite:///./chatbot.db
CORS_ORIGINS=*
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
FAQ_PATH=./data/faqs.json
```

## API contract

### `POST /chat`

Request:

```json
{
  "session_id": "visitor-123",
  "message": "What are your opening hours?"
}
```

Response:

```json
{
  "session_id": "visitor-123",
  "message": "Maple & Thyme Bistro is open Monday to Thursday from 11:30 AM to 10:00 PM...",
  "quick_replies": ["Reservations", "Location", "Parking"],
  "requires_contact": false,
  "lead_captured": false
}
```

## Embedding the widget

For a simple install on any site:

```html
<script>
  window.BusinessFAQChatbotConfig = {
    apiBaseUrl: "https://your-backend-url.onrender.com",
    title: "Maple & Thyme Bistro",
    subtitle: "Restaurant support and booking capture"
  };
</script>
<script src="https://your-backend-url.onrender.com/api/embed.js" defer></script>
```

## Deployment notes

### Render backend

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend

This project already serves the landing page and widget assets from FastAPI, so you can deploy the full demo as one service. If you want a separate static frontend on Netlify or Vercel later, point the widget config to the deployed backend URL and add that domain to `CORS_ORIGINS`.

## Testing

```bash
pytest
```

## Next upgrades

- Add LLM fallback for low-confidence questions
- Replace HTTP basic auth with proper admin login
- Add editable FAQ management UI
- Move from SQLite to PostgreSQL for multi-user production use
