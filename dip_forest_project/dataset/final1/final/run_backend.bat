@echo off
echo Starting StudySphere Backend with MySQL...

REM Set environment variables for MySQL
set DATABASE_URL=mysql+pymysql://root:Nalanda123@localhost:3307/studysphere_db
set JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
set SECRET_KEY=your-flask-secret-key-change-this-in-production
set GEMINI_API_KEY=your-gemini-api-key-here
set FLASK_ENV=development
set FLASK_DEBUG=True
set FLASK_APP=server.py

REM Install dependencies if needed
echo Installing dependencies...
pip install -r requirements.txt

REM Run the server
echo Starting server on http://localhost:5000
python server.py

pause 