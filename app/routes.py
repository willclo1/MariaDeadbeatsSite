from datetime import datetime
from functools import wraps

from flask_login import login_required, current_user, login_user, logout_user
import sqlalchemy as sa
from app import db
from app import app
from app.forms import LoginForm, RegistrationForm, BanUserForm, UnbanUserForm, UserLogsAvailable
from app.forms import LoginForm, RegistrationForm, BanUserForm
from flask import flash
from flask import render_template, request, redirect, url_for
from sqlalchemy import create_engine, false
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from csi3335f2024 import engineStr
from csi3335f2024 import sportradar_api_key
import json
from app.models import Users, BannedUsers, UserLogs
from urllib.parse import urlsplit
import os
from app.utils import *
from csi3335f2024 import basedir

engine = create_engine(engineStr)
# set a path so templates can be read with any file path
templates_path = os.path.join(basedir, 'templates')


@app.route('/home')
@app.route('/')
@app.route('/index')
@login_required
def index():
    # here is where we could query for interesting user info - cookies??
    if not current_user.is_admin:
        return render_template('index.html', title='Home Page')
    else:
        return render_template("admin_index.html", title="Admin landing page")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for('index'))
    elif current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(Users).where(Users.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        if not user.is_admin:
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# not sure if we need this, makes it work to import the css, probably a fix?
@app.route('/team-selection', methods=['GET', 'POST'])
@login_required
def team_selection():
    Session = sessionmaker(bind=engine)
    session = Session()

    teamSQL = text("SELECT DISTINCT team_name FROM teams ORDER BY yearID DESC;")
    teamResult = session.execute(teamSQL)
    tmOptions = [row[0] for row in teamResult]

    selected_team = None
    if request.method == 'POST':
        selected_team = request.form.get('team')
        print(selected_team)
        if (selected_team != ''):
            return redirect(url_for('year_selection', team=selected_team))
        else:
            flash("Please choose a team", 'danger')

    return render_template('team_selection.html', tmOptions=tmOptions)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.is_admin = False
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


def admin_status_required():
    def admin_status_decorator(func):
        @wraps(func)
        def admin_status_wrapper(*args, **kwargs):
            if current_user.is_admin:
                return func(*args, **kwargs)
            else:
                # Handle the case where the condition is not met
                return "Admin Status is required", 403  # For example, return a 403 Forbidden

        return admin_status_wrapper

    return admin_status_decorator


@app.route('/view-user-logs', methods=['GET', 'POST'])
@login_required
@admin_status_required()
def view_user_logs():
    form = UserLogsAvailable()

    user_logs = ''

    if form.validate_on_submit():
        user_logs = db.session.query(UserLogs).filter(UserLogs.username == form.username.data)
    for log in user_logs:
        print(log.username)

    return render_template('view_user_logs.html', title='View User Logs', UserLogsForm=form, UserLogs=user_logs)


@app.route('/ban-user', methods=['GET', 'POST'])
@login_required
@admin_status_required()
def ban_user():
    ban_form = BanUserForm()
    unban_form = UnbanUserForm()
    if 'ban_submit' in request.form and ban_form.validate_on_submit():
        print("ban form validated!")
        email = db.session.scalar(sa.select(Users.email).where(
            Users.username == ban_form.username.data))
        banned_user = BannedUsers(username=ban_form.username.data, email=email)
        print("banning user: ")
        print(ban_form.username.data + " " + email)
        db.session.add(banned_user)
        db.session.commit()
        output_string = "User Banned: " + banned_user.username + " - email: " + banned_user.email
        flash(output_string)
    elif 'unban_submit' in request.form and unban_form.validate_on_submit():
        print("unban form validated!")
        print("unbanning user: ", unban_form.username.data)
        unbanned_user = BannedUsers.query.filter_by(username=unban_form.username.data).scalar()
        db.session.delete(unbanned_user)
        db.session.commit()
        output_string = "Unbanned User: " + unbanned_user.username + " - email: " + unbanned_user.email
        flash(output_string)
    else:
        print("form not validated")
        print(ban_form.errors)  # This will print the errors if any
        print(unban_form.errors)  # This will print the errors if any

    banned_users = BannedUsers.query.all()
    return render_template('ban_user.html', title='Ban User',
                           BanForm=ban_form, UnbanForm=unban_form, BannedUsers=banned_users)


@app.route('/admin-register', methods=['GET', 'POST'])
@login_required
@admin_status_required()
def admin_register():
    form = RegistrationForm()
    if form.validate_on_submit():
        admin = Users(username=form.username.data, email=form.email.data)
        admin.set_password(form.password.data)
        admin.is_admin = True
        db.session.add(admin)
        db.session.commit()
        output_string = "New Admin User Created: " + admin.username
        flash(output_string)
    return render_template('admin_register.html', title='Register', form=form)


@app.route('/year-selection', methods=['GET', 'POST'])
@login_required
def year_selection():
    selected_team = request.args.get('team')

    Session = sessionmaker(bind=engine)
    session = Session()

    yearSQL = text("SELECT DISTINCT yearID FROM teams WHERE team_name = :team ORDER BY yearID;")
    yrResult = session.execute(yearSQL, {'team': selected_team})
    yrOptions = [row[0] for row in yrResult]

    if request.method == 'POST':
        selected_year = request.form.get('year')
        if (selected_year != ''):
            new_user_log = UserLogs(username=current_user.username,
                                    team_name=selected_team, yearID=selected_year)
            db.session.add(new_user_log)
            db.session.commit()
            print("logged: " + new_user_log.username
                  + " " + str(new_user_log.yearID) + " "
                  + new_user_log.team_name + " "
                  + str(new_user_log.time_of_query))
            return redirect(url_for('summary', team=selected_team, year=selected_year))
        else:
            flash('Please enter a year', 'danger')

    return render_template('year_selection.html', yrOptions=yrOptions, selected_team=selected_team)


@app.route('/season-countdown', methods=['GET', 'POST'])
@login_required
def season_countdown():
    url1 = f"https://api.sportradar.com/mlb/trial/v7/en/games/2025/REG/schedule.json?api_key={sportradar_api_key}"
    headers = {"accept": "application/json"}
    response = requests.get(url1, headers=headers)
    data = json.loads(response.text)
    games = data["games"]
    sorted_games = sorted(games, key=lambda game: datetime.fromisoformat(game["scheduled"]))
    first_game = sorted_games[0]

    # Format the date and time for the first game
    game_time = first_game["scheduled"]
    game_date_and_time = datetime.fromisoformat(game_time).strftime("%b %d, %Y %I:%M %p")
    date_object = datetime.fromisoformat(game_time)
    formatted_date = date_object.strftime("%A, %B %d, %Y at %I:%M %p")

    # Add the formatted date back to first_game for the template
    first_game["scheduled"] = formatted_date

    countdown_data = {
        'season': date_object.year,
        'datetime': date_object.strftime("%A, %B %d, %Y at %I:%M %p")
    }

    return render_template(
        'season_countdown.html',
        title='Season Countdown',
        countdown_data=countdown_data,
        first_game=first_game,
        game_date_and_time=game_date_and_time
    )


from datetime import datetime


@app.route('/get-all-games-for-a-team', methods=['GET', 'POST'])
@login_required
def get_all_games_for_a_team():
    url = f"https://api.sportradar.com/mlb/trial/v7/en/games/2025/REG/schedule.json?api_key={sportradar_api_key}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)

    team_games = {}
    for game in data["games"]:
        home_team = game["home"]["name"]
        away_team = game["away"]["name"]

        # Ensure teams exist in the dictionary
        if home_team not in team_games:
            team_games[home_team] = []
        if away_team not in team_games:
            team_games[away_team] = []

        # Append games to respective teams
        team_games[home_team].append(game)
        team_games[away_team].append(game)

    # Sort games by date and time for each team
    for key in team_games.keys():
        team_games[key] = sorted(team_games[key], key=lambda game: datetime.fromisoformat(game["scheduled"]))

    # Example debug output for a specific team
    team_name = "Yankees"
    if team_name in team_games:
        for game in team_games[team_name]:
            game_date = datetime.fromisoformat(game["scheduled"]).strftime('%B %d, %Y at %I:%M %p')
            print(game_date, game["home"]["name"], "vs", game["away"]["name"])

    # Prepare team options and selected team
    tmOptions = team_games.keys()
    selected_team = None

    if request.method == 'POST':
        selected_team = request.form.get('team')
        return render_template(
            'get_all_games_for_a_team.html',
            title='Get All Games',
            team_games=team_games[selected_team],
            tmOptions=tmOptions,
            format_date=lambda date: datetime.fromisoformat(date).strftime('%B %d, %Y at %I:%M %p')
        )

    return render_template(
        'get_all_games_for_a_team.html',
        title='Get All Games',
        team_games='',
        tmOptions=tmOptions,
        format_date=lambda date: datetime.fromisoformat(date).strftime('%B %d, %Y at %I:%M %p')
    )


@app.route('/summary', methods=['GET'])
@login_required
def summary():
    team = request.args.get('team')
    year = request.args.get('year')
    if not team or not year:
        return "Error: Team and year must be specified", 400

    with engine.connect() as connection:
        team_query = text("""
                SELECT teamID
                FROM teams
                WHERE yearID = :year AND team_name = :team
                LIMIT 1;
            """)
        result = connection.execute(team_query, {"year": year, "team": team}).mappings().first()

        if not result:
            return f"Error: Team '{team}' not found for the year {year}.", 404

        teamID = result["teamID"]

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
            ORDER BY b.b_AB DESC, (b.b_H / b.b_AB), b.b_G DESC
        """)
        batting_result = connection.execute(batting_team_query, {"teamID": teamID, "year": year}).mappings().all()

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
            war = row["war"] if row["war"] is not None else 'N/A'

            obp_denominator = at_bats + walks + hit_by_pitch + sac_flies
            slg_denominator = at_bats

            obp = (hits + walks + hit_by_pitch) / obp_denominator if obp_denominator > 0 else 0
            slg = (hits + 2 * doubles + 3 * triples + 4 * home_runs) / slg_denominator if slg_denominator > 0 else 0
            ops = obp + slg
            avg = hits / at_bats if at_bats > 0 else 0
            k_bb = strikeouts / walks if walks > 0 else 0
            if at_bats != 0:
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
                    "k_bb": f"{k_bb:.3f}" if walks > 0 else 'N/A',
                    "war": round(war, 2) if war != 'N/A' else 'N/A',
                })

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

        pitching_stats = []
        for row in pitching_result:
            outs_pitched = row["outs_pitched"] or 0
            hits = row["hits"] or 0
            walks = row["walks"] or 0
            strikeouts = row["strikeouts"] or 0
            home_runs = row["home_runs"] or 0

            innings_pitched = outs_pitched / 3 if outs_pitched > 0 else 0

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

        division_league_query = text("""
            SELECT divID, lgID
            FROM teams
            WHERE teamID = :teamID AND yearID = :year
        """)
        div_lg_result = connection.execute(division_league_query, {"teamID": teamID, "year": year}).mappings().first()

        if not div_lg_result:
            return f"Error: No division or league found for team '{team}' in year {year}.", 404

        divID = div_lg_result["divID"]
        lgID = div_lg_result["lgID"]
        if int(year) >= 1969 and divID and lgID:
            division_query = text("""
                SELECT 
                    t.team_name,
                    t.team_W,
                    t.team_L,
                    (t.team_W / (t.team_W + t.team_L)) AS winning_pct,
                    (SELECT (ABS(top.team_W - t.team_W) + ABS(top.team_L - t.team_L)) / 2
                     FROM teams top
                     WHERE top.yearID = :year AND top.divID = :divID AND top.lgID = :lgID
                     ORDER BY top.team_W DESC
                     LIMIT 1) AS GB
                FROM teams t
                WHERE t.yearID = :year AND t.divID = :divID AND t.lgID = :lgID
                ORDER BY t.team_W DESC;
            """)
            division_result = connection.execute(division_query,
                                                 {"year": year, "divID": divID, "lgID": lgID}).mappings().all()
            division_standings = []
            for row in division_result:
                division_standings.append({
                    "team_name": row["team_name"],
                    "wins": row["team_W"],
                    "losses": row["team_L"],
                    "winning_pct": f"{row['winning_pct']:.3f}",
                    "games_back": f"{row['GB']:.1f}" if row["GB"] is not None else "0.0",
                })
        elif lgID != 'NA':
            league_query = text("""
                SELECT 
                    t.team_name,
                    t.team_W,
                    t.team_L,
                    (t.team_W / (t.team_W + t.team_L)) AS winning_pct,
                    (SELECT (ABS(top.team_W - t.team_W) + ABS(top.team_L - t.team_L)) / 2
                     FROM teams top
                     WHERE top.yearID = :year AND top.lgID = :lgID
                     ORDER BY top.team_W DESC
                     LIMIT 1) AS GB
                FROM teams t
                WHERE t.yearID = :year AND t.lgID = :lgID
                ORDER BY t.team_W DESC;
            """)
            division_result = connection.execute(league_query, {"year": year, "lgID": lgID}).mappings().all()
            division_standings = []
            for row in division_result:
                division_standings.append({
                    "team_name": row["team_name"],
                    "wins": row["team_W"],
                    "losses": row["team_L"],
                    "winning_pct": f"{row['winning_pct']:.3f}",
                    "games_back": f"{row['GB']:.1f}" if row["GB"] is not None else "0.0",
                })
        else:
            division_standings = []

        team_stats_query = text("""
            SELECT 
                team_G AS games,
                team_W AS wins,
                team_L AS losses,
                ROUND(team_W / (team_W + team_L), 3) AS win_pct,
                team_R AS runs_scored,
                team_RA AS runs_allowed,
                team_ERA AS era,
                team_HR AS home_runs,
                team_SB AS stolen_bases,
                ROUND(team_FP, 3) AS fielding_pct
            FROM teams
            WHERE teamID = :teamID AND yearID = :year
        """)

        team_stats_result = connection.execute(team_stats_query, {"teamID": teamID, "year": year}).mappings().first()

        team_stats = {
            "games": team_stats_result["games"],
            "wins": team_stats_result["wins"],
            "losses": team_stats_result["losses"],
            "win_pct": f"{team_stats_result['win_pct']:.3f}" if team_stats_result["win_pct"] is not None else "N/A",
            "runs_scored": team_stats_result["runs_scored"],
            "runs_allowed": team_stats_result["runs_allowed"],
            "era": f"{team_stats_result['era']:.2f}" if team_stats_result["era"] is not None else "N/A",
            "home_runs": team_stats_result["home_runs"],
            "stolen_bases": team_stats_result["stolen_bases"],
            "fielding_pct": f"{team_stats_result['fielding_pct']:.3f}" if team_stats_result[
                                                                              "fielding_pct"] is not None else "N/A",
        }

    summary_data = {
        "team": team,
        "year": year,
        "info": f"Summary of {team} in {year}.",
        "batting_stats": batting_stats,
        "pitching_stats": pitching_stats,
        "division_standings": division_standings,
        "team_stats": team_stats
    }

    return render_template('summary.html', summary=summary_data)


@app.route("/comparePlayers", methods=['GET', 'POST'])
@login_required
def comparePlayers():
    message = None

    if request.method == 'POST':
        player1_name = request.form['player1']
        player2_name = request.form['player2']

        # Validate input
        try:
            player1_first, player1_last = player1_name.split()
            player2_first, player2_last = player2_name.split()
        except ValueError:
            message = "Invalid input. Falling back to Babe Ruth and Willie Mays."

        with engine.connect() as connection:
            player_query = text("""
                SELECT p.playerID, p.nameFirst, p.nameLast, 
                       SUM(b.b_H) AS total_hits, 
                       SUM(b.b_HR) AS total_home_runs,
                       SUM(b.b_RBI) AS total_rbi,
                       AVG(b.b_H / b.b_AB) AS avg,
                       sum(b.b_WAR) as total_war
                FROM people p
                JOIN batting b ON p.playerID = b.playerID
                WHERE p.nameFirst = :first AND p.nameLast = :last
                GROUP BY p.playerID;
            """)
            player1_stats = connection.execute(player_query, {"first": player1_first,
                                                              "last": player1_last}).mappings().first() if 'player1_first' in locals() else None
            player2_stats = connection.execute(player_query, {"first": player2_first,
                                                              "last": player2_last}).mappings().first() if 'player2_first' in locals() else None

            if not player1_stats or not player2_stats:
                player1_fallback = {"first": "Babe", "last": "Ruth"}
                player2_fallback = {"first": "Willie", "last": "Mays"}
                message = "Invalid input. Falling back to Babe Ruth and Willie Mays."
                player1_stats = connection.execute(player_query, player1_fallback).mappings().first()
                player2_stats = connection.execute(player_query, player2_fallback).mappings().first()
            player1_stats = dict(player1_stats) if player1_stats else None
            player2_stats = dict(player2_stats) if player2_stats else None

            # Format averages
            # Format averages and WAR
            if player1_stats and 'avg' in player1_stats and player1_stats['avg'] is not None:
                player1_stats['avg'] = f"{player1_stats['avg']:.3f}"
            if player2_stats and 'avg' in player2_stats and player2_stats['avg'] is not None:
                player2_stats['avg'] = f"{player2_stats['avg']:.3f}"

            if player1_stats and 'total_war' in player1_stats and player1_stats['total_war'] is not None:
                player1_stats['total_war'] = f"{player1_stats['total_war']:.3f}"
            if player2_stats and 'total_war' in player2_stats and player2_stats['total_war'] is not None:
                player2_stats['total_war'] = f"{player2_stats['total_war']:.3f}"
        return render_template(
            "compare.html",
            player1=player1_stats,
            player2=player2_stats,
            message=message
        )

    # If GET request, render the compare form
    return render_template("compare_form.html")


@app.route("/compareTeams", methods=['GET', 'POST'])
@login_required
def compare_teams():
    """
    [POST] Retrieve batting statistics for two given teams in a certain year,
    and produce HTML comparing the two teams. If the entered names of a team
    are invalid or the year is not applicable to either team, the produced
    HTML will use the Minnesota Twins and the Atlanta Braves during 1991
    as the output.

    [GET] produce HTML form to enter the names of the two teams and a year.

    :return: HTML for the results of a form or an unfilled form.
    """
    message = None

    if request.method == 'POST':
        team1 = request.form['team1']
        team2 = request.form['team2']
        team1 = team1.strip().title()
        team2 = team2.strip().title()
        year = request.form['year']
        print(f"Team 1: {team1}, Team 2: {team2}, Year: {year}")

        with engine.connect() as connection:
            team_query = text("""
                SELECT t.team_name as name,
                    t.lgID AS league,
                    t.team_rank AS rank,
                    t.team_G AS games,
                    t.team_W AS wins,
                    t.team_L AS losses,
                    t.team_projW AS projWins,
                    t.team_projL AS projLoss,
                    t.WSWin as WSWin,
                    t.team_R AS runs,
                    t.team_AB AS atBats,
                    t.team_H AS H,
                    t.team_2B AS "2B",
                    t.team_3B AS "3B",
                    t.team_HR AS HR,
                    (t.team_H + (2 * t.team_2B) + (3 * t.team_3B) + (4 * t.team_HR)) AS TB,
                    SUM(b.b_RBI) AS RBI,
                    t.team_BB AS BB,
                    t.team_SO AS SO,
                    t.team_SB AS SB,
                    t.team_CS AS CS,
                    (t.team_H / t.team_AB) AS AVG,
                    ((t.team_H + t.team_BB + t.team_HBP) 
                        / (t.team_AB + t.team_BB + t.team_HBP + t.team_SF)) AS OBP,
                    ((t.team_H + (2 * t.team_2B) + (3 * t.team_3B) + (4 * t.team_HR)) 
                        / t.team_AB) AS SLG,
                    (((t.team_H + t.team_BB + t.team_HBP) / (t.team_AB + t.team_BB + t.team_HBP + t.team_SF)) 
                        + ((t.team_H + (2 * t.team_2B) + (3 * t.team_3B) + (4 * t.team_HR)) / t.team_AB)) AS OPS
                FROM teams t JOIN batting b 
                    ON t.teamID = b.teamID 
                    AND t.yearID = b.yearId
                WHERE t.team_name = :teamName AND t.yearID = :year
                GROUP BY 
                    t.team_name, t.lgID, t.team_rank, t.team_G, t.team_W, t.team_L, 
                    t.team_projW, t.team_projL, t.WSWin, t.team_R, t.team_AB, t.team_H, 
                    t.team_2B, t.team_3B, t.team_HR, t.team_BB, t.team_SO, t.team_SB, t.team_CS;
            """)
            '''
            team1_stats = (
                connection
                    .execute(team_query, {"teamName": team1, "year": year})
                    .mappings().first() if team1 in locals() and year in locals()
                    else None
            )
            '''
            team1_stats = connection.execute(team_query, {"teamName": team1, "year": year}).mappings().first()
            print(f"{team1_stats}")
            team2_stats = connection.execute(team_query, {"teamName": team2, "year": year}).mappings().first()
            print(f"{team2_stats}")

            # Fallback, defaults to Minnesota Twins and Atlanta Braves in 1991
            if not team1_stats or not team2_stats or not year:
                message = """
                    Invalid input. Loading Minnesota Twins and Atlanta Braves 
                    in the year 1991 as default.
                """
                print(f"year: {year}\nteam1_stats: {team1_stats}\nteam2_stats: {team2_stats}")
                year = 1991
                default_team_1 = {"teamName": "Minnesota Twins", "year": 1991}
                default_team_2 = {"teamName": "Atlanta Braves", "year": 1991}
                team1_stats = connection.execute(team_query, default_team_1).mappings().first()
                team2_stats = connection.execute(team_query, default_team_2).mappings().first()

            # Dictionary conversion
            team1_stats = dict(team1_stats) if team1_stats else None
            team2_stats = dict(team2_stats) if team2_stats else None

            # AVG
            if team1_stats and 'AVG' in team1_stats and team1_stats['AVG']:
                team1_stats['AVG'] = f"{team1_stats['AVG']:.3f}"
            if team2_stats and 'AVG' in team2_stats and team2_stats['AVG']:
                team2_stats['AVG'] = f"{team2_stats['AVG']:.3f}"

            # OBP
            if team1_stats and 'OBP' in team1_stats and team1_stats['OBP']:
                team1_stats['OBP'] = f"{team1_stats['OBP']:.3f}"
            if team2_stats and 'OBP' in team2_stats and team2_stats['OBP']:
                team2_stats['OBP'] = f"{team2_stats['OBP']:.3f}"

            # SLG
            if team1_stats and 'SLG' in team1_stats and team1_stats['SLG']:
                team1_stats['SLG'] = f"{team1_stats['SLG']:.3f}"
            if team2_stats and 'SLG' in team2_stats and team2_stats['SLG']:
                team2_stats['SLG'] = f"{team2_stats['SLG']:.3f}"

            # OPS
            if team1_stats and 'OPS' in team1_stats and team1_stats['OPS']:
                team1_stats['OPS'] = f"{team1_stats['OPS']:.3f}"
            if team2_stats and 'OPS' in team2_stats and team2_stats['OPS']:
                team2_stats['OPS'] = f"{team2_stats['OPS']:.3f}"

        return render_template(
            "compare_team.html",
            team1=team1_stats,
            team2=team2_stats,
            year=year,
            message=message
        )

    # GET request returns form
    return render_template("compare_team_form.html")


@app.route('/depth_chart', methods=['GET'])
@login_required
def depth_chart():
    team = request.args.get('team')
    year = request.args.get('year')

    if not team or not year:
        return "Error: Team and year must be specified", 400

    with engine.connect() as connection:
        team_query = text("""
            SELECT teamID
            FROM teams
            WHERE yearID = :year AND team_name = :team
            LIMIT 1;
            """)
        result = connection.execute(team_query, {"year": year, "team": team}).mappings().first()
        if not result:
            return f"Error: Team {team} not found for year {year}.", 404
        teamID = result["teamID"]

        depth_chart_query = text("""
            SELECT
                f.position AS position,
                f.playerID,
                p.nameFirst AS first_name,
                p.nameLast AS last_name,
                f.f_G AS games_played,
                t.team_G AS team_games_played,
                ROUND((f.f_G / t.team_G) * 100, 2) AS playing_time_percentage
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            JOIN people p ON f.playerID = p.playerID AND f.teamID = t.teamID
            WHERE f.yearID = :year AND f.teamID = :teamID
            ORDER BY f.position, games_played DESC;
                """)
        depth_chart_result = connection.execute(depth_chart_query, {"year": year, "teamID": teamID}).mappings().all()

        depth_chart = {}
        for row in depth_chart_result:
            position = row["position"]
            player_info = {
                "name": f"{row['first_name']} {row['last_name']}",
                "games_played": row["games_played"],
                "playing_time_percentage": row["playing_time_percentage"]
            }
            if position not in depth_chart:
                depth_chart[position] = []
            depth_chart[position].append(player_info)

        # Handle diamond positions
        diamond_positions = {pos: None for pos in ["C", "P", "1B", "2B", "3B", "SS", "LF", "CF", "RF"]}
        for pos in diamond_positions.keys():
            if pos in depth_chart:
                diamond_positions[pos] = depth_chart[pos][0]  # Assign the first player for each position

        # Handle missing outfielders
        if "LF" not in depth_chart or "CF" not in depth_chart or "RF" not in depth_chart:
            if "OF" in depth_chart:
                top_outfielders = sorted(depth_chart["OF"], key=lambda x: x["games_played"], reverse=True)[:3]
                for idx, outfielder in enumerate(top_outfielders):
                    if idx == 0 and "LF" not in depth_chart:
                        diamond_positions["LF"] = outfielder
                    elif idx == 1 and "CF" not in depth_chart:
                        diamond_positions["CF"] = outfielder
                    elif idx == 2 and "RF" not in depth_chart:
                        diamond_positions["RF"] = outfielder

    return render_template(
        'depth_chart.html',
        depth_chart=depth_chart,
        diamond_positions=diamond_positions,
        team=team,
        year=year
    )


@app.route("/viewParks")
@login_required
def view_parks():
    try:
        # Connect to the database and fetch parks data
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT parkID, park_name, city, state, country, latitude, longitude FROM parks"))
            parks = [dict(row) for row in result.mappings()]

        return render_template("view_parks.html", parks=parks)
    except Exception as e:
        return f"An error occurred: {e}", 500


@app.route('/admin-landing-page')
@login_required
def admin_landing_page():
    return render_template("admin_index.html", title="Admin landing page")


@app.route('/grid-solver', methods=['GET', 'POST'])
@login_required
def grid_solver():
    """
    Load and solve the grid puzzle. By default, load the current day's puzzle.
    """
    puzzle_number = None  # Default to the current day's puzzle

    if request.method == 'POST':
        # Get the puzzle number from the form input, if provided
        puzzle_number = request.form.get('puzzle_number')
        if puzzle_number:
            try:
                puzzle_number = int(puzzle_number)
            except ValueError:
                puzzle_number = None  # Fallback to the current day's puzzle

        action = request.form.get('action')

        if action == 'solve_puzzle':
            # Solve the puzzle
            top_row, left_column, grid = solve_puzzle(puzzle_number)
            return render_template(
                'gridSolver.html',
                puzzle_number=puzzle_number,
                top_row=top_row,
                left_column=left_column,
                grid=grid
            )
        elif action == 'load_puzzle':
            # Load a specific puzzle
            top_row, left_column = scrape_immaculate_grid(puzzle_number)
            grid = [["" for _ in range(3)] for _ in range(3)]
            return render_template(
                'gridSolver.html',
                puzzle_number=puzzle_number,
                top_row=top_row,
                left_column=left_column,
                grid=grid
            )
    else:
        # GET request, load the current day's puzzle
        top_row, left_column = scrape_immaculate_grid()
        grid = [["" for _ in range(3)] for _ in range(3)]
        return render_template(
            'gridSolver.html',
            puzzle_number=None,
            top_row=top_row,
            left_column=left_column,
            grid=grid
        )


@app.route('/news', methods=['GET'])
@login_required
def show_articles():
    articles = scrape_espn_mlb_news()
    return render_template('articles.html', articles=articles)
