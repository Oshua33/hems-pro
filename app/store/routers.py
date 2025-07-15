from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.users.auth import get_current_user
from datetime import datetime
from app.users import schemas
from app.store import models as store_models
from app.store import schemas as store_schemas
from app.users.models import User  # assuming your user model is here
from app.bar import models as bar_models
from app.store.models import StoreIssue, StoreIssueItem, StoreStockEntry
from app.store.schemas import IssueCreate, IssueDisplay



from sqlalchemy import func, desc
from app.store import models as store_models


router = APIRouter()


@router.post("/categories", response_model=store_schemas.StoreCategoryDisplay)
def create_category(category: store_schemas.StoreCategoryCreate, db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
):
    existing = db.query(store_models.StoreCategory).filter_by(name=category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    new_cat = store_models.StoreCategory(**category.dict())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


@router.get("/categories", response_model=list[store_schemas.StoreCategoryDisplay])
def list_categories(db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
):
    return db.query(store_models.StoreCategory).all()




# ----------------------------
# 1. CREATE STORE ITEM
# ----------------------------

@router.post("/items", response_model=store_schemas.StoreItemDisplay)
def create_item(item: store_schemas.StoreItemCreate, db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
    ):
    existing = db.query(store_models.StoreItem).filter_by(name=item.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item already exists")
    new_item = store_models.StoreItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/items", response_model=list[store_schemas.StoreItemDisplay])
def list_items(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
):
    query = db.query(store_models.StoreItem)
    if category:
        query = query.filter(store_models.StoreItem.category == category)
    return query.order_by(store_models.StoreItem.name).all()


# ----------------------------
# 2. RECORD STOCK ENTRY (Purchase)
# ----------------------------

@router.post("/purchases", response_model=store_schemas.StoreStockEntryDisplay)
def record_stock_entry(entry: store_schemas.StoreStockEntryCreate, db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
):
    item = db.query(store_models.StoreItem).filter_by(id=entry.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # ✅ Calculate total amount
    total = (entry.quantity * entry.unit_price) if entry.unit_price else None

    stock_entry = store_models.StoreStockEntry(
        **entry.dict(),
        total_amount=total
    )
    db.add(stock_entry)
    db.commit()
    db.refresh(stock_entry)
    return stock_entry


@router.get("/entries", response_model=list[store_schemas.StoreStockEntryDisplay])
def list_stock_entries(db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
    ):
    return db.query(store_models.StoreStockEntry).order_by(store_models.StoreStockEntry.purchase_date.desc()).all()


# ----------------------------
# 3. ISSUE ITEMS TO BAR OR RESTAURANT
# ----------------------------

from app.bar.models import BarItem

@router.post("/issues", response_model=IssueDisplay)
def create_issue(
    issue_data: IssueCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
):
    issue = StoreIssue(
        issue_to=issue_data.issue_to,
        issued_to_id=issue_data.issued_to_id,
        issued_by_id=current_user.id,  # ✅ Set issued_by_id here
        issue_date=issue_data.issue_date or datetime.utcnow(),
    )
    db.add(issue)
    db.flush()  # get issue.id

    for item_data in issue_data.issue_items:
        item = StoreIssueItem(
            issue_id=issue.id,
            item_id=item_data.item_id,
            quantity=item_data.quantity,
        )
        db.add(item)

        if issue_data.issue_to.lower() == "bar":
            bar_item = db.query(BarItem).filter_by(
                bar_id=issue_data.issued_to_id,
                item_id=item_data.item_id
            ).first()

            if bar_item:
                bar_item.quantity += item_data.quantity
            else:
                latest_price = (
                    db.query(StoreStockEntry.unit_price)
                    .filter(StoreStockEntry.item_id == item_data.item_id)
                    .order_by(StoreStockEntry.id.desc())
                    .first()
                )
                bar_item = BarItem(
                    bar_id=issue_data.issued_to_id,
                    item_id=item_data.item_id,
                    quantity=item_data.quantity,
                    selling_price=latest_price[0] if latest_price else 0
                )
                db.add(bar_item)

    db.commit()
    db.refresh(issue)
    return issue


@router.get("/issues", response_model=list[store_schemas.IssueDisplay])
def list_issues(db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
    ):
    return db.query(store_models.StoreIssue).order_by(store_models.StoreIssue.issue_date.desc()).all()


@router.get("/balance", response_model=list[dict])
def get_store_balances(db: Session = Depends(get_db),
    current_user: schemas.UserDisplaySchema = Depends(get_current_user),
):
    

    # Total received per item
    received = db.query(
        store_models.StoreItem.id.label("item_id"),
        store_models.StoreItem.name,
        store_models.StoreItem.unit,
        func.sum(store_models.StoreStockEntry.quantity).label("total_received")
    ).join(store_models.StoreStockEntry).group_by(store_models.StoreItem.id).subquery()

    # Total issued per item
    issued = db.query(
        store_models.StoreIssueItem.item_id,
        func.sum(store_models.StoreIssueItem.quantity).label("total_issued")
    ).group_by(store_models.StoreIssueItem.item_id).subquery()

    # Join both
    result = db.query(
        received.c.item_id,
        received.c.name,
        received.c.unit,
        received.c.total_received,
        func.coalesce(issued.c.total_issued, 0).label("total_issued"),
        (received.c.total_received - func.coalesce(issued.c.total_issued, 0)).label("balance")
    ).outerjoin(issued, received.c.item_id == issued.c.item_id).all()

    response = []
    for r in result:
        # Get last stock entry for item
        latest_entry = db.query(store_models.StoreStockEntry).filter_by(item_id=r.item_id)\
            .order_by(store_models.StoreStockEntry.purchase_date.desc()).first()

        unit_price = latest_entry.unit_price if latest_entry else None
        total_amount = unit_price * r.balance if unit_price is not None else None

        response.append({
            "item_id": r.item_id,
            "item_name": r.name,
            "unit": r.unit,
            "total_received": r.total_received,
            "total_issued": r.total_issued,
            "balance": r.balance,
            "last_unit_price": unit_price,
            "balance_total_amount": round(total_amount, 2) if total_amount else None
        })

    return response
