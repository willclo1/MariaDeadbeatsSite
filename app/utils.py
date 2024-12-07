import pymysql
from cfg import cfg

import requests
from bs4 import BeautifulSoup


def scrape_espn_mlb_news():
    url = "https://www.espn.com/mlb/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    seen_titles = set()  # Use a set to track unique titles

    for item in soup.select('.headlineStack__list li'):
        try:
            headline = item.get_text(strip=True)
            link = item.find('a')['href']

            # Ensure the link is absolute
            if not link.startswith('http'):
                link = f"https://www.espn.com{link}"

            # Check if the title is already processed
            if headline not in seen_titles:
                articles.append({'title': headline, 'link': link})
                seen_titles.add(headline)
            else:
                print(f"Duplicate title found: {headline}")

        except (TypeError, KeyError):
            print(f"Error parsing item: {item}")

    return articles

def normalize_input(value):
    return " ".join(value.replace("\xa0", " ").split())

def normalize_team_name(team_name):
    return " ".join(team_name.replace("\xa0", " ").split())

# Connect to the database
def get_db_connection():
    return pymysql.connect(host=cfg.get(""),user=cfg.get("user"), password=cfg.get("password"), db=cfg.get("db"),cursorclass=pymysql.cursors.DictCursor)

# General function to execute SQL queries
def execute_query(query, params=None, column_name="playerID"):
    connection = get_db_connection()
    try:
        print(f"Executing Query: {query} with params {params}")  # Debugging
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            return set(row.get(column_name, None) for row in rows if column_name in row)
    except Exception as e:
        print(f"Error executing query: {e}")
        return set()
    finally:
        connection.close()

def get_franchise_id(team_name):
    """
    Map a normalized team name to its most recent franchID.
    """
    normalized_team_name = normalize_team_name(team_name)
    print(f"Looking up most recent franchID for team: '{normalized_team_name}'")

    # Query to find the most recent franchID based on the latest year
    query = """
    SELECT franchID
    FROM teams
    WHERE team_name = %s
    ORDER BY yearID DESC
    LIMIT 1
    """
    result = execute_query(query, (normalized_team_name,), column_name="franchID")
    if result:
        franch_id = list(result)[0]
        print(f"Found most recent franchID: {franch_id} for team: {normalized_team_name}")
        return franch_id

    # Debugging fallback if no match found
    print(f"No franchID found for team: {normalized_team_name}")
    return None

# Query players for a team
def get_players_for_team(team_name):
    """
    Fetch playerIDs for a given team, filtering by franchID to handle name changes.

    """
    # Query players by franchID
    team_name = normalize_team_name(team_name)
    query = """
    SELECT DISTINCT a.playerID
FROM appearances a
JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
WHERE t.franchid = (
    SELECT franchid
    FROM teams
    WHERE team_name = %s
    GROUP BY franchid
    ORDER BY COUNT(*) DESC
    LIMIT 1
);


    """
    return execute_query(query, (team_name,))






