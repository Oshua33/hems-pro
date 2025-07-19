from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from . import models, schemas
from app.bar.models import BarSale

router = APIRouter()

@router.post("/", response_model=schemas.BarPaymentDisplay)
def create_bar_payment(payment: schemas.BarPaymentCreate, db: Session = Depends(get_db)):
    # Validate sale exists
    sale = db.query(BarSale).filter(BarSale.id == payment.bar_sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Bar sale not found")

    db_payment = models.BarPayment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.get("/", response_model=list[schemas.BarPaymentDisplay])
def list_bar_payments(db: Session = Depends(get_db)):
    return db.query(models.BarPayment).all()


@router.put("/{payment_id}", response_model=schemas.BarPaymentDisplay)
def update_bar_payment(payment_id: int, update_data: schemas.BarPaymentUpdate, db: Session = Depends(get_db)):
    payment = db.query(models.BarPayment).filter(models.BarPayment.id == payment_id, models.BarPayment.status == "active").first()
    if not payment:
        raise HTTPException(status_code=404, detail="Active payment not found")

    if update_data.amount is not None:
        payment.amount = update_data.amount
    if update_data.payment_method is not None:
        payment.payment_method = update_data.payment_method

    db.commit()
    db.refresh(payment)
    return payment


@router.put("/{payment_id}/void", response_model=schemas.BarPaymentDisplay)
def void_bar_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(models.BarPayment).filter(models.BarPayment.id == payment_id, models.BarPayment.status == "active").first()
    if not payment:
        raise HTTPException(status_code=404, detail="Active payment not found")

    payment.status = "voided"
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/payment-status/{bar_sale_id}")
def get_payment_status(bar_sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(BarSale).filter(BarSale.id == bar_sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Bar sale not found")

    total_payment = sum(p.amount for p in sale.payments if p.status == "active")
    amount_due = sale.total_price  # or sale.amount_due if available

    if total_payment == 0:
        status = "unpaid"
    elif total_payment < amount_due:
        status = "part paid"
    else:
        status = "fully paid"

    return {
        "bar_sale_id": bar_sale_id,
        "amount_due": amount_due,
        "total_paid": total_payment,
        "payment_status": status
    }


@router.put("/{payment_id}/void", response_model=schemas.BarPaymentDisplay)
def void_bar_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(models.BarPayment).filter(
        models.BarPayment.id == payment_id,
        models.BarPayment.status == "active"
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Active payment not found")

    # Mark the payment as void
    payment.status = "voided"
    db.commit()
    db.refresh(payment)

    # Reopen the related bar sale if it was marked closed
    bar_sale = db.query(models.BarSale).filter(
        models.BarSale.id == payment.bar_sale_id
    ).first()

    if bar_sale:
        bar_sale.status = "open"
        db.commit()

    return payment
