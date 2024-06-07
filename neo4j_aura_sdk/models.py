from typing import List

from pydantic import BaseModel


# Model Defintion Here:
#   https://neo4j.com/docs/aura/platform/api/specification/#/


class AuraError(BaseModel):
    message: str
    reason: str
    field: str


class AuraErrors(BaseModel):
    errors: List[AuraError]


# TODO: Exactly what interfaces should be exposed on this exception is TBD.
#       This is just a starting point.
class AuraApiException(Exception):
    def __init__(self, errors: AuraErrors):
        self.errors = errors
        super().__init__(errors)


class AuthResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str


class ListedTenant(BaseModel):
    id: str
    name: str


class TenantsResponse(BaseModel):
    data: List[ListedTenant]
