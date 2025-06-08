from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, func
from models import Base, Favorite, User, BotStats
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")
        self.async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def create_tables(self):
        """Создает таблицы в базе данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_favorites(self, user_id: int) -> list:
        async with self.async_session() as session:
            result = await session.execute(
                select(
                    Favorite.user_id,
                    Favorite.recipe_id,
                    Favorite.title,
                    Favorite.image, 
                    Favorite.source_url  
                ).where(Favorite.user_id == user_id)
            )
            return [dict(row) for row in result.mappings()]

    async def add_favorite(self, user_id: int, recipe_data: dict) -> bool:
        async with self.async_session() as session:
            # Проверяем, не существует ли уже такой записи
            if await self._is_favorite_exists(session, user_id, recipe_data['id']):
                return False
                
            favorite = Favorite(
                user_id=user_id,
                recipe_id=recipe_data['id'],
                title=recipe_data['title'],
                image=recipe_data.get('image'),
                source_url=recipe_data.get('source_url') 
            )
            session.add(favorite)
            await session.commit()
            return True

    async def remove_favorite(self, user_id: int, recipe_id: int) -> bool:
        """Удаляет рецепт из избранного"""
        async with self.async_session() as session:
            favorite = await self._get_favorite(session, user_id, recipe_id)
            if favorite:
                await session.delete(favorite)
                await session.commit()
                logger.info(f"Removed favorite: {user_id}, {recipe_id}")
                return True
            logger.debug(f"Favorite not found: {user_id}, {recipe_id}")
            return False

    async def _is_favorite_exists(self, session: AsyncSession, 
                               user_id: int, recipe_id: int) -> bool:
        """Проверяет существование записи"""
        result = await session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.recipe_id == recipe_id
            )
        )
        return result.scalar() is not None

    async def _get_favorite(self, session: AsyncSession, 
                         user_id: int, recipe_id: int) -> Favorite:
        """Возвращает объект Favorite"""
        result = await session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.recipe_id == recipe_id
            )
        )
        return result.scalar()

    async def remove_all_favorites(self, user_id: int) -> int:
        """Удаляет все избранные рецепты пользователя. Возвращает количество удаленных"""
        async with self.async_session() as session:
            # Получаем все избранные для подсчета
            result = await session.execute(
                select(Favorite).where(Favorite.user_id == user_id)
            )
            favorites = result.scalars().all()
            count = len(favorites)
            
            # Удаляем все
            for favorite in favorites:
                await session.delete(favorite)
            
            await session.commit()
            logger.info(f"Removed all {count} favorites for user {user_id}")
            return count

    # методы для пользователей
    
    async def add_or_update_user(self, user_data: dict) -> bool:
        """Добавляет нового пользователя или обновляет существующего"""
        async with self.async_session() as session:
            # Проверяем существует ли пользователь
            result = await session.execute(
                select(User).where(User.user_id == user_data['user_id'])
            )
            user = result.scalar()
            
            if user:
                # Обновляем существующего
                user.username = user_data.get('username')
                user.first_name = user_data.get('first_name')
                user.last_name = user_data.get('last_name')
                user.last_activity = datetime.utcnow()
            else:
                # Создаем нового
                user = User(
                    user_id=user_data['user_id'],
                    username=user_data.get('username'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    first_seen=datetime.utcnow(),
                    last_activity=datetime.utcnow()
                )
                session.add(user)
            
            await session.commit()
            return True

    async def ban_user(self, user_id: int) -> bool:
        """Блокирует пользователя"""
        async with self.async_session() as session:
            result = await session.execute(
                update(User).where(User.user_id == user_id).values(is_banned=True)
            )
            await session.commit()
            return result.rowcount > 0

    async def unban_user(self, user_id: int) -> bool:
        """Разблокирует пользователя"""
        async with self.async_session() as session:
            result = await session.execute(
                update(User).where(User.user_id == user_id).values(is_banned=False)
            )
            await session.commit()
            return result.rowcount > 0

    async def is_user_banned(self, user_id: int) -> bool:
        """Проверяет заблокирован ли пользователь"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User.is_banned).where(User.user_id == user_id)
            )
            banned = result.scalar()
            return banned is True

    async def get_all_users(self) -> list:
        """Получает список всех пользователей"""
        async with self.async_session() as session:
            result = await session.execute(select(User))
            return [user for user in result.scalars().all()]

    # методы для статистики
    
    async def increment_stat(self, stat_name: str):
        """Увеличивает счетчик статистики"""
        async with self.async_session() as session:
            # Получаем или создаем запись статистики
            result = await session.execute(select(BotStats))
            stats = result.scalar()
            
            if not stats:
                stats = BotStats()
                session.add(stats)
            
            # Увеличиваем нужный счетчик
            if hasattr(stats, stat_name):
                current_value = getattr(stats, stat_name) or 0  # Если None, то 0
                setattr(stats, stat_name, current_value + 1)
                stats.last_updated = datetime.utcnow()
                
            await session.commit()

    async def get_bot_stats(self) -> Optional[Dict]:
        """Получает статистику бота"""
        async with self.async_session() as session:
            # Получаем статистику
            result = await session.execute(select(BotStats))
            stats = result.scalar()
            
            # Получаем количество пользователей
            result = await session.execute(select(func.count(User.id)))
            total_users = result.scalar() or 0
            
            # Получаем количество заблокированных
            result = await session.execute(
                select(func.count(User.id)).where(User.is_banned == True)
            )
            banned_users = result.scalar() or 0
            
            # Получаем количество избранных
            result = await session.execute(select(func.count(Favorite.id)))
            total_favorites = result.scalar() or 0
            
            if stats:
                return {
                    'total_users': total_users,
                    'banned_users': banned_users,
                    'total_favorites': total_favorites,
                    'total_commands': stats.total_commands,
                    'random_recipe_requests': stats.random_recipe_requests,
                    'ingredient_searches': stats.ingredient_searches,
                    'favorites_views': stats.favorites_views,
                    'last_updated': stats.last_updated
                }
            else:
                return {
                    'total_users': total_users,
                    'banned_users': banned_users,
                    'total_favorites': total_favorites,
                    'total_commands': 0,
                    'random_recipe_requests': 0,
                    'ingredient_searches': 0,
                    'favorites_views': 0,
                    'last_updated': datetime.utcnow()
                }