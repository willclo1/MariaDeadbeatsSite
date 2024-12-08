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

trivia_team_map = {
    "All Star": """
            SELECT DISTINCT ap.playerID
            FROM allstarfull ap
            JOIN appearances a ON ap.playerID = a.playerID AND ap.yearID = a.yearID
            JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID and ap.yearid = t.yearid
            WHERE t.team_name in (%s);
        """,
    "300+ HR CareerBatting": """
            SELECT playerID
            FROM (
                SELECT b.playerID, SUM(b.b_HR) AS total_hr
                FROM batting b
                GROUP BY b.playerID
                HAVING total_hr >= 300
            ) AS career_hr
            WHERE playerID IN (
                SELECT DISTINCT b.playerID
                FROM batting b
                JOIN teams t ON b.teamID = t.teamID AND b.yearID = t.yearID
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
    "300+ Save CareerPitching": """
            SELECT playerID
            FROM (
                SELECT p.playerID, SUM(p.p_SV) AS total_saves
                FROM pitching p
                GROUP BY p.playerID
                HAVING total_saves >= 300
            ) AS career_saves
            WHERE playerID IN (
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
    "300+ Wins CareerPitching": """
            SELECT playerID
            FROM (
                SELECT p.playerID, SUM(p.p_W) AS total_wins
                FROM pitching p
                GROUP BY p.playerID
                HAVING total_wins >= 300
            ) AS career_wins
            WHERE playerID IN (
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
    "3000+ Hits CareerBatting": """
            SELECT playerID
            FROM (
                SELECT b.playerID, SUM(b.b_H) AS total_hits
                FROM batting b
                GROUP BY b.playerID
                HAVING total_hits >= 3000
            ) AS career_hits
            WHERE playerID IN (
                SELECT DISTINCT b.playerID
                FROM batting b
                JOIN teams t ON b.teamID = t.teamID AND b.yearID = t.yearID
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
    "3000+ K CareerPitching": """
            SELECT playerID
            FROM (
                SELECT p.playerID, SUM(p.p_SO) AS total_strikes
                FROM pitching p
                GROUP BY p.playerID
                HAVING total_strikes >= 3000
            ) AS career_strikes
            WHERE playerID IN (
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
                  SELECT teamID FROM teams WHERE team_name in (%s)
              );
        """,
    "Canada": """
            SELECT playerID
            FROM players
            WHERE birthCountry = 'Canada'
              AND teamID IN (
                  SELECT teamID FROM teams WHERE team_name in (%s)
              );
        """,
    "Dominican Republic": """
            SELECT playerID
            FROM players
            WHERE birthCountry = 'Dominican Republic'
              AND teamID IN (
                  SELECT teamID FROM teams WHERE team_name in (%s)
              );
        """,
    "Pitchedmin. 1 game": """
            SELECT DISTINCT p.playerID
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID AND p.yearID = t.yearID
            WHERE t.team_name in (%s) AND p.p_G > 0;
        """,
    "Played In Major Negro Lgs": """
            SELECT DISTINCT n.playerID
            FROM negro_leagues n
            JOIN teams t ON n.teamID = t.teamID AND n.yearID = t.yearID
            WHERE t.team_name in (%s);
        """,
    "Puerto Rico": """
            SELECT playerID
            FROM players
            WHERE birthCountry = 'Puerto Rico'
              AND teamID IN (
                  SELECT teamID FROM teams WHERE team_name in (%s)
              );
        """,
    "United States": """
            SELECT p.playerID
    FROM people p
    JOIN batting b ON b.playerID = p.playerID
    JOIN teams t ON b.teamID = t.teamID
    WHERE p.birthCountry = 'USA' AND t.team_name in (%s);
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
            WHERE t.team_name in (%s);
        """,
    "First Round Draft Pick": """
            SELECT DISTINCT a.playerID
            FROM draft d
            JOIN batting a ON d.playerID = a.playerID
            JOIN teams t ON a.teamID = t.teamID AND d.yearID = t.yearID
            WHERE d.round = 1 AND t.team_name in (%s);
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
            WHERE t.team_name in (%s) AND b.b_WAR >= 6;
        """,
    ".300+ AVG CareerBatting": """
            SELECT playerID
            FROM (
                SELECT b.playerID, SUM(b.b_H) AS total_hits, SUM(b.b_AB) AS total_at_bats
                FROM batting b
                GROUP BY b.playerID
                HAVING SUM(b.b_H) / SUM(b.b_AB) > 0.300
            ) AS career_avg
            WHERE playerID IN (
                SELECT DISTINCT b.playerID
                FROM batting b
                JOIN teams t ON b.teamID = t.teamID AND b.yearID = t.yearID
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
    ".300+ AVG SeasonBatting": """
            SELECT b.playerID
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.team_name in (%s) AND b.b_H / b.b_AB > 0.300;
        """,
    "10+ HR SeasonBatting": """
            SELECT b.playerID
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.team_name in (%s) AND b.b_HR >= 10;
        """,
    "10+ Win SeasonPitching": """
            SELECT p.playerID
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID
            WHERE t.team_name in (%s) AND p.p_W >= 10;
        """,
    "100+ RBI SeasonBatting": """
            SELECT b.playerID
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.team_name in (%s) AND b.b_RBI >= 100;
        """,
    "100+ Run SeasonBatting": """
            SELECT b.playerID
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.team_name in (%s) AND b.b_R >= 100;
        """,
    "20+ Win SeasonPitching": """
            SELECT p.playerID
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID
            WHERE t.team_name in (%s) AND p.p_W >= 20;
        """,
    "200+ Hits SeasonBatting": """
            SELECT b.playerID
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.team_name in (%s) AND b.b_H >= 200;
        """,
    "200+ K SeasonPitching": """
            SELECT p.playerID
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID
            WHERE t.team_name in (%s) AND p.p_SO >= 200;
        """,
    "200+ Wins CareerPitching": """
            SELECT playerID
            FROM (
                SELECT p.playerID, SUM(p.p_W) AS total_wins
                FROM pitching p
                GROUP BY p.playerID
                HAVING total_wins >= 200
            ) AS career_wins
            WHERE playerID IN (
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
    "2000+ Hits CareerBatting": """
            SELECT playerID
            FROM (
                SELECT b.playerID, SUM(b.b_H) AS total_hits
                FROM batting b
                GROUP BY b.playerID
                HAVING total_hits >= 2000
            ) AS career_hits
            WHERE playerID IN (
                SELECT DISTINCT b.playerID
                FROM batting b
                JOIN teams t ON b.teamID = t.teamID AND b.yearID = t.yearID
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
    "2000+ K CareerPitching": """
        SELECT cs.playerID
        FROM (
            SELECT playerID, SUM(p_SO) AS total_ks
            FROM pitching
            GROUP BY playerID
            HAVING SUM(p_SO) >= 2000
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
          WHERE ap.awardID = 'Cy Young Award' AND t.team_name in (%s);
      """,

    "Gold Glove": """
          SELECT DISTINCT ap.playerID
          FROM awards ap
          JOIN appearances a ON ap.playerID = a.playerID AND ap.yearID = a.yearID
          JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
          WHERE ap.awardID = 'Gold Glove' AND t.team_name in (%s);
      """,

    "MVP": """
          SELECT DISTINCT ap.playerID
          FROM awards ap
          JOIN appearances a ON ap.playerID = a.playerID AND ap.yearID = a.yearID
          JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
          WHERE ap.awardID = 'Most Valuable Player' AND t.team_name in (%s);
      """,

    "Rookie of the Year": """
          SELECT DISTINCT ap.playerID
          FROM awards ap
          JOIN appearances a ON ap.playerID = a.playerID AND ap.yearID = a.yearID
          JOIN teams t ON a.teamID = t.teamID AND a.yearID = t.yearID
          WHERE ap.awardID = 'Rookie of the Year' AND t.team_name in (%s);
      """,

    "Silver Slugger": """
          SELECT DISTINCT ap.playerID
          FROM awards ap
          JOIN batting a ON ap.playerID = a.playerID
          JOIN teams t ON a.teamID = t.teamID
          WHERE ap.awardID = 'Silver Slugger' AND t.team_name in (%s) AND ap.yearid = t.yearid and a.yearid = t.yearid and ap.playerid != 'stantmi03';
      """,

    "Hall of Fame": """
          SELECT DISTINCT h.playerID
          FROM halloffame h
          JOIN appearances a ON h.playerID = a.playerID
          JOIN teams t ON a.teamID = t.teamID
          WHERE t.team_name in (%s) AND h.inducted = 'Y';
      """,

    "Threw a No-Hitter": """
          SELECT DISTINCT p.playerID
          FROM pitching p
          JOIN teams t ON p.teamID = t.teamID AND p.yearID = t.yearID
          WHERE t.team_name in (%s) AND p.p_NO != 0;
      """,

    "30+ HR / 30+ SB SeasonBatting": """
            SELECT b.playerID
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.team_name in (%s) AND b.b_HR >= 30 AND b.b_SB >= 30;
        """,
    "30+ HR SeasonBatting": """
            SELECT b.playerID
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.team_name in (%s) AND b.b_HR >= 30;
        """,
    "30+ SB Season": """
            SELECT b.playerID
            FROM batting b
            JOIN teams t ON b.teamID = t.teamID
            WHERE t.team_name in (%s) AND b.b_SB >= 30;
        """,
    "30+ Save SeasonPitching": """
            SELECT p.playerID
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID
            WHERE t.team_name in (%s) AND p.p_SV >= 30;
        """,
    "Played Catchermin. 1 game": """
            SELECT f.playerID
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            WHERE t.team_name in (%s) AND f.position = 'C' AND f.f_G > 0;
        """,

    "Played First Basemin. 1 game": """
            SELECT f.playerID
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            WHERE t.team_name in (%s) AND f.position = '1B' AND f.f_G > 0;
        """,

    "Played Second Basemin. 1 game": """
            SELECT f.playerID
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            WHERE t.team_name in (%s) AND f.position = '2B' AND f.f_G > 0;
        """,

    "Played Third Basemin. 1 game": """
            SELECT f.playerID
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            WHERE t.team_name in (%s) AND f.position = '3B' AND f.f_G > 0;
        """,

    "Played Shortstopmin. 1 game": """
            SELECT f.playerID
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            WHERE t.team_name in (%s) AND f.position = 'SS' AND f.f_G > 0;
        """,

    "Played Left Fieldmin. 1 game": """
            SELECT f.playerID
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            WHERE t.team_name in (%s) AND f.position = 'LF' AND f.f_G > 0;
        """,

    "Played Center Fieldmin. 1 game": """
            SELECT f.playerID
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            WHERE t.team_name in (%s) AND f.position = 'CF' AND f.f_G > 0;
        """,

    "Played Right Fieldmin. 1 game": """
            SELECT f.playerID
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            WHERE t.team_name in (%s) AND f.position = 'RF' AND f.f_G > 0;
        """,

    "Played Outfieldmin. 1 game": """
            SELECT f.playerID
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            WHERE t.team_name in (%s) AND f.position IN ('LF', 'CF', 'RF') AND f.f_G > 0;
        """,

    # If you have a trivia for "Played Designated Hittermin. 1 game":
    "Designated Hittermin. 1 game": """
            SELECT f.playerID
            FROM fielding f
            JOIN teams t ON f.teamID = t.teamID AND f.yearID = t.yearID
            WHERE t.team_name in (%s) AND f.position = 'DH' AND f.f_G > 0;
        """,
    "≤ 3.00 ERA CareerPitching": """
            SELECT playerID
            FROM (
                SELECT p.playerID, SUM(p.p_ER) / (SUM(p.p_IPOuts) / 3) AS era
                FROM pitching p
                GROUP BY p.playerID
                HAVING era <= 3.00
            ) AS career_era
            WHERE playerID IN (
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
    "≤ 3.00 ERA Season": """
            SELECT p.playerID
            FROM pitching p
            JOIN teams t ON p.teamID = t.teamID
            WHERE t.team_name in (%s) AND p.p_ER / (p.p_IPOuts / 3) <= 3.00;
        """,
    "Only One Team": """
            SELECT a.playerID
            FROM appearances a
            GROUP BY a.playerID
            HAVING SUM(CASE WHEN a.teamID NOT IN (
                SELECT DISTINCT teamID
                FROM teams
                WHERE team_name in (%s)
            ) THEN 1 ELSE 0 END) = 0;
        """,
}
