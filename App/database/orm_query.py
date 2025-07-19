from database.models import User, Iris
from werkzeug.security import generate_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

async def orm_add_user(session: AsyncSession, data: dict):
    session.add(User(
        first_name = data['first_name'],
        last_name = data['last_name'],
        user_name = data['user_name'],
        email = data['email'],
        password = generate_password_hash(data['password'])
    ))
    await session.commit()


async def orm_add_iris(session: AsyncSession, data: dict):
    new_iris = Iris(
        sepal_length = data['predictioniris'][0],
        sepal_width = data['predictioniris'][1],
        petal_length = data['predictioniris'][2],
        petal_width = data['predictioniris'][3],
        prediction = data['predictioniris'][4],
        user_name = data['user_name']
    )
    session.add(new_iris)
    await session.commit()


async def orm_get_user(session: AsyncSession, user_name: str):
    query = select(User).where(User.user_name == user_name)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_iris(session: AsyncSession, iris_id: int):
    query = select(Iris).where(Iris.id == iris_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_irises(session: AsyncSession, user_name: str):
    query = select(Iris).where(Iris.user_name == user_name)
    result = await session.execute(query)
    return result.scalars().all()