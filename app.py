from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from cfg import engineStr

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

@app.route('/', methods=['GET', 'POST'])
def home():
    # Database connection
    engine = create_engine(engineStr)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Fetch all teams
    teamSQL = text("SELECT DISTINCT team_name FROM teams ORDER BY yearID DESC;")
    teamResult = session.execute(teamSQL)
    tmOptions = [row[0] for row in teamResult]

    selected_team = None
    if request.method == 'POST':
        selected_team = request.form.get('team')
        return redirect(url_for('year_selection', team=selected_team))

    return render_template('team_selection.html', tmOptions=tmOptions)


@app.route('/year-selection', methods=['GET', 'POST'])
def year_selection():
    # Get the selected team from the query parameters
    selected_team = request.args.get('team')

    # Database connection
    engine = create_engine(engineStr)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Fetch years for the selected team
    yearSQL = text("SELECT DISTINCT yearID FROM teams WHERE team_name = :team ORDER BY yearID;")
    yrResult = session.execute(yearSQL, {'team': selected_team})
    yrOptions = [row[0] for row in yrResult]

    if request.method == 'POST':
        selected_year = request.form.get('year')
        return redirect(url_for('summary', team=selected_team, year=selected_year))

    return render_template('year_selection.html', yrOptions=yrOptions, selected_team=selected_team)


@app.route('/summary', methods=['GET'])
def summary():
    team = request.args.get('team')
    year = request.args.get('year')

    # Example: Perform additional logic to fetch summary data
    summary_data = {
        "team": team,
        "year": year,
        "info": f"Summary of {team} in {year}."
    }

    return render_template('summary.html', summary=summary_data)


if __name__ == '__main__':
    app.run(debug=True)