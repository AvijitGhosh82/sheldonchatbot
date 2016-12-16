import os
import sys
import json
from bs4 import BeautifulSoup
import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import random
from apscheduler.schedulers.blocking import BlockingScheduler
import re
from datetime import datetime
import logging
logging.basicConfig()


app = Flask(__name__)

#DB_URL is configured in Heroku Tokens

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL")
db = SQLAlchemy(app)

#class to define object to inserted into database

class db_Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(300),unique=True)

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return self.url

#function to update database - called by scheduler

def update_db():
	
	#fetch all records from database - convert raw data into strings

	db_records_tem=db_Meme.query.all()
	db_records=[]
	for record in db_records_tem:
		db_records.append(str(record))

	url = "http://www.memecenter.com/search/big%20bang%20theory"
	links = []
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	for line in soup.find_all('img', class_ = "rrcont"):
		links.append(line.get('src'))
		meme_object = str(db_Meme(line.get('src')))
		if not meme_object in db_records:		# Insert only New Memes that are not found in database
			db.session.add(meme_object)
			db.session.commit()
	
	url = "http://www.wapppictures.com/30-hilarious-memes-big-bang-theory/"
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	for line in soup.find_all('img', class_ = re.compile("aligncenter+")):
		links.append(line.get('src'))
		meme_object = str(db_Meme(line.get('src')))
		if not meme_object in db_records:		# Insert only New Memes that are not found in database
			db.session.add(meme_object)
			db.session.commit()


def log(message):  # simple wrapper for logging to stdout on heroku
	print str(message)
	sys.stdout.flush()


@app.route('/', methods=['GET'])
def verify():
	# when the endpoint is registered as a webhook, it must echo back
	# the 'hub.challenge' value it receives in the query arguments
	return "Welcome to Sheldon Database - This is intended for developers", 200

sched = BlockingScheduler()

#Update_db is scheduled to execute every day at 00:00 AM

@sched.scheduled_job('cron', day_of_week='0-6', hour=0)
def scheduled_job():
    update_db()
    log('Database was Updated - '+datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

sched.start()

if __name__ == '__main__':
	app.run(debug=True)
	log('App has been scheduled to Update Database every Day at 00:00 AM')
	sched.start()