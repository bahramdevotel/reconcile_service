# Transaction Reconciliation API

AI-powered transaction matching service using semantic similarity and multi-factor scoring to match transactions against invoice records.

## Features

- **Semantic Matching**: Uses SentenceTransformer embeddings for intelligent contact/seller name matching
- **Multi-Factor Scoring**: Combines amount, date, and contact similarity with configurable weights
- **Flexible Date Scoring**: Supports linear and exponential decay methods for date matching
- **Configurable Thresholds**: Adjust similarity thresholds and number of top matches
- **PostgreSQL Backend**: Efficient storage with embedded vectors for fast similarity search
- **FastAPI Framework**: High-performance async API with automatic documentation

## Tech Stack

- **FastAPI** - Modern web framework
- **PostgreSQL** - Database with array support for embeddings
- **SentenceTransformers** - Semantic text embeddings
- **SQLAlchemy** - Database ORM
- **Pandas & NumPy** - Data processing
- **Pydantic** - Data validation

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd reconcile_service
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Database Schema

### Table: `embeded_document_invoices`

```sql
CREATE TABLE embeded_document_invoices (
    id SERIAL PRIMARY KEY,
    invoice_file_name VARCHAR(500) NOT NULL,
    seller_name VARCHAR(500),
    invoice_date TIMESTAMP,
    invoice_total_amount DOUBLE PRECISION NOT NULL,
    seller_name_clean VARCHAR(500),
    seller_name_embedding DOUBLE PRECISION[]
);
```

## API Documentation

### Reconcile Transaction

**Endpoint:** `POST /reconcile`

Match a transaction against stored invoices using AI-powered similarity scoring.

#### Request Body

```json
{
  "amount": 1100.00,
  "date": "2023-12-26",
  "contact": "Hasan SARI",
  "top_n": 3,
  "threshold": 0.8,
  "factors": ["amount", "date", "contact"],
  "weights": {
    "amount": 0.90,
    "date": 0.05,
    "contact": 0.05
  },
  "date_method": "exponential"
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `amount` | float | Yes | - | Transaction amount to match |
| `date` | string | Yes | - | Transaction date (ISO format: YYYY-MM-DD) |
| `contact` | string | No | null | Contact/seller name to match |
| `top_n` | integer | No | 3 | Number of top matches to return (1-50) |
| `threshold` | float | No | 0.8 | Minimum similarity score (0-1) |
| `factors` | array | No | ["amount", "date", "contact"] | Factors to consider in matching |
| `weights` | object | No | See below | Custom weights for each factor |
| `date_method` | string | No | "exponential" | Date scoring: "linear" or "exponential" |

**Default Weights:**
```json
{
  "amount": 0.90,
  "date": 0.05,
  "contact": 0.05
}
```

#### Response

```json
{
  "matches": [
    {
      "score": 1.0,
      "input": {
        "amount": 1100.0,
        "date": "2023-12-26",
        "contact": "Hasan SARI"
      },
      "invoice": {
        "id": 1,
        "invoice_file_name": "001c5027-6b4b-477a-bd26-67e47593a9a2.pdf",
        "seller_name": "Hasan SARI",
        "invoice_date": "2023-12-26T00:00:00",
        "invoice_total_amount": 1100.0,
        "seller_name_clean": "Hasan SARI"
      }
    }
  ],
  "total_matches": 1,
  "total_invoices": 628,
  "request_params": {
    "threshold": 0.8,
    "top_n": 3,
    "factors": ["amount", "date", "contact"],
    "weights": {
      "amount": 0.9,
      "date": 0.05,
      "contact": 0.05
    },
    "date_method": "exponential",
    "input": {
      "amount": 1100.0,
      "date": "2023-12-26",
      "contact": "Hasan SARI"
    }
  }
}
```

## Usage Examples

### Example 1: Basic Match

```bash
curl -X POST "http://localhost:8000/reconcile" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1100.00,
    "date": "2023-12-26",
    "contact": "Hasan SARI"
  }'
```

### Example 2: Amount-Only Matching

```bash
curl -X POST "http://localhost:8000/reconcile" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1100.00,
    "date": "2023-12-26",
    "factors": ["amount"],
    "weights": {"amount": 1.0},
    "threshold": 0.9
  }'
```

### Example 3: Custom Weights

```bash
curl -X POST "http://localhost:8000/reconcile" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1100.00,
    "date": "2023-12-26",
    "contact": "Hasan SARI",
    "weights": {
      "amount": 0.7,
      "date": 0.2,
      "contact": 0.1
    },
    "date_method": "linear"
  }'
```

### Example 4: Python Client

```python
import requests

response = requests.post(
    "http://localhost:8000/reconcile",
    json={
        "amount": 1100.00,
        "date": "2023-12-26",
        "contact": "Hasan SARI",
        "top_n": 5,
        "threshold": 0.7
    }
)

data = response.json()
for match in data["matches"]:
    print(f"Score: {match['score']:.2f} - {match['invoice']['invoice_file_name']}")
```

## Matching Algorithm

The service calculates similarity using three factors:

### 1. Amount Similarity
```
score = 1 - |invoice_amount - input_amount| / max(invoice_amount, input_amount)
```

### 2. Date Similarity

**Linear Method:**
```
score = max(0, 1 - days_difference / 60)
```

**Exponential Method:**
```
score = e^(-0.01 * days_difference)
```

### 3. Contact Similarity

Uses cosine similarity between SentenceTransformer embeddings:
```
score = cosine_similarity(input_embedding, seller_embedding)
```

### Final Score
```
final_score = (amount_score * weight_amount + 
               date_score * weight_date + 
               contact_score * weight_contact) / total_weight
```

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
reconcile_service/
├── main.py                      # FastAPI application
├── requirements.txt             # Python dependencies
├── docker-compose.yml          # PostgreSQL container
├── .env                        # Configuration
├── models/
│   ├── __init__.py
│   ├── document_invoice.py     # Database model
│   └── schemas.py              # Request/response models
├── settings/
│   ├── __init__.py
│   └── config.py               # Configuration loader
└── utils/
    ├── __init__.py
    ├── model_loader.py         # ML model loader
    └── matching.py             # Matching algorithms
```

## Performance

- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Average Response Time**: ~100-200ms for 600 invoices
- **Memory Usage**: ~500MB with model loaded
- **Database**: PostgreSQL with connection pooling (10-30 connections)

## License

See LICENSE file for details.

## Support

For issues and questions, please open an issue in the repository.