# Query players for trivia
def get_players_for_trivia(trivia):

    trivia_map = {
        "30+ HR /30+ SB SeasonBatting": """
        SELECT playerID
        FROM batting
        GROUP BY playerID, yearID
        HAVING SUM(b_HR) >= 30 AND SUM(b_SB) >= 30;
    """,
        "First Round Draft Pick": """
            SELECT playerID
            FROM draft join batting using (playerid)
            WHERE round = 1 and batting.yearid > 1964 and nameFirst != 'Jerry' and nameLast != 'Johnson';
        """,
        "40+ WAR Career": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(b_WAR) AS career_war
                FROM batting
                GROUP BY playerID
                HAVING career_war >= 40
            ) AS career_war_table;
        """,

        "6+ WAR Season": """
            SELECT playerID
            FROM batting
            WHERE b_WAR >= 6;
        """,
        ".300+ AVG CareerBatting": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(b_H) AS total_hits, SUM(b_AB) AS total_at_bats
                FROM batting
                GROUP BY playerID
                HAVING total_hits / total_at_bats > 0.300
            ) AS career_avg;
        """,
        "300+ HR CareerBatting": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(b_HR) AS total_hr
                FROM batting
                GROUP BY playerID
                HAVING total_hr >= 300
            ) AS career_hr;
        """,
        "300+ Save CareerPitching": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(p_SV) AS total_saves
                FROM pitching
                GROUP BY playerID
                HAVING total_saves >= 300
            ) AS career_saves;
        """,
        "300+ Wins CareerPitching": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(p_W) AS total_wins
                FROM pitching
                GROUP BY playerID
                HAVING total_wins >= 300
            ) AS career_wins;
        """,
        "3000+ Hits CareerBatting": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(b_H) AS total_hits
                FROM batting
                GROUP BY playerID
                HAVING total_hits >= 3000
            ) AS career_hits;
        """,
        "3000+ K CareerPitching": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(p_SO) AS total_strikes
                FROM pitching
                GROUP BY playerID
                HAVING total_strikes >= 3000
            ) AS career_strikes;
        """,
        "40+ 2B SeasonBatting": """
            SELECT playerID
            FROM batting
            WHERE b_2B >= 40;
        """,
        "40+ HR SeasonBatting": """
            SELECT playerID
            FROM batting
            WHERE b_HR >= 40;
        """,
        "40+ Save SeasonPitching": """
            SELECT playerID
            FROM pitching
            WHERE p_SV >= 40;
        """,
        "500+ HR CareerBatting": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(b_HR) AS total_hr
                FROM batting
                GROUP BY playerID
                HAVING total_hr >= 500
            ) AS career_hr;
        """,
        "Born Outside US 50 States and DC": """
            SELECT playerID
            FROM people
            WHERE birthCountry NOT IN ('USA', 'United States');
        """,
        "Canada": """
            SELECT playerID
            FROM people
            WHERE birthCountry = 'Canada';
        """,
        "Dominican Republic": """
            SELECT playerID
            FROM people
            WHERE birthCountry = 'Dominican Republic';
        """,
        "Pitchedmin. 1 game": """
            SELECT DISTINCT playerID
            FROM pitching
            WHERE p_G > 0;
        """,
        "Played In Major Negro Lgs": """
            SELECT DISTINCT playerID
            FROM negro_leagues;
        """,
        "Puerto Rico": """
            SELECT playerID
            FROM people
            WHERE birthCountry = 'Puerto Rico';
        """,
        "United States": """
            SELECT playerID
            FROM people
            WHERE birthCountry = 'USA';
        """,
        "World Series Champ WS Roster": """
            SELECT DISTINCT playerID
            FROM world_series_rosters;
        """,
        ".300+ AVG SeasonBatting": "SELECT playerID FROM batting WHERE b_H / b_AB > 0.300;",
        "10+ HR SeasonBatting": "SELECT playerID FROM batting WHERE b_HR >= 10;",
        "10+ Win SeasonPitching": "SELECT playerID FROM pitching WHERE p_W >= 10;",
        "100+ RBI SeasonBatting": "SELECT playerID FROM batting WHERE b_RBI >= 100;",
        "100+ Run SeasonBatting": "SELECT playerID FROM batting WHERE b_R >= 100;",
        "20+ Win SeasonPitching": "SELECT playerID FROM pitching WHERE p_W >= 20;",
        "200+ Hits SeasonBatting": "SELECT playerID FROM batting WHERE b_H >= 200;",
        "200+ K SeasonPitching": "SELECT playerID FROM pitching WHERE p_SO >= 200;",
        "200+ Wins CareerPitching": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(p_W) AS total_wins
                FROM pitching
                GROUP BY playerID
                HAVING total_wins >= 200
            ) AS career_wins;
        """,
        "2000+ Hits CareerBatting": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(b_H) AS total_hits
                FROM batting
                GROUP BY playerID
                HAVING total_hits >= 2000
            ) AS career_hits;
        """,
        "2000+ K CareerPitching": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(p_SO) AS total_ks
                FROM pitching
                GROUP BY playerID
                HAVING total_ks >= 2000
            ) AS career_ks;
        """,
        "30+ HR /30+ SB SeasonBatting": "SELECT playerID FROM batting WHERE b_HR >= 30 AND b_SB >= 30;",
        "30+ HR SeasonBatting": "SELECT playerID FROM batting WHERE b_HR >= 30;",
        "30+ SB Season": "SELECT playerID FROM batting WHERE b_SB >= 30;",
        "30+ Save SeasonPitching": "SELECT playerID FROM pitching WHERE p_SV >= 30;",
        "300+ HR CareerBatting": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(b_HR) AS total_hr
                FROM batting
                GROUP BY playerID
                HAVING total_hr >= 300
            ) AS career_hr;
        """,
        "300+ Save CareerPitching": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(p_SV) AS total_saves
                FROM pitching
                GROUP BY playerID
                HAVING total_saves >= 300
            ) AS career_saves;
        """,
        "300+ Wins CareerPitching": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(p_W) AS total_wins
                FROM pitching
                GROUP BY playerID
                HAVING total_wins >= 300
            ) AS career_wins;
        """,
        "3000+ Hits CareerBatting": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(b_H) AS total_hits
                FROM batting
                GROUP BY playerID
                HAVING total_hits >= 3000
            ) AS career_hits;
        """,
        "3000+ K CareerPitching": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(p_SO) AS total_ks
                FROM pitching
                GROUP BY playerID
                HAVING total_ks >= 3000
            ) AS career_ks;
        """,
        "40+ 2B SeasonBatting": "SELECT playerID FROM batting WHERE b_2B >= 40;",
        "40+ HR SeasonBatting": "SELECT playerID FROM batting WHERE b_HR >= 40;",
        "40+ Save SeasonPitching": "SELECT playerID FROM pitching WHERE p_SV >= 40;",
        # Non-stats-related trivia
        "All Star": """
        SELECT DISTINCT playerID
        FROM allstarfull;
    """,
        "Born Outside US 50 States and DC": "SELECT playerID FROM people WHERE birthCountry NOT IN ('USA', 'United States', 'US');",
        "Canada": "SELECT playerID FROM people WHERE birthCountry = 'Canada';",
        "Cy Young": "SELECT playerID FROM awards WHERE awardID = 'Cy Young Award';",
        "Designated Hittermin. 1 game": "SELECT playerID FROM appearances WHERE G_dh > 0;",
        "Dominican Republic": "SELECT playerID FROM people WHERE birthCountry = 'Dominican Republic';",
        "Gold Glove": "SELECT playerID FROM awards WHERE awardID = 'Gold Glove';",
        "Hall of Fame": "SELECT playerID FROM halloffame where inducted = 'Y';",
        "MVP": "SELECT playerID FROM awards WHERE awardID = 'Most Valuable Player';",
        "Only One Team": """
            SELECT playerID
            FROM appearances
            GROUP BY playerID
            HAVING COUNT(DISTINCT teamID) = 1;
        """,
        "Pitchedmin. 1 game": "SELECT playerID FROM appearances WHERE G_p > 0;",
        "Played Catchermin. 1 game": "SELECT playerID FROM appearances WHERE G_c > 0;",
        "Played Center Fieldmin. 1 game": "SELECT playerID FROM appearances WHERE G_cf > 0;",
        "Played First Basemin. 1 game": "SELECT playerID FROM appearances WHERE G_1b > 0;",
        "Played In Major Negro Lgs": "SELECT playerID FROM people WHERE lgID = 'Negro';",
        "Played Left Fieldmin. 1 game": "SELECT playerID FROM appearances WHERE G_lf > 0;",
        "Played Outfieldmin. 1 game": "SELECT playerID FROM appearances WHERE G_of > 0;",
        "Played Right Fieldmin. 1 game": "SELECT playerID FROM appearances WHERE G_rf > 0;",
        "Played Second Basemin. 1 game": "SELECT playerID FROM appearances WHERE G_2b > 0;",
        "Played Shortstopmin. 1 game": "SELECT playerID FROM appearances WHERE G_ss > 0;",
        "Played Third Basemin. 1 game": "SELECT playerID FROM appearances WHERE G_3b > 0;",
        "Puerto Rico": "SELECT playerID FROM people WHERE birthCountry = 'Puerto Rico';",
        "Rookie of the Year": "SELECT playerID FROM awards WHERE awardID = 'Rookie of the Year Award';",
        "Silver Slugger": "SELECT playerID FROM awards WHERE awardID = 'Silver Slugger';",
        "Threw a No-Hitter": "SELECT playerID FROM pitching WHERE p_SHO > 0;",  # Approximation
        "United States": "SELECT playerID FROM people WHERE birthCountry = 'USA';",
        "World Series Champ WS Roster": """
            SELECT DISTINCT playerID
            FROM seriespost
            WHERE round = 'WS' AND teamID IN (
                SELECT teamID FROM teams WHERE WSWin = 'Y'
            );
        """,
        "≤ 3.00 ERA CareerPitching": """
            SELECT playerID
            FROM (
                SELECT playerID, SUM(p_ER) / (SUM(p_IPOuts) / 3) AS era
                FROM pitching
                GROUP BY playerID
                HAVING era <= 3.00
            ) AS career_era;
        """,
        "≤ 3.00 ERA Season": "SELECT playerID FROM pitching WHERE p_ER / (p_IPOuts / 3) <= 3.00;",
    }

    normalized_trivia = normalize_input(trivia)
    query = trivia_map.get(normalized_trivia)
    if not query:
        print(f"No SQL query mapped for trivia: {normalized_trivia}")
        return set()


    return execute_query(query)

