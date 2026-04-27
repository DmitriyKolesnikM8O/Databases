from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, text
from typing import Optional, List
from datetime import date

from models import (
    get_db,
    Category, User, Equipment, Rental, RentalItem, Payment, Review,
    EquipmentCatalogView, RentalDetailsView, ClientActivityView
)
from schemas import (
    CategoryCreate, CategoryResponse,
    UserCreate, UserUpdate, UserResponse,
    EquipmentCreate, EquipmentUpdate, EquipmentResponse,
    RentalCreate, RentalUpdate, RentalResponse,
    RentalItemCreate, RentalItemResponse,
    PaymentCreate, PaymentResponse,
    ReviewCreate, ReviewResponse,
    PaginatedResponse
)

app = FastAPI(
    title="Rental Equipment API",
    description="RESTful API for rental equipment database",
    version="1.0.0"
)


# ендпоинты для категорий

@app.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    return db.query(Category).offset(skip).limit(limit).all()


@app.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.dict().items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return None


# эндпоинты для юзеров

@app.get("/users", response_model=List[UserResponse])
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    city: Optional[str] = None,
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    query = db.query(User)
    if city:
        query = query.filter(User.city.ilike(f"%{city}%"))
    if sort:
        col = getattr(User, sort, User.id)
        query = query.order_by(desc(col) if order == "desc" else asc(col))
    return query.offset(skip).limit(limit).all()


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_user


@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return None


# эндпоинты для инвентаря

