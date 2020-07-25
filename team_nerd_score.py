import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime

now = datetime.datetime.now()

spotrac_ids = ['Boston Red Sox BOS', 'San Francisco Giants SF', 'Chicago Cubs CHC',
	'Washington Nationals WSH', 'Los Angeles Dodgers LAD',
	'Los Angeles Angels LAA', 'New York Yankees NYY', 'Toronto Blue Jays TOR',
	'St. Louis Cardinals STL', 'New York Mets NYM', 'Houston Astros HOU',
	'Seattle Mariners SEA', 'Texas Rangers TEX', 'Baltimore Orioles BAL',
	'Colorado Rockies COL', 'Detroit Tigers DET', 'Cleveland Indians CLE',
	'Arizona Diamondbacks ARI', 'Kansas City Royals KC', 'Minnesota Twins MIN',
	'Atlanta Braves ATL', 'Philadelphia Phillies PHI', 'Miami Marlins MIA',
	'San Diego Padres SD', 'Cincinnati Reds CIN', 'Pittsburgh Pirates PIT',
	'Milwaukee Brewers MIL', 'Tampa Bay Rays TB', 'Oakland Athletics OAK',
	'Chicago White Sox CHW']

fangraphs_ids = ['Red Sox','Giants','Cubs','Nationals','Dodgers','Angels',
	'Yankees','Blue Jays','Cardinals','Mets','Astros','Mariners','Rangers',
	'Orioles','Rockies','Tigers','Indians','Diamondbacks','Royals','Twins',
	'Braves','Phillies','Marlins','Padres','Reds','Pirates','Brewers','Rays',
	'Athletics','White Sox']

