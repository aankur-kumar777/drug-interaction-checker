# Quick Start Guide

Get the Drug Interaction Checker up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Web browser

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/drug-interaction-checker.git
cd drug-interaction-checker

# Run setup script
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

#### Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Frontend

The frontend is static HTML/CSS/JS - no build step required!

## Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # Skip if already activated
python app/main.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### Open Frontend

**Option A: Direct File**
```bash
# From project root
open frontend/index.html  # macOS
xdg-open frontend/index.html  # Linux
start frontend/index.html  # Windows
```

**Option B: Local Server**
```bash
# From project root
cd frontend
python -m http.server 3000
# Then visit http://localhost:3000
```

## First Steps

1. **Open the application** in your browser
2. **Search for a drug** (e.g., "Warfarin")
3. **Add multiple drugs** (e.g., add "Aspirin", then "Ibuprofen")
4. **Click "Analyze Interactions"**
5. **Review the results**:
   - Overall risk assessment
   - Detailed interaction information
   - Clinical recommendations
   - Safer alternatives
   - Visual interaction graph

## Example Workflow

### Try These Drug Combinations

**High-Risk Combination:**
- Warfarin
- Aspirin
- Ibuprofen

**Moderate-Risk Combination:**
- Lisinopril
- Ibuprofen
- Metformin

**Low-Risk Combination:**
- Metformin
- Lisinopril
- Amoxicillin

## Testing the API

### Using cURL

```bash
# Check interactions
curl -X POST http://localhost:5000/api/check-interactions \
  -H "Content-Type: application/json" \
  -d '{"drugs": ["warfarin", "aspirin"]}'

# Search for drugs
curl "http://localhost:5000/api/search?q=war"

# Get drug info
curl http://localhost:5000/api/drug/warfarin
```

### Using Python

```python
import requests

# Check interactions
response = requests.post(
    'http://localhost:5000/api/check-interactions',
    json={'drugs': ['warfarin', 'aspirin']}
)
print(response.json())
```

### Using Postman

1. Import the API endpoints from `docs/API.md`
2. Set base URL to `http://localhost:5000/api`
3. Try the endpoints!

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

Expected output:
```
tests/test_api.py::test_index_route PASSED
tests/test_api.py::test_health_check PASSED
...
====== 20 passed in 2.5s ======
```

## Docker Deployment

### Using Docker Compose

```bash
# Build and start containers
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:5000
```

### Individual Containers

```bash
# Build backend
docker build -t drug-checker-api .

# Run backend
docker run -p 5000:5000 drug-checker-api
```

## Troubleshooting

### Backend Won't Start

**Problem:** ModuleNotFoundError
```bash
# Solution: Activate virtual environment
source venv/bin/activate
```

**Problem:** Port 5000 already in use
```bash
# Solution: Change port in app/main.py or kill process
lsof -ti:5000 | xargs kill -9  # macOS/Linux
```

### Frontend Issues

**Problem:** API calls failing (CORS errors)
```bash
# Solution: Ensure backend is running
# Check backend logs for CORS configuration
```

**Problem:** Visualization not showing
```bash
# Solution: Check browser console
# Ensure D3.js is loading from CDN
```

### Empty Results

**Problem:** No interactions found
```bash
# Solution: Check data files exist
ls backend/data/drugs.json
ls backend/data/interactions.json
```

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Backend
FLASK_ENV=development
FLASK_DEBUG=1
API_PORT=5000

# Frontend
FRONTEND_PORT=3000
```

### Customization

**Change Port:**
Edit `backend/app/main.py`:
```python
app.run(host='0.0.0.0', port=8000)  # Change 5000 to 8000
```

**Add Drugs:**
Edit `backend/data/drugs.json`:
```json
{
  "newdrug": {
    "class": "drug_class",
    "description": "Drug description",
    ...
  }
}
```

## Next Steps

1. **Read the full documentation** in `docs/`
2. **Explore the API** using `docs/API.md`
3. **Add more drugs** to the database
4. **Customize the UI** in `frontend/`
5. **Train ML models** using your data
6. **Deploy to production** (see DEPLOYMENT.md)

## Getting Help

- **Documentation:** `/docs` directory
- **GitHub Issues:** Report bugs and request features
- **API Docs:** `docs/API.md`
- **Contributing:** `CONTRIBUTING.md`

## Important Notes

⚠️ **Medical Disclaimer:**
This tool is for educational purposes only. Always consult healthcare professionals for medical advice.

🔒 **Security:**
- Enable HTTPS in production
- Implement authentication
- Validate all inputs
- Use rate limiting

## Success Checklist

- [ ] Backend running on http://localhost:5000
- [ ] Frontend accessible in browser
- [ ] Can search for drugs
- [ ] Can check interactions
- [ ] Results display correctly
- [ ] Visualization working
- [ ] Tests passing

**Congratulations! You're all set up! 🎉**

Now try checking some drug interactions!
