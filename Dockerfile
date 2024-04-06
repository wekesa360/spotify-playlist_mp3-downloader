FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

# Serve static files using Nginx
RUN apt-get update && apt-get install -y nginx
COPY nginx.conf /etc/nginx/nginx.conf

CMD ["sh", "-c", "nginx && flask run"]