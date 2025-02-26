import uuid

from sqlalchemy import select, insert
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.engine import Row

from api.errors import NotFoundException
from api.db.data import async_session_maker
from api.logger import logger


class BaseDAO:
    """Класс для работы с объектами БД"""

    model = None

    @classmethod
    async def get_all_objects(cls, **kwargs):
        """Возвращает все объекты модели."""
        async with (async_session_maker() as session):
            query = (select(cls.model.__table__.columns).filter_by(**kwargs)
                     ).order_by(cls.model.uid)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def get_object(cls, **kwargs):
        """Возвращает объект модели."""
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**kwargs)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def get_object_or_none(cls, **filters) -> Row | None:
        """Находит объект по фильтру или возвращает None"""

        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filters)
            result = await session.execute(query)

            return result.mappings().one_or_none()

    @classmethod
    async def add_object(cls, **kwargs):
        """Добавляет объект в БД."""
        try:
            async with async_session_maker() as session:
                query = insert(cls.model).values(**kwargs)
                await session.execute(query)
                await session.commit()
        except (SQLAlchemyError, Exception) as error:
            if isinstance(error, SQLAlchemyError):
                message = 'Database Exception'
            elif isinstance(error, Exception):
                message = 'Unknown Exception'
            message += ': Не удается добавить данные.'

            logger.error(
                message,
                extra={'table': cls.model.__tablename__},
                exc_info=True
            )
            return None

    @classmethod
    async def delete_object(cls, **kwargs):
        """Удаляет объект из БД."""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**kwargs)
            result = await session.execute(query)
            result = result.scalar()

            if not result:
                raise NotFoundException
            await session.delete(result)
            await session.commit()
            return 'Удаление успешно завершено.'

    @classmethod
    async def add_objects(cls, *data):
        """Добавляет объекты в БД."""
        try:
            query = insert(cls.model).values(*data).returning(cls.model.uid)
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                return result.mappings().first()
        except (SQLAlchemyError, Exception) as error:
            if isinstance(error, SQLAlchemyError):
                message = 'Database Exception'
            elif isinstance(error, Exception):
                message = 'Unknown Exception'
            message += ': Не удается добавить данные.'

            logger.error(
                message,
                extra={'table': cls.model.__tablename__},
                exc_info=True
            )
            return None

    @classmethod
    async def get_by_uid(cls, uid: uuid.UUID) -> Row | None:
        """Возвращает 1 объект по его uid или None"""

        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(uid=uid)
            result = await session.execute(query)

            return result.mappings().one_or_none()
