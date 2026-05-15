from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.database import Base, engine
from app.models_sa import Product

Base.metadata.create_all(bind=engine)

with Session(engine) as session:
    if session.query(Product).count() == 0: 
        session.add_all([
            Product(title="Ноутбук", price=99999.99, count=5, description="Мощный игровой ноутбук"),
            Product(title="Мышка", price=1499.00, count=50, description="Беспроводная мышь")
        ])
        session.commit()
        print("Добавлено 2 продукта")