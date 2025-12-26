##################################################
# IMPORT
##################################################
import datetime
import json
import os
import random
import re
import sys
import textwrap
import time
from collections import Counter

##################################################
# CLASSES
##################################################
class Quote:
    def __init__(self, text, page_number):
        self.text = text
        self.page = page_number

    ##################################################
    # string representation
    ##################################################
    def __repr__(self):
        return f"Quote(text={self.text}, page_number={self.page})"

class Book:
    def __init__(self, title):
        self.title = title
        self.author = ""
        self.folder = ""
        self.file_id = ""
        self.annotation = ""
        self.pages_count = 0
        self.published_date = 0
        self.file_modified_time = 0
        self.have_read_time = 0
        self.activity_time = 0
        self.q_per_page = 0.0
        self.quotes = []
        self.short_quotes = []
        self.selected_set = set()
        self.first_q_date = 0
        self.last_q_date = 0
        self.rating = 0.0
        self.ratings_count = 0.0

    def add_quote(self, text, page_number, is_long=False):
        quote = Quote(text, page_number)
        if is_long:
            self.quotes.append(quote)
        else:
            self.short_quotes.append(quote)

    def get_all_quotes_list(self):
        return self.quotes + self.short_quotes

    def get_random_q(self):
        all_q = self.get_all_quotes_list()
        return self._rnd_q(all_q)

    def get_random_short_q(self):
        return self._rnd_q(self.short_quotes)

    def _rnd_q(self, quotes_list):
        quotes_left = 0
        random_quote = None
        unselected_quotes = [q for q in quotes_list if q not in self.selected_set]
        if unselected_quotes:
            random_quote = random.choice(unselected_quotes)
            self.selected_set.add(random_quote)
            quotes_left = len(unselected_quotes) - 1
        return random_quote, quotes_left

    def clear_selected_set(self):
        self.selected_set.clear()

    ##################################################
    # @property decorator is used to define a method
    # that can be accessed like an attribute
    ##################################################
    @property
    def total_q(self):
        return (len(self.quotes) + len(self.short_quotes))

    @property
    def total_short_q(self):
        return len(self.short_quotes)

    ##################################################
    # string representation
    ##################################################
    def __repr__(self):
        return f"Book(title={self.title}, quotes={len(self.quotes)})"


##################################################
# GLOBALS, CONSTANTS
##################################################
# The Collection will be a simple list containing the Book instances
The_Collection = []
Folders = {}
All_Quotes_Count = 0
Short_Quotes_Count = 0
Centuries = set()
Ratings_Available = False

# options order can be varied here, a dictionary will be built based
# on this list, with each option's list index as the key and the
# corresponding element from this list as the value (string)
Options = [
    "Random / All Quotes",
    "Random / Selected Author",
    "Random / Selected Folder",
    "Book / every quote",
    "Book / quote distribution",
    "Book / list by property",
    "Statistics",
    "Search",
    "Exit"
    ]

Lengths = ["Any length", "Short only"]

LENGTH_TO_ATTR = {
    "Any length": "total_q",
    "Short only": "total_short_q"
    }

LENGTH_TO_METHOD = {
    "Any length": "get_random_q",
    "Short only": "get_random_short_q"
    }

BOOK_RENAME_DICTIONARY = {
    "Dummy Author - Dummy Title":
        "Author - Title"
    }

MAX_CHAR_IN_SHORT_QUOTE = 300
ONE_DAY_IN_SECONDS = 86400
# 2024-02-23 0:00:00
READ_DATE_LIST_START = 1708642800

EXCLUDED_TITLES_FROM_READ_DURATION = {
    "Dummy Author - Dummy Title"
    }

EXCLUDED_TITLES_FROM_READ_DATE = {
    "Dummy Author - Dummy Title"
    }

EXCEPTION_TITLES_FOR_READ_DATE = {
    "Dummy Author - Dummy Title"
    }


####################################################################################################
# FUNCTIONS
####################################################################################################

##################################################
# FUNCTION: create the options dictionary
##################################################
def create_options_menu(opt_lst):
    result = {}
    counter = 1
    for element in opt_lst:
        if element != "Exit":
            result[str(counter)] = element
            counter += 1
        else:
            result['x'] = element
    return result


