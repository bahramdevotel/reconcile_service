from sqlalchemy import Column, String, Float, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_date = Column(DateTime, nullable=False)
    payee = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    reference = Column(String(500), nullable=True)
    payment_id = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    invoice_id = Column(String(500), nullable=False)
    tenant_id = Column(String(500), nullable=False)
    transaction_type = Column(String(100), nullable=False)
    
    payee_clean = Column(String(500), nullable=True)
    payee_embedding = Column(ARRAY(Float), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "payee": self.payee,
            "description": self.description,
            "reference": self.reference,
            "payment_id": self.payment_id,
            "amount": self.amount,
            "invoice_id": self.invoice_id,
            "tenant_id": self.tenant_id,
            "transaction_type": self.transaction_type,
            "payee_clean": self.payee_clean
        }
