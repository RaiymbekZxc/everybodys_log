
from pydantic import BaseModel

class GoogleLoginRequest(BaseModel):
    googleId: str
    imageUrl: str
    email: str
    name: str
    givenName: str