##################################################
# FUNCTION: build The Collection
##################################################
def build_the_collection():
    # these three are in the global scope
    global All_Quotes_Count
    global Short_Quotes_Count
    global Centuries
    global Ratings_Available

    # open and read the JSON file
    try:
        with open('library.json', 'r', encoding="utf8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)

    # get the folders dictionary, each value will be a set of book IDs
    for coll in data['colls']:
        Folders[coll['data']['coll_title']] = set(coll['docs'])

    for doc in data['docs']:
        if doc['data']['doc_active'] == 1:
            # Use regex to remove non-alphabet characters from the beginning of the title
            book_title = re.sub(r"^[^a-zA-Z]+", "", doc['data']['doc_file_name_title'])

            # handle renamed books, book_title is the default return
            book_title = BOOK_RENAME_DICTIONARY.get(book_title, book_title)

            # add the book to The Collection (which is a list of instances)
            this_book = Book(book_title)
            The_Collection.append(this_book)

            # store additional data
            this_book.file_id = doc['uri']
            this_book.author = doc['data'].get('user_authors') or doc['data'].get('doc_authors')
            this_book.annotation = doc['data'].get('doc_annotation', "")

            # store file date as a date object, activity time as a simple timestamp
            aux_date = datetime.datetime.fromtimestamp(doc['data'].get('file_modified_time') / 1000)
            this_book.file_modified_time = aux_date
            this_book.activity_time = doc['data'].get('doc_activity_time')

            # get the folder, if available
            if Folders:
                for folder, ids in Folders.items():
                    if this_book.file_id in ids:
                        this_book.folder = folder
                        break

            # get pages count if available
            try:
                doc_data = json.loads(doc['data']['doc_position'])
                this_book.pages_count = doc_data['pagesCount']
            except (KeyError, ValueError, IndexError, TypeError, AttributeError):
                this_book.pages_count = 0

            # get goodreads data if available
            try:
                review_note = doc['reviews'][0]['note_body']
                this_book.published_date = int(review_note.split(';')[0].strip())
                this_book.rating = float(review_note.split(';')[1].strip())
                this_book.ratings_count = float(review_note.split(';')[2].strip().replace('k', '.'))
            except (KeyError, ValueError, IndexError, TypeError, AttributeError):
                this_book.published_date = 0
                this_book.rating = 0.0
                this_book.ratings_count = 0.0

            # get the citations
            if len(doc['citations']) > 0:
                quote_dates = []
                for citation in doc['citations']:
                    q_is_long = len(citation['note_body']) > MAX_CHAR_IN_SHORT_QUOTE
                    this_book.add_quote(citation['note_body'], citation['note_page'], q_is_long)
                    quote_dates.append(citation['note_insert_time'])

                # sort the dates list to easily access first and last, convert to seconds
                quote_dates.sort()
                this_book.first_q_date = quote_dates[0] / 1000
                this_book.last_q_date = quote_dates[-1] / 1000

                # calculate the q/p ratio, avoid division by zero
                if this_book.pages_count > 0:
                    this_book.q_per_page = this_book.total_q / this_book.pages_count

            # check if current doc was finished or not
            if doc['data'].get('doc_have_read_time') != 0:
                if this_book.title in EXCEPTION_TITLES_FOR_READ_DATE:
                    # Dec 23, 2025 07:00:00 AM GMT+01:00
                    aux_date = datetime.datetime.fromtimestamp(1766473200)
                elif ((this_book.last_q_date - this_book.first_q_date) > ONE_DAY_IN_SECONDS and
                       this_book.title not in EXCLUDED_TITLES_FROM_READ_DATE ):
                    # use last quote date if available
                    aux_date = datetime.datetime.fromtimestamp(this_book.last_q_date)
                else:
                    # use default date
                    # # Dec 23, 2025 07:00:00 AM GMT+01:00
                    aux_date = datetime.datetime.fromtimestamp(1766473200)
            else:
                aux_date = datetime.datetime.fromtimestamp(0)

            # add the constructed date
            this_book.have_read_time = aux_date

    # gather quote counts
    for book in The_Collection:
        All_Quotes_Count += book.total_q
        Short_Quotes_Count += book.total_short_q

        # check and process goodreads data
        if book.published_date != 0:
            century = int(book.published_date / 100) + 1
            if century not in Centuries:
                Centuries.add(century)
        if book.rating > 0.0:
            Ratings_Available = True

    # set is ready, convert it to a list
    Centuries = list(Centuries)

    # alphabetical order by title
    The_Collection.sort(key=lambda book: book.title)

##################################################
# FUNCTION: get terminal width function def.
##################################################
def get_terminal_columns():
    """
    Return the current column size of the terminal window.
    """
    try:
        return os.get_terminal_size().columns
    except OSError:
        # Fallback to a default column size
        return 90

##################################################
# FUNCTION: print separator using hyphens
##################################################
def print_separator_line():
    print('-' * get_terminal_columns(), end='')

##################################################
# FUNCTION: print options menu
##################################################
def print_options():
    for key, value in Options_Menu.items():
        if key.isdigit():
            print(f" {int(key)}  -->  {value}")
        else:
            print(f" {key}  -->  {value}")

##################################################
# FUNCTION: get option
##################################################
def get_option():
    prompts = [
        " Choice is the act of hesitation.. ",
        " ..that we make before making a decision. ",
        " It is a mental wobble. ",
        " And so we are always in a dither of doubt.. ",
        " ..as to whether we are behaving the right way.. ",
        " ..or doing the right thing, and so on and so forth... "
        ]

    string = "Choose an option:"
    print(f"{string}\n{'-' * len(string)}")
    print_options()
    print_separator_line()

    iteration = 0
    while True:
        string = prompts[iteration] if iteration < len(prompts) else " It's time to choose an option.. "
        opt = input(string)
        iteration += 1

        if opt.isdigit() and opt in Options_Menu:
            return Options_Menu.get(opt, "Something went wrong")
        elif opt == 'x' or iteration >= 20:
            sys.exit()

##################################################
# FUNCTION: print count of quotes in passed list
##################################################
def print_quote_count(count):
    string = f"Random selection from {count} quotes"
    print(f"{string}\n{'-' * len(string)}\n")


##################################################
# FUNCTION: print random quotes
##################################################
def print_random_quotes(books, method, print_title=True):
    while True:
        # random book for every iteration (or same book for a single-element list)
        book = random.choice(books)
        random_quote, quotes_left = getattr(book, method)()

        # get random returns None if there is no more quote left in that book
        if random_quote:
            print_wrapped_text(random_quote.text)

            # "delay" title print, but exit immediately if requested
            if is_exit_requested():
                return

            # print the "delayed" title if needed
            if print_title:
                print(f"{book.title}   / {quotes_left} left /")
                print(f"{'-' * len(book.title)}")
                if is_exit_requested():
                    return

            # separate printed title from the next quote
            print('\n')
        else:
            # refresh the list if no more quote is in the book
            books.remove(book)

        if not books:
            input("All quotes were printed.")
            return

##################################################
# FUNCTION: check exit request ('x')
##################################################
def is_exit_requested():
    response = input()
    return response and response[0] == 'x'


##################################################
# FUNCTION: print wrapped text
##################################################
def print_wrapped_text(text):
    print(*textwrap.wrap(f"{text}\n", get_terminal_columns() - 1), sep='\n')


##################################################
# FUNCTION: print items with selection numbers
##################################################
def print_selection_list(items, option=""):
    for i, item in enumerate(items):
        print(f"{i + 1:2d}.  -->  {item}{get_century_suffix(item) if option else ''}")

############################################################
# FUNCTION: return century suffix
############################################################
def get_century_suffix(cent):
    # special case for 11th, 12th, 13th, etc.
    if 10 <= cent % 100 <= 20:
        return "th"
    else:
        # regular case for 1st, 2nd, 3rd, etc.
        suffixes = {1: "st", 2: "nd", 3: "rd"}
        return suffixes.get(cent % 10, "th")

##################################################
# FUNCTION: print items with selection numbers
##################################################
def get_user_choice(input_type, max_value, zero_is_valid=False, extra_prompt=""):
    number = None
    min_value = 0 if zero_is_valid else 1
    while True:
        article = ' a' if input_type != 'quote length' else ''
        n_suffix = 'n' if input_type == 'author' else ''
        user_input = input(f"\nChoose{article}{n_suffix} {input_type}{extra_prompt}: ")
        if user_input.isdigit():
            number = int(user_input)
            if min_value <= number <= max_value:
                # input is in the range
                break
            else:
                print("You should choose more wisely.")
        elif input_type not in ["folder", "century"] or (input_type == "folder" and extra_prompt == ""):
            print("This is not a valid number..")
        else:
            break
    print_separator_line()
    return number

############################################################
# FUNCTION: user can choose a book from the printed list
############################################################
def choose_a_book(attr):
    print(" 0.  -->  random book")

    if attr == "with_quotes":
        books = [book for book in The_Collection if book.total_q > 0]
    elif attr == "with_annotation":
        books = [book for book in The_Collection if book.annotation]

    titles = [book.title for book in books]
    print_selection_list(titles)
    choice = get_user_choice("book", len(books), zero_is_valid=True)
    return books[choice - 1] if choice else random.choice(books)

############################################################
# FUNCTION: user can choose an author
############################################################
def choose_an_author(authors):
    print_selection_list(authors)
    choice = get_user_choice("author", len(authors))
    return authors[choice - 1]

############################################################
# FUNCTION: user can choose a property
############################################################
def choose_a_property():
    global Ratings_Available

    properties = [
        "added on",
        "reading now",
        "finished list",
        "read duration",
        "publish date" if len(Centuries) else "",
        "number of quotes",
        "quote/page ratio",
        "rating" if Ratings_Available else "",
        "folder" if Folders else ""
        ]

    print_selection_list(properties)
    choice = get_user_choice("property", len(properties))
    return properties[choice - 1]

############################################################
# FUNCTION: user can choose a folder
############################################################
def choose_a_folder(allow_select_all=True):
    print_selection_list(list(Folders))
    choice = get_user_choice("folder", len(Folders), extra_prompt=" (or press Enter to list all)" if allow_select_all else "")
    return list(Folders.keys())[choice - 1] if choice else None

############################################################
# FUNCTION: user can choose a century
############################################################
def choose_a_century():
    print_selection_list(Centuries, option = "get_suffix")
    choice = get_user_choice("century", len(Centuries), extra_prompt=" (or press Enter to list all)")
    return Centuries[choice - 1] if choice else None

############################################################
# FUNCTION: user can choose between quote lengths
############################################################
def choose_quote_length():
    print_selection_list(Lengths)
    choice = get_user_choice("quote length", len(Lengths))
    return Lengths[choice - 1] if choice else None

##################################################
# FUNCTION: print statistics of The Collection
##################################################
def print_statistics():
    # create auxiliary dictionaries
    author_quotes = {}
    folder_q_count = {}
    folder_book_count = {}

    # gather book counts
    books_with_quotes, books_20th, books_21th = 0, 0, 0
    for book in The_Collection:
        if book.total_q > 0:
            books_with_quotes += 1
        if 1900 <= book.published_date < 2000:
            books_20th += 1
        if book.published_date >= 2000:
            books_21th += 1

        # gather folders statistics
        for folder in Folders:
            if book.folder == folder:
                folder_q_count[folder] = folder_q_count.get(folder, 0) + book.total_q
                folder_book_count[folder] = folder_book_count.get(folder, 0) + 1
                break

        if book.total_q > 0:
            author_quotes[book.author] = author_quotes.get(book.author, 0) + book.total_q

    ##################################################
    # books
    ##################################################
    string = "Statistics"
    print(f"{string}\n{'-' * len(string)}\n")
    books_count = len(The_Collection)
    print_stat_line("Books in The Collection", f"{books_count:4d} / 100%")
    if books_21th:
        print_stat_line("Books from the 21th century", f"{books_21th:4d} / {get_percentage_string(books_21th, books_count)}")
    if books_20th:
        print_stat_line("Books from the 20th century", f"{books_20th:4d} / {get_percentage_string(books_20th, books_count)}")
    print_stat_line("Books with quotes", f"{books_with_quotes:4d} / {get_percentage_string(books_with_quotes, books_count)}", blank_line=True)
    
    # Sort folders by book count (descending)
    folder_book_count = dict(sorted(folder_book_count.items(), key=lambda item: item[1], reverse=True))
    print_folder_dict(folder_book_count, books_count)
    
    ##################################################
    # quotes
    ##################################################
    input()
    print_stat_line("Quotes in total", f"{All_Quotes_Count:4d} / 100%")
    string = f"{Short_Quotes_Count:4d} / {get_percentage_string(Short_Quotes_Count, All_Quotes_Count)}"
    print_stat_line(f"Quotes that are less than {MAX_CHAR_IN_SHORT_QUOTE} characters", string)
    print_stat_line("Quotes per book on average", f"{round(All_Quotes_Count / books_with_quotes):4d}", blank_line=True)

    
    # Sort folders by total quotes (descending)
    folder_q_count = dict(sorted(folder_q_count.items(), key=lambda item: item[1], reverse=True))
    print_folder_dict(folder_q_count, All_Quotes_Count)

    ##################################################
    # authors
    ##################################################
    input()
    string = "Top 15 Authors"
    print(f"{string}\n{'-' * len(string)}")

    # Sort authors by total quotes (descending)
    author_quotes = dict(sorted(author_quotes.items(), key=lambda item: item[1], reverse=True))    
    cumulative = 0
    for i, (author, count) in enumerate(author_quotes.items(), start=1):
        cumulative += count

        print_stat_line(
            f" --> {author}",
            f"{count:4d} / {get_percentage_string(count, All_Quotes_Count, digit=2)}"
            f" / {get_percentage_string(cumulative, All_Quotes_Count, digit=2)}"
        )
        if i >= 15:
            break

    ##################################################
    # words
    ##################################################
    input()
    string = "Top 30 most used words"
    print(f"\n{string}\n{'-' * len(string)}")
    words_to_omit = [
        "that", "your", "this", "their", "they", "with", "have",
        "from", "what", "there", "will", "when", "which", "more",
        "only", "into", "because", "them", "cannot", "become", "other",
        "make", "every", "then", "than", "these", "through", "even",
        "always", "about", "must", "need", "very", "without", "such",
        "know", "things", "some", "something", "those", "want", "others",
        "find", "just", "becomes"
        ]

    all_quotes_list = []
    for book in The_Collection:
        all_quotes_list += book.get_all_quotes_list()
    all_text = ' '.join(quote.text for quote in all_quotes_list)

    pattern = r"\b(?:" + '|'.join(words_to_omit) + r")\b"
    updated_text = re.sub(pattern, "", all_text, flags=re.IGNORECASE)

    # convert to lowercase and split by non-word characters (e.g., punctuation)
    words = re.findall(r"\b\w{4,}\b", updated_text.lower())
    top_30 = Counter(words).most_common(30)

    # get word counts for each book, omitted words from top_30 will be
    # also counted, but there will be no match during later check
    book_word_counts = {}
    for book in The_Collection:
        quotes_text = ' '.join(quote.text for quote in book.get_all_quotes_list()).lower()
        word_counts = Counter(re.findall(r'\b\w{4,}\b', quotes_text))
        book_word_counts[book.title] = word_counts

    # process the top 30 words
    for word, count in top_30:
        print(f" --> {count:3d} x {word}", end='')

        # find the book with the most occurrence of the word
        max_count = 0
        book_string = ""
        for book in The_Collection:
            word_count = book_word_counts[book.title].get(word, 0)
            if word_count > max_count:
                max_count = word_count
                book_string = book.title

        # Print related data in one line
        print(f"{' ' * (12-len(word))}{max_count:3d} / {book_string}")

    ##################################################
    # all books
    ##################################################
    # input("\n")
    # for book in The_Collection:
        # print(f"  -->  {book.published_date:4d}  /  {book.pages_count:4d} pages  /  {book.title}")
    # print_separator_line()

def print_stat_line(string, value, blank_line=False):
    print(f"{string}  {'-' * (48-len(string))}>  {value}")
    if blank_line:
        print()

def get_percentage_string(count, total, digit=3):
    return f"{int((count/total)*100):{digit}d}%" if total else "0%"
    
def print_folder_dict(folder_dict, total):
    cumulative = 0
    for folder in folder_dict:
        cumulative += folder_dict[folder]
        print_stat_line(
            f" --> {folder}",
            f"{folder_dict[folder]:4d} / {get_percentage_string(folder_dict[folder], total)}"
        )
    print("\n")

####################################################################################################
# MAIN
####################################################################################################
Options_Menu = create_options_menu(Options)
build_the_collection();

##################################################
# main loop for printing
##################################################
while True:
    # start with empty window
    os.system('cls')

    # print the main title and options
    string = f"== The Collection =="
    separator = '=' * len(string)
    print(f"{separator}\n{string}\n{separator}\n")

    # get option also prints the options menu
    option = get_option();
    print_separator_line()

    ##################################################
    # random quotes
    ##################################################
    if (option == "Random / All Quotes" or
        option == "Random / Selected Author" or
        option == "Random / Selected Folder"):

        if option == "Random / All Quotes":
            books = [book for book in The_Collection if book.total_q > 0]
        elif option == "Random / Selected Author":
            # avoid duplicates using set (built with set comprehension)
            authors = sorted(list({book.author for book in The_Collection if book.author and book.total_q > 0}))
            selected_author = choose_an_author(authors)
            books = [book for book in The_Collection if (book.author == selected_author and book.total_q > 0)]
        elif option == "Random / Selected Folder":
            selected_folder = choose_a_folder(allow_select_all=False) if Folders else None
            books = [book for book in The_Collection if (book.folder == selected_folder and book.total_q > 0)]

        length = choose_quote_length()
        print_quote_count(sum(getattr(book, LENGTH_TO_ATTR[length]) for book in books))
        print_random_quotes(books, LENGTH_TO_METHOD[length])

    ##################################################
    # selected book section
    ##################################################
    elif (option == "Book / every quote" or
          option == "Book / quote distribution"):

        # get a book from the printed list
        selected_book = choose_a_book("with_quotes")

        ##################################################
        # all quotes in page order
        ##################################################
        if option == "Book / every quote":
            # open output file with context manager
            with open(f"{selected_book.title}.txt", "w", encoding="utf8") as f_output:
                # create a list sorted by page number of all quotes in the book
                sorted_by_page = sorted(selected_book.get_all_quotes_list(), key=lambda quote: quote.page)

                print(selected_book.title)
                print('-' * len(selected_book.title))
                f_output.write(f"{selected_book.title}\n")
                f_output.write(f"{'-' * len(selected_book.title)}\n")

                for i, quote in enumerate(sorted_by_page):
                    string = f"{i + 1} / {len(sorted_by_page)}  (p.{str(quote.page)})"
                    print(string)
                    print_wrapped_text(quote.text)
                    print()
                    f_output.write(f"{string}\n")
                    f_output.write(f"{quote.text}\n\n")

        ##################################################
        # quote distribution
        ##################################################
        elif option == "Book / quote distribution":
            print(f"{selected_book.title}\n{'-' * len(selected_book.title)}\n")

            # use terminal width as the base of the diagram size
            space = "    "
            columns = get_terminal_columns() - 10
            rows = round(columns * 0.2)
            res = selected_book.pages_count / columns

            # collect the distribution of quotes based on calculated resolution
            # use length of each quote instead of simply just the numbers
            q_distr = []
            for i in range(columns):
                q_distr.append(0)
                start_page = res * i
                end_page = res * (i + 1)
                for quote in selected_book.get_all_quotes_list():
                    if (quote.page > start_page) and (quote.page <= end_page):
                        q_distr[i] += len(quote.text)

            # map the distribution from (0) to (rows)
            old_min, old_max = min(q_distr), max(q_distr)
            new_min, new_max = 0, rows
            mapped_distr = [(new_max - new_min) * (x - old_min) / (old_max - old_min) + new_min for x in q_distr]

            print(f"{space}↑")
            # range is exclusive of the end value, but it's not a problem that rows number
            # will not be reached, because in this way, compare value (new max - i) will
            # not reach zero, so a row full of '*' character will not be printed
            for i in range(rows):
                row_str_list = []
                for j in range(columns):
                    row_str_list.append('*' if mapped_distr[j] >= (new_max - i) else ' ')

                # print the updated row immediately
                print(f"{space}|{''.join(row_str_list)}")

            print(f"{space}{'-' * columns}→")
            print(f"{space}1{' ' * (columns - len(str(selected_book.pages_count)) + 1)}{selected_book.pages_count}")

    ##################################################
    # generate book list by chosen property
    ##################################################
    elif option == "Book / list by property":

        book_property = choose_a_property()

        if book_property == "added on":
            sorted_books = sorted(The_Collection, key=lambda book: book.file_modified_time, reverse=True)
        elif book_property == "reading now":
            sorted_books = sorted(The_Collection, key=lambda book: book.published_date, reverse=True)
        elif book_property == "finished list":
            sorted_books = sorted(The_Collection, key=lambda book: book.have_read_time, reverse=True)
        elif book_property == "read duration":
            sorted_books = sorted(The_Collection, key=lambda book: book.first_q_date, reverse=True)
        elif book_property == "publish date":
            sorted_books = sorted(The_Collection, key=lambda book: book.published_date, reverse=True)
            century = choose_a_century()
        elif book_property == "number of quotes":
            sorted_books = sorted(The_Collection, key=lambda book: book.total_q, reverse=True)
        elif book_property == "quote/page ratio":
            sorted_books = sorted(The_Collection, key=lambda book: book.q_per_page, reverse=True)
        elif book_property == "rating":
            sorted_books = sorted(The_Collection, key=lambda book: book.rating, reverse=True)
        elif book_property == "folder":
            sorted_books = sorted(The_Collection, key=lambda book: book.title, reverse=False)

        # choose function returns none if all is requested
        not_an_exception = book_property not in ["read duration", "reading now", "finished list"]
        folder = choose_a_folder() if (Folders and not_an_exception) else None

        while True:
            for book in sorted_books:
                if not folder or book.folder == folder:
                    # print book data according to chosen property
                    if book_property == "added on":
                        print(f"  -->  {book.file_modified_time.strftime('%Y-%b-%d')}  /  {book.title}")

                    elif book_property == "reading now":
                        if (book.activity_time != 0) and (book.have_read_time.year == 1970):
                            print(f"  -->  "
                                  f"{book.published_date:4d}  /  "
                                  f"{book.rating:.2f}  /  "
                                  f"{book.ratings_count:>{6}}k  /  "
                                  f"{book.pages_count:4d} pages  /  "
                                  f"{book.title}")

                    elif book_property == "finished list" or book_property == "continued_as_publish_date_of_finished":
                        if book.have_read_time.year > 1970:
                            if book_property == "finished list":
                                print(f"  -->  {book.have_read_time.strftime('%Y-%b-%d')}  /  {book.title}")
                            else:
                                print(f"  -->  {book.published_date}  /  {book.title}")

                    elif book_property == "read duration":
                        if ( book.first_q_date > READ_DATE_LIST_START and
                            (book.last_q_date - book.first_q_date) > ONE_DAY_IN_SECONDS and
                             book.title not in EXCLUDED_TITLES_FROM_READ_DURATION and
                             book.have_read_time.year > 1970):
                            dt_first = datetime.datetime.fromtimestamp(book.first_q_date)
                            elapsed_days = (book.have_read_time - dt_first).days + 1
                            if dt_first.year == book.have_read_time.year:
                                dt_string = f"{dt_first.strftime('%Y %b.%d')} - {book.have_read_time.strftime('%b.%d')}"
                            else:
                                dt_string = f"{dt_first.strftime('%Y %b.%d')} - {book.have_read_time.strftime('%Y %b.%d')}"

                            print(f"  -->  {dt_string}{' ' * (25-len(dt_string))}  /  "
                                  f"{book.title}{' ' * (62-len(book.title))}"
                                  f"/ {book.pages_count:4d} pages  /  {int((book.pages_count / elapsed_days)+0.5):2d} / day")

                    elif book_property == "publish date":
                        if century:
                            date_match = ((century - 1) * 100) <= book.published_date < (century * 100)
                        if not century or date_match:
                            date_data = f"{book.published_date:4d}" if book.published_date else " N/A"
                            pages_count = f"{book.pages_count:4d}" if book.pages_count else " N/A"
                            print(f"  -->  {date_data}  /  {pages_count} pages  /  {book.title}")

                    elif book_property == "number of quotes":
                        if book.total_q > 0:
                            print(f"  -->  {book.total_q:3d}  /  {book.title}")

                    elif book_property == "quote/page ratio":
                        if book.q_per_page > 0.0:
                            # remove funny character
                            clean_title = book.title.replace('\u200b', '').strip()
                            string = (f"  -->  {book.q_per_page:.3f}  /  {clean_title}")
                            print(f"{string}{' ' * (85-len(string))} ( {book.total_q:3d} / {book.pages_count:4d} )")

                    elif book_property == "rating" or book_property == "continued_as_ratings_count":
                        print(f"  -->  {book.rating:.2f}  /  {book.ratings_count:>{6}}k  /  {book.title}")
                    
                    elif book_property == "folder":
                        date_data = f"{book.published_date:4d}" if book.published_date else " N/A"
                        pages_count = f"{book.pages_count:4d}" if book.pages_count else " N/A"
                        print(f"  -->  {date_data}  /  {pages_count} pages  /  {book.title}")
                        

            if book_property != "rating" and book_property != "finished list":
                break
            else:
                # rating and finished lists are special
                print_separator_line()
                input()
                if book_property == "rating":
                    # print based on ratings count in the second round
                    sorted_books = sorted(The_Collection, key=lambda book: book.ratings_count, reverse=True)
                    book_property = "continued_as_ratings_count"
                elif book_property == "finished list":
                    # print based on ratings count
                    sorted_books = sorted(The_Collection, key=lambda book: book.published_date, reverse=True)
                    book_property = "continued_as_publish_date_of_finished"
                else:
                    break

        print_separator_line()

    ##################################################
    # statistics
    ##################################################
    elif option == "Statistics":
        print_statistics()

    ##################################################
    # search
    ##################################################
    elif option == "Search":
        while True:
            search_prompt = "Search for at least 3 characters: "
            str_to_search = input(search_prompt).lower()
            print('-' * (len(search_prompt) + len(str_to_search)))

            if len(str_to_search) >= 3:
                counter = 0
                for book in The_Collection:
                    match_in_book = False

                    for quote in book.get_all_quotes_list():
                        quote_text = quote.text.lower()

                        if str_to_search in quote_text:

                            # check if it's the first match in this book
                            if not match_in_book:
                                print_separator_line()
                                print(f"{book.title}\n{'-' * len(book.title)}\n")
                                match_in_book = True

                            # print the quote with the search term highlighted
                            print_wrapped_text(quote.text.replace(str_to_search, str_to_search.upper()))
                            print('\n')

                            # use findall, because a quote may contain the searched word multiple times
                            counter += len(re.findall(str_to_search, quote_text))

                result = f"Matched {counter} time{'s' if counter > 1 else ''}."
                print(result if counter else "No match found.")
                print('-' * len(result) if counter else '')

            elif str_to_search == 'x':
                break
            else:
                print("Incorrect input.")
            print('\n')
            print_separator_line()

    ##################################################
    # error
    ##################################################
    elif option == "Something went wrong":
        print("Error.")

    ##################################################
    # hold on and clear sceen before next iteration
    ##################################################
    if (option != "Random / All Quotes"        and
        option != "Random / Short Quotes"      and
        option != "Random / Selected Author"   and
        option != "Random / Selected Folder"   and
        option != "Search"):
        input()

    # start over with next iteration
    for book in The_Collection:
        book.clear_selected_set()


    os.system('cls')
