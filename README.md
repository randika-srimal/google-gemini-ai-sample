# Python + Google Gemini - Employee Skill Reader

This is an sample tool developed for test Google Gemini and Python integration. Steps to test.

1. Install docker and docker compose tools.
2. Run `make up` command to spin up docker containers.
3. Use the provided db.sql file as the database structure.(PhpMyadmin can be accessed via localhost:8002).
4. Generate Gemini API key and add it and DB connection details to `.env` file.
5. Seed the DB with some sample data. Make sure to only use "Good, Bad" as skill levels in DB table "employee_skills".
6. Execute `make shell` command to access the container shell.
7. Run `python app.py` and ask your question and Google Gemini will analyse the question and return results by using your Database data.