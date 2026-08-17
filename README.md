# BMI Calculator with MongoDB Atlas

This project is now a single `Streamlit` app that connects directly to MongoDB Atlas.

## Setup

1. Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Add your MongoDB Atlas connection string to `.env`.

4. Start the app:

```powershell
streamlit run frontend/app.py
```

## MongoDB Atlas

Example connection string:

```text
mongodb+srv://your-user:your-password@your-cluster.mongodb.net/?retryWrites=true&w=majority&appName=bmi-calculator
```

If Atlas blocks the connection, make sure your current IP address or deployment platform is allowed in the Atlas network access list.
