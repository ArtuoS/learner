from fastapi import APIRouter, Depends, HTTPException, Request, status

from schemas.authentication import LoginOutput, LoginSchema, RegisterOutput, RegisterSchema
from services.authentication import AuthenticationService

router = APIRouter()


def get_auth_service(request: Request) -> AuthenticationService:
    return request.app.state.auth_service


@router.post("/authentication/login", response_model=LoginOutput, status_code=status.HTTP_200_OK)
def login(
    login_input: LoginSchema,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    try:
        token = auth_service.login(login_input.email, login_input.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    return LoginOutput(access_token=token)


@router.post("/authentication/register", response_model=RegisterOutput, status_code=status.HTTP_201_CREATED)
def register(
    register_input: RegisterSchema,
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    try:
        token = auth_service.register(register_input.name, register_input.email, register_input.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return RegisterOutput(access_token=token)
