import uuid
from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src import app
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer, RoleChecker
from src.books.schemas import Book
from src.db.main import get_session

mock_db_session = Mock()
mock_user_service = Mock()
mock_book_service = Mock()

access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(['admin'])

app.dependency_overrides[get_session] = mock_db_session
app.dependency_overrides[access_token_bearer] = Mock()
app.dependency_overrides[refresh_token_bearer] = Mock()
app.dependency_overrides[role_checker] = Mock()


@pytest.fixture
def fake_db_session():
    return mock_db_session


@pytest.fixture
def fake_user_service():
    return mock_user_service


@pytest.fixture
def fake_book_service():
    return mock_book_service


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def test_book():
    return Book(
        uid=uuid.uuid4(),
        user_uid=uuid.uuid4(),
        title="Fun book fixture title",
        author='Fixture author',
        publisher='Fixture House',
        page_count=200,
        language="English",
        create_date=datetime.now(),
        update_date=datetime.now()
    )
