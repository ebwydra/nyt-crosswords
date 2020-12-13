import json

##########################
## Function definitions ##
##########################

# Returns puzzle for a given date as a dictionary
def get_puzzle_for_date(year=1976,month=1,day=1):
    year_str = str(year)
    month_str = str(month)
    if len(month_str) == 1: # if it's a one-digit month...
        month_str = "0" + month_str # add a 0 at the front
    day_str = str(day)
    if len(day_str) == 1: # if it's a one-digit day...
        day_str = "0" + day_str # add a 0 at the front
    date_string = year_str + '/' + month_str + '/' + day_str
    fname_date = 'data/' + date_string + '.json'
    try:
        puzz_file=open(fname_date, 'r', encoding='utf-8')
        puzz_contents = puzz_file.read()
        puzz_dict = json.loads(puzz_contents)
        puzz_file.close()
        return(puzz_dict)
    except:
        return None # If there's no puzzle for the date, return None

# Returns all puzzles (1976-2018) in a nested dictionary
def load_all_puzzles_into_nested_dict():
    puzz_dict = {}
    for year in range(1976, 2019):
        puzz_dict[year] = {}
        for month in range (1,13):
            puzz_dict[year][month] = {}
            for day in range(1,32):
                puzz = get_puzzle_for_date(year, month, day)
                if puzz != None:
                    date_str = str(year) + str(month) + str(day)
                    puzz_dict[year][month][day] = puzz
    return puzz_dict

# Helper function to clean up the clue format
def strip_number_from_clue(clue_str):
    clue_as_list = clue_str.split('. ') # split at every period with a space after it
    clue_as_list_clean = clue_as_list[1:] # drop the first element of the list (i.e., the number)
    clue_str_clean = '. '.join(clue_as_list_clean) # join the string back together
    return clue_str_clean

# Extracts all answer-clue pairs from a single puzzle dictionary as tuples and returns a list of tuples
def get_answer_clue_pairs(puzz):
    # Get all answers into big list
    answers_across_list = puzz['answers']['across']
    answers_down_list = puzz['answers']['down']
    answers_list = answers_across_list + answers_down_list
    # Get all clues into big list
    clues_across_list = puzz['clues']['across']
    clues_down_list = puzz['clues']['down']
    clues_across_down_list = clues_across_list + clues_down_list
    # Strip number from clues
    clues_list = [] # empty list for clean clues
    for clue in clues_across_down_list:
        clean_clue = strip_number_from_clue(clue)
        clues_list.append(clean_clue)
    # combine into a list of tuples
    zipped = zip(answers_list, clues_list)
    list_of_tups = list(zipped)
    return list_of_tups

# Converts top-level nested puzzle dictionary to list of (answer, clue) tuples
def convert_to_list_of_tups_all(nested_puzz_dict):
    all_answer_clue_pairs = []
    for year in nested_puzz_dict.keys():
        for month in nested_puzz_dict[year].keys():
            for day in nested_puzz_dict[year][month].keys():
                puzz_dict = nested_puzz_dict[year][month][day]
                answer_clue_pairs = get_answer_clue_pairs(puzz_dict) # Extract answer-clue pairs as tuples
                all_answer_clue_pairs += answer_clue_pairs # Add to list
    return all_answer_clue_pairs

# Converts single-year nested puzzle dictionary to list of (answer, clue) tuples
def convert_to_list_of_tups_for_year(nested_puzz_dict, year):
    all_answer_clue_pairs = []
    for month in nested_puzz_dict[year].keys():
        for day in nested_puzz_dict[year][month].keys():
            puzz_dict = nested_puzz_dict[year][month][day]
            answer_clue_pairs = get_answer_clue_pairs(puzz_dict) # Extract answer-clue pairs as tuples
            all_answer_clue_pairs += answer_clue_pairs # Add to list
    return all_answer_clue_pairs

# Converts list of answer-clue pair tuples to a dictionary where keys are answers and values are lists of clues
def convert_to_answer_dict(list_of_tups):
    # Make a dictionary of (unique) answers as keys with lists of clues as values
    answer_dict = {}
    for tup in list_of_tups:
        if tup[0] not in answer_dict.keys(): # if it's not in the dictionary...
            answer_dict[tup[0]] = [tup[1]] # add the key
        else: # if it's already in the dictionary...
            value = answer_dict[tup[0]] # get the existing value
            value.append(tup[1]) # append the new clue to the end of the list
            answer_dict[tup[0]] = value # replace the value in the dictionary
    return answer_dict

# Key for sorting list of tuples (clue, num of times clue appeared) by number of times clue appeared (largest first)
def second_elem(clue_count_tuple):
    return clue_count_tuple[1]

# Returns sorted list of tuples (clue, num of times clue appeared) for a given answer
def get_clues_for_word(answer_dict, word_str):
    word_cap = word_str.upper()
    if word_cap in answer_dict.keys():
        clues = answer_dict[word_cap]
        #print(clues)
        unique_clues_sorted = []
        sorted_clues = sorted(clues) # alphabetical order
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
    else:
        #print('Word not found!')
        return None

# Takes in output from get_clues_for_word() and a given number
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

# Find most common answers in a list of clue-answer tuples
def get_most_common_answers(tup_list):
    answer_count_dict = {} # Will contain answers as keys, counts as values
    for tup in tup_list: # Iterate through list of tuples
        if tup[0] in answer_count_dict.keys(): # If it's already in the dictionary...
            answer_count_dict[tup[0]] += 1 # Increment value
        else: # If it's not in the dictionary...
            answer_count_dict[tup[0]] = 1 # Add it with value=1
    # Iterate through dictionary keys (answers) and add all key-value pairs to a list
    answer_count_list = []
    for answer in answer_count_dict.keys():
        count = answer_count_dict[answer]
        tup = (answer, count)
        answer_count_list.append(tup)
    # Now sort the list
    answer_count_list_sorted = sorted(answer_count_list, key=second_elem, reverse=True)
    return answer_count_list_sorted

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

def process_string_input(word_str):
    # Strip any whitespace
    trimmed_word = word_str.strip()
    char_list = []
    for char in trimmed_word:
        if char != " ":
            char_list.append(char)
    clean_word = "".join(char_list)
    return clean_word

def init():
    global all_puzzles
    #all_puzzles = load_all_puzzles_into_dict()
    all_puzzles = load_all_puzzles_into_nested_dict()

def load_all_puzzles():
    global all_puzzles
    return all_puzzles
