from enum import Enum

class BookDetails(Enum):
    TITLE = "title"
    AUTHORS = "authors"
    PUBLISH_DATE = "publish_date"
    GOODREADS = "goodreads"
    IDENTIFIERS = "identifiers"
    PUBLISHERS = "publishers"
    NUMBER_OF_PAGES = "number_of_pages"
    DESCRIPTION = "description"
    EXCERPTS = "excerpts" # First sentence
    LAST_MODIFIED = "last_modified"
    KEY = "key"
    VALUE = "value"
    TEXT = "text"
    NAME = "name"
    FIRST_SENTENCE = "first_sentence"
    IS_MONTH_INFO = "is_month_info"


class Questions(Enum):
    ONE = "1. How many different books are in the list?"
    TWO = "2. What is the book with the most number of different ISBNs?"
    THREE = "3. How many books don’t have a goodreads id?"
    FOUR = "4. How many books have more than one author?"
    FIVE = "5. What is the number of books published per publisher?"
    SIX = "6. What is the median number of pages for books in this list?"
    SEVEN = "7. What is the month with the most number of published books?"
    EIGHT = "8. What is/are the longest word/s that appear/s either in a book’s description or in the first sentence of a book? In which book (title) it appears?"
    NINE = "9. What was the last book published in the list?"
    TEN = "10. What is the year of the most updated entry in the list?"
    ELEVEN = "11. What is the title of the second published book for the author with the highest number of different titles in the list?"
    TWELVE = "12. What is the pair of (publisher, author) with the highest number of books published?"