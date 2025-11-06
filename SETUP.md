# Setup Guide

## Prerequisites

- Docker
- Python 3.12+
- Node.js and npm

## Step-by-Step Setup

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <repo-url>
cd trafficlaw_chatbot

# Install Python dependencies
# Option A: Create and use a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Option B: Install system-wide (not recommended)
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (see `example.env` for reference):

```bash
# Database
DATABASE_URL="postgresql+asyncpg://root:rootpass@localhost:5432/trafficlawdb"
POSTGRES_USER=root
POSTGRES_PASSWORD=rootpass
POSTGRES_DB=trafficlawdb
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# External APIs
GROQ_API_KEY="your_groq_api_key_here"

# Data paths (adjust to your system)
DATA_RAW_PATH="/path/to/data/raw"
DATA_PROCESSED_PATH="/path/to/data/processed"
EVAL_TESTSET_PATH="/path/to/evaluation_testset.csv"
```

### 3. Start PostgreSQL with Docker

```bash
docker compose up -d
```

### 4. Set Up Database Extension

```bash
docker exec -it trafficlaw psql -U root -d trafficlawdb
```

Then in the psql prompt:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### 5. Configure Frontend Environment Variables

**For Next.js API Gateway** (`frontend/api/.env.local`):
```bash
PYTHON_API_URL="http://127.0.0.1:8000"
```

**For Next.js Frontend** (`frontend/web/.env.local`):
```bash
NEXT_PUBLIC_API_URL="http://localhost:3001"
```

### 6. Add PDF Files

Place your PDF files in the directory specified by `DATA_RAW_PATH` in your `.env` file.

### 7. Run the Application

**Important**: Make sure your Python virtual environment is activated before running!

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run all services together
npm run dev

# Or run services individually:
npm run dev:python  # Backend (requires activated venv)
npm run dev:api     # API Gateway
npm run dev:web     # Frontend
```

## Troubleshooting

### "python: command not found" or "python3: command not found"

**Solution**: 

1. **Check if Python is installed**:
   ```bash
   python3 --version  # On macOS/Linux
   python --version   # On Windows or if python3 alias exists
   ```

2. **If Python is not installed**, install it:
   - macOS: `brew install python3` or download from python.org
   - Linux: `sudo apt install python3` (Debian/Ubuntu) or `sudo yum install python3` (RHEL/CentOS)
   - Windows: Download from python.org

3. **Create and activate your virtual environment**:
   ```bash
   # Create venv if it doesn't exist
   python3 -m venv venv  # On macOS/Linux
   # OR
   python -m venv venv   # On Windows

   # Activate it
   source venv/bin/activate  # On macOS/Linux
   # OR
   venv\Scripts\activate    # On Windows PowerShell
   # OR
   venv\Scripts\activate.bat  # On Windows CMD
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Make sure venv is activated before running npm**:
   ```bash
   source venv/bin/activate  # Keep this terminal active
   npm run dev
   ```

### "uvicorn: command not found"

**Solution**: This usually means:
- Virtual environment is not activated
- Dependencies are not installed

Follow steps 3-4 above to activate venv and install dependencies.

### PYTHONPATH Issues

The `dev:python` script uses `PYTHONPATH=.` to ensure Python can find the backend modules. If you still encounter import errors:

1. Make sure you're running from the project root directory
2. Ensure your virtual environment is activated
3. Verify that all dependencies are installed: `pip install -r requirements.txt`

### Database Connection Issues

- Ensure Docker is running: `docker ps`
- Check container is healthy: `docker compose ps`
- Verify `DATABASE_URL` in `.env` matches `docker-compose.yml` settings

### Module Import Errors

If you see errors like "No module named 'backend.main'", make sure:
- You're in the project root directory when running `npm run dev`
- Your virtual environment is activated
- All dependencies are installed: `pip install -r requirements.txt`

