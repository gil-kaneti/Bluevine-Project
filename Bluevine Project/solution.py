import logging
import os
import calendar

from datetime import datetime

import requests
import pandas as pd


from dateutil import parser

from questions_solutions import get_all_solutions_functions_list, longest_word_in_sentence
from enums import BookDetails, Questions

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler('answers.txt', mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(file_handler)

    return logger

def fetch_data_from_open_library(isbn):
    """
    This function fetches data from Open Library API and returns the result as 2 dictionaries.
    The first dictionary contains the book details and the second dictionary contains extra data.
    :param isbn:
    :return: result_json, extra_data
    """
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    result_json = None
    extra_details_json = None
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            result_json = response.json()
            result_json = result_json.get(f'ISBN:{isbn}', {})
            if result_json:
                extra_details_json = fetch_extra_data(result_json,isbn)

            return result_json, extra_details_json

    except Exception:
        logger.exception(f"Failed to get data for ISBN: {isbn}")

    return result_json, extra_details_json


def fetch_extra_data(result_json,isbn):
    """
    Fetches additional book data from the Open Library API based on the book key.
    :param result_json: A dictionary containing book details, including the 'key' field used to
                        fetch extra data from the Open Library API.
    :return: A dictionary containing additional book data if the API call is successful, or
             None if the data cannot be fetched.
    """
    url = "https://openlibrary.org/"
    key = result_json.get(BookDetails.KEY.value, '')
    if key:
        url += key + '.json'
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.exception(f"Failed to get extra data for ISBN: {isbn}")# Since handling TimeoutException is the same, we catch general exception
            return None
    return None


def has_month_info(date_str):
    """
    Returns True if the date string contains month information, False otherwise.
    """
    months = [month for month in calendar.month_name if month] + [month for month in calendar.month_abbr if month]
    return any(month in date_str for month in months)


def parse_date_from_string(date_str):
    """
    Returns a parsed date object from the given date string, or None if parsing fails.
    Also returns a boolean indicating whether the date string contains month information.
    """
    parsed_date = None
    is_month_in_date = False

    if date_str:
        try:
            parsed_date = parser.parse(date_str, fuzzy=True, default=datetime(1900, 1, 1))
            is_month_in_date = has_month_info(date_str)
        except Exception as e:
            logger.exception(f"Failed to parse {date_str}: {e}")

    return parsed_date, is_month_in_date


def normalize_data(result_json, extra_details_json):
    full_details_dict = {}

    full_details_dict[BookDetails.TITLE.value] = result_json.get(BookDetails.TITLE.value, '')  # string

    # Author returns as list of dicts like: [{'url': 'url', 'name': 'JK rowling'}]
    authors = [author[BookDetails.NAME.value] for author in result_json.get(BookDetails.AUTHORS.value, [])
               if BookDetails.NAME.value in author]
    full_details_dict[BookDetails.AUTHORS.value] = authors

    publish_date_str = result_json.get(BookDetails.PUBLISH_DATE.value, None)  # default common value
    parsed_date, is_month_in_date = parse_date_from_string(publish_date_str)
    full_details_dict[BookDetails.PUBLISH_DATE.value] = parsed_date
    full_details_dict[BookDetails.IS_MONTH_INFO.value] = is_month_in_date

    goodreads_ids = result_json.get(BookDetails.IDENTIFIERS.value, {}).get(BookDetails.GOODREADS.value, [])
    full_details_dict[BookDetails.GOODREADS.value] = True if goodreads_ids else False

    publishers = [publisher[BookDetails.NAME.value] for publisher in result_json.get(BookDetails.PUBLISHERS.value, [])
                  if BookDetails.NAME.value in publisher]
    full_details_dict[BookDetails.PUBLISHERS.value] = publishers

    full_details_dict[BookDetails.NUMBER_OF_PAGES.value] = result_json.get(BookDetails.NUMBER_OF_PAGES.value, None)

    # The ISBN is a list of dicts like: [{'identifier': 'isbn', 'type': 'ISBN'}]
    # Finds only the rows where type is description
    description_dict = extra_details_json.get(BookDetails.DESCRIPTION.value, {}) if extra_details_json else {}
    # in some cases the description comes as a string, though the common case is a dict
    description = description_dict.get(BookDetails.VALUE.value, '') \
        if isinstance(description_dict,dict) else description_dict
    full_details_dict[BookDetails.DESCRIPTION.value] = description

    excerpts_list = result_json.get(BookDetails.EXCERPTS.value, [])
    excerpts = excerpts_list[0].get(BookDetails.TEXT.value, '') if excerpts_list else ''
    full_details_dict[BookDetails.FIRST_SENTENCE.value] = excerpts

    last_modified_dict = extra_details_json.get(BookDetails.LAST_MODIFIED.value, None) if extra_details_json else None
    last_modified_str = last_modified_dict.get(BookDetails.VALUE.value, None) if last_modified_dict else None
    last_modified = datetime.fromisoformat(last_modified_str) if last_modified_str else None
    full_details_dict[BookDetails.LAST_MODIFIED.value] = last_modified

    return full_details_dict


def get_file_lines_as_list(file_name):
    if not os.path.exists(file_name):
        logger.error("Could not find file {file_name} exiting...")
        return None

    with open(file_name, 'r') as file:
        lines = file.readlines()
        return [line.strip() for line in lines]


def answer_all_questions():
    """
    This is the main function that will run all relevant code pieces to fetch data from Open Library API,
    Answer all relevant questions and log the answers to screen and file.
    """
    isbn_list = get_file_lines_as_list("books-isbns.txt")
    normalized_data_list = []
    full_data_list = [fetch_data_from_open_library(isbn) for isbn in isbn_list]
    all_question_functions = get_all_solutions_functions_list()
    for result_json, extra_details_json in full_data_list:
        if result_json:
            normalized_data = normalize_data(result_json, extra_details_json)
            normalized_data_list.append(normalized_data)


    for idx, question in enumerate(Questions):
        df = pd.DataFrame(normalized_data_list)
        logger.info(question.value)
        answer = all_question_functions[idx](df)
        if isinstance(answer, pd.DataFrame):
            answer = answer.to_string(index=False)
        logger.info(f"Answer: \n {answer}")
        logger.info("--------------------------------")


if __name__ == '__main__':
    logger = get_logger()
    answer_all_questions()
