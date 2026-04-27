from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, ARRAY, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), unique=True, nullable=False)
    description = Column(Text)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(256), nullable=False)
    last_name = Column(String(256))
    patronymic = Column(String(256))
    login = Column(String(256), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    city = Column(String(100), nullable=False)

    equipment = relationship("Equipment", back_populates="owner")
    rentals = relationship("Rental", back_populates="renter")
    reviews = relationship("Review", back_populates="renter")


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(256), nullable=False)
    description = Column(Text)
    price_per_day = Column(Numeric(10, 2), nullable=False)
    total_quantity = Column(Integer, nullable=False, default=0)

    owner = relationship("User", back_populates="equipment")
    category = relationship("Category")
    rental_items = relationship("RentalItem", back_populates="equipment")
    reviews = relationship("Review", back_populates="equipment")


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    renter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False, default="Новый")

    renter = relationship("User", back_populates="rentals")
    items = relationship("RentalItem", back_populates="rental")
    payments = relationship("Payment", back_populates="rental")


class RentalItem(Base):
    __tablename__ = "rental_items"

    rental_id = Column(Integer, ForeignKey("rentals.id", ondelete="CASCADE"), primary_key=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id", ondelete="CASCADE"), primary_key=True)
    quantity = Column(Integer, nullable=False)
    price_at_booking = Column(Numeric(10, 2), nullable=False)

    rental = relationship("Rental", back_populates="items")
    equipment = relationship("Equipment", back_populates="rental_items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id", ondelete="CASCADE"), nullable=False)
    payment_amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)

    rental = relationship("Rental", back_populates="payments")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    renter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text)
    created_at = Column(Date, nullable=False)

    renter = relationship("User", back_populates="reviews")
    equipment = relationship("Equipment", back_populates="reviews")


# Views (из лабы 2)
class EquipmentCatalogView(Base):
    __tablename__ = "v_equipment_catalog"
    __table_args__ = {"extend_existing": True}

    equipment_id = Column(Integer, primary_key=True)
    equipment_name = Column(String(256))
    category_name = Column(String(256))
    price_per_day = Column(Numeric(10, 2))
    owner_name = Column(String(512))
    avg_rating = Column(Numeric(10, 2))


class RentalDetailsView(Base):
    __tablename__ = "v_rental_details"
    __table_args__ = {"extend_existing": True}

    rental_id = Column(Integer, primary_key=True)
    customer_name = Column(String(512))
    item_name = Column(String(256))
    start_date = Column(Date)
    end_date = Column(Date)
    price_at_booking = Column(Numeric(10, 2))
    status = Column(String(50))


class ClientActivityView(Base):
    __tablename__ = "v_client_activity"
    __table_args__ = {"extend_existing": True}

    user_id = Column(Integer, primary_key=True)
    full_name = Column(String(512))
    city = Column(String(100))
    total_rentals = Column(Integer)
    total_spent = Column(Numeric(10, 2))
    last_rental_date = Column(Date)


DATABASE_URL = "postgresql://user:password@localhost:5432/bigdata_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