# Determine if input is a team
def is_team(input_value):
    query = "SELECT COUNT(*) AS count FROM teams WHERE team_name = %s;"
    normalized_value = normalize_input(input_value)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (normalized_value,))
            result = cursor.fetchone()
            return result and result["count"] > 0
    except Exception as e:
        print(f"Error in is_team(): {e}")
        return False
    finally:
        connection.close()

def get_players_for_team_and_trivia(team_name, trivia):
    """
    Fetch playerIDs where the trivia condition is met while the player was with the specified team.
    """
    # Fetch the trivia query
    team_name = normalize_team_name(team_name)
    trivia = normalize_input(trivia)
    query = trivia_team_map.get(trivia)
    if not query:
        print(f"No team-specific query mapped for trivia: {trivia}")
        return set()


    params = (team_name,)
    team_specific_results = execute_query(query, params)

    if team_specific_results:
        return team_specific_results

    print(f"No team-specific match found for trivia: {trivia}. Trying general trivia query.")
    return []

# Fetch the playerName from the MySQL database using playerID
def get_player_name_and_years_from_db(player_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
            SELECT nameFirst, nameLast, debutDate, finalGameDate
            FROM people
            WHERE playerID = %s;
            """
            cursor.execute(query, (player_id,))
            result = cursor.fetchone()
            if result:
                name = f"{result['nameFirst']} {result['nameLast']}"
                # Extract years from 'debut' and 'finalGame' dates
                debut_year = result['debutDate'].year if result['debutDate'] else 'Unknown'
                final_year = result['finalGameDate'].year if result['finalGameDate'] else 'Unknown'
                career_years = f"{debut_year}-{final_year}"
                return name, career_years
            else:
                return None, None
    except Exception as e:
        print(f"Error fetching player name and years: {e}")
        return None, None
    finally:
        connection.close()


def remove_duplicates_keep_detailed(items):
    """
    Removes duplicates while keeping the most detailed version of each entry.
    Uses substring matching to compare strings flexibly.
    """
    # Normalize items to replace non-breaking spaces with regular spaces
    normalized_items = items
    filtered_items = []
    for i, item in enumerate(normalized_items):
        is_duplicate = False
        for j, other_item in enumerate(normalized_items):
            if i != j and item != other_item:
                # Check if one string is a substring of the other
                if len(item) < len(other_item) and all(word in other_item for word in item.split()):
                    is_duplicate = True
                    break
        if not is_duplicate:
            filtered_items.append(items[i])  # Append the original unnormalized item
    return filtered_items

# Scrape the grid
def scrape_immaculate_grid(puzzle_number=None):
    """
    Scrape the grid from immaculategrid.com. If a puzzle number is provided,
    construct the URL with the given number. Otherwise, scrape the current day's grid.
    """
    url = f"https://www.immaculategrid.com"
    if puzzle_number:
        url = f"{url}/grid-{puzzle_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Request failed: {e}")
        return [], []

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract raw top row and left column
    top_row_raw = soup.select(
        ".w-24.sm\\:w-36.md\\:w-48.h-16.sm\\:h-24.md\\:h-36 img, .w-24.sm\\:w-36.md\\:w-48.h-16.sm\\:h-24.md\\:h-36 div.leading-tight"
    )
    left_column_raw = soup.select(
        ".h-24.sm\\:h-36.md\\:h-48 img, .h-24.sm\\:h-36.md\\:h-48 div.leading-tight"
    )

    # Process top row
    top_row = []
    for element in top_row_raw:
        if element.name == "img":
            top_row.append(element["alt"])
        elif element.name == "div":
            top_row.append(element.get_text(strip=True))

    # Process left column
    left_column = []
    for element in left_column_raw:
        if element.name == "img":
            left_column.append(element["alt"])
        elif element.name == "div":
            left_column.append(element.get_text(strip=True))

    # Deduplicate and ensure 3 unique items
    top_row = remove_duplicates_keep_detailed(list(dict.fromkeys(top_row)))[:3]
    left_column = remove_duplicates_keep_detailed(list(dict.fromkeys(left_column)))[:3]

    # Debugging: Print results
    print("Top Row:", top_row)
    print("Left Column:", left_column)

    return top_row, left_column


# Define your trivia_team_map with all the necessary queries
trivia_team_map = {
"All Star": """
        SELECT DISTINCT ap.playerID
        FROM allstarfull ap
        JOIN appearances a ON ap.playerID = a.playerID AND ap.yearID = a.yearID
        JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID and ap.yearid = t.yearid
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) ;
    """,
"300+ HR CareerBatting": """
        SELECT playerID
        FROM (
            SELECT b.playerID, SUM(b.b_HR) AS total_hr
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
            GROUP BY b.playerID
            HAVING total_hr >= 300
        ) AS career_hr;
    """,
    "300+ Save CareerPitching": """
        SELECT playerID
        FROM (
            SELECT p.playerID, SUM(p.p_SV) AS total_saves
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID
            WHERE t.team_name = %s
            GROUP BY p.playerID
            HAVING total_saves >= 300
        ) AS career_saves;
    """,
    "300+ Wins CareerPitching": """
        SELECT playerID
        FROM (
            SELECT p.playerID, SUM(p.p_W) AS total_wins
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID
            WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
            GROUP BY p.playerID
            HAVING total_wins >= 300
        ) AS career_wins;
    """,
    "3000+ Hits CareerBatting": """
        SELECT playerID
        FROM (
            SELECT b.playerID, SUM(b.b_H) AS total_hits
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
            GROUP BY b.playerID
            HAVING total_hits >= 3000
        ) AS career_hits;
    """,
    "3000+ K CareerPitching": """
        SELECT playerID
        FROM (
            SELECT p.playerID, SUM(p.p_SO) AS total_strikes
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID
            WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
            GROUP BY p.playerID
            HAVING total_strikes >= 3000
        ) AS career_strikes;
    """,
    "40+ 2B SeasonBatting": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID AND b.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_2B >= 40;
    """,
    "40+ HR SeasonBatting": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID AND b.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_HR >= 40;
    """,
    "40+ Save SeasonPitching": """
        SELECT p.playerID
        FROM pitching p
        JOIN teams t ON p.teamID = t.teamID AND p.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND p.p_SV >= 40;
    """,
    "500+ HR CareerBatting": """
       SELECT p.playerID
