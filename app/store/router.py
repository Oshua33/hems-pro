from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.database import get_db
from app.users.auth import get_current_user
from app.users.models import User
from app.users import schemas as user_schemas
from app.store import models as store_models
from app.store import schemas as store_schemas
from app.bar.models import BarInventory  
from app.store.models import StoreIssue, StoreIssueItem, StoreStockEntry, StoreCategory
from app.vendor import models as vendor_models
from app.store.models import StoreInventoryAdjustment
from app.store.schemas import  StoreInventoryAdjustmentCreate, StoreInventoryAdjustmentDisplay
from sqlalchemy.orm import joinedload
from fastapi import File, UploadFile, Form
import os

from fastapi.responses import JSONResponse
import shutil



from sqlalchemy.orm import selectinload

router = APIRouter()

# ----------------------------
# CATEGORY ROUTES
# ----------------------------

@router.post("/categories", response_model=store_schemas.StoreCategoryDisplay)
def create_category(
    category: store_schemas.StoreCategoryCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
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
def list_categories(
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    return db.query(store_models.StoreCategory).all()


@router.put("/categories/{category_id}", response_model=store_schemas.StoreCategoryDisplay)
def update_category(
    category_id: int,
    update_data: store_schemas.StoreCategoryCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    category = db.query(store_models.StoreCategory).filter_by(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    existing = db.query(store_models.StoreCategory).filter(
        store_models.StoreCategory.name == update_data.name,
        store_models.StoreCategory.id != category_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")

    category.name = update_data.name
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    category = db.query(store_models.StoreCategory).filter_by(id=category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"detail": "Category deleted successfully"}



# ----------------------------
# ITEM ROUTES
# ----------------------------

@router.post("/items", response_model=store_schemas.StoreItemDisplay)
def create_item(
    item: store_schemas.StoreItemCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
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
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    query = db.query(store_models.StoreItem)
    if category:
        query = query.join(store_models.StoreItem.category).filter(StoreCategory.name == category)
    return query.order_by(store_models.StoreItem.name).all()




@router.put("/items/{item_id}", response_model=store_schemas.StoreItemDisplay)
def update_item(
    item_id: int,
    update_data: store_schemas.StoreItemCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    item = db.query(store_models.StoreItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    existing = db.query(store_models.StoreItem).filter(
        store_models.StoreItem.name == update_data.name,
        store_models.StoreItem.id != item_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Item name already exists")

    for field, value in update_data.dict().items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    item = db.query(store_models.StoreItem).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"detail": "Item deleted successfully"}


# ----------------------------
# PURCHASE / STOCK ENTRY
# ----------------------------




@router.post("/purchases", response_model=store_schemas.PurchaseCreateList)
async def receive_inventory(
    entry: store_schemas.StoreStockEntryCreate = Depends(),
    attachment: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    # Check if item exists
    item = db.query(store_models.StoreItem).filter_by(id=entry.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Calculate total amount
    total = (entry.quantity * entry.unit_price) if entry.unit_price else None

    # Set attachment path (default is None)
    attachment_path = None

    # Save attachment if provided
    if attachment:
        #upload_dir = "attachments/store_invoices"
        upload_dir = "uploads/store_invoices"

        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{attachment.filename}"
        file_location = os.path.join(upload_dir, filename)

        with open(file_location, "wb") as f:
            f.write(await attachment.read())

        # Store relative path or public URL if needed
        attachment_path = file_location

    # Create stock entry
    stock_entry = store_models.StoreStockEntry(
        item_id=entry.item_id,
        item_name=entry.item_name,
        quantity=entry.quantity,
        original_quantity=entry.quantity,
        unit_price=entry.unit_price,
        total_amount=total,
        vendor_id=entry.vendor_id,
        purchase_date=entry.purchase_date,
        created_by=current_user.username,
        attachment=attachment_path,
    )

    db.add(stock_entry)
    db.commit()
    db.refresh(stock_entry)

    # Load related vendor for full response
    stock_entry = db.query(store_models.StoreStockEntry)\
        .options(selectinload(store_models.StoreStockEntry.vendor))\
        .get(stock_entry.id)

    return stock_entry

@router.get("/purchases", response_model=List[store_schemas.StoreStockEntryDisplay])
def list_purchases(
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    purchases = (
        db.query(store_models.StoreStockEntry)
        .options(
            selectinload(store_models.StoreStockEntry.vendor),
            selectinload(store_models.StoreStockEntry.item),
        )
        .order_by(store_models.StoreStockEntry.created_at.desc())
        .all()
    )

    results = []
    for purchase in purchases:
        # Generate attachment URL if attachment exists
        attachment_url = (
            f"/files/{os.path.relpath(purchase.attachment, 'uploads').replace(os.sep, '/')}"
            if purchase.attachment else None
        )

        results.append({
            "id": purchase.id,
            "item_id": purchase.item_id,
            "item_name": purchase.item.name if purchase.item else "",
            "quantity": purchase.quantity,
            "unit_price": purchase.unit_price,
            "total_amount": purchase.total_amount,
            "vendor_id": purchase.vendor_id,
            "vendor_name": purchase.vendor.business_name if purchase.vendor else "",
            "purchase_date": purchase.purchase_date,
            "created_by": purchase.created_by,
            "created_at": purchase.created_at,
            "attachment_url": attachment_url,
        })

    return results



@router.put("/purchases/{entry_id}", response_model=store_schemas.UpdatePurchase)
def update_purchase(
    entry_id: int,
    update_data: store_schemas.StoreStockEntryCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    entry = db.query(store_models.StoreStockEntry).filter_by(id=entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Purchase entry not found")

    # Check that the item exists
    item = db.query(store_models.StoreItem).filter_by(id=update_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    total = (update_data.quantity * update_data.unit_price) if update_data.unit_price else None

    # Exclude 'created_by' from update_data
    update_fields = update_data.dict(exclude={"created_by"})

    for field, value in update_fields.items():
        setattr(entry, field, value)

    entry.total_amount = total
    entry.created_by = current_user.username  # Ensure created_by is updated with current user

    db.commit()
    db.refresh(entry)

    # Load related vendor (if needed for the frontend like in POST route)
    entry = db.query(store_models.StoreStockEntry)\
        .options(selectinload(store_models.StoreStockEntry.vendor))\
        .get(entry.id)

    return entry



@router.delete("/purchases/{entry_id}")
def delete_purchase(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    entry = db.query(store_models.StoreStockEntry).filter_by(id=entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Purchase entry not found")

    db.delete(entry)
    db.commit()
    return {"detail": "Purchase entry deleted successfully"}



# ----------------------------
# ISSUE TO BAR (Update BarInventory)
# ----------------------------

@router.post("/issues", response_model=store_schemas.IssueDisplay)
def supply_to_bars(
    issue_data: store_schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    issue = StoreIssue(
        issue_to=issue_data.issue_to,
        issued_to_id=issue_data.issued_to_id,
        issued_by_id=current_user.id,
        issue_date=issue_data.issue_date or datetime.utcnow(),
    )
    db.add(issue)
    db.flush()

    for item_data in issue_data.issue_items:
        # 1. Check available stock
        total_available_stock = db.query(func.sum(StoreStockEntry.quantity))\
            .filter(StoreStockEntry.item_id == item_data.item_id)\
            .scalar() or 0

        if total_available_stock < item_data.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough inventory for item {item_data.item_id}")

        # 2. Create the issue item record
        issue_item = StoreIssueItem(
            issue_id=issue.id,
            item_id=item_data.item_id,
            quantity=item_data.quantity,
        )
        db.add(issue_item)

        # 3. Deduct from store using FIFO (oldest entries first)
        remaining_quantity = item_data.quantity
        stock_entries = db.query(StoreStockEntry)\
            .filter(StoreStockEntry.item_id == item_data.item_id, StoreStockEntry.quantity > 0)\
            .order_by(StoreStockEntry.purchase_date.asc())\
            .all()

        for stock_entry in stock_entries:
            if remaining_quantity <= 0:
                break

            if stock_entry.quantity >= remaining_quantity:
                stock_entry.quantity -= remaining_quantity
                remaining_quantity = 0
            else:
                remaining_quantity -= stock_entry.quantity
                stock_entry.quantity = 0

        # ✅ All quantity has been successfully deducted at this point

        # 4. Add or update BarInventory
        if issue_data.issue_to.lower() == "bar":
            bar_inventory = db.query(BarInventory).filter_by(
                bar_id=issue_data.issued_to_id,
                item_id=item_data.item_id
            ).first()

            if bar_inventory:
                bar_inventory.quantity += item_data.quantity
            else:
                latest_stock = db.query(StoreStockEntry)\
                    .filter(StoreStockEntry.item_id == item_data.item_id)\
                    .order_by(StoreStockEntry.id.desc())\
                    .first()

                bar_inventory = BarInventory(
                    bar_id=issue_data.issued_to_id,
                    item_id=item_data.item_id,
                    quantity=item_data.quantity,
                    selling_price=latest_stock.unit_price if latest_stock else 0
                )
                db.add(bar_inventory)

    db.commit()
    db.refresh(issue)
    return issue


@router.get("/issues", response_model=list[store_schemas.IssueDisplay])
def list_issues(
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    return db.query(StoreIssue).order_by(StoreIssue.issue_date.desc()).all()



@router.put("/issues/{issue_id}", response_model=store_schemas.IssueDisplay)
def update_issue(
    issue_id: int,
    update_data: store_schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    issue = db.query(StoreIssue).filter_by(id=issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Delete old issue items
    db.query(StoreIssueItem).filter_by(issue_id=issue_id).delete()

    # Update metadata
    issue.issue_to = update_data.issue_to
    issue.issued_to_id = update_data.issued_to_id
    issue.issue_date = update_data.issue_date or datetime.utcnow()
    issue.issued_by_id = current_user.id

    for item_data in update_data.issue_items:
        new_issue_item = StoreIssueItem(
            issue_id=issue_id,
            item_id=item_data.item_id,
            quantity=item_data.quantity,
        )
        db.add(new_issue_item)

    db.commit()
    db.refresh(issue)
    return issue


@router.delete("/issues/{issue_id}")
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    issue = db.query(StoreIssue).filter_by(id=issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.query(StoreIssueItem).filter_by(issue_id=issue.id).delete()
    db.delete(issue)
    db.commit()
    return {"detail": "Issue deleted successfully"}


# ----------------------------
# STORE BALANCE REPORT
# ----------------------------

@router.get("/balance-stock", response_model=list[dict])
def get_store_balances(
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    
    # Fetch total adjustments per item
    adjustments = db.query(
        StoreInventoryAdjustment.item_id,
        func.sum(StoreInventoryAdjustment.quantity_adjusted).label("total_adjusted")
    ).group_by(StoreInventoryAdjustment.item_id).all()

    adjustment_map = {a.item_id: a.total_adjusted for a in adjustments}

    # Group by item: total received and current balance
    received_data = db.query(
        store_models.StoreItem.id.label("item_id"),
        store_models.StoreItem.name,
        store_models.StoreItem.unit,
        func.sum(StoreStockEntry.original_quantity).label("total_received"),
        func.sum(StoreStockEntry.quantity).label("balance")
    ).join(StoreStockEntry).group_by(store_models.StoreItem.id).all()

    response = []
    for item in received_data:
        latest_entry = db.query(StoreStockEntry)\
            .filter_by(item_id=item.item_id)\
            .order_by(StoreStockEntry.purchase_date.desc())\
            .first()

        unit_price = latest_entry.unit_price if latest_entry else None
        total_issued = item.total_received - item.balance
        total_amount = unit_price * item.balance if unit_price is not None else None

        adjusted = adjustment_map.get(item.item_id, 0)
        total_issued = item.total_received - item.balance - adjusted

        response.append({
            "item_id": item.item_id,
            "item_name": item.name,
            "unit": item.unit,
            "total_received": item.total_received,
            "total_issued": total_issued,
            "total_adjusted": adjusted,
            "balance": item.balance,
            "last_unit_price": unit_price,
            "balance_total_amount": round(total_amount, 2) if total_amount else None
        })


    return response


@router.post("/adjust", response_model=StoreInventoryAdjustmentDisplay)
def adjust_store_inventory(
    adjustment_data: StoreInventoryAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can adjust inventory.")

    # Get latest stock entry
    latest_entry = db.query(StoreStockEntry).filter(
        StoreStockEntry.item_id == adjustment_data.item_id,
        StoreStockEntry.quantity > 0
    ).order_by(StoreStockEntry.purchase_date.desc()).first()

    if not latest_entry:
        raise HTTPException(status_code=404, detail="Item not found or out of stock.")

    if adjustment_data.quantity_adjusted > latest_entry.quantity:
        raise HTTPException(status_code=400, detail="Adjustment exceeds available stock.")

    # Deduct quantity
    latest_entry.quantity -= adjustment_data.quantity_adjusted
    db.add(latest_entry)

    # Log adjustment
    adjustment = StoreInventoryAdjustment(
        item_id=adjustment_data.item_id,
        quantity_adjusted=adjustment_data.quantity_adjusted,
        reason=adjustment_data.reason,
        adjusted_by=current_user.username
    )
    db.add(adjustment)
    db.commit()
    db.refresh(adjustment)

    return adjustment


@router.get("/adjustments", response_model=List[StoreInventoryAdjustmentDisplay])
def list_store_inventory_adjustments(
    item_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(StoreInventoryAdjustment)

    if item_id:
        query = query.filter(StoreInventoryAdjustment.item_id == item_id)
    if start_date:
        query = query.filter(StoreInventoryAdjustment.adjusted_at >= start_date)
    if end_date:
        query = query.filter(StoreInventoryAdjustment.adjusted_at <= end_date)

    return query.order_by(StoreInventoryAdjustment.adjusted_at.desc()).all()


@router.delete("/adjustments/{adjustment_id}")
def delete_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete adjustments.")

    adjustment = db.query(StoreInventoryAdjustment)\
        .options(joinedload(StoreInventoryAdjustment.item))\
        .filter(StoreInventoryAdjustment.id == adjustment_id).first()

    if not adjustment:
        raise HTTPException(status_code=404, detail="Adjustment not found.")

    # Restore quantity to stock
    stock_entry = db.query(StoreStockEntry).filter(
        StoreStockEntry.item_id == adjustment.item_id
    ).order_by(StoreStockEntry.purchase_date.desc()).first()

    if not stock_entry:
        raise HTTPException(status_code=404, detail="No stock entry found to revert the quantity.")

    stock_entry.quantity += adjustment.quantity_adjusted
    db.add(stock_entry)

    db.delete(adjustment)
    db.commit()

    return {
        "message": "Adjustment deleted successfully.",
        "restored_quantity": adjustment.quantity_adjusted,
        "item_id": adjustment.item_id
    }