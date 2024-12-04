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
6. Set up a virtual environment and install requirements:
   ```bash
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

## **How to Run the Flask App**

### **Step-by-Step Instructions**

1. Clone the repository:
   ```bash
   git clone https://github.com/willclo1/MariaDeadbeatsSite.git
   ```
2. Set up a virtual environment and install requirements:
   ```bash
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

