from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.users.auth import get_current_user
from fastapi import Query
from datetime import datetime
from datetime import date
from app.users import schemas as user_schemas
from app.bar import models as bar_models
from app.bar import schemas as bar_schemas
from app.store import models as store_models
from app.bar.models import Bar  # ✅ Import Bar model

from app.bar.models import BarSale, BarSaleItem
from app.users.models import User
from sqlalchemy import func


from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
import openpyxl
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


router = APIRouter()


# ----------------------------
# BAR ROUTES
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


@router.get("/bars", response_model=list[bar_schemas.BarDisplay])
def list_bars(
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    return db.query(bar_models.Bar).order_by(bar_models.Bar.name).all()


# ----------------------------
# BAR ITEM ROUTES
# ----------------------------
@router.post("/items", response_model=bar_schemas.BarItemDisplay)
def create_bar_item(
    item: bar_schemas.BarItemCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    # Ensure store item exists
    from app.store.models import StoreItem
    store_item = db.query(StoreItem).filter_by(id=item.item_id).first()
    if not store_item:
        raise HTTPException(status_code=404, detail="Store item not found")

    bar = db.query(bar_models.Bar).filter_by(id=item.bar_id).first()
    if not bar:
        raise HTTPException(status_code=404, detail="Bar not found")

    # Check if item already exists in bar
    existing = db.query(bar_models.BarItem).filter_by(
        bar_id=item.bar_id, item_id=item.item_id
    ).first()
    if existing:
        existing.quantity += item.quantity
        existing.selling_price = item.selling_price  # Update selling price
        db.commit()
        db.refresh(existing)
        return existing

    # Else, create new bar item
    new_bar_item = bar_models.BarItem(**item.dict())
    db.add(new_bar_item)
    db.commit()
    db.refresh(new_bar_item)
    return new_bar_item


@router.get("/items", response_model=list[bar_schemas.BarItemDisplay])
def list_bar_items(
    bar_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    query = db.query(bar_models.BarItem)
    if bar_id:
        query = query.filter_by(bar_id=bar_id)
    return query.order_by(bar_models.BarItem.created_at.desc()).all()




@router.put("/items/update-price", response_model=bar_schemas.BarItemDisplay)
def update_bar_item_price(
    data: bar_schemas.BarPriceUpdate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    # 🔍 Log the data you're using for the lookup
    print(f"🔍 Updating price for bar_id={data.bar_id}, item_id={data.item_id}, new_price={data.new_price}")

    # 🛠 Try to find the bar item
    bar_item = db.query(bar_models.BarItem).filter_by(
        bar_id=data.bar_id,
        item_id=data.item_id
    ).first()

    # ❌ If not found, raise an error with specific info
    if not bar_item:
        raise HTTPException(
            status_code=404,
            detail=f"Bar item with bar_id={data.bar_id} and item_id={data.item_id} not found"
        )

    # ✅ Update the price
    bar_item.selling_price = data.new_price
    db.commit()
    db.refresh(bar_item)

    print(f"✅ Updated price for BarItem ID={bar_item.id}: {bar_item.selling_price}")
    return bar_item


@router.post("/sales", response_model=bar_schemas.BarSaleDisplay)
def create_bar_sale(
    sale_data: bar_schemas.BarSaleCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user)
):
    bar = db.query(bar_models.Bar).filter_by(id=sale_data.bar_id).first()
    if not bar:
        raise HTTPException(status_code=404, detail="Bar not found")

    sale = bar_models.BarSale(
        bar_id=sale_data.bar_id,
        created_by_id=current_user.id
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)

    for item_data in sale_data.items:
        bar_item = db.query(bar_models.BarItem).filter_by(id=item_data.bar_item_id).first()
        if not bar_item:
            raise HTTPException(status_code=404, detail=f"Bar item ID {item_data.bar_item_id} not found")

        if bar_item.quantity < item_data.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

        bar_item.quantity -= item_data.quantity

        # ✅ Calculate total amount
        total_amount = item_data.quantity * (bar_item.selling_price or 0)

        sale_item = bar_models.BarSaleItem(
            sale_id=sale.id,
            bar_item_id=item_data.bar_item_id,
            quantity=item_data.quantity,
            total_amount=total_amount  # ✅ Save it
        )
        db.add(sale_item)

    db.commit()
    db.refresh(sale)
    return sale


@router.get("/sales", response_model=List[bar_schemas.BarSaleDisplay])
def list_bar_sales(
    bar_id: Optional[int] = None,
    sale_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user)
):
    query = db.query(bar_models.BarSale)
    if bar_id:
        query = query.filter(bar_models.BarSale.bar_id == bar_id)
    if sale_date:
        query = query.filter(db.func.date(bar_models.BarSale.sale_date) == sale_date)
    return query.order_by(bar_models.BarSale.sale_date.desc()).all()

@router.get("/sales/daily-report")
def get_bar_daily_sales_report(
    bar_id: int,
    date: datetime = Query(..., description="Date for the report (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    start = datetime(date.year, date.month, date.day)
    end = datetime(date.year, date.month, date.day, 23, 59, 59)

    sales = db.query(BarSale).filter(
        BarSale.bar_id == bar_id,
        BarSale.sale_date >= start,
        BarSale.sale_date <= end

    ).all()

    total_amount = sum(s.total_amount for s in sales)

    # Aggregate items
    from collections import defaultdict
    item_summary = defaultdict(lambda: {"quantity": 0, "total": 0.0})

    for sale in sales:
        for item in sale.items:
            name = item.bar_item.item.name
            item_summary[name]["quantity"] += item.quantity
            item_summary[name]["total"] += item.quantity * item.selling_price

    report = {
        "bar_id": bar_id,
        "date": date.strftime("%Y-%m-%d"),
        "total_sales_amount": total_amount,
        "items": [
            {"item_name": name, "quantity": data["quantity"], "total": data["total"]}
            for name, data in item_summary.items()
        ]
    }

    return report


@router.get("/sales/daily-report/download")
def download_bar_daily_report(
    bar_id: int,
    date: datetime = Query(..., description="Report date"),
    format: str = Query("excel", enum=["excel", "pdf"]),
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    start = datetime(date.year, date.month, date.day)
    end = datetime(date.year, date.month, date.day, 23, 59, 59)

    sales = db.query(BarSale).filter(
        BarSale.bar_id == bar_id,
        BarSale.sale_time >= start,
        BarSale.sale_time <= end
    ).all()

    total_amount = sum(s.total_amount for s in sales)

    # Aggregate sales
    from collections import defaultdict
    item_summary = defaultdict(lambda: {"quantity": 0, "total": 0.0})

    for sale in sales:
        for item in sale.items:
            name = item.bar_item.item.name
            item_summary[name]["quantity"] += item.quantity
            item_summary[name]["total"] += item.quantity * item.selling_price

    # Return Excel file
    if format == "excel":
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Bar Sales Report"

        ws.append(["Date", date.strftime("%Y-%m-%d")])
        ws.append(["Bar ID", bar_id])
        ws.append([])
        ws.append(["Item", "Quantity Sold", "Total Amount"])

        for name, data in item_summary.items():
            ws.append([name, data["quantity"], data["total"]])

        ws.append([])
        ws.append(["Total Sales", "", total_amount])

        temp_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
        wb.save(temp_file.name)
        temp_file.close()
        return FileResponse(temp_file.name, filename=f"bar_report_{date.date()}.xlsx")

    # Return PDF file
    elif format == "pdf":
        temp_file = NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(temp_file.name, pagesize=A4)
        width, height = A4

        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Bar Sales Report - {date.strftime('%Y-%m-%d')} (Bar ID: {bar_id})")

        y -= 30
        c.setFont("Helvetica", 12)
        c.drawString(50, y, "Item")
        c.drawString(250, y, "Quantity Sold")
        c.drawString(400, y, "Total")

        y -= 20
        for name, data in item_summary.items():
            c.drawString(50, y, name)
            c.drawString(250, y, str(data["quantity"]))
            c.drawString(400, y, f"{data['total']:.2f}")
            y -= 20

        y -= 20
        c.drawString(50, y, "Total Sales:")
        c.drawString(400, y, f"{total_amount:.2f}")

        c.showPage()
        c.save()
        return FileResponse(temp_file.name, filename=f"bar_report_{date.date()}.pdf")



@router.get("/received-items", response_model=list[dict])
def get_received_items(
    bar_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserDisplaySchema = Depends(get_current_user),
):
    if bar_id is not None:
        bar = db.query(Bar).filter(Bar.id == bar_id).first()
        if not bar:
            raise HTTPException(status_code=404, detail=f"Bar with ID {bar_id} not found.")

    query = db.query(
        store_models.StoreIssueItem.item_id,
        store_models.StoreItem.name,
        store_models.StoreItem.unit,
        store_models.StoreIssue.issued_to_id.label("bar_id"),
        store_models.StoreIssue.issue_date,
        store_models.StoreIssueItem.quantity,
        store_models.StoreStockEntry.unit_price
    ).join(
        store_models.StoreIssue, store_models.StoreIssue.id == store_models.StoreIssueItem.issue_id
    ).join(
        store_models.StoreItem, store_models.StoreItem.id == store_models.StoreIssueItem.item_id
    ).outerjoin(
        store_models.StoreStockEntry,
        store_models.StoreStockEntry.item_id == store_models.StoreIssueItem.item_id
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
