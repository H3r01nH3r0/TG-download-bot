from typing import List

from src import tables
from src.database import Session
from src.models.users import CreateUser, UpdateUser


class UsersService:
    def __init__(self):
        self.session = Session()

    async def create(self, user_data: CreateUser) -> tables.Users:
        user = tables.Users(
            **user_data.dict()
        )
        self.session.add(user)
        self.session.commit()
        return user

    async def _get(self, user_id: int, connection_name: str) -> tables.Users:
        user = (
            self.session
            .query(tables.Users)
            .filter_by(
                user_id=user_id,
                connection_name=connection_name
            )
            .first()
        )
        return user

    async def get(self, user_id: int, connection_name: str) -> tables.Users:
        return await self._get(user_id, connection_name)

    async def get_all(self, user_id: int) -> List[tables.Users]:
        users = (
            self.session
            .query(tables.Users)
            .filter_by(user_id=user_id)
            .all()
        )
        return users

    async def update(self,user_id: int, connection_name: str, user_data: UpdateUser) -> tables.Users:
        user = await self._get(user_id, connection_name)
        async for field, value, in user_data:
            setattr(user, field, value)
        self.session.commit()
        return user

    async def delete(self, user_id: int, connection_name: str) -> None:
        user = await self._get(user_id, connection_name)
        self.session.delete(user)
        self.session.commit()
