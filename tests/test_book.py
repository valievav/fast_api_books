from src.books.schemas import BookCreateModel

books_prefix = f"/api/v1/books"


def test_get_all_books(test_client, fake_book_service, fake_db_session):
    response = test_client.get(
        url=f"{books_prefix}"
    )

    assert fake_book_service.get_all_books_called_once()
    assert fake_book_service.get_all_books_called_once_with(fake_db_session)


def test_create_book(test_client, fake_book_service, fake_db_session):
    book_data =     {
        "title": "The Color of Magic 222",
        "author": "Terry Pratchett",
        "publisher": "Corgi",
        "page_count": 287,
        "language": "English"
    }
    response = test_client.post(
        url=f"{books_prefix}",
        json=book_data
    )
    book_create_data = BookCreateModel(**book_data)

    assert fake_book_service.create_book_called_once()
    assert fake_book_service.create_book_called_once_with(book_create_data, fake_db_session)


def test_get_book(test_client, fake_book_service,test_book, fake_db_session):
    response = test_client.get(f"{books_prefix}/{test_book.uid}")

    assert fake_book_service.get_book_called_once()
    assert fake_book_service.get_book_called_once_with(test_book.uid,fake_db_session)
