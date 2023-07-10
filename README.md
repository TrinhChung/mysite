Django Trainee

################################
Running database migrations

- python3 manage.py makemigrations
- python3 manage.py migrate

#################################
Seed data by command

- python3 manage.py loaddata seeder.json

################################
Running the website

- python3 manage.py runserver
  root: 127.0.0.1:8000

###############################
django with mysql

- install mysqlclient==2.03
- create database {name} in settings
- config file my.cnf according to file example.my.cnf

############################
tao i18n

- install gettext
- wrap text
- django-admin makemessages -l {short name language}
- django-admin compilemessages