class TeamLeaderboard:

	def __init__(self,year):
		if (int(year) < 2011):
			raise ValueError('Incomplete or missing data from this year! Please try another year.')
		pd.options.mode.chained_assignment = None #this keeps my console from getting spammed with stupid messages
		team_url = ('https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=c,53,11,6,111,199,3,58&season=%s&month=0&season1=%s&ind=0&team=0,ts&rost=&age=&filter=&players=0' % (str(year),str(year)))
		team_page = requests.get(team_url)
		team_soup = bs(team_page.content, 'html.parser')
		table = team_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="LeaderBoard1_dg1_ctl00")
		df = pd.read_html(str(table),header=1)
		df = df[0]
		df = df.iloc[:-1]
		df['PA'] = pd.to_numeric(df['PA'], downcast="float")
		if (min(list(df['PA'])) >= 225): #makes sure that at least a week of play has passed roughly
			#This part grabs and attaches bullpen xFIP data to the main DF
			bullpen_url = ('https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=c,6,62&season=%s&month=0&season1=%s&ind=0&team=0,ts&rost=0&age=0&filter=&players=0' % (str(year),str(year)))
			bullpen_page = requests.get(bullpen_url)
			bullpen_soup = bs(bullpen_page.content, 'html.parser')
			table = bullpen_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="LeaderBoard1_dg1_ctl00")
			bp_df = pd.read_html(str(table),header=1)
			bp_df = bp_df[0]
			bp_df = bp_df.iloc[:-1]
			df = df.merge(bp_df, on='Team')
			#This part, a pain in the ass, attaches payroll data from SportTrac to the main DF
			payroll_url = 'https://www.spotrac.com/mlb/payroll/'
			payroll_page = requests.get(payroll_url)
			payroll_soup = bs(payroll_page.content,'lxml')
			table = payroll_soup.find_all('table')[0]
			pr_df = pd.read_html(str(table),header=0)
			pr_df = pr_df[0]
			pr_df.loc[pr_df['Team'] != 'League Average'] #removes annoying "league average" stuff
			for index in range(0,len(spotrac_ids)): #replaces spotrac ids with FanGraphs IDs
				pr_df['Team'].loc[pr_df['Team'] == spotrac_ids[index]] = fangraphs_ids[index]
			df = df.merge(pr_df, on='Team')
			#grabs pitching WAR and Wins to determine team luckiness
			pitch_url = ('https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=0&type=c,59,4&season=%s&month=0&season1=%s&ind=0&team=0,ts&rost=0&age=0&filter=&players=0' %  (str(year),str(year)))
			pitch_page = requests.get(pitch_url)
			pitch_soup = bs(pitch_page.content, 'html.parser')
			table = pitch_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="LeaderBoard1_dg1_ctl00")
			pit_df = pd.read_html(str(table),header=1)
			pit_df = pit_df[0]
			pit_df = pit_df.iloc[:-1]
			df = df.merge(pit_df, on='Team')
			#grabs park factors for adjusting HR rate
			pf_url = ('https://www.fangraphs.com/guts.aspx?type=pf&teamid=0&season=%s' % (str(year)))
			pf_page = requests.get(pf_url)
			pf_soup = bs(pf_page.content,'html.parser')
			table = pf_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="GutsBoard1_dg1_ctl00")
			pf_df = pd.read_html(str(table),header=0)
			pf_df = pf_df[0]
			df = df.merge(pf_df, on='Team')
			#calculates NERD
			df['Bat'] = pd.to_numeric(df['Bat'], downcast="float")
			df['HR_x'] = pd.to_numeric(df['HR_x'], downcast="float")
			df['HR_y'] = pd.to_numeric(df['HR_y'], downcast="float")
			df['BsR'] = pd.to_numeric(df['BsR'], downcast="float")
			df['xFIP'] = pd.to_numeric(df['xFIP'], downcast="float")
			df['Def'] = pd.to_numeric(df['Def'], downcast="float")
			df['Total Payroll'] = df[str(now.year) + ' Total Payroll'].replace('[\$,]', '', regex=True).astype(float)
			df['Total Payroll'] = pd.to_numeric(df['Total Payroll'], downcast="float")
			df['Age'] = pd.to_numeric(df['Age'], downcast="float")
			df['WAR_x'] = pd.to_numeric(df['WAR_x'], downcast="float")
			df['WAR_y'] = pd.to_numeric(df['WAR_y'], downcast="float")
			df['W'] = pd.to_numeric(df['W'], downcast="float")

			df['zBat'] = (df['Bat'] - df['Bat'].mean())/df['Bat'].std(ddof=0) #Finds Z-score values for calculation
			df['HRpPA'] = df['HR_x'] / df['PA'] #calculates HR per PA per team
			df['HRpPA'] = df['HRpPA'] * df['HR_y'] / 100 #adjusts for park factors
			df['zHRpPA'] = (df['HRpPA'] - df['HRpPA'].mean())/df['HRpPA'].std(ddof=0)
			df['zBsR'] = (df['BsR'] - df['BsR'].mean())/df['BsR'].std(ddof=0)
			df['zBull'] = -((df['xFIP'] - df['xFIP'].mean())/df['xFIP'].std(ddof=0))
			df['zDef'] = (df['Def'] - df['Def'].mean())/df['Def'].std(ddof=0)
			df['Total Payroll'] = df['Total Payroll'].replace('[\$,]', '', regex=True).astype(float) #converts dollar amounts to numbers
			df['zPay'] = -((df['Total Payroll'] - df['Total Payroll'].mean())/df['Total Payroll'].std(ddof=0))
			df['zAge'] = -((df['Age'] - df['Age'].mean())/df['Age'].std(ddof=0))
			df['tWAR'] = df['WAR_x'] + df['WAR_y']
			df['Luck'] = (df['tWAR'] - df['W'])/20 #Adjusted for calculation
			df['zPay'][df['zPay'] < 0] = 0 #replaces values. These throw warnings for no reason because Pandas can't act like R without throwing a goddamn fit
			df['zAge'][df['zAge'] < 0] = 0
			df['Luck'][df['Luck'] < 0] = 0
			df['Luck'][df['Luck'] > 2] = 2
			df['NERD'] = df['zBat'] + df['zHRpPA'] + df['zBsR'] + (df['zBull'] / 2) + (df['zDef'] / 2) + df['zPay'] + df['zAge'] + df['Luck'] #unadjusted NERD
			df['NERD'] = (((df['NERD'] - min(list(df['NERD']))) * (10)) / (max(list(df['NERD'])) - min(list(df['NERD'])))) #feature scaled
			self.df  = df
			self.year = year
		else: #This does the exact same stuff as above, except it does it for the previous year if there aren't enough teams in the previous year.
			pd.options.mode.chained_assignment = None #this keeps my console from getting spammed with stupid messages
			team_url = ('https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=c,53,11,6,111,199,3,58&season=%s&month=0&season1=%s&ind=0&team=0,ts&rost=&age=&filter=&players=0' % (str(year-1),str(year-1)))
			team_page = requests.get(team_url)
			team_soup = bs(team_page.content, 'html.parser')
			table = team_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="LeaderBoard1_dg1_ctl00")
			df = pd.read_html(str(table),header=1)
			df = df[0]
			df = df.iloc[:-1]
			bullpen_url = ('https://www.fangraphs.com/leaders.aspx?pos=all&stats=rel&lg=all&qual=0&type=c,6,62&season=%s&month=0&season1=%s&ind=0&team=0,ts&rost=0&age=0&filter=&players=0' % (str(year-1),str(year-1)))
			bullpen_page = requests.get(bullpen_url)
			bullpen_soup = bs(bullpen_page.content, 'html.parser')
			table = bullpen_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="LeaderBoard1_dg1_ctl00")
			bp_df = pd.read_html(str(table),header=1)
			bp_df = bp_df[0]
			bp_df = bp_df.iloc[:-1]
			df = df.merge(bp_df, on='Team')
			#This part, a pain in the ass, attaches payroll data from SportTrac to the main DF
			payroll_url = 'https://www.spotrac.com/mlb/payroll/' #yo, please don't use this to do previous years because payroll data might be off
			payroll_page = requests.get(payroll_url)
			payroll_soup = bs(payroll_page.content,'lxml')
			table = payroll_soup.find_all('table')[0]
			pr_df = pd.read_html(str(table),header=0)
			pr_df = pr_df[0]
			pr_df = pr_df.loc[:14].append(pr_df.loc[17:]) #removes annoying "league average" stuff
			for index in range(0,len(spotrac_ids)): #replaces spotrac ids with FanGraphs IDs
				pr_df['Team'].loc[pr_df['Team'] == spotrac_ids[index]] = fangraphs_ids[index]
			df = df.merge(pr_df, on='Team')
			#grabs pitching WAR and Wins to determine team luckiness
			pitch_url = ('https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=0&type=c,59,4&season=%s&month=0&season1=%s&ind=0&team=0,ts&rost=0&age=0&filter=&players=0' %  (str(year-1),str(year-1)))
			pitch_page = requests.get(pitch_url)
			pitch_soup = bs(pitch_page.content, 'html.parser')
			table = pitch_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="LeaderBoard1_dg1_ctl00")
			pit_df = pd.read_html(str(table),header=1)
			pit_df = pit_df[0]
			pit_df = pit_df.iloc[:-1]
			df = df.merge(pit_df, on='Team')
			#grabs park factors for adjusting HR rate
			pf_url = ('https://www.fangraphs.com/guts.aspx?type=pf&teamid=0&season=%s' % (str(year-1)))
			pf_page = requests.get(pf_url)
			pf_soup = bs(pf_page.content,'html.parser')
			table = pf_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="GutsBoard1_dg1_ctl00")
			pf_df = pd.read_html(str(table),header=0)
			pf_df = pf_df[0]
			df = df.merge(pf_df, on='Team')
			#calculates NERD
			df['Bat'] = pd.to_numeric(df['Bat'], downcast="float")
			df['HR_x'] = pd.to_numeric(df['HR_x'], downcast="float")
			df['PA'] = pd.to_numeric(df['PA'], downcast="float")
			df['HR_y'] = pd.to_numeric(df['HR_y'], downcast="float")
			df['BsR'] = pd.to_numeric(df['BsR'], downcast="float")
			df['xFIP'] = pd.to_numeric(df['xFIP'], downcast="float")
			df['Def'] = pd.to_numeric(df['Def'], downcast="float")
			df['Total Payroll'] = df[str(now.year) + ' Total Payroll'].replace('[\$,]', '', regex=True).astype(float)
			df['Total Payroll'] = pd.to_numeric(df['Total Payroll'], downcast="float")
			df['Age'] = pd.to_numeric(df['Age'], downcast="float")
			df['WAR_x'] = pd.to_numeric(df['WAR_x'], downcast="float")
			df['WAR_y'] = pd.to_numeric(df['WAR_y'], downcast="float")
			df['W'] = pd.to_numeric(df['W'], downcast="float")

			df['zBat'] = (df['Bat'] - df['Bat'].mean())/df['Bat'].std(ddof=0) #Finds Z-score values for calculation
			df['HRpPA'] = df['HR_x'] / df['PA'] #calculates HR per PA per team
			df['HRpPA'] = df['HRpPA'] * df['HR_y'] / 100 #adjusts for park factors
			df['zHRpPA'] = (df['HRpPA'] - df['HRpPA'].mean())/df['HRpPA'].std(ddof=0)
			df['zBsR'] = (df['BsR'] - df['BsR'].mean())/df['BsR'].std(ddof=0)
			df['zBull'] = -((df['xFIP'] - df['xFIP'].mean())/df['xFIP'].std(ddof=0))
			df['zDef'] = (df['Def'] - df['Def'].mean())/df['Def'].std(ddof=0)
			df['Total Payroll'] = df['Total Payroll'].replace('[\$,]', '', regex=True).astype(float) #converts dollar amounts to numbers
			df['zPay'] = -((df['Total Payroll'] - df['Total Payroll'].mean())/df['Total Payroll'].std(ddof=0))
			df['zAge'] = -((df['Age'] - df['Age'].mean())/df['Age'].std(ddof=0))
			df['tWAR'] = df['WAR_x'] + df['WAR_y']
			df['Luck'] = (df['tWAR'] - df['W'])/20 #Adjusted for calculation
			df['zPay'][df['zPay'] < 0] = 0 #replaces values. These throw warnings for no reason because Pandas can't act like R without throwing a goddamn fit
			df['zAge'][df['zAge'] < 0] = 0
			df['Luck'][df['Luck'] < 0] = 0
			df['Luck'][df['Luck'] > 2] = 2
			df['NERD'] = df['zBat'] + df['zHRpPA'] + df['zBsR'] + (df['zBull'] / 2) + (df['zDef'] / 2) + df['zPay'] + df['zAge'] + df['Luck'] #unadjusted NERD
			df['NERD'] = (((df['NERD'] - min(list(df['NERD']))) * (10)) / (max(list(df['NERD'])) - min(list(df['NERD'])))) #feature scaled
			self.df  = df
			self.year = year
	def team_nerd_score(self,team):
		team_df = self.df
		return(float(team_df[team_df['Team']==team]['NERD']))
