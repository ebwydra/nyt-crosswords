import json
import sqlite3 as sqlite

DBNAME = 'data/puzzles.db'

def get_all_answer_clue_tups():
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
    SELECT Answer, Clue, Length
    FROM AnswerCluePairs
    '''
    results = cur.execute(statement)
    result_list = results.fetchall() # list of tuples: (ANSWER, Clue, Length)
    conn.close()
    return result_list

def get_answer_clue_tups_for_year(year):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
    SELECT Answer, Clue, Length
    FROM AnswerCluePairs LEFT JOIN Puzzles ON AnswerCluePairs.PuzzId = Puzzles.Id
    WHERE Year = \"{}\"
    '''.format(year)
    results = cur.execute(statement)
    result_list = results.fetchall() # list of tuples: (ANSWER, Clue, Length)
    conn.close()
    return result_list

# Attempts to parse user input (string) as a year between 1976 and 2018; returns None if not
def process_year_input(year_str):
    if year_str == "": # If the year is left blank...
        return None
    else: # If something was entered...
        try: # First try parsing it as an integer
            year = int(year_str)
            if 1976 <= year <= 2018: # If the year is in the valid range...
                return year
            else: # If integer does not correspond to a valid year...
                return None
        except: # If the input couldn't be coerced to an integer...
            return None

# Cleans up user input search string to all caps, trims whitespace
def process_string_input(word_str):
    # Strip any whitespace
    trimmed_word = word_str.strip()
    char_list = []
    for char in trimmed_word:
        if char != " ":
            char_list.append(char)
    clean_word = "".join(char_list)
    return clean_word

# Key for sorting list of tuples (clue, num of times clue appeared) by number of times clue appeared (largest first)
def second_elem(clue_count_tuple):
    return clue_count_tuple[1]

# Converts raw list of clue strings into list of (Clue, # appearances) tuples (alphabetical for ties)
def sort_clues(unsorted_clue_list):
    unique_clues_sorted = []
    sorted_clues = sorted(unsorted_clue_list) # alphabetical order
    for clue in sorted_clues:
        if clue not in unique_clues_sorted:
            unique_clues_sorted.append(clue)
    #print(unique_clues_sorted)
    clue_count_tups = []
    for unique_clue in unique_clues_sorted:
        counter = 0
        for clue in sorted_clues:
            if unique_clue == clue:
                counter += 1
        clue_count = (unique_clue, counter)
        clue_count_tups.append(clue_count)
    #print(clue_count_tups)
    clue_count_tups_sorted = sorted(clue_count_tups, key=second_elem, reverse=True)
    #print(clue_count_tups_sorted)
    return clue_count_tups_sorted

# Takes in list of clues sorted by number of appearances and a desired number of results
def get_top_n_clues_for_word(all_clues, n):
    if all_clues:
        if n > len(all_clues):
            top_n_clues = all_clues
        elif 0 < n <= len(all_clues):
            top_n_clues = all_clues[0:n]
        else:
            top_n_clues = None
    else:
        top_n_clues = None
    return top_n_clues

# Queries database and returns top n clues for a given word in a given year or for all years
def get_clues_for_word(word, n=1000, year=None):
    # Retrieve results from db
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    if year: # retrieve results for specific year
        statement = '''
        SELECT Clue
        FROM AnswerCluePairs LEFT JOIN Puzzles ON AnswerCluePairs.PuzzId = Puzzles.Id
        WHERE Answer LIKE \"{}\"
        AND Year LIKE \"{}\"
        '''.format(word, year)
    else: # retrieve results for all years
        statement = '''
        SELECT Clue
        FROM AnswerCluePairs
        WHERE Answer LIKE \"{}\"
        '''.format(word)

    results = cur.execute(statement)
    result_tup_list = results.fetchall() # List of tuples
    conn.close()
    # Convert list of tuples to list of strings
    result_list = []
    for tup in result_tup_list:
        clue_str = tup[0]
        result_list.append(clue_str)
    # Sort the list by number of appearances
    sorted_clues = sort_clues(result_list)
    # Get top n clues
    top_clues = get_top_n_clues_for_word(sorted_clues, n)
    return top_clues

# Queries database for n most common answers for a given year and number of letters
def get_most_common_answers(length=None, n=1000, year=None):
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    if length == 15: # Greater than or equal to 15
        if year: #
            statement = '''
            SELECT Answer, COUNT(*) AS num_appearances
            FROM AnswerCluePairs LEFT JOIN Puzzles ON AnswerCluePairs.PuzzId = Puzzles.Id
            WHERE Length >= 15 AND Year LIKE \"{}\"
            GROUP BY Answer
            ORDER BY num_appearances DESC
            '''.format(year)
        else:
            statement = '''
            SELECT Answer, COUNT(*) AS num_appearances
            FROM AnswerCluePairs LEFT JOIN Puzzles ON AnswerCluePairs.PuzzId = Puzzles.Id
            WHERE Length >= 15
            GROUP BY Answer
            ORDER BY num_appearances DESC
            '''
    elif length:
        if year: # Length and year are specified
            statement = '''
            SELECT Answer, COUNT(*) AS num_appearances
            FROM AnswerCluePairs LEFT JOIN Puzzles ON AnswerCluePairs.PuzzId = Puzzles.Id
            WHERE Length LIKE \"{}\" AND Year LIKE \"{}\"
            GROUP BY Answer
            ORDER BY num_appearances DESC
            '''.format(length, year)
        else: # Length but no year:
            statement = '''
            SELECT Answer, COUNT(*) AS num_appearances
            FROM AnswerCluePairs
            WHERE Length LIKE \"{}\"
            GROUP BY Answer
            ORDER BY num_appearances DESC
            '''.format(length)
    else:
        if year: # Year but no length
            statement = '''
            SELECT Answer, COUNT(*) AS num_appearances
            FROM AnswerCluePairs LEFT JOIN Puzzles ON AnswerCluePairs.PuzzId = Puzzles.Id
            WHERE Year LIKE \"{}\"
            GROUP BY Answer
            ORDER BY num_appearances DESC
            '''.format(year)
        else: # No year and no length
            statement = '''
            SELECT Answer, COUNT(*) AS num_appearances
            FROM AnswerCluePairs
            GROUP BY Answer
            ORDER BY num_appearances DESC
            '''
    results = cur.execute(statement)
    result_tup_list = results.fetchall()
    conn.close()
    if n < len(result_tup_list):
        result_list = result_tup_list[0:n]
    else:
        result_list = result_tup_list

    return result_list
