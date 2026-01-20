# main.py
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# ============================
# Настройка логирования
# ============================
logger = logging.getLogger("shop_api")
logger.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Лог в консоль (с цветами через uvicorn)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Лог в файл с ротацией (макс. 5 МБ, храним 5 старых файлов)
file_handler = RotatingFileHandler(
    "app.log",
    maxBytes=5_000_000,      # 5 МБ
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ============================
# FastAPI приложение
# ============================
app = FastAPI(title="Мой простой REST API с логированием")

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    description: Optional[str] = None

# "База данных" в памяти
products = [
    Product(id=1, name="Чайник", price=2500.0),
    Product(id=2, name="Тостер", price=3200.0)
]
next_id = 3


@app.get("/products", response_model=List[Product])
def get_all():
    logger.info("Запрос всех товаров | Всего товаров: %d", len(products))
    return products


@app.get("/products/{product_id}", response_model=Product)
def get_one(product_id: int):
    product = next((p for p in products if p.id == product_id), None)
    if not product:
        logger.warning("Попытка получить несуществующий товар | ID: %s", product_id)
        raise HTTPException(404, "Товар не найден")
    
    logger.info("Товар найден | ID: %s | Название: %s", product_id, product.name)
    return product


@app.post("/products", response_model=Product, status_code=201)
def create(product: Product):
    global next_id
    product.id = next_id
    next_id += 1
    products.append(product)
    
    logger.info("Создан новый товар | ID: %d | Название: %s | Цена: %.2f", 
                product.id, product.name, product.price)
    return product


@app.put("/products/{product_id}", response_model=Product)
def update(product_id: int, updated: Product):
    product = next((p for p in products if p.id == product_id), None)
    if not product:
        logger.warning("Попытка обновить несуществующий товар | ID: %s", product_id)
        raise HTTPException(404, "Товар не найден")
    
    old_name = product.name
    updated.id = product_id
    products[products.index(product)] = updated
    
    logger.info("Товар обновлён | ID: %d | Было: %s → Стало: %s", 
                product_id, old_name, updated.name)
    return updated


@app.delete("/products/{product_id}")
def delete(product_id: int):
    global products
    product = next((p for p in products if p.id == product_id), None)
    if not product:
        logger.warning("Попытка удалить несуществующий товар | ID: %s", product_id)
        raise HTTPException(404, "Товар не найден")
    
    products = [p for p in products if p.id != product_id]
    logger.info("Товар удалён | ID: %s | Название: %s", product_id, product.name)
    return {"message": "Удалено"}


# ============================
# Запуск
# ============================
if __name__ == "__main__":
    logger.info("Запуск сервера FastAPI...")
    uvicorn.run("lab5:app", host="127.0.0.1", port=8000, reload=True, log_level="info")