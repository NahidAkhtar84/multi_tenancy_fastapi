from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = True
    is_superuser: bool = False
    full_name: str | None = None


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    pass


class UserProfileUpdate(UserBase):
    email: EmailStr | None = None
    full_name: str | None = None


class UserPassUpdate(BaseModel):
    old_password: str
    new_password: str


class UserInDBBase(UserBase):
    id: int | None = None

    class Config:
        orm_mode = True


class UserRegister(BaseModel):
    full_name: str
    password: str


class ResetPassword(BaseModel):
    new_password: str
