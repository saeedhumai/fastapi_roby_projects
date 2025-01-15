# Import necessary modules for the FastAPI application
from typing import Optional  # Allows fields to be optional (can be None)
from fastapi import FastAPI, Path, Query, HTTPException, Body  # FastAPI framework components:
    # Path - for path parameter validation
    # Query - for query parameter validation
    # HTTPException - for raising HTTP errors
    # Body - for request body handling
from pydantic import BaseModel, Field  # Pydantic for data validation:
    # BaseModel - base class for request/response models
    # Field - for detailed field validation
from starlette import status  # HTTP status codes for responses
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI application instance
# This creates the core application object that handles all API functionality
app = FastAPI()

# 2. Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the Book class that represents our core data structure
# This is a regular Python class (not a Pydantic model) used for storing book data
class Book:
    # Define class attributes with type hints for better code understanding
    # These type hints help with IDE support and code documentation
    id: int          # Unique identifier for each book
    title: str       # Book title
    author: str      # Book author
    description: str # Brief description of the book
    rating: int      # Rating from 1-5
    published_date: int  # Year of publication

    # Constructor method to create new Book instances
    # Takes all required fields and sets up the object's attributes
    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


# BookRequest class for validating incoming book data
# Inherits from Pydantic BaseModel for automatic data validation
class BookRequest(BaseModel):
    # Define fields with validation rules using Pydantic Field
    id: Optional[int] = Field(
        description='ID is not needed on create',
        default=None  # Makes the field optional with None as default
    )
    title: str = Field(min_length=3)  # Title must be at least 3 characters long
    author: str = Field(min_length=1)  # Author name must not be empty
    description: str = Field(
        min_length=1,
        max_length=100  # Description must be between 1-100 characters
    )
    rating: int = Field(
        gt=0,
        lt=6  # Rating must be between 1-5
    )
    published_date: int = Field(gt=1999 , lt = 2024)

    # Configuration for API documentation
    # Provides an example of valid book data in the Swagger UI
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                "published_date":2024
            }
        }
    }
        






# In-memory database of books
# In a real application, this would be replaced with a proper database
BOOKS = [
    # Sample book data with various attributes
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 5, 2030),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5, 2030),
    Book(3, 'Master Endpoints', 'codingwithroby', 'A awesome book!', 5, 2029),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2028),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2027),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 2026)
]


# GET endpoint to retrieve all books
# Returns the complete list of books with 200 OK status
@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS  # Simply returns the entire BOOKS list


@app.get("/books/published_year/{year}", status_code=status.HTTP_200_OK)
async def get_books_by_years(year: int):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == year:
            books_to_return.append(book)
    if not books_to_return:
        raise HTTPException(status_code=404, detail='No books found for this year')
    return books_to_return
@app.get("/books/published_year/{year}")
async def get_books_by_years(year:int ):
    for i in BOOKS:
        if i.published_date == year:
            return i
    raise HTTPException(status_code=404, detail='Item not found')

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book 
    raise HTTPException(status_code=404, detail='Item not found')


# GET endpoint to retrieve a specific book by ID
# Path parameter validation ensures book_id is positive
# @app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
# async def read_book(book_id: int = Path(gt=0)):
#     # Search through books to find matching ID
#             return book
#     for book in BOOKS:
#         if book.id == book_id:
#     # If book not found, raise 404 error
#     raise HTTPException(status_code=404, detail='Item not found')


# GET endpoint to retrieve books by rating
# Query parameter validation ensures rating is between 1-5
@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    # Filter books by matching rating
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return



# POST endpoint to create a new book
# Returns 201 Created status code on success
@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    # Convert BookRequest to Book object using model_dump()
    # ** unpacks the dictionary into keyword arguments
    new_book = Book(**book_request.model_dump())
    # Add book to list after generating ID
    BOOKS.append(find_book_id(new_book))

# Helper function to generate a new book ID
# Takes a Book object and sets its ID based on existing books
def find_book_id(book: Book):
    # If no books exist, use ID 1; otherwise increment last book's ID
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.get("books/update_book")
async def update_book(book:BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id==book.id:
            BOOKS[i]=book
            book_changed=True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')



# # PUT endpoint to update an existing book
# # Returns 204 No Content status code on success
# @app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
# async def update_book(book: BookRequest):
#     book_changed = False
#     # Search for book by ID and update if found
#     for i in range(len(BOOKS)):
#         if BOOKS[i].id == book.id:
#             BOOKS[i] = book
#             book_changed = True
#     # Raise 404 error if book not found
#     if not book_changed:
#         raise HTTPException(status_code=404, detail='Item not found')


@app.put("books/update_book")
async def update_book(book:BookRequest):
    for i in range(len(BOOKS)):
        if BOOKS[i].id==book.id:
            BOOKS[i]=book
            book_changed=True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')






# DELETE endpoint to remove a book
# Returns 204 No Content status code on success
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    # Search for book by ID and remove if found
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    # Raise 404 error if book not found
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')










def main():
    import uvicorn
    # Change host to "127.0.0.1" instead of "0.0.0.0" for local development
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
