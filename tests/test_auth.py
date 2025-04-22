from src.auth.schemas import UserCreateModel

auth_prefix = f'api/v1/auth'


def test_create_user_account(fake_db_session, fake_user_service, test_client):
    signup_data = {
            "email": "johndoe@gmail.com",
            "username": "john doe",
            "first_name": "john",
            "last_name": "doe",
            "password": "12345"
        }
    response = test_client.post(
        url='{auth_prefix}/signup',
        json=signup_data,
    )
    user_create_data = UserCreateModel(**signup_data)

    assert fake_user_service.user_exists_called_once()
    assert fake_user_service.user_exists_called_once(signup_data['email'], fake_db_session)
    assert fake_user_service.create_user_called_once()
    assert fake_user_service.create_user_called_once(user_create_data, fake_db_session)
