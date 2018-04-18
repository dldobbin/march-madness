import random
import os
import re
import least_squares
from datetime import date
import results
import model

def sign(a):
	return (a>0) - (a<0)

class Team():
	def __init__(self, name, seed):
		self.name = name
		self.seed = int(seed)

	def __repr__(self):
		return (self.name, self.seed).__repr__()

class NCAA():
	"""docstring for NCAA"""
	def __init__(self, year=date.today().year):
		self.year = str(year)
		self.results = [map(lambda x: Team(x[0],x[1]), round) for round in results.results[self.year]]
		self.adj_factor = self.get_adjustment_factor()
		if not os.path.exists('data/y'+self.year):
			os.makedirs('data/y'+self.year)

	def get_team_base_line(self, team_name):
		team_strengths = [0 for _ in xrange(13)]
		totals = [0 for _ in xrange(13)]
		count = 0
		with open('data/y'+self.year+'/'+team_name+"/gamelogs.csv") as fp:
			for game in fp:
				count += 1
				#[outcome, ps, pa, fg, fga, fgp, thp, thpa, thpp, ft, fta, ftp, orb, trb, ast, stl, blk, tov, pf, opp_fg, opp_fga, opp_fgp, opp_thp, opp_thpa, opp_thpp, opp_ft, opp_fta, opp_ftp, opp_orb, opp_trb, opp_ast, opp_stl, opp_blk, opp_tov, opp_pf] = gamearr
				gamearr = game.split(",")
				gamearr[1:] = map(lambda x: float(x) if x else 0, gamearr[1:])
				team_stats = model.process_game_line(gamearr[3:19])
				opp_stats = model.process_game_line(gamearr[19:])				
				#twp, twpa, thp, thpa, ft, fta, orb, drb, ast, stl, blk, tov, pf
				team_strengths = [c+strength for c,strength in zip([1 if t > o else .5 if t == o else 0 for t,o in zip(team_stats,opp_stats)],team_strengths)]
				totals = [s+t for s,t in zip(team_stats,totals)]
		return ([t/count for t in totals], [t/count for t in team_strengths])

	def get_team_adjusted_line(self, team_name, opp_name):
		team_line = self.get_team_base_line(team_name)	
		opp_line = self.get_team_base_line(opp_name)
		return [self.get_team_conference_adj(team_name, opp_name)+t+abs(s-os)*(s if s > os else -os) for t,s,os in zip(team_line[0],team_line[1],opp_line[1])]

	def compare_teams(self, team_name, opp_name):
		###############     twp,      twpa,       thp,      thpa,       ft,        fta,       orb,      drb,       ast,       stl,       blk,       tov,        pf
		team_adjusted_line = self.get_team_adjusted_line(team_name, opp_name)
		opp_adjusted_line = self.get_team_adjusted_line(opp_name, team_name)
		line = model.model(team_adjusted_line,opp_adjusted_line)
		return sum([a*l for l,a in zip(line,self.adj_factor)])

	def get_team_conference_adj(self, team_name, opp_name):
		with open('data/y'+self.year+'/'+opp_name+"/conference.csv") as fp:
			opp_SRS = float(fp.readline())
			opp_SOS = float(fp.readline())
			opp_Ortg = float(fp.readline())
			opp_Drtg = float(fp.readline())
		with open('data/y'+self.year+'/'+team_name+"/conference.csv") as fp:
			team_SRS = float(fp.readline())
			team_SOS = float(fp.readline())
			team_Ortg = float(fp.readline())
			team_Drtg = float(fp.readline())
			conf_record = float(fp.readline())
			conf_SRS = float(fp.readline())
		return (
			team_Ortg+opp_Drtg
			#team_SRS
				#+
				#conf_SRS
			) * conf_record * .1

	#########################################
	# CHALK 								#
	#########################################

	def chalk(self):
		chalk_results = self.__chalk_round([self.results[0]])
		return {'score': self.__score(chalk_results), 'outcome': chalk_results}

	def __chalk_round(self, outcome):
		teams = outcome[-1]
		if len(teams) == 1:
			return outcome
		next_round = [[t,o][random.randint(0,1) if t.seed == o.seed else t.seed > o.seed] for t,o in zip(teams[0::2],teams[1::2])]
		outcome.append(next_round)
		return self.__chalk_round(outcome)

	#########################################
	# SIM 	 								#
	#########################################		

	def sim(self):
		sim_results = self.__sim_round([self.results[0]])
		return {'score': self.__score(sim_results), 'outcome': sim_results}

	def __sim_round(self, outcome):
		teams = outcome[-1]
		if len(teams) == 1:
			return outcome
		next_round = [[t,o][(sign(self.compare_teams(t.name,o.name))-1)/2] for t,o in zip(teams[0::2],teams[1::2])]
		outcome.append(next_round)
		return self.__sim_round(outcome)

	def __score(self, sim_results):
		s = 0
		for i in range(1,len(sim_results)):
			s += sum([2**(i-1) if t.name==s.name else 0 for t,s in zip(self.results[i],sim_results[i])])
		return s

	def get_adjustment_factor(self):
		data = []
		for team_name in os.walk('data/y'+self.year).next()[1]:
			team_stats = self.get_team_base_line(team_name)[0]
			with open('data/y'+self.year+'/'+team_name+'/gamelogs.csv') as fp:
				for game in fp:
					gamearr = game.split(",")
					gamearr[1:] = map(lambda x: float(x) if x else 0, gamearr[1:])
					opp_stats = model.process_game_line(gamearr[19:])

					line = model.model(team_stats,opp_stats) + [gamearr[1]-gamearr[2]]
					data.append(line)
		return least_squares.adj(data).reshape(13).tolist()