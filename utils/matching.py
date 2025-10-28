import numpy as np
import pandas as pd
from sentence_transformers import util
from typing import List, Dict, Any, Optional
from datetime import datetime


def date_score_linear(date_diff, max_days=60):
    return np.maximum(0, 1 - (date_diff / max_days))


def date_score_exponential(date_diff, decay_rate=0.01):
    return np.exp(-decay_rate * date_diff)


def calculate_similarity_vectorized(
    input_data: Dict[str, Any],
    invoices: List,
    factors: List[str],
    weights: Dict[str, float],
    model,
    contact_embedding = None,
    date_method: str = "linear"
) -> pd.Series:
    if not invoices:
        return pd.Series([])
    
    df_data = []
    for inv in invoices:
        df_data.append({
            'amount': inv.amount,
            'transaction_date': inv.transaction_date,
            'payee_embedding': inv.payee_embedding,
            'index': inv.id
        })
    
    inv_df = pd.DataFrame(df_data)
    inv_df.set_index('index', inplace=True)
    
    scores = pd.DataFrame(index=inv_df.index)
    
    if "amount" in factors:
        input_amount = input_data["amount"]
        diff = np.abs(inv_df["amount"] - input_amount)
        max_vals = np.maximum(inv_df["amount"], input_amount)
        scores["amount"] = np.where(max_vals == 0, 0, 1 - diff / max_vals)

    if "date" in factors:
        input_date = input_data["date"]
        if isinstance(input_date, str):
            input_date = pd.to_datetime(input_date, errors='coerce')
        elif isinstance(input_date, datetime):
            input_date = pd.Timestamp(input_date)
        
        inv_df['transaction_date'] = pd.to_datetime(inv_df['transaction_date'])
        date_diff = np.abs((inv_df["transaction_date"] - input_date).dt.days)
        
        if date_method == "linear":
            scores["date"] = date_score_linear(date_diff)
        elif date_method == "exponential":
            scores["date"] = date_score_exponential(date_diff)
        else:
            scores["date"] = date_score_linear(date_diff)

    if "contact" in factors:
        input_contact = str(input_data.get("contact", "")).strip()
        if input_contact:
            if contact_embedding is None:
                contact_embedding = model.encode(input_contact, convert_to_tensor=False)
            
            if hasattr(contact_embedding, 'cpu'):
                contact_embedding = contact_embedding.cpu().numpy()
            
            contact_scores = []
            for idx, row in inv_df.iterrows():
                if row['payee_embedding'] is not None and len(row['payee_embedding']) > 0:
                    payee_emb = np.array(row['payee_embedding'], dtype=np.float32)
                    contact_emb_norm = contact_embedding / np.linalg.norm(contact_embedding)
                    payee_emb_norm = payee_emb / np.linalg.norm(payee_emb)
                    cos_sim = np.dot(contact_emb_norm, payee_emb_norm)
                    contact_scores.append(float(cos_sim))
                else:
                    contact_scores.append(0.0)
            
            scores["contact"] = contact_scores
        else:
            scores["contact"] = np.zeros(len(inv_df))

    total_score = sum(scores[f] * weights.get(f, 0) for f in factors if f in scores.columns)
    total_weight = sum(weights.get(f, 0) for f in factors if f in scores.columns)
    
    return total_score / total_weight if total_weight > 0 else pd.Series(np.zeros(len(inv_df)), index=inv_df.index)


def find_best_matches(
    input_data: Dict[str, Any],
    invoices: List,
    model,
    top_n: int = 3,
    threshold: float = 0.8,
    factors: Optional[List[str]] = None,
    weights: Optional[Dict[str, float]] = None,
    date_method: str = "exponential"
) -> List[Dict[str, Any]]:
    if not invoices:
        return []
    
    if factors is None:
        factors = ["amount", "date", "contact"]
    if weights is None:
        weights = {"amount": 0.90, "date": 0.05, "contact": 0.05}

    contact_embedding = None
    if "contact" in factors:
        input_contact = str(input_data.get("contact", "")).strip()
        if input_contact:
            contact_embedding = model.encode(input_contact, convert_to_tensor=False)

    scores = calculate_similarity_vectorized(
        input_data, invoices, factors, weights, model, contact_embedding, date_method
    )
    
    if len(scores) == 0:
        return []

    top_indices = scores.nlargest(min(top_n, len(scores))).index.tolist()

    matches = []
    
    inv_map = {inv.id: inv for inv in invoices}
    
    for idx in top_indices:
        score = scores.loc[idx]
        
        inv = inv_map.get(idx)
        if not inv:
            continue

        match_info = {
            "score": float(score),
            "input": input_data,
            "invoice": inv.to_dict(),
        }

        matches.append(match_info)

    matches = [match for match in matches if match['score'] >= threshold]

    return matches
