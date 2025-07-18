from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import aliased
from typing import Optional, List
from datetime import datetime, date
from app.database import get_db
from app.users.auth import get_current_user
from app.users import schemas as user_schemas
from app.bar import models as bar_models, schemas as bar_schemas
from app.store import models as store_models
from app.bar.models import Bar, BarInventory, BarSale, BarSaleItem
from app.users.models import User
from app.bar.models import BarInventory
from typing import Optional




router = APIRouter()

# ----------------------------
# BAR
# ----------------------------

@router.post("/bars", response_model=bar_schemas.BarDisplay)
def create_bar(
    bar: bar_schemas.BarCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    existing = db.query(bar_models.Bar).filter_by(name=bar.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bar name already exists")

    new_bar = bar_models.Bar(**bar.dict())
    db.add(new_bar)
    db.commit()
    db.refresh(new_bar)
    return new_bar


@router.get("/bars", response_model=List[bar_schemas.BarDisplay])
def list_bars(
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    return db.query(bar_models.Bar).order_by(bar_models.Bar.name).all()


# ----------------------------
# BAR INVENTORY (Replace BarItem)
# ----------------------------

@router.put("/bars/{bar_id}", response_model=bar_schemas.BarDisplay)
def update_bar(
    bar_id: int,
    bar_update: bar_schemas.BarCreate,  # Same schema used in creation
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    bar = db.query(bar_models.Bar).filter_by(id=bar_id).first()
    if not bar:
        raise HTTPException(status_code=404, detail="Bar not found")

    # Check if name is being changed to an existing bar name
    existing = db.query(bar_models.Bar).filter(
        bar_models.Bar.name == bar_update.name,
        bar_models.Bar.id != bar_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bar name already exists")

    for field, value in bar_update.dict().items():
        setattr(bar, field, value)

    db.commit()
    db.refresh(bar)
    return bar




@router.get("/inventory", response_model=List[bar_schemas.BarInventorySummaryDisplay])
def list_bar_inventory(
    bar_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    # 1. Total Issued to Bar
    issued_query = db.query(
        store_models.StoreIssueItem.item_id,
        store_models.StoreIssue.issued_to_id.label("bar_id"),
        func.sum(store_models.StoreIssueItem.quantity).label("total_issued")
    ).join(
        store_models.StoreIssue, store_models.StoreIssue.id == store_models.StoreIssueItem.issue_id
    )

    if bar_id:
        issued_query = issued_query.filter(store_models.StoreIssue.issued_to_id == bar_id)

    issued_subq = issued_query.group_by(
        store_models.StoreIssueItem.item_id,
        store_models.StoreIssue.issued_to_id
    ).subquery()

    # 2. Total Sold from Bar
    bar_inventory_alias = aliased(bar_models.BarInventory)
    bar_sale_item_alias = aliased(bar_models.BarSaleItem)
    bar_sale_alias = aliased(bar_models.BarSale)

    sold_query = db.query(
        bar_inventory_alias.item_id.label("item_id"),
        bar_inventory_alias.bar_id.label("bar_id"),
        func.sum(bar_sale_item_alias.quantity).label("total_sold")
    ).join(
        bar_sale_item_alias, bar_inventory_alias.id == bar_sale_item_alias.bar_inventory_id
    ).join(
        bar_sale_alias, bar_sale_item_alias.bar_sale_id == bar_sale_alias.id  # ✅ FIXED HERE
    )

    if bar_id:
        sold_query = sold_query.filter(bar_sale_alias.bar_id == bar_id)

    sold_subq = sold_query.group_by(
        bar_inventory_alias.item_id,
        bar_inventory_alias.bar_id
    ).subquery()

    # 3. Latest Unit Price
    latest_price_subq = (
        db.query(
            store_models.StoreStockEntry.item_id,
            store_models.StoreStockEntry.unit_price
        )
        .order_by(
            store_models.StoreStockEntry.item_id,
            store_models.StoreStockEntry.purchase_date.desc()
        )
        .distinct(store_models.StoreStockEntry.item_id)
        .subquery()
    )

    # 4. Selling price
    selling_price_query = db.query(
        bar_models.BarInventory.item_id,
        bar_models.BarInventory.bar_id,
        bar_models.BarInventory.selling_price
    )

    if bar_id:
        selling_price_query = selling_price_query.filter(bar_models.BarInventory.bar_id == bar_id)

    selling_price_subq = selling_price_query.subquery()

    # 5. Final query
    query = db.query(
        store_models.StoreItem.id.label("item_id"),
        store_models.StoreItem.name.label("item_name"),
        issued_subq.c.bar_id,
        func.coalesce(issued_subq.c.total_issued, 0).label("total_issued"),
        func.coalesce(sold_subq.c.total_sold, 0).label("total_sold"),
        (
            func.coalesce(issued_subq.c.total_issued, 0) -
            func.coalesce(sold_subq.c.total_sold, 0)
        ).label("available_quantity"),
        func.coalesce(latest_price_subq.c.unit_price, 0).label("current_unit_price"),
        func.coalesce(selling_price_subq.c.selling_price, 0).label("selling_price")
    ).join(
        issued_subq, store_models.StoreItem.id == issued_subq.c.item_id
    ).outerjoin(
        sold_subq,
        (store_models.StoreItem.id == sold_subq.c.item_id) &
        (issued_subq.c.bar_id == sold_subq.c.bar_id)
    ).outerjoin(
        latest_price_subq,
        store_models.StoreItem.id == latest_price_subq.c.item_id
    ).outerjoin(
        selling_price_subq,
        (store_models.StoreItem.id == selling_price_subq.c.item_id) &
        (issued_subq.c.bar_id == selling_price_subq.c.bar_id)
    )

    results = query.all()

    return [
        {
            "item_id": r.item_id,
            "item_name": r.item_name,
            "bar_id": r.bar_id,
            "quantity": r.available_quantity,
            "current_unit_price": r.current_unit_price,
            "selling_price": r.selling_price,
        }
        for r in results if r.available_quantity > 0
    ]

@router.put("/inventory/set-price", response_model=bar_schemas.BarInventoryDisplay)
def update_selling_price(
    data: bar_schemas.BarPriceUpdate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    # Try to find existing bar_inventory record
    bar_item = db.query(bar_models.BarInventory).filter_by(
        bar_id=data.bar_id,
        item_id=data.item_id
    ).first()

    if bar_item:
        # Update existing price
        bar_item.selling_price = data.new_price
    else:
        # Create new record if not exists
        bar_item = bar_models.BarInventory(
            bar_id=data.bar_id,
            item_id=data.item_id,
            selling_price=data.new_price,
            quantity=0  # quantity is not used now, keep default
        )
        db.add(bar_item)

    db.commit()
    db.refresh(bar_item)
    return bar_item


# ----------------------------
# BAR SALES
# ----------------------------

@router.post("/sales", response_model=bar_schemas.BarSaleDisplay)
def create_bar_sale(
    sale_data: bar_schemas.BarSaleCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    bar = db.query(bar_models.Bar).filter_by(id=sale_data.bar_id).first()
    if not bar:
        raise HTTPException(status_code=404, detail="Bar not found")

    sale = bar_models.BarSale(
        bar_id=sale_data.bar_id,
        created_by_id=current_user.id
    )
    db.add(sale)
    db.flush()

    for item_data in sale_data.items:
        # Get inventory record
        inventory = db.query(bar_models.BarInventory).filter_by(
            bar_id=sale_data.bar_id,
            item_id=item_data.item_id
        ).first()

        if not inventory:
            raise HTTPException(status_code=404, detail="Bar inventory record not found")

        # Calculate available quantity
        total_issued = db.query(func.sum(store_models.StoreIssueItem.quantity)).join(
            store_models.StoreIssue
        ).filter(
            store_models.StoreIssue.issued_to_id == sale_data.bar_id,
            store_models.StoreIssueItem.item_id == item_data.item_id
        ).scalar() or 0

        total_sold = db.query(func.sum(bar_models.BarSaleItem.quantity)).join(
            bar_models.BarSale
        ).filter(
            bar_models.BarSale.bar_id == sale_data.bar_id,
            bar_models.BarSaleItem.bar_inventory_id == inventory.id
        ).scalar() or 0

        available = total_issued - total_sold

        if available < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for item ID {item_data.item_id} (available: {available})"
            )

        total = item_data.quantity * inventory.selling_price

        sale_item = bar_models.BarSaleItem(
            bar_sale_id=sale.id,
            bar_inventory_id=inventory.id,
            quantity=item_data.quantity,
            total_amount=total
        )
        db.add(sale_item)

    db.commit()
    db.refresh(sale)

    # Re-fetch with joins for full details
    sale = db.query(bar_models.BarSale).options(
        joinedload(bar_models.BarSale.bar),
        joinedload(bar_models.BarSale.created_by_user),
        joinedload(bar_models.BarSale.sale_items).joinedload(bar_models.BarSaleItem.bar_inventory).joinedload(bar_models.BarInventory.item)
    ).get(sale.id)

    sale_items = []
    total_amount = 0.0

    for item in sale.sale_items:
        inventory = item.bar_inventory
        store_item = inventory.item if inventory else None
        item_name = store_item.name if store_item else "Unknown"

        sale_items.append({
            "item_id": inventory.item_id if inventory else 0,
            "item_name": item_name,
            "quantity": item.quantity,
            "selling_price": inventory.selling_price if inventory else 0.0,
            "total_amount": item.total_amount
        })

        total_amount += item.total_amount

    return {
        "id": sale.id,
        "sale_date": sale.sale_date,
        "bar_id": sale.bar_id,
        "bar_name": sale.bar.name if sale.bar else "",
        "created_by": sale.created_by_user.username if sale.created_by_user else "",
        "status": getattr(sale, "status", "completed"),
        "total_amount": total_amount,
        "sale_items": sale_items
    }






@router.get("/sales", response_model=bar_schemas.BarSaleListResponse)
def list_bar_sales(
    bar_id: Optional[int] = None,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    query = db.query(BarSale).options(
        joinedload(BarSale.bar),
        joinedload(BarSale.created_by_user),
        joinedload(BarSale.sale_items).joinedload(BarSaleItem.bar_inventory).joinedload(BarInventory.item)
    )

    if bar_id:
        query = query.filter(BarSale.bar_id == bar_id)
    if start_date and end_date:
        query = query.filter(func.date(BarSale.sale_date).between(start_date, end_date))
    elif start_date:
        query = query.filter(func.date(BarSale.sale_date) >= start_date)
    elif end_date:
        query = query.filter(func.date(BarSale.sale_date) <= end_date)

    sales = query.order_by(BarSale.sale_date.desc()).all()

    result = []
    for sale in sales:
        sale_items = []
        total_amount = 0.0

        for item in sale.sale_items:
            inventory = item.bar_inventory
            store_item = inventory.item if inventory else None
            item_name = store_item.name if store_item else "Unknown"

            sale_items.append({
                "item_id": inventory.item_id if inventory else 0,
                "item_name": item_name,
                "quantity": item.quantity,
                "selling_price": inventory.selling_price if inventory else 0.0,
                "total_amount": item.total_amount
            })

            total_amount += item.total_amount

        sale_data = {
            "id": sale.id,
            "sale_date": sale.sale_date,
            "bar_id": sale.bar_id,
            "bar_name": sale.bar.name if sale.bar else "",
            "created_by": sale.created_by_user.username if sale.created_by_user else "",
            "status": getattr(sale, "status", "completed"),
            "total_amount": total_amount,
            "sale_items": sale_items
        }

        result.append(sale_data)

    total_sales_amount = sum(sale["total_amount"] for sale in result)
    total_entries = len(result)

    return {
        "total_entries": total_entries,
        "total_sales_amount": total_sales_amount,
        "sales": result
    }

@router.put("/sales/{sale_id}", response_model=bar_schemas.BarSaleDisplay)
def update_bar_sale(
    sale_id: int,
    sale_data: bar_schemas.BarSaleCreate,  # Same structure as create
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    sale = db.query(bar_models.BarSale).filter_by(id=sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    if sale.bar_id != sale_data.bar_id:
        raise HTTPException(status_code=400, detail="Bar ID mismatch")

    # Delete old sale items
    db.query(bar_models.BarSaleItem).filter_by(sale_id=sale.id).delete()

    # Re-create sale items with updated quantities
    for item_data in sale_data.items:
        inventory = db.query(bar_models.BarInventory).filter_by(
            bar_id=sale_data.bar_id,
            item_id=item_data.item_id
        ).first()

        if not inventory:
            raise HTTPException(status_code=404, detail=f"Inventory not found for item {item_data.item_id}")

        # Re-calculate availability excluding current sale quantities
        total_issued = db.query(func.sum(store_models.StoreIssueItem.quantity)).join(
            store_models.StoreIssue
        ).filter(
            store_models.StoreIssue.issued_to_id == sale_data.bar_id,
            store_models.StoreIssueItem.item_id == item_data.item_id
        ).scalar() or 0

        total_sold_excluding_current = db.query(func.sum(bar_models.BarSaleItem.quantity)).join(
            bar_models.BarSale
        ).filter(
            bar_models.BarSale.bar_id == sale_data.bar_id,
            bar_models.BarSaleItem.bar_inventory_id == inventory.id,
            bar_models.BarSaleItem.sale_id != sale.id  # exclude current
        ).scalar() or 0

        available = total_issued - total_sold_excluding_current

        if item_data.quantity > available:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for item ID {item_data.item_id} (available: {available})"
            )

        total = item_data.quantity * inventory.selling_price

        sale_item = bar_models.BarSaleItem(
            sale_id=sale.id,
            bar_inventory_id=inventory.id,
            quantity=item_data.quantity,
            total_amount=total
        )
        db.add(sale_item)

    db.commit()
    db.refresh(sale)
    return sale


# ----------------------------
# RECEIVED ITEMS
# ----------------------------

@router.get("/received-items", response_model=List[dict])
def get_received_items(
    bar_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    if bar_id:
        bar = db.query(Bar).filter(Bar.id == bar_id).first()
        if not bar:
            raise HTTPException(status_code=404, detail="Bar not found")

    subquery = (
        db.query(
            store_models.StoreStockEntry.item_id,
            store_models.StoreStockEntry.unit_price
        )
        .order_by(
            store_models.StoreStockEntry.item_id,
            store_models.StoreStockEntry.purchase_date.desc()
        )
        .distinct(store_models.StoreStockEntry.item_id)
        .subquery()
    )

    query = db.query(
        store_models.StoreIssueItem.item_id,
        store_models.StoreItem.name,
        store_models.StoreItem.unit,
        store_models.StoreIssue.issued_to_id.label("bar_id"),
        store_models.StoreIssue.issue_date,
        store_models.StoreIssueItem.quantity,
        subquery.c.unit_price
    ).join(
        store_models.StoreIssue, store_models.StoreIssue.id == store_models.StoreIssueItem.issue_id
    ).join(
        store_models.StoreItem, store_models.StoreItem.id == store_models.StoreIssueItem.item_id
    ).outerjoin(
        subquery, subquery.c.item_id == store_models.StoreIssueItem.item_id
    )

    if bar_id:
        query = query.filter(store_models.StoreIssue.issued_to_id == bar_id)

    results = query.all()

    return [
        {
            "item_id": r.item_id,
            "item_name": r.name,
            "unit": r.unit,
            "bar_id": r.bar_id,
            "issue_date": r.issue_date,
            "quantity": r.quantity,
            "unit_price": r.unit_price,
            "total_amount": round(r.quantity * r.unit_price, 2) if r.unit_price else None
        }
        for r in results
    ]


@router.delete("/bars/{bar_id}")
def delete_bar(
    bar_id: int,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    bar = db.query(bar_models.Bar).filter_by(id=bar_id).first()
    if not bar:
        raise HTTPException(status_code=404, detail="Bar not found")

    # Optional: Check if this bar has sales or inventory, and block deletion if necessary

    db.delete(bar)
    db.commit()
    return {"detail": "Bar deleted successfully"}


@router.delete("/sales/{sale_id}")
def delete_bar_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    sale = db.query(bar_models.BarSale).filter_by(id=sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    # Delete all sale items first
    db.query(bar_models.BarSaleItem).filter_by(sale_id=sale.id).delete()
    
    # Then delete the sale itself
    db.delete(sale)
    db.commit()
    return {"detail": "Bar sale deleted successfully"}
