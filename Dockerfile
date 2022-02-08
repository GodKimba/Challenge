FROM python:alpine
COPY . /app
RUN pip install flask flask_sqlalchemy flask_marshmallow
CMD python /app/main.py 