from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.celery_tasks import send_email_task
from src.config import Config
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from src.errors import (UserAlreadyExistsException, InvalidCredentialsException,
                        InvalidTokenException, UserNotFoundException, PasswordsDoNotMatchException)
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from .schemas import (UserBooks, UserCreateModel, UserLoginModel, EmailModel,
                      PasswordResetModel, PasswordResetConfirmModel)
from .service import UserService
from .utils import (create_access_token, verify_password, REFRESH_TOKEN_EXPIRY,
                    create_url_safe_token, decode_url_safe_token, generate_password_hash)

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin', 'user'])


@auth_router.post('/send_email')
async def send_email(emails: EmailModel):
    emails = emails.addresses
    subject = 'Welcome to the app'
    html_message = "<h1>Welcome to the BOOKLY</h1>"

    # run celery task (runs on background, no need to wait in order to send response)
    send_email_task.delay(emails, subject, html_message)

    return {'message': 'Email was sent successfully'}


@auth_router.post('/signup',
                  status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel,
                              session: AsyncSession = Depends(get_session)):
    """
    Create new user based on provided data
    """
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise UserAlreadyExistsException()

    new_user = await user_service.create_user(user_data, session)

    # send email verification link that user needs to follow to set is_verified=True
    token = create_url_safe_token({'email': email})
    link = f'http://{Config.DOMAIN}/api/v1/auth/verify/{token}'
    subject = 'Verify your email'
    html_message = f"""
    <h1> Verify your email </h1>
    <p> Please click this <a href="{link}">link</a> to verify your email </p>
    """

    # run celery task (runs on background, no need to wait in order to send response)
    send_email_task.delay([email], subject, html_message)

    return {
        'message': 'Account created. Please check email to verify your account.',
        'user': new_user
    }


@auth_router.get('/verify/{token}')
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    """
    Verifies user account via email link (sets is_verified=True).
    For this user needs to signup -> get link to their email -> follow the link to verify the email.
    """
    token_data = decode_url_safe_token(token)
    user_email = token_data.get('email')
    if not user_email:
        return JSONResponse(content={'message': 'Error occurred during verification'},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise UserNotFoundException()

    await user_service.update_user(user, {'is_verified': True}, session)
    return JSONResponse(content={'message': 'Account verified successfully!'},
                        status_code=status.HTTP_200_OK)


@auth_router.post('/login')
async def login_users(user_data: UserLoginModel,
                      session: AsyncSession = Depends(get_session)):
    """
    Login existing user (return access and refresh token)
    """
    email = user_data.email
    password = user_data.password
    user = await user_service.get_user_by_email(email, session)
    if not user:
        raise InvalidCredentialsException()

    password_valid = verify_password(password, user.password_hash)
    if not password_valid:
        raise InvalidCredentialsException()

    data = {
        'email': email,
        'user_uid': str(user.uid),
        'role': user.role,
    }
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


@auth_router.post('/refresh_access_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    """
    Get new access token based on valid refresh token
    """
    expiry_ts = token_details['exp']
    if datetime.fromtimestamp(expiry_ts) < datetime.now():
        raise InvalidTokenException()

    new_access_token = create_access_token(user_data=token_details['user'])
    return JSONResponse(
        content={'access_token': new_access_token}
    )


@auth_router.get('/me',
                 response_model=UserBooks,
                 dependencies=[Depends(role_checker)])
async def get_current_user(user = Depends(get_current_user)):
    """
    Get currently logged-in user details
    """
    return user


@auth_router.post('/logout')
async def revoke_token(token_data: dict = Depends(AccessTokenBearer())):
    """
    Logout existing user (blocklist current access token)
    """
    jti = token_data['jti']
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={
            'message': 'Logged out successfully'
        },
        status_code=status.HTTP_200_OK
    )


@auth_router.post('/password_reset')
async def password_reset_request(email_data: PasswordResetModel):
    """
    Reset password for requested email
    """
    email = email_data.email

    # send email with link to reset password
    token = create_url_safe_token({'email': email})
    link = f'http://{Config.DOMAIN}/api/v1/auth/confirm_password_reset/{token}'
    subject = 'Reset password'
    html_message = f"""
    <h1> Reset password for your account </h1>
    <p> Please click this <a href="{link}">link</a> to reset password </p>
    """

    # run celery task (runs on background, no need to wait in order to send response)
    send_email_task.delay([email], subject, html_message)

    return JSONResponse(
        content={'message': 'Password reset link sent. Please check your email to reset the password.'},
        status_code=status.HTTP_200_OK
    )


@auth_router.get('/confirm_password_reset/{token}')
async def confirm_password_reset(token: str, password_data: PasswordResetConfirmModel,
                                 session: AsyncSession = Depends(get_session)):
    """
    Confirm password reset to new password value.
    For this user needs to send password reset request -> get link to their email -> follow the link to reset the password.
    """
    new_password = password_data.new_password
    confirm_password = password_data.confirm_new_password
    if new_password != confirm_password:
        raise PasswordsDoNotMatchException()

    token_data = decode_url_safe_token(token)
    user_email = token_data.get('email')
    if not user_email:
        return JSONResponse(content={'message': 'Error occurred during password reset'},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise UserNotFoundException()

    new_hash = generate_password_hash(new_password)
    await user_service.update_user(user, {'password_hash': new_hash}, session)
    return JSONResponse(content={'message': 'Password updated successfully!'},
                        status_code=status.HTTP_200_OK)
