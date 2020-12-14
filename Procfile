web: gunicorn -k eventlet -w 1 run:app
worker: celery worker -A modules.matchmaking.utils.async_task --loglevel=info
