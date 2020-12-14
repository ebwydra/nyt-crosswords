from flask import Flask, render_template, request, redirect, g
import nytxw

app = Flask(__name__)

@app.before_first_request
def load_puzzles():
    g.all_puzzles = nytxw.load_all_puzzles_into_nested_dict()

@app.before_request
def access_puzzles():
    return g.all_puzzles

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    search_str = request.form["word"]
    year_str = request.form["year"]
    n_str = request.form["n"]

    trimmed_search_string = nytxw.process_string_input(search_str)

    if search_str:
        puzz_dict = g.all_puzzles
        #puzz_dict = nytxw.load_all_puzzles() # Load all puzzles in a nested dictionary
        year = nytxw.process_year_input(year_str)
        if year:
            clue_answer_tups = nytxw.convert_to_list_of_tups_for_year(puzz_dict, year)
            year_as_text = year_str
        else:
            clue_answer_tups = nytxw.convert_to_list_of_tups_all(puzz_dict)
            year_as_text = "all years"

        if n_str == "all":
            n = 1000
        else:
            n = int(n_str)

        answer_dict = nytxw.convert_to_answer_dict(clue_answer_tups)
        clues_for_word = nytxw.get_clues_for_word(answer_dict, trimmed_search_string)
        clue_list = nytxw.get_top_n_clues_for_word(clues_for_word, n)

        if clue_list: # If there were results for the search string, show them.
            return render_template("result.html", search_type="clues", n=len(clue_list), search_str=trimmed_search_string.upper(), year_as_text=year_as_text, clue_list=clue_list)

        else: # Render result template, but with no results and "No results found!" message.
            return render_template("result.html", search_type="clues", n=0, search_str=trimmed_search_string.upper(), year_as_text=year_as_text, clue_list=clue_list)

    else: # If nothing was entered, just render the start page.
        return render_template("index.html")

@app.route("/top", methods=["POST"])
def top():
    year_str = request.form["year"]
    n_str = request.form["n"]
    letters_str = request.form["letters"]
    puzz_dict = g.all_puzzles
    #puzz_dict = nytxw.load_all_puzzles() # Load all puzzles in a nested dictionary
    year = nytxw.process_year_input(year_str)
    if year:
        clue_answer_tups = nytxw.convert_to_list_of_tups_for_year(puzz_dict, year)
        year_as_text = year_str
    else:
        clue_answer_tups = nytxw.convert_to_list_of_tups_all(puzz_dict)
        year_as_text = "all years"

    n = int(n_str)
    all_answers = nytxw.get_most_common_answers(clue_answer_tups)
    if letters_str == "all":
        answer_list = all_answers[0:n]
        letters = "any"
    elif letters_str == "10":
        answer_list_over10 = []
        for answer in all_answers:
            if len(answer[0]) >= 10:
                answer_list_over10.append(answer)
        if len(answer_list_over10) < n:
            answer_list = answer_list_over10
        else:
            answer_list = answer_list_over10[0:n]
        letters = "10 or more"
    else:
        letters_int = int(letters_str)
        answer_list_bylength = []
        for answer in all_answers:
            if len(answer[0]) == letters_int:
                answer_list_bylength.append(answer)
        if len(answer_list_bylength) < n:
            answer_list = answer_list_bylength
        else:
            answer_list = answer_list_bylength[0:n]
        letters = letters_str

    return render_template("result.html", search_type="top_answers", n=len(answer_list), letters=letters, year_as_text=year_as_text, answer_list=answer_list)


if __name__=="__main__":
    nytxw.init()
    app.run(debug=True)
