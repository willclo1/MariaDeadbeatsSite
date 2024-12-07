# **MariaDeadbeats: Database Setup and Flask App Guide**

## **Update Database (Python - Long Way)**

### **Step-by-Step Instructions**

1. Clone the repository:
   ```bash
   git clone https://github.com/willclo1/MariaDeadbeats.git
   ```
2. Log into your MariaDB server using the shell:
   ```bash
   mysql -u your_username -p
   ```
3. Create a new empty database:
   ```sql
   CREATE DATABASE MariaDeadbeats;
   ```
4. Switch to the `MariaDeadbeats` database:
   ```sql
   USE MariaDeadbeats;
   ```
5. Run the `baseball.sql` file to initialize the database:
   - **macOS/Linux**:
     ```sql
     source /path/to/baseball.sql;
     ```
   - **Windows**:
     ```sql
     source C:\\path\\to\\baseball.sql;
     ```
6. Set up a virtual environment and install requirements in the project directory:
   ```bash
   cd MariaDeadbeats
   python -m venv project_env
   source project_env/bin/activate  # macOS/Linux
   project_env\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```
7. Configure the `cfg.py` file with the correct connection information for your database.
8. Navigate to the project root and run the Python script:
   ```bash
   python -m tableActions.updateDB
   ```
9. Your database is updated!

---

## **Update Database (SQL Dump - Short/Better Way)**

### **Step-by-Step Instructions**

1. Create a new database:
   ```sql
   CREATE DATABASE MariaDeadbeats;
   ```
2. Run the SQL dump file:
   - **macOS/Linux**:
     ```bash
     mysql -u your_username -p MariaDeadbeats < /path/to/sql_dump.sql
     ```
   - **Windows**:
     ```cmd
     mysql -u your_username -p MariaDeadbeats < C:\\path\\to\\sql_dump.sql
     ```
3. Your database is updated!
---
## **How to Run the Flask App**

### **Step-by-Step Instructions**

1. Clone the repository:
   ```bash
   git clone https://github.com/willclo1/MariaDeadbeatsSite.git
   ```
2. Set up a virtual environment and install requirements:
   ```bash
   cd MariaDeadbeatsSite
   python -m venv project_env
   source project_env/bin/activate  # macOS/Linux
   project_env\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```
3. Navigate to the project root directory and run the Flask app:
   ```bash
   flask run
   ```
4. The project should now be running!
---

## **Updates to the Database**

- **Banned_Users**:
  - A table with `id`, `username`, and `email`.
  - Used to show users banned from the Flask application.

- **Batting**:
  - Added a new column `b_WAR` from a CSV found at [MLB WAR Data Historical](https://github.com/Neil-Paine-1/MLB-WAR-data-historical).

- **Draft**:
  - A table with `draft_id`, `playerID`, `yearID`, `nameFirst`, `nameLast`, `round`, `pick`, `description`.
  - Only shows players from the Amateur Draft (indicated by the `description` column).
  - Data sourced from [Baseball Draft Data](https://github.com/double-dose-larry/baseball_draft_data).

- **Parks**:
  - Added `latitude` and `longitude` columns for displaying a map of parks.
  - Used Google Geocoding API to obtain these values (configured in `cfg.py`).

- **Pitching**:
  - Added a new column `p_WAR` from a CSV found at [MLB WAR Data Historical](https://github.com/Neil-Paine-1/MLB-WAR-data-historical).
  - Added a new column `p_NH` for no-hitters, sourced from [Baseball Reference](https://www.baseball-reference.com/friv/no-hitters-and-perfect-games.shtml?utm_campaign=2023_07_ig_possible_answers&utm_source=ig&utm_medium=sr_xsite).

- **Users**:
  - A table with `id`, `username`, `email`, `time_of_last_access`, `password_hash`, and `is_admin`.
  - This table is used to register new users in the Flask application.

---

## **MariaDeadbeats App Features**

- **Team Summary**:
   - A page that shows a team from a specific year and stats about that team and the players from that team
   - Some shown stats are things like `war` and `k/9`
   - This page also displays information about the teams performance on the year
   
- **Depth Chart**
  - A page that shows the players for a team and how often they played throughout the season
  - Shows a projected starting lineup based on the playing time for each player
    
 - **Compare Batters**
   - A page that allows the user to enter the name of two batters and compares their stats
   - It compares the following stats: `hits`, `homeruns`, `RBIs`, `avg`, `WAR`

- **Solve Grid**
  - A page thar solves the immaculate grid game for any game
  
- **View Parks**
  - A page that shows the location of every baseball park on an interactive map
  - It contains links to Google Street View to examine the locations of these stadiums
  - Historical stadiums are attempted to be displayed but commercial areas often replace these stadiums
 
- **News**
  - A page that shows current news from ESPN about the MLB
  - Article titles can be selected to read the ESPN article on their website

- **Admin Account**
  - An account that can be used to control access to the application
  - Has the ability to ban users, unban users, view a list of banned users,
  - and create other admin users.

- **Season Countdown** 
  - A page that counts down until the start of the season and will also display information about
  - the first game of the season. Uses sportradar api to get up to date information.
 
Check out the app! It is really cool and has a lot of awesome features!

