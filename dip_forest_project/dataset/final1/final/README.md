# StudySphere - AI-Powered Learning Progress Tracker

StudySphere is a comprehensive learning progress tracker that helps students manage subjects, log study sessions, set academic goals, and receive AI-generated suggestions for improving performance. The app includes a dashboard to visualize study hours, session consistency, and allows users to record voice reflections on study habits or challenges.

## 🚀 Features

### Core Features
- **User Authentication**: JWT-secured login/signup with role-based access
- **Subject Management**: Create, edit, and delete subjects with color coding
- **Study Session Logging**: Track study time, topics, focus levels, and notes
- **AI-Powered Suggestions**: Get personalized study recommendations using Azure OpenAI
- **Voice Reflections**: Record and manage audio notes for self-reflection
- **Progress Analytics**: Visualize study patterns, streaks, and performance metrics
- **Real-Time Updates**: Live dashboard updates using WebSocket connections
- **Admin Panel**: Comprehensive admin dashboard for system management

### Technical Features
- **Frontend**: React with TypeScript, Tailwind CSS, Chart.js
- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with SQLite fallback for development
- **Authentication**: JWT tokens with secure password hashing
- **AI Integration**: Azure OpenAI for intelligent study suggestions
- **Real-Time**: Flask-SocketIO for live updates
- **Responsive Design**: Mobile-first approach with modern UI/UX

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**
- **Flask 2.3.3** - Web framework
- **Flask-SQLAlchemy 3.0.5** - Database ORM
- **Flask-JWT-Extended 4.5.3** - JWT authentication
- **Flask-SocketIO 5.3.6** - Real-time communication
- **Flask-CORS 4.0.0** - Cross-origin resource sharing
- **psycopg2-binary 2.9.7** - PostgreSQL adapter
- **openai 1.3.0** - Azure OpenAI integration
- **python-dotenv 1.0.0** - Environment variable management

### Frontend
- **React 18.2.0** - UI library
- **TypeScript 4.9.0** - Type safety
- **Tailwind CSS 3.2.0** - Utility-first CSS framework
- **Chart.js 4.2.0** - Data visualization
- **React Router DOM 6.8.0** - Client-side routing
- **Axios 1.3.0** - HTTP client
- **Socket.IO Client 4.6.0** - Real-time communication
- **Lucide React 0.263.0** - Icon library
- **React Hook Form 7.43.0** - Form management
- **React Hot Toast 2.4.0** - Notifications

## 📋 Prerequisites

Before running StudySphere, ensure you have:

- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- **PostgreSQL** database (optional, SQLite used for development)
- **Azure OpenAI** account and API credentials

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd studysphere
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Database Setup

The application will automatically create SQLite database tables on first run. For PostgreSQL:

```bash
# Create database
createdb studysphere_db

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@localhost/studysphere_db
```

### 5. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/studysphere_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Flask Configuration
SECRET_KEY=your-flask-secret-key-change-this-in-production

# Azure OpenAI Configuration
AZURE_OPENAI_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 6. Run the Application

