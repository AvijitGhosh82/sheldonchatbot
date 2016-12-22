import os
import sys
import json
from bs4 import BeautifulSoup
import requests
import types
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import random
from random import randint
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

#class to define Meme object to be inserted into database

class db_Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(300),unique=True)

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return self.url

#class to define Quote object to be inserted into database

class db_Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote = db.Column(db.String(5000),unique=True)

    def __init__(self, quote):
        self.quote = quote

    def __repr__(self):
        return self.quote

db.create_all() #create all the tables

#function to update database - called by scheduler

def update_db():
	
	log('Database Update Started - '+datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
	
	#fetch all Meme records from database - convert raw data into strings

	db_records_tem=db_Meme.query.all()
	db_records=[]
	for record in db_records_tem:
		db_records.append(str(record))

	url = "http://www.memecenter.com/search/big%20bang%20theory"
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	for line in soup.find_all('img', class_ = "rrcont"):
		meme_object = str(db_Meme(line.get('src')))
		if not meme_object in db_records:		# Insert only New Memes that are not found in database
			db.session.add(meme_object)
			db.session.commit()
	
	url = "http://www.wapppictures.com/30-hilarious-memes-big-bang-theory/"
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	for line in soup.find_all('img', class_ = re.compile("aligncenter+")):
		meme_object = str(db_Meme(line.get('src')))
		if not meme_object in db_records:		# Insert only New Memes that are not found in database
			db.session.add(meme_object)
			db.session.commit()

	log('All Memes Up to date')

	url = "http://www.imdb.com/character/ch0064640/quotes"
	r  = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data,"html.parser")
	quoteblock = soup.find("div", {"id": "tn15content"})
	quoteblock.find('div').decompose()
	quoteblock.find('h5').decompose()
	quoteblock = replace_with_newlines(quoteblock)
	quotes = quoteblock.split("\n\n")
	
	no_of_quotes = len(quotes)
	no_of_records = db.session.query(db_Quote).count()

	if no_of_quotes != no_of_records:
		
		db_records_tem=db_Quote.query.all()
		db_records=[]
		for record in db_records_tem:
			db_records.append(record.quote)

		for quote in quotes:
			quote_object = db_Quote(quote)
			if not quote_object.quote in db_records:		# Insert only New quotes that are not found in database
				db.session.add(quote_object)
				db.session.commit()
				no_of_quotes=no_of_quotes-1
			if no_of_quotes == no_of_records:				# Insert only until last update
				break
	
	log('All Quotes Up to date')
	log('Database Update Finished')


def replace_with_newlines(element):
    text = ''
    for elem in element.recursiveChildGenerator():
        if isinstance(elem, types.StringTypes):
            text += elem.strip()
        elif elem.name == 'br':
            text += '\n'
    return text


def log(message):  # simple wrapper for logging to stdout on heroku
	print str(message)
	sys.stdout.flush()


@app.route('/', methods=['GET'])
def verify():
	# when the endpoint is registered as a webhook, it must echo back
	# the 'hub.challenge' value it receives in the query arguments
	return "Welcome to Sheldon Database - This is intended for developers", 200

update_db()
print('Initialized Database')

sched = BlockingScheduler()

#Update_db is scheduled to execute every day at 00:00 AM

@sched.scheduled_job('cron', day_of_week='0-6', hour=0)
def scheduled_job():
    update_db()
    log('Database was successfully Updated - '+datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

log('App has been scheduled to Update Database every Day at 00:00 AM')
sched.start()

if __name__ == '__main__':
	app.run(debug=True)
	log('App has been scheduled to Update Database every Day at 00:00 AM')
	sched.start())
