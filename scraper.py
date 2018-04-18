from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import time
import results
import sys
import os
import re

class NCAA():
	url_base = "http://www.sports-reference.com"

	def __init__(self,year):
		self.year = str(year)
	
	def get_data(self):
		for team in results.results[self.year][0]:
			self.__get_team_data(team[0])
			time.sleep(10)
			self.__get_team_game_log_data(team[0])
			time.sleep(10)

	def __get_soup_for(self, url):
		r = requests.get(url)
		return BeautifulSoup(r.text, 'html.parser')

	def __get_team_data(self, team_name):
		url = NCAA.url_base + "/cbb/schools/" + team_name + "/" + self.year + ".html"
		soup = self.__get_soup_for(url)
		if not os.path.exists('y'+self.year+'/'+team_name):
			os.makedirs('y'+self.year+'/'+team_name)
		team_p = soup.find(id="meta").find_all("p")
		conf_url = NCAA.url_base + team_p[3].a['href']
		conf_soup = self.__get_soup_for(conf_url)
		conf_p = conf_soup.find(id="meta").find_all("p")
		with open('data/y'+self.year+"/"+team_name+"/conference.csv",mode="w") as fp:
			#SRS
			print(float(re.search(' .*? ', team_p[7].text).group(0)),file=fp)
			#SOS
			print(float(re.search(' .*? ', team_p[8].text).group(0)),file=fp)
			#Ortg
			print(float(re.search(' .*? ', team_p[9].text).group(0)),file=fp)
			#Drtg
			print(float(re.search(' .*? ', team_p[10].text).group(0)),file=fp)
			#Conf record
			print(float(re.search(' \.\d\d\d ', conf_p[0].text).group(0)),file=fp)
			#Conf SRS
			print(float(re.search(' .*? ', conf_p[1].text).group(0)),file=fp)

	def __get_team_game_log_data(self, team_name):
		url = NCAA.url_base + "/cbb/schools/" + team_name + "/" + self.year + "-gamelogs.html"
		soup = self.__get_soup_for(url)
		if not os.path.exists('y'+self.year+'/'+team_name):
			os.makedirs('y'+self.year+'/'+team_name)
		with open('data/y'+self.year+"/"+team_name+"/gamelogs.csv",mode="w") as fp:
			for game in soup.find_all('tr',id=re.compile('^sgl-basic')):
				line = map(lambda x: x.text, game.find_all("td"))
				if line[0] <= results.season_end_date[self.year]:
					del line[22]
					print(",".join(line[3:]).encode('utf-8'),file=fp)
if __name__ == '__main__':
	n = NCAA(sys.argv[1])
	n.get_data()