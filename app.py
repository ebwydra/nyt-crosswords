from flask import Flask, render_template, request, redirect, g
import nytxw
import sqlite3 as sqlite

DBNAME = 'data/puzzles.db'
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/explore")
def explore():
    return render_template("explore.html")

@app.route("/solve")
def solve():
    return render_template("solve.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/explore/search", methods=["POST"])
def exploresearch():
    search_str = request.form["word"]
    year_str = request.form["year"]
    n_str = request.form["n"]

    # Process search string
    trimmed_search_string = nytxw.process_string_input(search_str)
    # Process year input
    year = nytxw.process_year_input(year_str)
    if year:
        year_as_text = year_str
    else:
        year_as_text = "all years"
    # Process number of results
    if n_str == "all":
        n = 1000
    else:
        n = int(n_str)
    # If there was a search string, search for it!
    if search_str:
        clue_list = nytxw.get_clues_for_word(trimmed_search_string, n, year)
        # If there were results for the search string, show them.
        if clue_list:
            return render_template("explore-result.html", search_type="clues", n=len(clue_list), search_str=trimmed_search_string.upper(), year_as_text=year_as_text, clue_list=clue_list)
        # If not, render result template, but with no results and "No results found!" message.
        else:
            return render_template("explore-result.html", search_type="clues", n=0, search_str=trimmed_search_string.upper(), year_as_text=year_as_text, clue_list=clue_list)
    # If nothing was entered, just render the start page.
    else:
        return render_template("explore.html")

@app.route("/explore/top", methods=["POST"])
def top():
    year_str = request.form["year"]
    n_str = request.form["n"]
    letters_str = request.form["letters"]
    # Process year input
    year = nytxw.process_year_input(year_str)
    if year:
        year_as_text = year_str
    else:
        year_as_text = "all years"
    # Process number of results
    n = int(n_str)
    # Process number of letters
    if letters_str == "all":
        letters = None
        letters_display = "any number of"
    elif letters_str == "15":
        letters = int(letters_str)
        letters_display = "15 or more"
    else:
        letters = int(letters_str)
        letters_display = letters_str

    answer_list = nytxw.get_most_common_answers(length=letters, n=n, year=year)

    return render_template("explore-result.html", search_type="top_answers", n=len(answer_list), letters=letters_display, year_as_text=year_as_text, answer_list=answer_list)

@app.route("/solve/search", methods=["POST"])
def solvesearch():
    search_str = request.form["word"]

    if search_str:
        try:
            result_list = nytxw.search_for_matching_answers(search_str)
            if result_list:
                return render_template("solve-result.html", n=len(result_list), search_str=search_str.upper(), result_list=result_list)
            else:
                return render_template("solve-result.html", n=0, search_str=search_str.upper(), result_list=result_list)
        except:
            return render_template("solve.html")
    else:
        return render_template("solve.html")

if __name__=="__main__":
    app.run(debug=True)