FROM (
    -- Step 1: Find players with 500+ career home runs across all franchises
    SELECT playerID
    FROM batting
    GROUP BY playerID
    HAVING SUM(b_HR) >= 500
) AS p
WHERE EXISTS (
    -- Step 2: Ensure the player has at least one game with a team matching the team_name pattern
    SELECT 1
    FROM batting b
    JOIN teams t ON b.teamID = t.teamID
    WHERE b.playerID = p.playerID
      AND t.franchid = (
          SELECT franchid
          FROM teams
          WHERE team_name LIKE %s
          GROUP BY franchid
          ORDER BY COUNT(*) DESC
          LIMIT 1
      )
    LIMIT 1
);

    """,
    "Born Outside US 50 States and DC": """
        SELECT playerID
        FROM players
        WHERE (birthCountry NOT IN ('USA', 'US'))
          AND teamID IN (
              SELECT teamID FROM teams WHERE franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
          );
    """,
    "Canada": """
        SELECT playerID
        FROM players
        WHERE birthCountry = 'Canada'
          AND teamID IN (
              SELECT teamID FROM teams WHERE franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
          );
    """,
    "Dominican Republic": """
        SELECT playerID
        FROM players
        WHERE birthCountry = 'Dominican Republic'
          AND teamID IN (
              SELECT teamID FROM teams WHERE franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
          );
    """,
    "Pitchedmin. 1 game": """
        SELECT DISTINCT p.playerID
        FROM pitching p
        JOIN teams t ON p.teamID = t.teamID AND p.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND p.p_G > 0;
    """,
    "Played In Major Negro Lgs": """
        SELECT DISTINCT n.playerID
        FROM negro_leagues n
        JOIN teams t ON n.teamID = t.teamID AND n.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) ;
    """,
    "Puerto Rico": """
        SELECT playerID
        FROM players
        WHERE birthCountry = 'Puerto Rico'
          AND teamID IN (
              SELECT teamID FROM teams WHERE franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
          );
    """,
    "United States": """
        SELECT p.playerID
