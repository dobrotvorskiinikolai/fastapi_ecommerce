from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db

from app.models.reviews import Review as ReviewModel
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.auth import get_current_buyer, get_current_admin

router = APIRouter(
    prefix='/reviews',
    tags=['reviews'],
)

async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = round(avg_rating, 2)
    await db.commit()

@router.get('/', response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех отзывов
    """
    stmt = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    result = stmt.all()
    return result

@router.get('/products/{product_id}/reviews/', response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_reviews_by_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список отзывов по ID продукта
    """
    stmt_product = await db.scalars(select(ProductModel).where(ProductModel.is_active == True, ProductModel.id == product_id))
    result_product = stmt_product.first()
    if result_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    stmt = await db.scalars(select(ReviewModel).where(ReviewModel.product_id == product_id, ReviewModel.is_active == True))
    result = stmt.all()
    return result

@router.post('/', response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate, db: AsyncSession = Depends(get_async_db), current_user: UserModel = Depends(get_current_buyer)):
    """
    Добавление нового отзыва
    """
    stmt_product = await db.scalars(select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True))
    result_product = stmt_product.first()
    if result_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The product has been deleted or does not exist')
    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await update_product_rating(db, review.product_id)
    await db.commit()
    await db.refresh(db_review)
    return db_review

@router.delete('/reviews/{review_id}')
async def delete_review(review_id: int, db: AsyncSession = Depends(get_async_db), current_user: UserModel = Depends(get_current_admin)):
    """
    Удаление отзыва (доступно только админу)
    """
    stmt_review = await db.scalars(select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active == True))
    result_review = stmt_review.first()
    if result_review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.execute(
        update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False)
    )
    await update_product_rating(db, result_review.product_id)
    await db.commit()
    await db.refresh(result_review)
    return result_review