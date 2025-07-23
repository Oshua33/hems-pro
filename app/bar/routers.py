from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import aliased
from typing import Optional, List
from sqlalchemy import and_
from datetime import datetime, date
from app.database import get_db
from app.users.auth import get_current_user
from app.users import schemas as user_schemas
from app.bar import models as bar_models, schemas as bar_schemas
from app.store import models as store_models
from app.bar.models import Bar, BarInventory, BarSale, BarSaleItem
from app.users.models import User
from app.bar.models import Bar, BarInventoryReceipt

from app.store.models import StoreItem
#from models.bars import Bar
from app.bar.schemas import BarStockReceiveCreate, BarInventoryDisplay
from datetime import datetime
from app.bar.schemas import  BarInventoryReceiptDisplay  # <- New response schema


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




@router.post("/receive-stock", response_model=BarInventoryReceiptDisplay)
def receive_bar_stock(data: BarStockReceiveCreate, db: Session = Depends(get_db)):
    # Validate bar and item
    bar = db.query(Bar).filter(Bar.id == data.bar_id).first()
    if not bar:
        raise HTTPException(status_code=404, detail="Bar not found")

    item = db.query(StoreItem).filter(StoreItem.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update or create inventory
    inventory = db.query(BarInventory).filter(
        BarInventory.bar_id == data.bar_id,
        BarInventory.item_id == data.item_id
    ).first()

    if inventory:
        inventory.quantity += data.quantity
        inventory.selling_price = data.selling_price
        inventory.note = data.note
    else:
        inventory = BarInventory(
            bar_id=data.bar_id,
            bar_name=bar.name,
            item_id=data.item_id,
            item_name=item.name,
            quantity=data.quantity,
            selling_price=data.selling_price,
            note=data.note
        )
        db.add(inventory)

    # Create receipt log
    receipt = BarInventoryReceipt(
        bar_id=data.bar_id,
        bar_name=bar.name,
        item_id=data.item_id,
        item_name=item.name,
        quantity=data.quantity,
        selling_price=data.selling_price,
        note=data.note,
        created_by="fcn"
    )
    db.add(receipt)

    db.commit()
    db.refresh(receipt)

    return receipt



@router.get("/received-stocks", response_model=List[BarInventoryDisplay])
def list_received_stocks(
    bar_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(BarInventoryReceipt)

    filters = []
    if bar_id:
        filters.append(BarInventoryReceipt.bar_id == bar_id)
    if start_date:
        filters.append(BarInventoryReceipt.created_at >= start_date)
    if end_date:
        filters.append(BarInventoryReceipt.created_at <= end_date)

    if filters:
        query = query.filter(and_(*filters))

    receipts = query.order_by(BarInventoryReceipt.created_at.desc()).all()
    return receipts


@router.put("/update-received-stock", response_model=bar_schemas.BarInventoryDisplay)
def update_received_stock(data: bar_schemas.BarStockUpdate, db: Session = Depends(get_db)):
    # Validate bar
    bar = db.query(Bar).filter(Bar.id == data.bar_id).first()
    if not bar:
        raise HTTPException(status_code=404, detail="Bar not found")

    # Validate item
    item = db.query(StoreItem).filter(StoreItem.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Find the inventory record
    inventory = db.query(BarInventory).filter(
        BarInventory.bar_id == data.bar_id,
        BarInventory.item_id == data.item_id
    ).first()

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found for update")

    # Update fields
    inventory.quantity = data.new_quantity
    if data.selling_price is not None:
        inventory.selling_price = data.selling_price
    if data.note is not None:
        inventory.note = data.note

    db.commit()
    db.refresh(inventory)

    return inventory


@router.delete("/bar-inventory/{inventory_id}", status_code=204)
def delete_bar_inventory(inventory_id: int, db: Session = Depends(get_db)):
    inventory = db.query(BarInventory).filter(BarInventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")

    db.delete(inventory)
    db.commit()
    return {"message": "Inventory entry deleted successfully"}



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
    try:
        total_amount = 0.0

        # Create the sale record
        sale = bar_models.BarSale(
            bar_id=sale_data.bar_id,
            created_by_id=current_user.id
        )
        db.add(sale)
        db.flush()  # Get sale.id before committing

        for item_data in sale_data.items:
            # Step 1: Get BarInventory record
            inventory = db.query(bar_models.BarInventory).filter_by(
                bar_id=sale_data.bar_id,
                item_id=item_data.item_id
            ).first()

            if not inventory:
                raise HTTPException(
                    status_code=404,
                    detail=f"Inventory not found for item ID {item_data.item_id}"
                )

            # Step 2: Check available quantity directly from inventory
            if inventory.quantity < item_data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for item ID {item_data.item_id} (available: {inventory.quantity})"
                )

            # Step 3: Update inventory quantity
            inventory.quantity -= item_data.quantity

            # Step 4: Calculate total for item
            item_total = item_data.quantity * inventory.selling_price
            total_amount += item_total

            # Step 5: Add the sale item
            sale_item = bar_models.BarSaleItem(
            sale_id=sale.id,
            bar_inventory_id=inventory.id,
            quantity=item_data.quantity,
            unit_price=inventory.selling_price,  # <-- This line is required
            total_amount=item_total
        )



            db.add(sale_item)

        # Step 6: Finalize sale
        sale.total_amount = total_amount
        db.commit()
        db.refresh(sale)

        # Step 7: Load response
        sale = db.query(bar_models.BarSale).options(
            joinedload(bar_models.BarSale.bar),
            joinedload(bar_models.BarSale.created_by_user),
            joinedload(bar_models.BarSale.sale_items).joinedload(bar_models.BarSaleItem.bar_inventory).joinedload(bar_models.BarInventory.item)
        ).get(sale.id)

        sale_items = []
        for item in sale.sale_items:
            inventory = item.bar_inventory
            store_item = inventory.item if inventory else None
            item_name = store_item.name if store_item else "Unknown"

            sale_items.append(bar_schemas.BarSaleItemSummary(
                item_id=inventory.item_id if inventory else 0,
                item_name=item_name,
                quantity=item.quantity,
                selling_price=inventory.selling_price if inventory else 0.0,
                total_amount=item.total_amount
            ))

        return bar_schemas.BarSaleDisplay(
            id=sale.id,
            sale_date=sale.sale_date,
            bar_id=sale.bar_id,
            bar_name=sale.bar.name if sale.bar else "",
            created_by=sale.created_by_user.username if sale.created_by_user else "",
            status=getattr(sale, "status", "completed"),
            total_amount=total_amount,
            sale_items=sale_items
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


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
        joinedload(BarSale.sale_items)
            .joinedload(BarSaleItem.bar_inventory)
            .joinedload(BarInventory.item)
    )

    if bar_id:
        query = query.filter(BarSale.bar_id == bar_id)

    if start_date and end_date:
        query = query.filter(func.date(BarSale.sale_date).between(start_date, end_date))
    elif start_date:
        query = query.filter(func.date(BarSale.sale_date) >= start_date)
    elif end_date:
        query = query.filter(func.date(BarSale.sale_date) <= end_date)

    query = query.order_by(BarSale.sale_date.desc())
    sales = query.all()

    result = []
    total_sales_amount = 0.0

    for sale in sales:
        sale_items = []
        sale_total = 0.0

        for item in sale.sale_items:
            inventory = item.bar_inventory
            item_model = inventory.item if inventory else None
            item_name = item_model.name if item_model else "Unknown"

            sale_items.append({
                "item_id": inventory.item_id if inventory else None,
                "item_name": item_name,
                "quantity": item.quantity,
                "selling_price": inventory.selling_price if inventory else 0.0,
                "total_amount": item.total_amount
            })

            sale_total += item.total_amount

        result.append({
            "id": sale.id,
            "sale_date": sale.sale_date,
            "bar_id": sale.bar_id,
            "bar_name": sale.bar.name if sale.bar else "",
            "created_by": sale.created_by_user.username if sale.created_by_user else "",
            "status": sale.status if hasattr(sale, "status") else "completed",
            "total_amount": sale_total,
            "sale_items": sale_items
        })

        total_sales_amount += sale_total

    return {
        "total_entries": len(result),
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

@router.delete("/sales/{sale_id}")
def delete_bar_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    sale = db.query(bar_models.BarSale).filter_by(id=sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    db.delete(sale)
    db.commit()
    return {"detail": "Bar sale deleted successfully"}



@router.get("/stock-balance", response_model=List[bar_schemas.BarStockBalance])
def get_bar_stock_balance(
    bar_id: Optional[int] = None,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    try:
        # Step 1: Fetch issued items
        issued_query = db.query(
            store_models.StoreIssueItem.item_id,
            func.sum(store_models.StoreIssueItem.quantity).label("total_issued")
        ).join(store_models.StoreIssue)

        if bar_id:
            issued_query = issued_query.filter(store_models.StoreIssue.issued_to_id == bar_id)

        if start_date:
            issued_query = issued_query.filter(store_models.StoreIssue.issued_at >= start_date)
        if end_date:
            issued_query = issued_query.filter(store_models.StoreIssue.issued_at <= end_date)

        issued_query = issued_query.group_by(store_models.StoreIssueItem.item_id)
        issued_data = {row.item_id: row.total_issued for row in issued_query.all()}

        # Step 2: Fetch sold items
        sold_query = db.query(
            bar_models.BarInventory.item_id,
            func.sum(bar_models.BarSaleItem.quantity).label("total_sold")
        ).join(bar_models.BarSaleItem.bar_inventory).join(bar_models.BarSaleItem.sale)

        if bar_id:
            sold_query = sold_query.filter(bar_models.BarSale.bar_id == bar_id)

        if start_date:
            sold_query = sold_query.filter(bar_models.BarSale.sale_date >= start_date)
        if end_date:
            sold_query = sold_query.filter(bar_models.BarSale.sale_date <= end_date)

        sold_query = sold_query.group_by(bar_models.BarInventory.item_id)
        sold_data = {row.item_id: row.total_sold for row in sold_query.all()}

        # Step 3: Combine issued and sold to compute balances
        all_item_ids = set(issued_data.keys()).union(sold_data.keys())
        results = []

        for item_id in all_item_ids:
            issued = issued_data.get(item_id, 0)
            sold = sold_data.get(item_id, 0)
            balance = issued - sold

            item = db.query(store_models.StoreItem).get(item_id)

            results.append(bar_schemas.BarStockBalance(
                item_id=item_id,
                item_name=item.name if item else "Unknown",
                total_issued=issued,
                total_sold=sold,
                balance=balance
            ))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stock balance: {str(e)}")


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



# ----------------------------
# RECEIVED ITEMS
# ----------------------------

@router.get("/store-issue-control", response_model=List[dict])
def get_store_items_received(
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



