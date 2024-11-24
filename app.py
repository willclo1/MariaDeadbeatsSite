from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from cfg import engineStr

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Database connection
    engine = create_engine(engineStr)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Fetch all teams
    teamSQL = text("SELECT DISTINCT team_name FROM teams order by yearID desc;")
    teamResult = session.execute(teamSQL)
    tmOptions = [row[0] for row in teamResult]

    # Initialize variables
    selected_team = None
    yrOptions = []
    dropdown_locked = False

    if request.method == 'POST':
        # Capture the selected team
        selected_team = request.form.get('tmDropdown')

        # Avoid processing if no team is selected
        if selected_team and selected_team != "":
            dropdown_locked = True  # Lock the dropdown after submission

            # Fetch years for the selected team
            yearSQL = text("SELECT DISTINCT yearID FROM teams WHERE team_name = :team ORDER BY yearID;")
            yrResult = session.execute(yearSQL, {'team': selected_team})
            yrOptions = [row[0] for row in yrResult]

        # Capture selected year
        yrSelect = request.form.get('yrDropdown')

        if yrSelect and yrSelect != "":
            return f'You selected: Team - {selected_team}, Year - {yrSelect}'

    # Render the template
    return render_template(
        'dropdown.html',
        tmOptions=tmOptions,
        yrOptions=yrOptions,
        selected_team=selected_team,
        dropdown_locked=dropdown_locked
    )


if __name__ == '__main__':
    app.run(debug=True)