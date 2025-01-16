FROM python:3.9-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
EXPOSE 5000
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]