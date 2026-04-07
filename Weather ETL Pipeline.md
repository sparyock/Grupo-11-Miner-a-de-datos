# Weather ETL Pipeline

Automated ETL pipeline that extracts weather data from Weatherstack API every 5 minutes, transforms it, and stores a historical dataset in JSON and CSV formats.

## Architecture
- Extract → Transform → Load (ETL)
- Cron scheduler runs every 5 minutes
- Logs stored in `logs/cron.log`
- Historical data in `data/`

## Technologies
- Python (requests, pandas, python-dotenv)
- Linux (WSL Ubuntu)
- Cron (automation)
- Git/GitHub

## Setup
1. Clone the repo
2. Create a virtual environment and activate it
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your API key and city

## Running
- Run manually: `python src/main.py`
- Run automatically via Cron (configured every 5 minutes)

## Output
- `weather.json` → historical JSON data
- `weather.csv` → converted CSV data
- `logs/cron.log` → execution logs
