import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.document_invoice import DocumentInvoice, Base
from utils.model_loader import model_loader
from settings import settings


def insert_document_invoices_to_database(csv_path: str = "document_invoices.csv"):
    print("=" * 60)
    print("Document Invoices CSV to Database Insertion")
    print("=" * 60)
    
    print("\n1. Initializing database connection...")
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    print("   Dropping existing document_invoices table if exists...")
    Base.metadata.drop_all(engine)
    print("   Creating fresh document_invoices table...")
    Base.metadata.create_all(engine)
    
    print("\n2. Loading ML model for embeddings...")
    model_loader.initialize()
    model = model_loader.get_model()
    
    print(f"\n3. Loading CSV file: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"   Found {len(df)} invoices")
    print(f"   Columns: {df.columns.tolist()}")
    
    print("\n4. Preprocessing data...")
    # Convert invoice_date to datetime
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')
    df['invoice_total_amount'] = pd.to_numeric(df['invoice_total_amount'], errors='coerce').fillna(0)
    
    # Clean seller_name for embedding
    df['seller_name_clean'] = df['seller_name'].fillna("").astype(str).str.strip()
    
    print("\n5. Generating embeddings for seller_name (contact)...")
    print("   This may take a few minutes...")
    seller_texts = df['seller_name_clean'].tolist()
    embeddings = model.encode(seller_texts, batch_size=128, show_progress_bar=True)
    
    print("\n6. Inserting document invoices into database...")
    session: Session = SessionLocal()
    
    try:
        inserted_count = 0
        batch_size = 1000
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_embeddings = embeddings[i:i+batch_size]
            
            for idx, row in batch_df.iterrows():
                doc_invoice = DocumentInvoice(
                    invoice_file_name=str(row['invoice_file_name']),
                    seller_name=row['seller_name'] if pd.notna(row['seller_name']) else None,
                    invoice_date=row['invoice_date'].to_pydatetime() if pd.notna(row['invoice_date']) else None,
                    invoice_total_amount=float(row['invoice_total_amount']),
                    seller_name_clean=row['seller_name_clean'],
                    seller_name_embedding=batch_embeddings[idx - i].tolist()
                )
                session.add(doc_invoice)
                inserted_count += 1
            
            session.commit()
            print(f"   Inserted {inserted_count}/{len(df)} invoices...")
        
        print(f"\n✅ Successfully inserted {inserted_count} invoices!")
        
        # Show some statistics
        print("\n" + "=" * 60)
        print("Database Statistics:")
        print("=" * 60)
        print(f"Total invoices: {inserted_count}")
        print(f"Unique sellers: {df['seller_name'].nunique()}")
        print(f"Date range: {df['invoice_date'].min()} to {df['invoice_date'].max()}")
        print(f"Amount range: ${df['invoice_total_amount'].min():.2f} to ${df['invoice_total_amount'].max():.2f}")
        print(f"Total amount: ${df['invoice_total_amount'].sum():.2f}")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error during insertion: {e}")
        raise
    finally:
        session.close()
    
    print("\n" + "=" * 60)
    print("Insertion completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "document_invoices.csv"
    insert_document_invoices_to_database(csv_file)
