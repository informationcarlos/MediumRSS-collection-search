import csv
import xmltodict
import json
import requests
import re
from datetime import date, datetime, timedelta, timezone
from dateutil import parser


today = str(date.today())

###calculate how far back i want to check in the feed (cron job runs weekly so 7 days)####
datelimit = datetime.now(timezone.utc) - timedelta(days=7)


###TJM RSS feed###
url = "https://medium.com/feed/@thejewishmuseum"

r = requests.get(url)

xml_feed = r.text


###use xmltodict to turn xml to json##
d = xmltodict.parse(xml_feed)
json_file = json.dumps(d, indent=4)

###turn json to dict###
rss_dict = json.loads(json_file)

###list i'll use to write to CSV###
big_list = []

###iterate through rss####
for post in rss_dict['rss']['channel']['item']:

	##use dateutil parser to transform UTC string into date object####
	post_date = post['atom:updated']
	post_date_object = parser.parse(post_date)

	###only look in posts ON/AFTER my datelimit####
	if post_date_object >= datelimit:
		
		post_url = post['guid']['#text']

		post_text = post['content:encoded']

		##use regex to find URLs of TJM online collection objects within posts##
		collection_link_search = re.findall('"(http://thejewishmuseum.org/collection/\d.*?)"', post_text)
		
		##use a set to get only unique URLs##
		unique_collection_link_search = set(collection_link_search)

		###skip if there aren't any collection URLs found in a post###
		if len(unique_collection_link_search) > 0:

			for link in unique_collection_link_search:
				
				###smaller list to add collection urls/medium post url/dates of posts###
				lil_list = []
				lil_list.append(link)
				lil_list.append(post_url)
				lil_list.append(post_date)

				###add smaller list to larger list for easy writing to CSV###
				big_list.append(lil_list)
		else:
			pass
	else:
		pass

###write to csv###
with open(str(today)+'_objects_with_Medium_links.csv', "w", encoding = 'utf-8') as newfile:
	writer = csv.writer(newfile)
	
	###write headers###
	writer.writerow(['Online Collection Link', 'Medium URL', 'Date of Medium Post'])
	
	for item in big_list:
		writer.writerow(item)







	







			


