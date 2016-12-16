# Sheldonisms Database

A scheduled job that keeps sheldonism's database updated

## To setup a database

Follow this link : http://blog.y3xz.com/blog/2012/08/16/flask-and-postgresql-on-heroku

### Environment Variables for heroku

DB_URL = token from heroku postgres database credentials <br>
SQLALCHEMY_TRACK_MODIFICATIONS = true <br>


Note: you have to run Python from heroku and initialize your database as follows
>>from app import db <br>
>>db.create_all()

*Sheldonisms* is participating in Kharagpur Winter of Code 2016. Join this [Facebook group](https://www.facebook.com/groups/1125067874207040/?fref=nf) to ask doubts and discuss. 
