web: cd web_service && gunicorn --bind 0.0.0.0:$PORT app:app
api: cd backend && python unified_server.py
backend: cd backend && python api_server.py
