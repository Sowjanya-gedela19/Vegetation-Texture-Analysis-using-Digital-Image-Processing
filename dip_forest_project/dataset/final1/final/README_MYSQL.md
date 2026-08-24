# StudySphere MySQL Setup Guide

## Prerequisites

1. **MySQL Server** - Make sure MySQL is installed and running
2. **MySQL Workbench** - For database management
3. **Python** - With virtual environment

## Step 1: MySQL Database Setup

### Option A: Using MySQL Workbench
1. Open MySQL Workbench
2. Connect to your MySQL server
3. Open the `setup_mysql.sql` file
4. Execute the script to create the database

### Option B: Using MySQL Command Line
```bash
mysql -u root -p
```
Then run:
```sql
CREATE DATABASE IF NOT EXISTS studysphere_db;
```

## Step 2: Update Database Configuration

### Edit the run script with your MySQL credentials:

**For PowerShell (`run_backend.ps1`):**
```powershell
$env:DATABASE_URL = "mysql+pymysql://YOUR_USERNAME:YOUR_PASSWORD@localhost:3306/studysphere_db"
```

**For Batch (`run_backend.bat`):**
```cmd
set DATABASE_URL=mysql+pymysql://YOUR_USERNAME:YOUR_PASSWORD@localhost:3306/studysphere_db
```

### Common MySQL configurations:

**Default MySQL installation:**
```
mysql+pymysql://root:password@localhost:3306/studysphere_db
```

**If you have a different password:**
```
mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/studysphere_db
```

**If you created a specific user:**
```
mysql+pymysql://studysphere_user:YOUR_PASSWORD@localhost:3306/studysphere_db
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Run the Backend

### Using PowerShell:
```powershell
.\run_backend.ps1
```

### Using Batch:
```cmd
run_backend.bat
```

### Manual run:
```bash
python server.py
```

## Troubleshooting

### Connection Issues:
1. **Check MySQL is running:**
   ```bash
   # Windows
   net start mysql
   
   # Or check services
   services.msc
   ```

2. **Test MySQL connection:**
   ```bash
   mysql -u root -p
   ```

3. **Verify database exists:**
   ```sql
   SHOW DATABASES;
   USE studysphere_db;
   ```

### Common Error Solutions:

**Error: "Access denied for user"**
- Check username/password in DATABASE_URL
- Verify user has access to studysphere_db

**Error: "Can't connect to MySQL server"**
- Ensure MySQL service is running
- Check if MySQL is on port 3306

**Error: "Unknown database"**
- Run the setup_mysql.sql script
- Or manually create: `CREATE DATABASE studysphere_db;`

## Database Tables

The following tables will be created automatically:
- `user` - User accounts and profiles
- `subject` - Study subjects
- `study_session` - Study sessions
- `audio_note` - Audio notes and transcripts

## Environment Variables

Make sure these are set in your run script:
- `DATABASE_URL` - MySQL connection string
- `JWT_SECRET_KEY` - For authentication
- `SECRET_KEY` - Flask secret key
- `GEMINI_API_KEY` - For AI features (optional) 