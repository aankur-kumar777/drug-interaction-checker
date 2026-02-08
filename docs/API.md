# API Documentation

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, no authentication is required. In production, implement OAuth2 or API key authentication.

## Endpoints

### 1. Check Drug Interactions

Check for interactions between multiple drugs.

**Endpoint:** `POST /api/check-interactions`

**Request Body:**
```json
{
  "drugs": ["warfarin", "aspirin", "ibuprofen"],
  "patient_factors": {
    "age": 65,
    "conditions": ["hypertension"],
    "allergies": []
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "drug_count": 3,
    "drugs": ["warfarin", "aspirin", "ibuprofen"],
    "interactions_found": 3,
    "interactions": [
      {
        "drug_pair": ["warfarin", "aspirin"],
        "severity": "major",
        "risk_score": 0.89,
        "description": "Increased risk of bleeding",
        "mechanism": "Additive anticoagulant effects",
        "clinical_effects": "Hemorrhage, bruising",
        "recommendations": ["Monitor INR closely"],
        "evidence_level": "A",
        "references": ["PMID:12345678"]
      }
    ],
    "overall_risk": "high",
    "recommendations": [...],
    "safer_alternatives": [...]
  }
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Server error

---

### 2. Get Drug Information

Retrieve detailed information about a specific drug.

**Endpoint:** `GET /api/drug/{drug_name}`

**Parameters:**
- `drug_name` (path): Name of the drug

**Example:** `GET /api/drug/warfarin`

**Response:**
```json
{
  "status": "success",
  "data": {
    "class": "anticoagulant",
    "description": "Anticoagulant used to prevent blood clots",
    "mechanism": "Vitamin K antagonist",
    "half_life": 40,
    "contraindications": ["active bleeding", "severe liver disease"]
  }
}
```

**Status Codes:**
- `200 OK`: Drug found
- `404 Not Found`: Drug not found
- `500 Internal Server Error`: Server error

---

### 3. Search Drugs

Search for drugs by name.

**Endpoint:** `GET /api/search`

**Query Parameters:**
- `q` (required): Search query (minimum 2 characters)
- `limit` (optional): Maximum results (default: 10, max: 50)

**Example:** `GET /api/search?q=war&limit=5`

**Response:**
```json
{
  "status": "success",
  "data": {
    "query": "war",
    "results": [
      {
        "name": "warfarin",
        "class": "anticoagulant",
        "description": "Anticoagulant used to prevent blood clots"
      }
    ]
  }
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Query too short
- `500 Internal Server Error`: Server error

---

### 4. Get Alternatives

Find safer alternative medications.

**Endpoint:** `GET /api/alternatives/{drug_name}`

**Parameters:**
- `drug_name` (path): Name of the drug
- `context` (query, multiple): Context drugs to check against

**Example:** `GET /api/alternatives/ibuprofen?context=warfarin&context=aspirin`

**Response:**
```json
{
  "status": "success",
  "data": {
    "original_drug": "ibuprofen",
    "alternatives": [
      {
        "name": "acetaminophen",
        "class": "analgesic",
        "description": "Pain reliever",
        "interaction_count": 0
      }
    ]
  }
}
```

---

### 5. Get Interaction Severity

Get severity information for two specific drugs.

**Endpoint:** `GET /api/severity/{drug1}/{drug2}`

**Parameters:**
- `drug1` (path): First drug name
- `drug2` (path): Second drug name

**Example:** `GET /api/severity/warfarin/aspirin`

**Response:**
```json
{
  "status": "success",
  "data": {
    "interaction": true,
    "drug1": "warfarin",
    "drug2": "aspirin",
    "severity": "major",
    "description": "Increased risk of bleeding",
    "mechanism": "Additive anticoagulant effects",
    "recommendations": ["Monitor INR closely"],
    "references": ["PMID:12345678"]
  }
}
```

---

### 6. Visualize Interactions

Generate visualization data for drug interaction graph.

**Endpoint:** `POST /api/visualize`

**Request Body:**
```json
{
  "drugs": ["warfarin", "aspirin", "ibuprofen"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "nodes": [
      {
        "id": "warfarin",
        "label": "Warfarin",
        "type": "drug",
        "class": "anticoagulant",
        "color": "#e74c3c"
      }
    ],
    "edges": [
      {
        "source": "warfarin",
        "target": "aspirin",
        "type": "interacts_with",
        "severity": "major",
        "color": "#e74c3c",
        "width": 3
      }
    ],
    "statistics": {
      "total_drugs": 3,
      "total_interactions": 3,
      "severity_distribution": {
        "major": 2,
        "moderate": 1
      }
    }
  }
}
```

---

### 7. Batch Check

Check multiple drug combinations in a single request.

**Endpoint:** `POST /api/batch-check`

**Request Body:**
```json
{
  "drug_combinations": [
    ["warfarin", "aspirin"],
    ["metformin", "lisinopril"],
    ["simvastatin", "amlodipine"]
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_combinations": 3,
    "results": [
      {
        "drugs": ["warfarin", "aspirin"],
        "analysis": { ... }
      }
    ]
  }
}
```

---

## Error Responses

All endpoints return error responses in this format:

```json
{
  "status": "error",
  "message": "Error description"
}
```

### Common Errors

- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

---

## Rate Limiting

Current implementation has no rate limiting. For production:
- Implement rate limiting (e.g., 100 requests/hour)
- Use API keys for authentication
- Monitor usage patterns

---

## Severity Levels

Interactions are classified into 4 severity levels:

1. **Minor**: Low clinical significance
   - Usually doesn't require intervention
   - Monitor if concerned

2. **Moderate**: Moderate clinical significance
   - May require monitoring
   - Consider alternatives if available

3. **Major**: High clinical significance
   - Requires intervention (monitoring, dose adjustment)
   - Use combination only if benefits outweigh risks

4. **Contraindicated**: Should not be used together
   - Absolute contraindication
   - Find alternatives immediately

---

## Evidence Levels

- **A**: Strong evidence (multiple RCTs, meta-analyses)
- **B**: Moderate evidence (cohort studies, case-control)
- **C**: Limited evidence (case reports, expert opinion)

---

## Best Practices

1. **Always provide patient context** when available
2. **Check for updates** regularly as drug databases evolve
3. **Validate results** with clinical judgment
4. **Report issues** if you find incorrect information
5. **Use HTTPS** in production
6. **Implement caching** for frequently requested data

---

## Example Usage

### Python

```python
import requests

url = "http://localhost:5000/api/check-interactions"
data = {
    "drugs": ["warfarin", "aspirin"]
}

response = requests.post(url, json=data)
result = response.json()

print(f"Found {result['data']['interactions_found']} interactions")
```

### JavaScript

```javascript
const url = 'http://localhost:5000/api/check-interactions';
const data = {
  drugs: ['warfarin', 'aspirin']
};

fetch(url, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(result => {
    console.log(`Found ${result.data.interactions_found} interactions`);
  });
```

### cURL

```bash
curl -X POST http://localhost:5000/api/check-interactions \
  -H "Content-Type: application/json" \
  -d '{"drugs": ["warfarin", "aspirin"]}'
```

---

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/yourusername/drug-interaction-checker/issues
- Email: support@example.com

---

## Version History

- **v1.0.0** (2024): Initial release
  - Basic interaction checking
  - Drug search
  - Alternative recommendations
  - Visualization support
