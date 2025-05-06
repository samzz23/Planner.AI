# Planner.AI

A media automation platform built with FastAPI and SQLAlchemy.

## Features

- Media planning and campaign management
- Campaign pacing optimization
- Metrics export and reporting
- Real-time tracking

## Prerequisites

- Python 3.9+
- PostgreSQL 14+
- Node.js 16+ (for frontend)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Planner.AI.git
cd Planner.AI
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

3. Create a `.env` file in the `backend` directory with the following variables:
```
DATABASE_URL=postgresql://postgres:postgres@localhost/planner_ai
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

4. Initialize the database:
```bash
createdb planner_ai
alembic upgrade head
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload
```

## Deployment

The application can be deployed on Railway. Follow these steps:

1. Push your code to GitHub
2. Create a new project on Railway
3. Connect your GitHub repository
4. Add the following environment variables in Railway:
   - `DATABASE_URL` (Railway will provide this automatically)
   - `SECRET_KEY` (generate a secure random string)
   - `ENVIRONMENT=production`
5. Deploy the application

The application will be accessible at `https://<your-app-name>.up.railway.app`

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Endpoints

- `POST /api/plans/` - Create a new media plan
- `GET /api/plans/{plan_id}` - Get media plan details
- `POST /api/plans/{plan_id}/channels/` - Add channel allocation
- `GET /api/analysis/historical/` - Analyze historical data
- `GET /api/analysis/forecast/` - Generate forecasts
- `POST /api/plans/{plan_id}/scenarios/` - Create scenario analysis

## Development

### Running Tests
```bash
pytest
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 