FROM people p
JOIN batting b ON b.playerID = p.playerID
JOIN teams t ON b.teamID = t.teamID
WHERE p.birthCountry = 'USA' AND t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) ;
    """,
    "World Series ChampWS Roster": """
        SELECT DISTINCT playerID
        from batting b
        JOIN teams t ON b.teamID = t.teamID AND b.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s and t.yearid > 1902
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) AND WSWin = 'Y';
    """,
"30+ HR /30+ SB SeasonBatting": """
        SELECT DISTINCT s.playerID
        FROM (
            SELECT playerID, yearID
            FROM batting
            GROUP BY playerID, yearID
            HAVING SUM(b_HR) >= 30 AND SUM(b_SB) >= 30
        ) s
        JOIN batting b ON s.playerID = b.playerID AND s.yearID = b.yearID
        JOIN teams t ON b.teamID = t.teamID AND b.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) ;
    """,
 "First Round Draft Pick": """
        SELECT DISTINCT a.playerID
        FROM draft d
        JOIN batting a ON d.playerID = a.playerID
        JOIN teams t ON a.teamID = t.teamID AND d.yearID = t.yearID
        WHERE d.round = 1 AND t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) ;
    """,
"40+ WAR Career": """
    SELECT playerID
    FROM (
        SELECT b.playerID, SUM(b.b_WAR) AS career_war
        FROM batting b
        GROUP BY b.playerID
        HAVING career_war >= 40
    ) AS career_war_table
    WHERE playerID IN (
        SELECT DISTINCT a.playerID
        FROM appearances a
        JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
    );
