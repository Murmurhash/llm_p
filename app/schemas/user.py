from pydantic import BaseModel, EmailStr


class UserPublic(BaseModel):
    """Public user representation returned by the API (no password / hash)."""

    id: int
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}
