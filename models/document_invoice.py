from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class DocumentInvoice(Base):
    __tablename__ = "embeded_document_invoices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_file_name = Column(String(500), nullable=False)
    seller_name = Column(String(500), nullable=True)
    invoice_date = Column(DateTime, nullable=True)
    invoice_total_amount = Column(Float, nullable=False)
    
    seller_name_clean = Column(String(500), nullable=True)
    seller_name_embedding = Column(ARRAY(Float), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "invoice_file_name": self.invoice_file_name,
            "seller_name": self.seller_name,
            "invoice_date": self.invoice_date.isoformat() if self.invoice_date else None,
            "invoice_total_amount": self.invoice_total_amount,
            "seller_name_clean": self.seller_name_clean
        }