""",

    "6+ WAR Season": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID AND b.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_WAR >= 6;
    """,
    ".300+ AVG CareerBatting": """
        SELECT playerID
        FROM (
            SELECT b.playerID, SUM(b.b_H) AS total_hits, SUM(b.b_AB) AS total_at_bats
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
            GROUP BY b.playerID
            HAVING total_hits / total_at_bats > 0.300
        ) AS career_avg;
    """,
    ".300+ AVG SeasonBatting": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_H / b.b_AB > 0.300;
    """,
    "10+ HR SeasonBatting": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_HR >= 10;
    """,
    "10+ Win SeasonPitching": """
        SELECT p.playerID
        FROM pitching p
        JOIN teams t ON p.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND p.p_W >= 10;
    """,
    "100+ RBI SeasonBatting": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_RBI >= 100;
    """,
    "100+ Run SeasonBatting": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_R >= 100;
    """,
    "20+ Win SeasonPitching": """
        SELECT p.playerID
        FROM pitching p
        JOIN teams t ON p.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND p.p_W >= 20;
    """,
    "200+ Hits SeasonBatting": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_H >= 200;
    """,
    "200+ K SeasonPitching": """
        SELECT p.playerID
        FROM pitching p
        JOIN teams t ON p.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND p.p_SO >= 200;
    """,
    "200+ Wins CareerPitching": """
        SELECT playerID
        FROM (
            SELECT p.playerID, SUM(p.p_W) AS total_wins
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID
            WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
            GROUP BY p.playerID
            HAVING total_wins >= 200
        ) AS career_wins;
    """,
    "2000+ Hits CareerBatting": """
        SELECT playerID
        FROM (
            SELECT b.playerID, SUM(b.b_H) AS total_hits
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
            GROUP BY b.playerID
            HAVING total_hits >= 2000
        ) AS career_hits;
    """,
    "2000+ K CareerPitching": """
    SELECT cs.playerID
    FROM (
        SELECT playerID, SUM(p_SO) AS total_ks
        FROM pitching
        GROUP BY playerID
        HAVING total_ks >= 2000
    ) AS cs
    WHERE cs.playerID IN (
        SELECT DISTINCT p.playerID
        FROM pitching p
        JOIN teams t ON p.teamID = t.teamID AND p.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
    );
