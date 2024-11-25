from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from cfg import engineStr
from teamMapping import team_map

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

engine = create_engine(engineStr)
@app.route('/', methods=['GET', 'POST'])
def home():
    # Database connection
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
    show_all = request.args.get('show_all', 'false').lower() == 'true'
    player_limit = None if show_all else 5
    if not team or not year:
        return "Error: Team and year must be specified", 400

    teamID = team_map.get(team)

    if not teamID:
        return f"Error: Team '{team}' not found in the mapping.", 404

    with engine.connect() as connection:
        # Batting stats query
        # Batting stats query
        batting_team_query = text(f"""
            SELECT 
                p.nameFirst AS first_name,
                p.nameLast AS last_name,
                b.playerID,
                b.b_G AS games,
                b.b_AB AS at_bats,
                b.b_H AS hits,
                b.b_2B AS doubles,
                b.b_3B AS triples,
                b.b_HR AS home_runs,
                b.b_BB AS walks,
                b.b_SO AS strikeouts,
                b.b_HBP AS hit_by_pitch,
                b.b_SF AS sac_flies,
                b.b_WAR as war
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID AND b.yearId = t.yearID
            JOIN people p ON b.playerID = p.playerID
            WHERE b.teamID = :teamID AND b.yearId = :year
            ORDER BY b.b_G DESC, (b.b_H / b.b_AB) DESC
        """)
        batting_result = connection.execute(batting_team_query, {"teamID": teamID, "year": year}).mappings().all()

        # Calculate advanced batting stats
        batting_stats = []
        for row in batting_result:
            at_bats = row["at_bats"] or 0
            walks = row["walks"] or 0
            hits = row["hits"] or 0
            hit_by_pitch = row["hit_by_pitch"] or 0
            sac_flies = row["sac_flies"] or 0
            strikeouts = row["strikeouts"] or 0
            doubles = row["doubles"] or 0
            triples = row["triples"] or 0
            home_runs = row["home_runs"] or 0
            war = row["war"] or 'N/A'

            # Prevent division by zero
            obp_denominator = at_bats + walks + hit_by_pitch + sac_flies
            slg_denominator = at_bats

            # Compute stats
            obp = (hits + walks + hit_by_pitch) / obp_denominator if obp_denominator > 0 else 0
            slg = (hits + 2 * doubles + 3 * triples + 4 * home_runs) / slg_denominator if slg_denominator > 0 else 0
            ops = obp + slg
            avg = hits / at_bats if at_bats > 0 else 0
            k_bb = strikeouts / walks if walks > 0 else 0

            batting_stats.append({
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "games": row["games"],
                "at_bats": at_bats,
                "hits": hits,
                "home_runs": home_runs,
                "walks": walks,
                "strikeouts": strikeouts,
                "avg": f"{avg:.3f}",
                "obp": f"{obp:.3f}",
                "slg": f"{slg:.3f}",
                "ops": f"{ops:.3f}",
                 "k_bb": f"{k_bb:.3f}" if k_bb != 0 else 'N/A',
                "war": round(war, 2) if war != 'N/A' else 'N/A',


            })

        # Pitching stats query
        # Pitching stats query
        pitching_team_query = text(f"""
            SELECT 
                p.nameFirst AS first_name,
                p.nameLast AS last_name,
                pt.playerID,
                pt.p_G AS games,
                pt.p_IPOuts AS outs_pitched,
                pt.p_W AS wins,
                pt.p_L AS losses,
                pt.p_SV AS saves,
                pt.p_H AS hits,
                pt.p_BB AS walks,
                pt.p_SO AS strikeouts,
                pt.p_HR AS home_runs,
                pt.p_ERA AS era
            FROM pitching pt
            JOIN teams t ON pt.teamID = t.teamID AND pt.yearID = t.yearID
            JOIN people p ON pt.playerID = p.playerID
            WHERE pt.teamID = :teamID AND pt.yearID = :year
            ORDER BY pt.p_G DESC, pt.p_ERA ASC
        """)
        pitching_result = connection.execute(pitching_team_query, {"teamID": teamID, "year": year}).mappings().all()

        # Calculate advanced pitching stats
        pitching_stats = []
        for row in pitching_result:
            outs_pitched = row["outs_pitched"] or 0
            hits = row["hits"] or 0
            walks = row["walks"] or 0
            strikeouts = row["strikeouts"] or 0
            home_runs = row["home_runs"] or 0

            innings_pitched = outs_pitched / 3 if outs_pitched > 0 else 0

            # Prevent division by zero
            whip = (walks + hits) / innings_pitched if innings_pitched > 0 else 0
            k_per_nine = (strikeouts / innings_pitched * 9) if innings_pitched > 0 else 0
            bb_per_nine = (walks / innings_pitched * 9) if innings_pitched > 0 else 0
            hr_per_nine = (home_runs / innings_pitched * 9) if innings_pitched > 0 else 0
            k_bb = strikeouts / walks if walks > 0 else 0

            pitching_stats.append({
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "games": row["games"],
                "wins": row["wins"],
                "losses": row["losses"],
                "saves": row["saves"],
                "era": row["era"],
                "whip": round(whip, 3),
                "k_per_nine": round(k_per_nine, 2),
                "bb_per_nine": round(bb_per_nine, 2),
                "hr_per_nine": round(hr_per_nine, 2),
                "k_bb": round(k_bb, 2),
            })

    # Pass the data to the template
    summary_data = {
        "team": team,
        "year": year,
        "info": f"Summary of {team} in {year}.",
        "batting_stats": batting_stats,
        "pitching_stats": pitching_stats,
    }

    return render_template('summary.html', summary=summary_data)
if __name__ == '__main__':
    app.run(debug=True)