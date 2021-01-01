import json
import sqlite3 as sqlite

DBNAME = 'puzzles.db'

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

# Create database
def create_db():
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()

    # Drop existing tables
    statement = "DROP TABLE IF EXISTS Puzzles"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS AnswerCluePairs"
    cur.execute(statement)
    conn.commit()

    # Create tables
    statement = '''
    CREATE TABLE Puzzles (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    DateStr TEXT,
    Year INTEGER,
    Month INTEGER,
	Day INTEGER,
    DayOfWeek TEXT,
    Editor TEXT,
    Author TEXT,
    Title TEXT
    );
    '''
    cur.execute(statement)
    statement = '''
    CREATE TABLE AnswerCluePairs (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    PuzzId INTEGER REFERENCES Puzzles(Id),
    Answer TEXT,
    Clue TEXT
    );
    '''
    cur.execute(statement)
    conn.commit()

    # Get all puzzles from files into a nested dictionary
    print("Loading puzzle data...")
    all_puzzles = load_all_puzzles_into_nested_dict()

    # Populate tables
    list_of_puzz_tups = []
    list_of_answer_clue_tups = []
    for y in all_puzzles.keys():
        for m in all_puzzles[y].keys():
            for d in all_puzzles[y][m].keys():
                date_str = all_puzzles[y][m][d]['date']
                dow = all_puzzles[y][m][d]['dow']
                editor = all_puzzles[y][m][d]['editor']
                author = all_puzzles[y][m][d]['author']
                title = all_puzzles[y][m][d]['title']
                puzz_tup = (date_str, y, m, d, dow, editor, author, title)
                list_of_puzz_tups.append(puzz_tup)

                answers_across = all_puzzles[y][m][d]['answers']['across']
                answers_down = all_puzzles[y][m][d]['answers']['down']
                clues_across = all_puzzles[y][m][d]['clues']['across']
                clues_down = all_puzzles[y][m][d]['clues']['down']

                answers = answers_across + answers_down
                clues = clues_across + clues_down
                clues_clean = []
                for c in clues:
                    clean_clue = strip_number_from_clue(c)
                    clues_clean.append(clean_clue)

                for i in range(1, len(answers)):
                    answer_clue_tup = (date_str, answers[i], clues_clean[i])
                    list_of_answer_clue_tups.append(answer_clue_tup)

    print("Populating Puzzles table...")
    for tup in list_of_puzz_tups:
        statement = '''
        INSERT INTO Puzzles (DateStr, Year, Month, Day, DayOfWeek, Editor, Author, Title)
        VALUES (?,?,?,?,?,?,?,?)
        '''
        cur.execute(statement, tup)
        conn.commit()

    print("Populating AnswerCluePairs table...")
    for tup in list_of_answer_clue_tups: # (date_str, answer, clue)
        statement = '''
        SELECT Id
        FROM Puzzles
        WHERE DateStr LIKE \"{}\"
        '''.format(tup[0])
        cur.execute(statement)
        result = cur.fetchone()
        try:
            id = result[0]
        except:
            id = None
        new_tup = (id, tup[1], tup[2])

        statement = '''
        INSERT INTO AnswerCluePairs (PuzzId, Answer, Clue)
        VALUES (?,?,?)
        '''
        cur.execute(statement, new_tup)
        conn.commit()

    conn.close()

def add_answer_length():
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor()
    # Create new column in AnswerCluePairs table
    addColumn = "ALTER TABLE AnswerCluePairs ADD COLUMN Length INTEGER"
    cur.execute(addColumn)
    conn.commit()

    # Populate length of answer
    statement = '''
    UPDATE AnswerCluePairs
    SET Length=length(Answer)
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()

#create_db()
#add_answer_length()