""",

    "Cy Young": """
      SELECT DISTINCT ap.playerID
      FROM awards ap
      JOIN appearances a ON ap.playerID = a.playerID AND ap.yearID = a.yearID
      JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
      WHERE ap.awardID = 'Cy Young Award' AND t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) ;
  """,

    "Gold Glove": """
      SELECT DISTINCT ap.playerID
      FROM awards ap
      JOIN appearances a ON ap.playerID = a.playerID AND ap.yearID = a.yearID
      JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
      WHERE ap.awardID = 'Gold Glove' AND t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) ;
  """,

    "MVP": """
      SELECT DISTINCT ap.playerID
      FROM awards ap
      JOIN appearances a ON ap.playerID = a.playerID AND ap.yearID = a.yearID
      JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
      WHERE ap.awardID = 'Most Valuable Player' AND t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) ;
  """,

    "Rookie of the Year": """
      SELECT DISTINCT ap.playerID
      FROM awards ap
      JOIN appearances a ON ap.playerID = a.playerID AND ap.yearID = a.yearID
      JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
      WHERE ap.awardID = 'Rookie of the Year' AND t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) ;
  """,

    "Silver Slugger": """
      SELECT DISTINCT ap.playerID
      FROM awards ap
      JOIN batting a ON ap.playerID = a.playerID
      JOIN teams t ON a.teamID = t.teamID
      WHERE ap.awardID = 'Silver Slugger' AND t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND ap.yearid = t.yearid and a.yearid = t.yearid and ap.playerid != 'stantmi03';
  """,

    "Hall of Fame": """
      SELECT DISTINCT h.playerID
      FROM halloffame h
      JOIN appearances a ON h.playerID = a.playerID
      JOIN teams t ON a.teamID = t.teamID
      WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND h.inducted = 'Y';
  """,

    "Threw a No-Hitter": """
      SELECT DISTINCT p.playerID
      FROM pitching p
      JOIN teams t ON p.teamID = t.teamID AND p.yearID = t.yearID
      WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND p.p_NO != 0;
  """,

    "30+ HR / 30+ SB SeasonBatting": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_HR >= 30 AND b.b_SB >= 30;
    """,
    "30+ HR SeasonBatting": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_HR >= 30;
    """,
    "30+ SB Season": """
        SELECT b.playerID
        FROM batting b
        JOIN teams t ON b.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND b.b_SB >= 30;
    """,
    "30+ Save SeasonPitching": """
        SELECT p.playerID
        FROM pitching p
        JOIN teams t ON p.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND p.p_SV >= 30;
    """,
    "Played Catchermin. 1 game": """
        SELECT f.playerID
        FROM fielding f
        JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND f.position = 'C' AND f.f_G > 0;
    """,

    "Played First Basemin. 1 game": """
        SELECT f.playerID
        FROM fielding f
        JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND f.position = '1B' AND f.f_G > 0;
    """,

    "Played Second Basemin. 1 game": """
        SELECT f.playerID
        FROM fielding f
        JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND f.position = '2B' AND f.f_G > 0;
    """,

    "Played Third Basemin. 1 game": """
        SELECT f.playerID
        FROM fielding f
        JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND f.position = '3B' AND f.f_G > 0;
    """,

    "Played Shortstopmin. 1 game": """
        SELECT f.playerID
        FROM fielding f
        JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND f.position = 'SS' AND f.f_G > 0;
    """,

    "Played Left Fieldmin. 1 game": """
        SELECT f.playerID
        FROM fielding f
        JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND f.position = 'LF' AND f.f_G > 0;
    """,

    "Played Center Fieldmin. 1 game": """
        SELECT f.playerID
        FROM fielding f
        JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND f.position = 'CF' AND f.f_G > 0;
    """,

    "Played Right Fieldmin. 1 game": """
        SELECT f.playerID
        FROM fielding f
        JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND f.position = 'RF' AND f.f_G > 0;
    """,

    "Played Outfieldmin. 1 game": """
        SELECT f.playerID
        FROM fielding f
        JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND f.position IN ('LF', 'CF', 'RF') AND f.f_G > 0;
    """,

    # If you have a trivia for "Played Designated Hittermin. 1 game":
    "Designated Hittermin. 1 game": """
        SELECT f.playerID
        FROM fielding f
        JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND f.position = 'DH' AND f.f_G > 0;
    """,
    "≤ 3.00 ERA CareerPitching": """
        SELECT playerID
        FROM (
            SELECT p.playerID, SUM(p.p_ER) / (SUM(p.p_IPOuts) / 3) AS era
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID
            WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
            GROUP BY p.playerID
            HAVING era <= 3.00
        ) AS career_era;
    """,
    "≤ 3.00 ERA Season": """
        SELECT p.playerID
        FROM pitching p
        JOIN teams t ON p.teamID = t.teamID
        WHERE t.franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    )  AND p.p_ER / (p.p_IPOuts / 3) <= 3.00;
    """,
"Only One Team": """
        SELECT a.playerID
        FROM appearances a
        GROUP BY a.playerID
        HAVING SUM(CASE WHEN a.teamID NOT IN (
            SELECT DISTINCT teamID
            FROM teams
            WHERE franchid = (
        SELECT franchid
        FROM teams
        WHERE team_name = %s
        GROUP BY franchid
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) 
        ) THEN 1 ELSE 0 END) = 0;
    """,
}



# Function to solve the puzzle
def solve_puzzle(puzzle_number=None):
    """
    Solve the puzzle for the given puzzle number. If no puzzle number is provided,
    solve the current day's puzzle.
    """
    selected_player_ids = set()
    top_row, left_column = scrape_immaculate_grid(puzzle_number)

    # Ensure we have 3x3 grid values
    if len(top_row) != 3 or len(left_column) != 3:
        print("Error: Grid scraping did not produce a 3x3 grid.")
        return top_row, left_column, [["Error"]] * 3

    # Initialize a 3x3 grid for results
    grid = [["" for _ in range(3)] for _ in range(3)]

    # Populate the grid with player names
    for i, row_value in enumerate(left_column):
        for j, col_value in enumerate(top_row):
            print(f"\nProcessing Cell: Row='{row_value}', Column='{col_value}'")

            # Determine whether row and column are team or trivia
            row_is_team = is_team(row_value)
            col_is_team = is_team(col_value)

            # Initialize intersected_players
            intersected_players = set()

            if row_is_team and col_is_team:
                # Team vs. Team
                print(f"Handling Team vs. Team: {row_value} vs. {col_value}")
                team1_players = get_players_for_team(row_value)
                team2_players = get_players_for_team(col_value)
                intersected_players = team1_players & team2_players
            elif row_is_team and not col_is_team:
                # Team vs. Trivia
                print(f"Handling Team vs. Trivia: {row_value} vs. {col_value}")
                intersected_players = get_players_for_team_and_trivia(row_value, col_value)
            elif not row_is_team and col_is_team:
                # Trivia vs. Team
                print(f"Handling Trivia vs. Team: {row_value} vs. {col_value}")
                intersected_players = get_players_for_team_and_trivia(col_value, row_value)
            else:
                # Trivia vs. Trivia
                print(f"Handling Trivia vs. Trivia: {row_value} vs. {col_value}")
                trivia1_players = get_players_for_trivia(row_value)
                trivia2_players = get_players_for_trivia(col_value)
                intersected_players = trivia1_players & trivia2_players

            # Log the intersected players
            print(f"Intersected Players for Cell ({row_value}, {col_value}): {intersected_players}")

            if intersected_players:
                # Get the oldest player not already selected
                player_id = get_oldest_player(intersected_players, selected_player_ids)
                if player_id:
                    player_name, career_years = get_player_name_and_years_from_db(player_id)
                    grid[i][j] = (player_name, career_years)
                    # Add the player_id to the selected set
                    selected_player_ids.add(player_id)
                else:
                    grid[i][j] = "No Match"
            else:
                grid[i][j] = "No Match"

    return top_row, left_column, grid


# Define the Flask route

def get_oldest_player(player_ids, selected_player_ids):
    """
    Given a set of playerIDs, returns the playerID with the earliest debut year,
    excluding any playerIDs in selected_player_ids.
    """
    if not player_ids:
        return None

    # Exclude already selected player IDs
    available_player_ids = player_ids - selected_player_ids
    if not available_player_ids:
        return None

    player_ids_tuple = tuple(available_player_ids)
    placeholders = ','.join(['%s'] * len(player_ids_tuple))

    query = f"""
    SELECT a.playerID, MIN(a.yearID) AS debut_year
    FROM appearances a
    WHERE a.playerID IN ({placeholders})
    GROUP BY a.playerID
    ORDER BY debut_year ASC
    LIMIT 1
    """
    params = player_ids_tuple

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result and result['playerID']:
                return result['playerID']
            else:
                return None
    except Exception as e:
        print(f"Error in get_oldest_player(): {e}")
        return None
    finally:
        connection.close()

