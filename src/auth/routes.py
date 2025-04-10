from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from .dependencies import RefreshTokenBearer
from .schemas import User, UserCreateModel, UserLoginModel
from .service import UserService
from .utils import create_access_token, verify_password, REFRESH_TOKEN_EXPIRY

auth_router = APIRouter()
user_service = UserService()


@auth_router.post('/signup', response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User already exists')

    new_user = await user_service.create_user(user_data, session)
    return new_user


@auth_router.post('/login')
async def login_users(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    password = user_data.password
    user = await user_service.get_user(email, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    password_valid = verify_password(password, user.password_hash)
    if not password_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    data = {'email': email, 'user_uid': str(user.uid)}
    access_token = create_access_token(
        user_data=data
    )
    refresh_token = create_access_token(
        user_data=data,
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
    )
    return JSONResponse(
        content={
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'email': user.email,
                'uid': str(user.uid)
            }
        }
    )


@auth_router.get('/refresh_access_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    """
    Get access token based on valid refresh token
    """
    expiry_ts = token_details['exp']
    if datetime.fromtimestamp(expiry_ts) < datetime.now():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid or expired refresh token')

    new_access_token = create_access_token(user_data=token_details['user'])
    return JSONResponse(
        content={'access_token': new_access_token}
    )
