from fastapi import FastAPI, HTTPException, status
from typing import List
from model import Book, BookUpdateModel
from data import books
from datetime import datetime

app = FastAPI()


@app.get('/', response_model=dict)
async def get_root():
    return {'message': 'Root page of the books API'}


@app.get('/books', response_model=List[Book])
async def get_all_books():
    return books


@app.post('/books', response_model=Book, status_code= status.HTTP_201_CREATED)
async def create_book(book_data: Book):
    new_book = book_data.model_dump()  # convert to dict
    books.append(new_book)
    return new_book


@app.get('/books/{book_id}', response_model=Book)
async def get_book(book_id: int):
    for book in books:
        if book['id'] == book_id:
            return book

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')


@app.patch('/books/{book_id}')
async def update_book(book_id: int, update_data: BookUpdateModel):
    for book in books:
        if book['id'] == book_id:
            book['title'] = update_data.title
            book['author'] = update_data.author
            book['publisher'] = update_data.publisher
            book['page_count'] = update_data.page_count
            book['language'] = update_data.language
            book['entry_date'] = datetime.today().date().isoformat()
            return book

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')


@app.delete('/books/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book['id'] == book_id:
            books.remove(book)
            return {}

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')
