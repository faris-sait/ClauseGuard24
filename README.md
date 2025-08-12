# ClauseGuard 🛡️

**Protect yourself from hidden risks in legal agreements**

ClauseGuard is a powerful web application that analyzes Terms & Conditions, Privacy Policies, and EULAs to identify potential risks and provide clear summaries in plain language.

## 🌟 Features

- **🔍 Smart Document Analysis** - Paste any T&C/Privacy Policy URL for instant analysis
- **📊 Risk Scoring System** - 0-100 risk score with visual indicators
- **🎯 Risk Detection Engine** - Identifies 7 critical risk categories:
  - Data sharing with third parties
  - Mandatory arbitration clauses
  - Automatic subscription renewals
  - Limited company liability
  - Extensive tracking & advertising
  - Content rights issues
  - Account termination risks
- **📝 Plain Language Summaries** - Complex legal text converted to bullet points
- **📥 Export Reports** - Download analysis results
- **🌙 Dark/Light Mode** - Beautiful interface with theme toggle
- **📱 Responsive Design** - Works perfectly on all devices

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Python 3.11+
- MongoDB
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd clauseguard
   ```

2. **Set up environment variables**
   ```bash
   # Copy example environment file
   cp backend/.env.example backend/.env
   
   # Add your OpenAI API key to backend/.env
   OPENAI_API_KEY="your-openai-api-key-here"
   ```

3. **Install dependencies**
   ```bash
   # Backend dependencies
   cd backend
   pip install -r requirements.txt
   
   # Frontend dependencies
   cd ../frontend
   yarn install
   ```

4. **Start the services**
   ```bash
   # Start backend (from backend directory)
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   
   # Start frontend (from frontend directory)
   yarn start
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="clauseguard"
CORS_ORIGINS="*"
OPENAI_API_KEY="your-openai-api-key-here"
```

**Frontend (.env):**
```env
REACT_APP_BACKEND_URL="http://localhost:8001"
```

### OpenAI API Key Setup

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy the key and add it to your environment variables

## 🚀 Deployment

### Using Environment Variables (Recommended for Production)

Instead of using .env files, set environment variables directly:

```bash
export OPENAI_API_KEY="your-key-here"
export MONGO_URL="your-mongodb-connection-string"
export REACT_APP_BACKEND_URL="https://your-backend-domain.com"
```

### Platform-Specific Deployment

#### Vercel (Frontend)
```bash
vercel --prod
```

Set environment variables in Vercel dashboard:
- `REACT_APP_BACKEND_URL`

#### Railway/Render (Backend)
```bash
# Deploy backend to Railway/Render
```

Set environment variables in platform dashboard:
- `OPENAI_API_KEY`
- `MONGO_URL`
- `CORS_ORIGINS`

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd backend
python backend_test.py
```

## 🏗️ Tech Stack

- **Frontend**: React 18, Tailwind CSS, shadcn/ui components
- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB
- **AI**: OpenAI GPT-4o
- **Web Scraping**: BeautifulSoup4, Requests
- **Styling**: Tailwind CSS with dark mode support

## 📁 Project Structure

```
clauseguard/
├── frontend/          # React application
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── App.js        # Main application
│   │   └── App.css       # Styles
│   ├── package.json
│   └── tailwind.config.js
├── backend/           # FastAPI application
│   ├── server.py         # Main server
│   ├── requirements.txt  # Python dependencies
│   ├── .env.example     # Environment template
│   └── .env            # Environment variables
├── .gitignore
└── README.md
```

## 🔒 Security

- ✅ API keys stored as environment variables (not in code)
- ✅ CORS properly configured
- ✅ Input validation and sanitization
- ✅ Rate limiting on API endpoints
- ✅ Secure headers and HTTPS ready

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o API
- shadcn/ui for beautiful components
- Tailwind CSS for styling system
- FastAPI for the excellent backend framework

## 💡 Usage Examples

### Analyze GitHub Terms
```
URL: https://github.com/site/terms
Risk Score: 21/100 (Low Risk)
Risks Found: Data Sharing, Limited Liability
```

### Analyze Social Media Privacy Policy
```
URL: https://example-social.com/privacy
Risk Score: 67/100 (High Risk)
Risks Found: Data Sharing, Tracking, Content Rights, Arbitration
```

---

**⚠️ Disclaimer**: ClauseGuard is designed to help identify potential risks in legal documents. Always consult with a qualified legal professional for important decisions involving legal agreements.

**Made with ❤️ for protecting users from hidden legal risks**
