FROM python:3.6

RUN mkdir -p /usr/app/
WORKDIR /usr/app
COPY . .
RUN pip install -r requirements.txt

CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:80
