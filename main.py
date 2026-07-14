"""
Самостоятельный скрипт для заполнения БД реалистичными тестовыми данными.
Не требует management-команды — просто настраивает Django вручную.

Установка зависимостей:
    pip install Faker Pillow

Куда положить:
    Можно оставить в корне проекта (там же, где находится папка marketplace_product
    с manage.py внутри) — путь определяется автоматически, переносить не нужно.

Запуск (из любой директории):
    python main.py
    python main.py --products 100
    python main.py --images-per-product-min 5 --images-per-product-max 6
    python main.py --flush
"""

import argparse
import os
import random
import sys
from decimal import Decimal
from io import BytesIO

# --- Настройка Django ---
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Ищем папку, где лежит manage.py (сам django-проект), чтобы Python
# нашёл marketplace_product_app и settings, откуда бы скрипт ни запускался.
_candidates = [
    SCRIPT_DIR,                          # main.py лежит рядом с manage.py
    SCRIPT_DIR / 'marketplace_product',  # main.py лежит на уровень выше
]
PROJECT_DIR = next((c for c in _candidates if (c / 'manage.py').exists()), SCRIPT_DIR)
sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_product.settings')

import django
django.setup()

from django.core.files.base import ContentFile
from django.db import transaction

from marketplace_product_app.models import Category, Product, ProductImage

try:
    from faker import Faker
except ImportError:
    raise SystemExit("Не найден пакет Faker. Установите: pip install Faker")

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Не найден пакет Pillow. Установите: pip install Pillow")


fake = Faker('ru_RU')

CATEGORIES_DATA = {
    "Электроника": [
        "Смартфон", "Ноутбук", "Наушники", "Планшет", "Умные часы",
        "Powerbank", "Веб-камера", "Беспроводная клавиатура", "Игровая мышь",
    ],
    "Одежда": [
        "Футболка", "Джинсы", "Куртка", "Свитер", "Платье",
        "Кроссовки", "Рубашка", "Шорты", "Толстовка",
    ],
    "Дом и сад": [
        "Постельное белье", "Кастрюля", "Настольная лампа", "Плед",
        "Набор посуды", "Ваза", "Декоративная подушка", "Органайзер",
    ],
    "Красота и здоровье": [
        "Крем для лица", "Шампунь", "Парфюм", "Электробритва",
        "Фен для волос", "Массажер", "Зубная щетка электрическая",
    ],
    "Спорт и отдых": [
        "Гантели", "Коврик для йоги", "Велосипед", "Туристический рюкзак",
        "Палатка", "Скакалка", "Фитнес-браслет",
    ],
    "Игрушки и хобби": [
        "Конструктор", "Настольная игра", "Плюшевая игрушка",
        "Пазл 1000 деталей", "Радиоуправляемая машина", "Набор для рисования",
    ],
}

BRANDS = [
    "TechnoPro", "UrbanStyle", "HomeComfort", "NatureLine", "PlayMax",
    "EcoLife", "MaxPower", "TrendGoods", "NovaTech", "PrimeChoice",
]

DESCRIPTION_INTROS = [
    "Отличное качество по доступной цене.",
    "Идеально подходит для повседневного использования.",
    "Товар от проверенного производителя с гарантией качества.",
    "Стильный дизайн и практичность в одном изделии.",
    "Пользуется высоким спросом благодаря надежности и удобству.",
]


def generate_placeholder_image(seed_text, size=(600, 600)):
    random.seed(hash(seed_text) % (2 ** 32))
    color = tuple(random.randint(100, 230) for _ in range(3))
    random.seed()

    image = Image.new("RGB", size, color=color)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)

    filename = f"{fake.uuid4()}.jpg"
    return filename, ContentFile(buffer.read(), name=filename)


@transaction.atomic
def seed(products_count, min_images, max_images, flush):
    if flush:
        print('Удаляю существующие данные...')
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

    print('Создаю категории...')
    categories = []
    for cat_name in CATEGORIES_DATA.keys():
        category, created = Category.objects.get_or_create(category_name=cat_name)
        if created or not category.category_image:
            filename, file_content = generate_placeholder_image(cat_name)
            category.category_image.save(filename, file_content, save=True)
        categories.append(category)
    print(f'  Категорий готово: {len(categories)}')

    print('Создаю товары...')
    used_articles = set(Product.objects.values_list('article_number', flat=True))
    created_products = 0
    created_images = 0

    for _ in range(products_count):
        category = random.choice(categories)
        product_type = random.choice(CATEGORIES_DATA[category.category_name])
        brand = random.choice(BRANDS)
        product_name = f"{product_type} {brand} {fake.word().capitalize()}"

        article_number = random.randint(100000, 999999)
        while article_number in used_articles:
            article_number = random.randint(100000, 999999)
        used_articles.add(article_number)

        price = Decimal(random.randrange(500, 150000, 50))

        description = (
            f"{random.choice(DESCRIPTION_INTROS)} {fake.paragraph(nb_sentences=4)} "
            f"Артикул: {article_number}. Бренд: {brand}."
        )

        product = Product.objects.create(
            category=category,
            product_name=product_name,
            price=price,
            article_number=article_number,
            is_official=random.choice([True, False]),
            description=description,
            owner=random.randint(1, 20),
        )

        images_count = random.randint(min_images, max_images)
        for i in range(images_count):
            filename, file_content = generate_placeholder_image(f"{product_name}-{i}")
            image_obj = ProductImage(product=product)
            image_obj.product_image.save(filename, file_content, save=True)
            created_images += 1

        created_products += 1
        if created_products % 10 == 0:
            print(f'  ...создано товаров: {created_products}/{products_count}')

    print(f'  Товаров создано: {created_products}')
    print(f'  Изображений товаров создано: {created_images}')
    print('Заполнение базы данных завершено успешно!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Заполнение БД тестовыми данными')
    parser.add_argument('--products', type=int, default=40)
    parser.add_argument('--images-per-product-min', type=int, default=5)
    parser.add_argument('--images-per-product-max', type=int, default=6)
    parser.add_argument('--flush', action='store_true')
    args = parser.parse_args()

    seed(
        products_count=args.products,
        min_images=args.images_per_product_min,
        max_images=args.images_per_product_max,
        flush=args.flush,
    )