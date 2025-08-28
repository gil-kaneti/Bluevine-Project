import calendar

from enums import BookDetails
import re


def longest_word_in_sentence(sentence):
    # Split hyphenated words into individual parts
    words = re.findall(r'[a-zA-Z]+', sentence)
    longest_word = max(words, key=len) if words else ''
    return longest_word

# Function to solve question 1, counts the number of books in the CSV file
def question1_sol(df):
    unique_books = df.drop_duplicates(subset=[BookDetails.TITLE.value], keep='first')
    return  len(unique_books)

# Function to solve question 2, finds the book with the most isbn and return his title
def question2_sol(df):
    group_by_title = df.groupby(BookDetails.TITLE.value)
    return group_by_title.size().idxmax()


# Function to solve question 3, counts the number of books with missing Goodreads ID
def question3_sol(df):
    count = df[BookDetails.GOODREADS.value].sum() # Since True/False is treated like 1/0 when using sum.
    return count


# Function to solve question 4, counts the number of books with multiple authors
def question4_sol(df):
    # Count rows where the 'author' column contains more than one author
    count = df[df[BookDetails.AUTHORS.value].str.len() > 1].shape[0]
    return count


# Function to solve question 5, counts the number of books per publisher and returns a dictionary with publisher names as keys and counts as values
def question5_sol(df):
    # Explode the 'publishers' list into multiple rows, i.e. if 'harry potter'
    # has 2 publishers, we will get a line per publisher
    df_exploded = df.explode(BookDetails.PUBLISHERS.value)
    publisher_counts = df_exploded[BookDetails.PUBLISHERS.value].value_counts()
    return publisher_counts.reset_index().rename(columns={'index': 'publisher',
                                                          BookDetails.PUBLISHERS.value: 'publisher'})


# Function to solve question 6, returns the median number of pages
def question6_sol(df):
    df_pages = df.dropna(subset=[BookDetails.NUMBER_OF_PAGES.value])
    return df_pages[BookDetails.NUMBER_OF_PAGES.value].median()


# Function to solve question 7, returns the month with the most books published
def question7_sol(df):
    # Filter only rows where month info exists, using copy to avoid pandas warning for df slicing
    df_with_month = df[df[BookDetails.IS_MONTH_INFO.value]].copy()
    # Extract month from parsed_date
    df_with_month['publish_month'] = df_with_month[BookDetails.PUBLISH_DATE.value].dt.month
    # Find the most common month (by month number)
    most_common_month_num = df_with_month['publish_month'].value_counts().idxmax()
    # Get the month name (like "May")
    most_common_month_name = calendar.month_name[most_common_month_num]

    return most_common_month_name


# Function to solve question 8, finds the longest word in the title and first sentence of each book,
# and returns the title(s) of the book(s) containing the longest word
def question8_sol(df):
    df = df.dropna(subset=[BookDetails.DESCRIPTION.value, BookDetails.FIRST_SENTENCE.value], how='all').copy()

    # Combine 'description' and 'first_sentence' into one column for processing
    df['combined_text'] = df[BookDetails.DESCRIPTION.value].fillna('') + ' ' + df[
        BookDetails.FIRST_SENTENCE.value].fillna('')
    # Find the longest word in the combined text
    df['longest_word'] = df['combined_text'].apply(longest_word_in_sentence)
    df['longest_word'] = df['longest_word'].fillna('')
    max_length = df['longest_word'].str.len().max()

    # Filter rows where the longest word has the maximum length
    result = df[df['longest_word'].str.len() == max_length]

    return result[[BookDetails.TITLE.value, 'longest_word']]

# Function to solve question 9, finds the last published book and returns its title and publish year
def question9_sol(df):
    df = df.dropna(subset=[BookDetails.PUBLISH_DATE.value])
    # Find the row with the latest publication year
    latest_book = df.loc[df[BookDetails.PUBLISH_DATE.value].idxmax()]
    # Return the title of the last published book
    return latest_book[BookDetails.TITLE.value]

def question10_sol(df):
    """"
    This function solves question 10. It takes a dataframe as input and returns the year with the most books updated.
    """
    df = df.dropna(subset=[BookDetails.LAST_MODIFIED.value])
    most_updated_year = df[BookDetails.LAST_MODIFIED.value].dt.year.max()

    return most_updated_year


def question11_sol(df):
    """
    This function solves question 11. It takes a dataframe as input and returns the title of the second book
     published by the author with the highest number of books published.
    But since not all dates are full, we might get an answer which is not 100% accurate.
    For example, if Author1 has 3 books and publish dates are 2019, 2019, 2019 -> second one is not guaranteed.
    :param df:
    :return:
    """
    # Step 1: Explode authors so each author has one row
    df_exploded = df.explode(BookDetails.AUTHORS.value).copy()

    # Step 2: Group by author, count unique titles
    author_title_counts = df_exploded.groupby(BookDetails.AUTHORS.value)['title'].nunique()

    # Step 3: Find the author with the highest number of different titles
    top_author = author_title_counts.idxmax()

    # Step 4: Filter original exploded df to only rows with that author
    df_top_author = df_exploded[df_exploded[BookDetails.AUTHORS.value] == top_author]

    # Step 5: Drop missing publish dates and sort by publish date
    df_top_author = df_top_author.dropna(subset=[BookDetails.PUBLISH_DATE.value]).copy()
    df_top_author = df_top_author.sort_values(by=BookDetails.PUBLISH_DATE.value)

    # Step 6: Pick the second book (index 1 after sorting)
    if len(df_top_author) >= 2:
        second_published_title = df_top_author.iloc[1]['title']
    else:
        second_published_title = None  # or handle case if not enough books

    return second_published_title

def question12_sol(df):
    # Step 1: Explode publishers
    df = df.explode(BookDetails.PUBLISHERS.value).copy()

    # Step 2: Explode authors
    df = df.explode(BookDetails.AUTHORS.value).copy()

    # Step 3: Group by (publisher, author) and count
    pair_counts = df.groupby([BookDetails.PUBLISHERS.value, BookDetails.AUTHORS.value]).size()

    # Step 4: Find the (publisher, author) pair with the highest number of books
    most_common_pair = pair_counts.idxmax()

    return most_common_pair


def get_all_solutions_functions_list():
    return [question1_sol, question2_sol, question3_sol, question4_sol, question5_sol, question6_sol,
            question7_sol, question8_sol, question9_sol, question10_sol, question11_sol, question12_sol]