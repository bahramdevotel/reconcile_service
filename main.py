from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn

from models import ReconcileRequest, ReconcileResponse
from utils import db_manager, model_loader, find_best_matches
from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("Starting Transaction Reconciliation API")
    print("=" * 60)
    
    model_loader.initialize()
    db_manager.initialize()
    db_manager.create_tables()
    
    print("=" * 60)
    print("API ready to accept requests!")
    print("=" * 60)
    
    yield
    
    print("Shutting down...")


app = FastAPI(
    title="Transaction Reconciliation API",
    version="2.0.0",
    description="AI-powered transaction matching service with PostgreSQL backend",
    lifespan=lifespan
)


@app.post("/reconcile", response_model=ReconcileResponse)
async def reconcile_transaction(request: ReconcileRequest):
    if not model_loader.is_ready():
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    
    try:
        invoices = db_manager.get_all_invoices()
        total_invoices = len(invoices)
        
        if total_invoices == 0:
            return {
                "matches": [],
                "total_matches": 0,
                "total_invoices": 0,
                "request_params": {
                    "threshold": request.threshold,
                    "top_n": request.top_n,
                    "factors": request.factors,
                    "weights": request.weights or {
                        "amount": 0.90,
                        "date": 0.05,
                        "contact": 0.05
                    },
                    "date_method": request.date_method,
                    "input": {
                        "amount": request.amount,
                        "date": request.date,
                        "contact": request.contact
                    }
                }
            }
        
        weights = request.weights if request.weights else {
            "amount": 0.90,
            "date": 0.05,
            "contact": 0.05
        }
        
        input_data = {
            "amount": request.amount,
            "date": request.date,
            "contact": request.contact
        }
        
        model = model_loader.get_model()
        
        matches = find_best_matches(
            input_data=input_data,
            invoices=invoices,
            model=model,
            top_n=request.top_n,
            threshold=request.threshold,
            factors=request.factors,
            weights=weights,
            date_method=request.date_method
        )
        
        response = {
            "matches": matches,
            "total_matches": len(matches),
            "total_invoices": total_invoices,
            "request_params": {
                "threshold": request.threshold,
                "top_n": request.top_n,
                "factors": request.factors,
                "weights": weights,
                "date_method": request.date_method,
                "input": input_data
            }
        }
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT
    )
