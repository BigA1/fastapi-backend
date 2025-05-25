# MyStoree Backend

The backend service for MyStoree, built with FastAPI, providing speech-to-text transcription, user authentication, and story management.

## Features

- 🎤 Speech-to-text transcription using OpenAI's Whisper API
- 🔒 JWT-based authentication
- 📝 Story CRUD operations
- 🗄️ Supabase database integration
- 🔄 Async request handling
- 📚 OpenAPI documentation

## Tech Stack

- FastAPI
- Supabase (PostgreSQL)
- SQLAlchemy
- OpenAI API (Whisper)
- Python-Jose (JWT)
- Passlib (Password Hashing)
- Python-multipart (File Uploads)
- Uvicorn (ASGI Server)

## Prerequisites

- Python 3.8+
- Supabase account and project
- OpenAI API key

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
OPENAI_API_KEY=your_openai_api_key
```

4. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
fastapi-backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API endpoints
│   │   └── endpoints/   # Route handlers
│   ├── core/            # Core functionality
│   ├── db/              # Database models and session
│   ├── schemas/         # Pydantic models
│   └── services/        # Business logic
├── tests/               # Test files
├── .env                 # Environment variables
├── .env.example         # Example environment variables
├── alembic.ini          # Alembic configuration
├── requirements.txt     # Project dependencies
└── main.py             # Application entry point
```

## API Endpoints

### Authentication
- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Login user
- `POST /api/auth/logout`: Logout user

### Stories
- `GET /api/stories`: Get all stories
- `POST /api/stories`: Create a new story
- `GET /api/stories/{id}`: Get a specific story
- `PUT /api/stories/{id}`: Update a story
- `DELETE /api/stories/{id}`: Delete a story

### Transcription
- `POST /api/transcribe`: Transcribe audio to text

## Database Migrations

To create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

To apply migrations:
```bash
alembic upgrade head
```

## Testing

Run tests with pytest:
```bash
pytest
```

## Environment Variables

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key
- `JWT_SECRET`: Secret key for JWT token generation
- `JWT_ALGORITHM`: Algorithm for JWT token generation (default: HS256)
- `OPENAI_API_KEY`: OpenAI API key for Whisper transcription

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS middleware enabled
- Environment variable protection
- Input validation with Pydantic

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details. 