```bash
# Start backend server (from root directory)
python server.py

# Start frontend (from frontend directory)
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 📁 Project Structure

```
studysphere/
├── backend/
│   ├── server.py              # Main Flask application
│   ├── models.py              # Database models
│   ├── auth.py                # Authentication blueprint
│   ├── subjects.py            # Subjects management
│   ├── sessions.py            # Study sessions
│   ├── audio.py               # Audio notes
│   ├── ai.py                  # AI suggestions
│   ├── admin.py               # Admin panel
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── App.tsx           # Main app component
│   │   └── index.tsx         # Entry point
│   ├── package.json          # Node.js dependencies
│   └── tailwind.config.js    # Tailwind configuration
├── audio_uploads/            # Audio file storage
├── env.example              # Environment variables template
└── README.md               # This file
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/change-password` - Change password

### Subjects
- `GET /api/subjects/` - Get user subjects
- `POST /api/subjects/` - Create new subject
- `GET /api/subjects/<id>` - Get specific subject
- `PUT /api/subjects/<id>` - Update subject
- `DELETE /api/subjects/<id>` - Delete subject
- `GET /api/subjects/stats` - Get subject statistics

### Study Sessions
- `GET /api/sessions/` - Get study sessions
- `POST /api/sessions/` - Create new session
- `GET /api/sessions/<id>` - Get specific session
- `PUT /api/sessions/<id>` - Update session
- `DELETE /api/sessions/<id>` - Delete session
- `GET /api/sessions/analytics` - Get session analytics
- `GET /api/sessions/streak` - Get study streak data

### Audio Notes
- `GET /api/audio/` - Get audio notes
- `POST /api/audio/` - Upload audio note
- `GET /api/audio/<id>` - Get specific audio note
- `PUT /api/audio/<id>` - Update audio note
- `DELETE /api/audio/<id>` - Delete audio note
- `GET /api/audio/recent` - Get recent audio notes
- `GET /api/audio/stats` - Get audio statistics

### AI Suggestions
- `GET /api/ai/suggestions` - Get AI study suggestions
- `GET /api/ai/weekly-insights` - Get weekly insights
- `GET /api/ai/subject-feedback/<id>` - Get subject-specific feedback

### Admin (Admin only)
- `GET /api/admin/dashboard` - Admin dashboard data
- `GET /api/admin/users` - Get all users
- `GET /api/admin/users/<id>` - Get user details
- `PUT /api/admin/users/<id>/role` - Update user role
- `GET /api/admin/subjects/categories` - Get subject categories
- `POST /api/admin/subjects/categories` - Create category
- `DELETE /api/admin/subjects/categories/<name>` - Delete category
- `GET /api/admin/audio/monitor` - Monitor audio notes
- `POST /api/admin/audio/<id>/flag` - Flag audio note
- `GET /api/admin/analytics/usage` - Get usage analytics

## 🎯 Key Features Explained

### AI-Powered Study Suggestions
The application uses Azure OpenAI to analyze study patterns and provide personalized recommendations:
- Analyzes study time distribution across subjects
- Identifies focus level trends
- Considers user goals and focus areas
- Provides actionable improvement suggestions
- Offers motivational messages

### Voice Reflections
Students can record audio notes to reflect on their study sessions:
- Record voice memos about study challenges
- Transcribe audio for text search
- Track emotional and self-awareness patterns
- Review weekly reflection logs

### Real-Time Dashboard
Live updates provide immediate feedback:
- Real-time session logging
- Live chart updates
- Instant AI suggestion refresh
- WebSocket-based notifications

### Study Analytics
Comprehensive analytics help track progress:
- Daily/weekly study time breakdown
- Subject-wise performance metrics
- Focus level trends
- Study streak tracking
- Consistency analysis

## 🚀 Deployment

### Backend Deployment (Render)

1. **Create Render Account**: Sign up at [render.com](https://render.com)

2. **Create Web Service**:
   - Connect your GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn server:app`

3. **Environment Variables**:
   - Add all variables from `.env` file
   - Set `FLASK_ENV=production`
   - Set `FLASK_DEBUG=False`

4. **Database**: Use Render's PostgreSQL service

### Frontend Deployment (Vercel)

1. **Create Vercel Account**: Sign up at [vercel.com](https://vercel.com)

2. **Import Project**:
   - Connect your GitHub repository
   - Set root directory to `frontend`
   - Set build command: `npm run build`
   - Set output directory: `build`

3. **Environment Variables**:
   - Add `REACT_APP_API_URL` pointing to your backend

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password encryption
- **CORS Protection**: Cross-origin request security
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: SQLAlchemy ORM protection
- **File Upload Security**: Audio file type validation

## 🧪 Testing

### Backend Testing
```bash
# Run tests (when implemented)
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the API documentation

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Basic authentication and user management
- ✅ Subject and session tracking
- ✅ AI suggestions integration
- ✅ Audio notes functionality
- ✅ Admin dashboard

### Phase 2 (Planned)
- 🔄 Advanced analytics and reporting
- 🔄 Mobile app development
- 🔄 Social features and study groups
- 🔄 Integration with learning management systems
- 🔄 Advanced AI features

### Phase 3 (Future)
- 📋 Gamification elements
- 📋 Peer tutoring features
- 📋 Advanced machine learning models
- 📋 Multi-language support
- 📋 Offline functionality

---

**StudySphere** - Empowering students to track, analyze, and improve their learning journey with AI-powered insights. 