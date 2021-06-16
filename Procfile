# web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
#web: gunicorn main:app -w 4 -b 0.0.0.0:5000 -k uvicorn.workers.UvicornWorker
web: uvicorn main:app --host=0.0.0.0 --port=${PORT:-5000}