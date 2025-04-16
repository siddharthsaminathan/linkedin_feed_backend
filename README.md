# JobTech API Client

A Python client and FastAPI wrapper for the JobTech API (Arbetsförmedlingen's job search API).

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jobtech-api-client.git
cd jobtech-api-client
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

Start the FastAPI server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Search Jobs
- `GET /search?query=software&limit=10&offset=0`
  - Search for jobs using free text and filters
  - Parameters:
    - `query`: Search query (optional)
    - `limit`: Number of results per page (default: 10)
    - `offset`: Pagination offset (default: 0)

### Get Job Details
- `GET /job/{job_id}`
  - Get details for a specific job ad

### Get Job Logo
- `GET /job/{job_id}/logo`
  - Get the logo for a specific job ad

### Get Search Suggestions
- `GET /suggestions?query=sof&limit=10&contextual=true`
  - Get typeahead suggestions for search terms
  - Parameters:
    - `query`: Search query
    - `limit`: Maximum number of suggestions (default: 10)
    - `contextual`: Whether to use contextual suggestions (default: true)

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The API includes basic error handling for:
- Invalid requests
- Server errors

## License

MIT License 