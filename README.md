# AI Research Blog - Flask Application

A Flask-based web application that automatically generates blog posts from the latest AI research papers on arXiv using Groq AI. This project replicates the functionality of an n8n workflow in a standalone Flask application.

## Features

- 🤖 **Automated Blog Generation**: Fetches latest AI research papers from arXiv and generates comprehensive blog posts using Groq AI
- 📝 **Manual Blog Creation**: Create and publish custom blog posts with HTML formatting
- 📊 **Blog Management**: View, list, and delete blog posts with a modern web interface
- ⏰ **Scheduled Generation**: Automatic daily blog post generation at 9 AM
- 🎨 **Modern UI**: Beautiful, responsive design with Bootstrap 5
- 🔍 **Search & Filter**: Browse through paginated blog posts
- 📱 **Mobile Friendly**: Fully responsive design for all devices

## Technology Stack

- **Backend**: Flask, SQLAlchemy, APScheduler
- **Frontend**: Bootstrap 5, Font Awesome, JavaScript
- **AI Integration**: Groq API for content generation
- **Data Source**: arXiv API for research papers
- **Database**: PostgreSQL (production) / SQLite (development)

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (for production) or SQLite (for development)
- Groq API key

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd "c:\Users\Prasanna\OneDrive\Documents\blog post flask"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   copy .env.example .env
   ```
   
   Edit the `.env` file with your configuration:
   ```env
   # Database Configuration
   DATABASE_URL=sqlite:///blog.db  # For development
   # DATABASE_URL=postgresql://username:password@localhost:5432/blog_db  # For production

   # Groq AI Configuration
   GROQ_API_KEY=your_groq_api_key_here

   # Flask Configuration
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here

   # ArXiv API Configuration
   ARXIV_MAX_RESULTS=20
   ```

5. **Get a Groq API Key**
   - Visit [Groq Console](https://console.groq.com/)
   - Sign up for an account
   - Generate an API key
   - Add it to your `.env` file

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Usage

### Generating Blog Posts

1. **Automatic Generation**:
   - Click "Generate Blog" in the navigation
   - The system will fetch the latest AI research papers from arXiv
   - Groq AI will generate a comprehensive blog post
   - The post will be automatically saved and displayed

2. **Manual Creation**:
   - Click "Create Blog" in the navigation
   - Fill in the title, subtitle (optional), and content
   - Use HTML tags for formatting
   - Click "Publish Blog Post"

3. **Scheduled Generation**:
   - Blog posts are automatically generated daily at 9:00 AM
   - This can be configured in `scheduler.py`

### Managing Blog Posts

- **View Posts**: Click on any blog post from the home page
- **Delete Posts**: Use the delete button on individual posts
- **Browse Posts**: Use pagination to navigate through all posts

## API Endpoints

The application also provides REST API endpoints:

- `GET /api/blogs` - Get paginated list of blogs
- `GET /api/blog/<id>` - Get specific blog post
- `POST /api/generate` - Generate new blog post

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///blog.db` |
| `GROQ_API_KEY` | Groq AI API key | Required |
| `FLASK_ENV` | Flask environment | `development` |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `ARXIV_MAX_RESULTS` | Max papers to fetch from arXiv | `20` |

### Database Configuration

**Development (SQLite - Recommended)**:
```env
DATABASE_URL=sqlite:///blog.db
```

**Production (PostgreSQL - Optional)**:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/blog_db
```

Note: PostgreSQL requires additional setup and psycopg2 installation. For simplicity, this project uses SQLite by default.

## Project Structure

```
blog post flask/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── scheduler.py          # Background task scheduler
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── services/            # Business logic services
│   ├── __init__.py
│   ├── arxiv_service.py    # arXiv API integration
│   ├── groq_service.py     # Groq AI integration
│   └── blog_service.py     # Blog management service
└── templates/           # HTML templates
    ├── base.html           # Base template
    ├── index.html          # Home page
    ├── blog_detail.html    # Blog post view
    ├── generate.html       # Blog generation page
    ├── create.html         # Manual blog creation
    ├── 404.html           # 404 error page
    └── 500.html           # 500 error page
```

## How It Works

1. **Paper Fetching**: The `ArxivService` fetches the latest AI research papers from arXiv API using specific search queries (cs.AI, cs.LG, cs.CL)

2. **Content Processing**: Papers are filtered for relevance using AI-related keywords and formatted for blog generation

3. **AI Generation**: The `GroqService` uses the Groq API to generate comprehensive blog content from the research papers

4. **Content Formatting**: Generated content is cleaned, formatted with proper HTML, and saved to the database

5. **Web Interface**: Flask serves the content through a modern, responsive web interface

## Customization

### Modifying Search Criteria

Edit `services/arxiv_service.py` to change:
- Search categories
- Number of papers fetched
- Relevance keywords
- Paper filtering logic

### Changing AI Prompts

Edit `services/groq_service.py` to modify:
- Blog generation prompts
- Content structure
- Writing style
- Output format

### Scheduling

Edit `scheduler.py` to change:
- Generation frequency
- Scheduled time
- Add custom scheduled tasks

## Troubleshooting

### Common Issues

1. **Groq API Key Error**:
   - Ensure your API key is valid and added to `.env`
   - Check your Groq account limits

2. **Database Connection Error**:
   - Verify your database URL in `.env`
   - Ensure PostgreSQL is running (if using PostgreSQL)

3. **arXiv API Timeout**:
   - Check your internet connection
   - The arXiv API may be temporarily unavailable

4. **Blog Generation Fails**:
   - Check the application logs for specific errors
   - Verify all services are properly configured

### Logs

Check the console output for detailed error messages and debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the application logs
3. Ensure all dependencies are properly installed
4. Verify your environment configuration

---

**Note**: This application requires a valid Groq API key to function. The free tier should be sufficient for testing and light usage.