@app.get("/equipment", response_model=List[EquipmentResponse])
def get_equipment(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    query = db.query(Equipment)
    if category_id:
        query = query.filter(Equipment.category_id == category_id)
    if owner_id:
        query = query.filter(Equipment.owner_id == owner_id)
    if min_price:
        query = query.filter(Equipment.price_per_day >= min_price)
    if max_price:
        query = query.filter(Equipment.price_per_day <= max_price)
    if sort:
        col = getattr(Equipment, sort, Equipment.id)
        query = query.order_by(desc(col) if order == "desc" else asc(col))
    return query.offset(skip).limit(limit).all()


@app.get("/equipment/{equipment_id}", response_model=EquipmentResponse)
def get_equipment_item(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@app.post("/equipment", response_model=EquipmentResponse, status_code=201)
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    db_equipment = Equipment(**equipment.dict())
    db.add(db_equipment)
    try:
        db.commit()
        db.refresh(db_equipment)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_equipment


@app.patch("/equipment/{equipment_id}", response_model=EquipmentResponse)
def update_equipment(equipment_id: int, equipment: EquipmentUpdate, db: Session = Depends(get_db)):
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    for key, value in equipment.dict(exclude_unset=True).items():
        setattr(db_equipment, key, value)
    try:
        db.commit()
        db.refresh(db_equipment)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_equipment


@app.delete("/equipment/{equipment_id}", status_code=204)
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    db.delete(db_equipment)
    db.commit()
    return None


# эндпоинты для аренд

@app.get("/rentals", response_model=List[RentalResponse])
def get_rentals(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    renter_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    query = db.query(Rental)
    if renter_id:
        query = query.filter(Rental.renter_id == renter_id)
    if status:
        query = query.filter(Rental.status == status)
    return query.offset(skip).limit(limit).all()


@app.get("/rentals/{rental_id}", response_model=RentalResponse)
def get_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    return rental


@app.post("/rentals", response_model=RentalResponse, status_code=201)
def create_rental(rental: RentalCreate, db: Session = Depends(get_db)):
    db_rental = Rental(**rental.dict())
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental


@app.patch("/rentals/{rental_id}", response_model=RentalResponse)
def update_rental(rental_id: int, rental: RentalUpdate, db: Session = Depends(get_db)):
    db_rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not db_rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    for key, value in rental.dict(exclude_unset=True).items():
        setattr(db_rental, key, value)
    db.commit()
    db.refresh(db_rental)
    return db_rental


@app.delete("/rentals/{rental_id}", status_code=204)
def delete_rental(rental_id: int, db: Session = Depends(get_db)):
    db_rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not db_rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    db.delete(db_rental)
    db.commit()
    return None


@app.get("/rentals/{rental_id}/items", response_model=List[RentalItemResponse])
def get_rental_items(rental_id: int, db: Session = Depends(get_db)):
    items = db.query(RentalItem).filter(RentalItem.rental_id == rental_id).all()
    return items


@app.post("/rentals/{rental_id}/items", response_model=RentalItemResponse, status_code=201)
def add_rental_item(rental_id: int, item: RentalItemCreate, db: Session = Depends(get_db)):
    db_item = RentalItem(rental_id=rental_id, **item.dict(exclude={"rental_id"}))
    db.add(db_item)
    try:
        db.commit()
        db.refresh(db_item)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_item


# эндпоинты для платежей

@app.get("/payments", response_model=List[PaymentResponse])
def get_payments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    return db.query(Payment).offset(skip).limit(limit).all()


@app.post("/payments", response_model=PaymentResponse, status_code=201)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    db_payment = Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


# эндпоинты для отзывов

@app.get("/reviews", response_model=List[ReviewResponse])
def get_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    equipment_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Review)
    if equipment_id:
        query = query.filter(Review.equipment_id == equipment_id)
    return query.offset(skip).limit(limit).all()


@app.post("/reviews", response_model=ReviewResponse, status_code=201)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    db_review = Review(**review.dict())
    db.add(db_review)
    try:
        db.commit()
        db.refresh(db_review)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return db_review


# эндпоинты для views

@app.get("/views/equipment-catalog", response_model=List[dict])
def get_equipment_catalog_view(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    results = db.query(EquipmentCatalogView).offset(skip).limit(limit).all()
    return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]


@app.get("/views/rental-details", response_model=List[dict])
def get_rental_details_view(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    results = db.query(RentalDetailsView).offset(skip).limit(limit).all()
    return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]


@app.get("/views/client-activity", response_model=List[dict])
def get_client_activity_view(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    results = db.query(ClientActivityView).offset(skip).limit(limit).all()
    return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]


# агрегации для отчетов

@app.get("/reports/sales-by-category")
def get_sales_by_category(db: Session = Depends(get_db)):
    result = db.query(
        Category.name,
        func.count(Equipment.id).label("equipment_count"),
        func.avg(Equipment.price_per_day).label("avg_price"),
        func.sum(Equipment.price_per_day * Equipment.total_quantity).label("total_value")
    ).join(Equipment).group_by(Category.id, Category.name).all()
    return [{"category": str(r[0]), "count": r[1], "avg_price": float(r[2]) if r[2] else 0, "total_value": float(r[3]) if r[3] else 0} for r in result]


@app.get("/reports/top-customers")
def get_top_customers(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    result = db.query(
        User.id,
        User.first_name,
        User.last_name,
        func.count(Rental.id).label("rental_count"),
        func.sum(Payment.payment_amount).label("total_spent")
    ).join(Rental, User.id == Rental.renter_id).join(Payment, Rental.id == Payment.rental_id).filter(
        Payment.status == "Успешно"
    ).group_by(User.id, User.first_name, User.last_name).order_by(
        desc("total_spent")
    ).limit(limit).all()
    return [{"id": r[0], "name": f"{r[1]} {r[2]}", "rentals": r[3], "spent": float(r[4]) if r[4] else 0} for r in result]


@app.get("/reports/top-equipment")
def get_top_equipment(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    result = db.query(
        Equipment.id,
        Equipment.name,
        Equipment.price_per_day,
        func.count(RentalItem.equipment_id).label("rent_count"),
        func.avg(Review.rating).label("avg_rating")
    ).outerjoin(RentalItem, Equipment.id == RentalItem.equipment_id).outerjoin(
        Review, Equipment.id == Review.equipment_id
    ).group_by(Equipment.id, Equipment.name, Equipment.price_per_day).order_by(
        desc("rent_count")
    ).limit(limit).all()
    return [{"id": r[0], "name": str(r[1]), "price": float(r[2]), "rent_count": r[3], "avg_rating": float(r[4]) if r[4] else None} for r in result]


# функции

@app.get("/users/{user_id}/rentals-count")
def get_user_rentals_count(user_id: int, db: Session = Depends(get_db)):
    if user_id < 1:
        raise HTTPException(status_code=400, detail="ID пользователя должен быть положительным числом")
    
    user_exists = db.query(User.id).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail=f"Пользователь с ID={user_id} не найден")
    
    try:
        result = db.execute(
            text("SELECT get_total_rentals_by_userId(:user_id)"),
            {"user_id": user_id}
        ).fetchone()
        return {"user_id": user_id, "rentals_count": result[0] if result else 0}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при вызове функции: {str(e)}")


@app.get("/rentals/{rental_id}/total-price")
def get_rental_total_price(rental_id: int, db: Session = Depends(get_db)):
    if rental_id < 1:
        raise HTTPException(status_code=400, detail="ID аренды должен быть положительным числом")
    
    rental_exists = db.query(Rental.id).filter(Rental.id == rental_id).first()
    if not rental_exists:
        raise HTTPException(status_code=404, detail=f"Аренда с ID={rental_id} не найдена")
    
    try:
        result = db.execute(
            text("SELECT get_rental_total_price(:rental_id)"),
            {"rental_id": rental_id}
        ).fetchone()
        return {"rental_id": rental_id, "total_price": float(result[0]) if result else 0}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при вызове функции: {str(e)}")


# HEALTH CHECK

@app.get("/")
def root():
    return {"message": "Rental Equipment API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
