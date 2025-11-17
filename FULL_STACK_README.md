# 🚀 MedSummarize - Full-Stack AI Medical Report System

A complete full-stack application for AI-powered medical report summarization using OCR, NLP, and Large Language Models.

## 📋 Project Overview

MedSummarize is a comprehensive system that transforms complex medical reports into clear, actionable insights using advanced AI technologies. The system includes both a professional marketing website and a fully functional backend API for processing medical documents.

## 🏗️ Architecture

### Frontend (React + Vite)
- **Framework**: React 18+ with hooks
- **Build Tool**: Vite for fast development
- **Styling**: Tailwind CSS with medical theme
- **Animations**: Framer Motion
- **State Management**: React hooks and context
- **API Client**: Axios with custom hooks
- **Components**: Professional medical UI

### Backend (FastAPI + Python)
- **Framework**: FastAPI for high-performance APIs
- **Database**: SQLAlchemy with SQLite (production-ready for PostgreSQL/MongoDB)
- **OCR**: Tesseract and Google Vision integration
- **NLP**: spaCy with medical entity recognition
- **PHI Redaction**: Presidio for HIPAA compliance
- **LLM Integration**: OpenAI GPT-4 and Google Gemini
- **File Storage**: Local storage with S3 support
- **Security**: JWT authentication and encryption

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Tesseract OCR (for medical document processing)
- AI API keys (OpenAI and/or Google Gemini)

### Installation

1. **Clone and setup the project**:
```bash
git clone <repository-url>
cd MedSafe
```

2. **Setup Backend**:
```bash
cd backend
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys and settings

# Initialize database
npm run db-init

# Start backend server
npm run dev
```

3. **Setup Frontend**:
```bash
cd frontend
npm install

# Setup environment variables
cp .env.example .env

# Start frontend development server
npm run dev
```

4. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## 📱 Features

### Website Features
- **Hero Section**: Compelling landing with call-to-action
- **About**: Technology explanation and dual summary types
- **Features**: Complete feature showcase with animations
- **How It Works**: Interactive 6-step process visualization
- **Tech Stack**: Technology demonstration
- **Why Choose**: Benefits and ROI calculator
- **Demo**: Interactive demonstration
- **Contact**: Professional contact form

### Backend API Features
- **File Upload**: Secure medical report upload
- **OCR Processing**: Text extraction from PDFs and images
- **PHI Redaction**: HIPAA-compliant privacy protection
- **NLP Processing**: Medical entity extraction and analysis
- **AI Summarization**: Clinician and patient-friendly summaries
- **Q&A System**: Interactive question answering
- **Processing Pipeline**: Real-time status tracking
- **Database**: Complete audit trail and metadata

### Integration Features
- **Real-time Processing**: Live progress tracking
- **Error Handling**: Comprehensive error management
- **Security**: End-to-end encryption and PHI protection
- **Scalability**: Async processing and caching
- **Monitoring**: Health checks and logging

## 🛠️ Technical Stack

### Frontend Technologies
- **React 18+**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **Lucide React**: Professional icons
- **Axios**: HTTP client with interceptors

### Backend Technologies
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **OCR**: Tesseract, Google Vision, PyMuPDF
- **NLP**: spaCy with medical models
- **LLM**: OpenAI GPT-4, Google Gemini
- **Presidio**: PHI detection and redaction

### AI/ML Stack
- **Text Extraction**: OCR with preprocessing
- **Entity Recognition**: Medical terminology extraction
- **Privacy Protection**: HIPAA/GDPR compliant PHI redaction
- **Summarization**: Dual clinician/patient summaries
- **Question Answering**: Context-aware Q&A
- **Confidence Scoring**: Quality metrics

## 🔒 Security & Compliance

### HIPAA Compliance
- **End-to-end encryption**: All data encrypted in transit
- **PHI Redaction**: Automatic sensitive data removal
- **Audit Logging**: Complete processing audit trail
- **Access Controls**: User authentication and authorization
- **Data Retention**: Configurable data retention policies

### GDPR Compliance
- **Data Minimization**: Only collect necessary data
- **Consent Management**: User consent tracking
- **Right to Deletion**: Data removal on request
- **Portability**: Data export capabilities

## 📊 Processing Pipeline

The complete processing pipeline includes:

1. **File Upload**: Secure file handling with validation
2. **OCR Processing**: Text extraction with 99%+ accuracy
3. **PHI Redaction**: HIPAA-compliant privacy protection
4. **NLP Analysis**: Medical entity extraction
5. **AI Summarization**: Dual summary generation
6. **Quality Assurance**: Confidence scoring and validation

## 🚀 Deployment

### Development
```bash
# Backend
cd backend
npm run dev

# Frontend
cd frontend
npm run dev
```

### Production
```bash
# Backend (Docker)
docker build -t medsummarize-backend .
docker run -p 8000:8000 medsummarize-backend

# Frontend (Static hosting)
cd frontend
npm run build
# Deploy dist/ folder to any static hosting service
```

### Environment Variables
- **Frontend**: `VITE_API_BASE_URL`, `VITE_ENABLE_ANALYTICS`
- **Backend**: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `DATABASE_URL`

## 📚 API Documentation

The FastAPI backend provides automatic API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI**: http://localhost:8000/api/openapi.json

### Key Endpoints

#### File Management
- `POST /api/upload/report` - Upload medical report
- `GET /api/upload/status/{report_id}` - Get upload status
- `GET /api/upload/list` - List user reports
- `DELETE /api/upload/{report_id}` - Delete report

#### Processing
- `POST /api/process/report/{report_id}` - Start processing
- `GET /api/process/status/{report_id}` - Get processing status
- `POST /api/process/report/{report_id}/qa` - Ask question

#### Summaries
- `GET /api/summarize/report/{report_id}` - Get report summaries
- `GET /api/summarize/{summary_id}` - Get specific summary
- `POST /api/summarize/{summary_id}/feedback` - Submit feedback

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test
```

### Backend Tests
```bash
cd backend
pytest
```

### Integration Tests
```bash
# Test complete pipeline
python -m pytest tests/integration/
```

## 📈 Performance

### Metrics
- **Frontend Load Time**: <3 seconds on 3G
- **Backend Response**: <500ms for non-processing endpoints
- **File Processing**: <2 minutes for average report
- **OCR Accuracy**: 99%+ for printed text
- **Uptime**: 99.9% availability target

### Optimizations
- **Frontend**: Code splitting, lazy loading, service workers
- **Backend**: Async processing, caching, connection pooling
- **Database**: Optimized queries, indexing
- **File Storage**: CDN integration, compression

## 🔧 Configuration

### Database Configuration
```python
# SQLite (development)
DATABASE_URL=sqlite:///./medsummarize.db

# PostgreSQL (production)
DATABASE_URL=postgresql://user:pass@localhost/medsummarize
```

### AI Model Configuration
```python
# spaCy model
SPACY_MODEL=en_core_web_sm

# OCR settings
TESSERACT_CMD=/usr/bin/tesseract
MAX_FILE_SIZE=10485760  # 10MB
```

## 🌐 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Documentation**: See docs/ directory
- **Issues**: Create GitHub issue
- **Email**: support@medsummarize.com

## 🌟 Acknowledgments

- Medical professionals for clinical guidance
- Open source community for tools and frameworks
- AI researchers for model development
- Healthcare compliance experts for HIPAA guidance

---

**MedSummarize** - Transforming medical documentation with the power of AI. Built with ❤️ for healthcare professionals and patients.