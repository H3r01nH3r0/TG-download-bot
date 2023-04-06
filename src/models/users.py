from pydantic import BaseModel


class BaseUser(BaseModel):
    user_id: int
    connection_name: str
    connection_file: str


class CreateUser(BaseUser):
    pass


class UpdateUser(BaseUser):
    pass


class User(BaseUser):
    id: int

    class Config:
        orm_mode = True
