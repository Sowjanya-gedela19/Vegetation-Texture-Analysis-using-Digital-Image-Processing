# StudySphere Backend Runner for Windows with MySQL
Write-Host "Starting StudySphere Backend with MySQL..." -ForegroundColor Green

# Set environment variables for MySQL
$env:DATABASE_URL = "mysql+pymysql://root:Nalanda123@localhost:3307/studysphere_db"
$env:JWT_SECRET_KEY = "your-super-secret-jwt-key-change-this-in-production"
$env:SECRET_KEY = "your-flask-secret-key-change-this-in-production"
$env:GEMINI_API_KEY = "your-gemini-api-key-here"
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "True"
$env:FLASK_APP = "server.py"

# Install dependencies if needed
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Run the server
Write-Host "Starting server on http://localhost:5000" -ForegroundColor Green
python server.py 