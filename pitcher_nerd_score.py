import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime

team_names = ('Astros','Yankees','Red Sox','Mariners','Indians','Cubs','Dodgers'
	,'Nationals','Brewers','Diamondbacks','Braves','Athletics','Cardinals',
	'Phillies','Angels','Giants','Blue Jays','Rockies','Pirates','Rays','Twins',
	'Rangers','Mets','Padres','Reds','Tigers','Marlins','White Sox','Royals',
	'Orioles','2 Teams','3 Teams','4 Teams','5 Teams','6 Teams','7 Teams',
	'8 Teams','9 Teams','10 Teams')


class PitcherLeaderboard:

	def __init__(self,year):
		if (int(year) < 2006):
			raise ValueError('Incomplete or missing data from this year! Please try another year.')
		pd.options.mode.chained_assignment = None #this keeps my console from getting spammed with stupid messages
		leaders_url = ('https://www.fangraphs.com/leaders.aspx?pos=all&stats=sta&lg=all&qual=20&type=c,119,113,30,31,76,3,211,117,87&season=%s&month=0&season1=%s&ind=0&team=0&rost=0&age=0&filter=&players=0&page=1_1000' % (str(year),str(year)))
		leaders_page = requests.get(leaders_url)
		leaders_soup = bs(leaders_page.content, 'html.parser')
		table = leaders_soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="LeaderBoard1_dg1_ctl00")
		df = pd.read_html(str(table),header=1)
		df = df[0]
		df = df.iloc[:-1]
		if len(df) > 2: #checks if any pitchers qualify
			df['xFIP-'] = pd.to_numeric(df['xFIP-'], downcast="float")
			df['SwStr%'] = (df['SwStr%'].str.replace('%','')).astype('double')#removes % symbol from DF
			df['SwStr%'] = pd.to_numeric(df['SwStr%'], downcast="float")
			df['Strikes'] = pd.to_numeric(df['Strikes'], downcast="float")
			df['Pitches']  = pd.to_numeric(df['Pitches'] , downcast="float")
			df['FBv']  = pd.to_numeric(df['FBv'] , downcast="float")
			df['Age']  = pd.to_numeric(df['Age'] , downcast="float")
			df['Pace']  = pd.to_numeric(df['Pace'] , downcast="float")
			df['ERA-']  = pd.to_numeric(df['ERA-'] , downcast="float")
			df['KN%'] = ((df['KN%'].str.replace('%','')).astype('double'))/100 #fangraphs % stuff formats weird so I have to do this
			df['KN%']  = pd.to_numeric(df['KN%'] , downcast="float")

			df['zxFIP-'] = (df['xFIP-'] - df['xFIP-'].mean())/df['xFIP-'].std(ddof=0) #Finds Z-score values for calculation
			df['zSwStr%'] = (df['SwStr%'] - df['SwStr%'].mean())/df['SwStr%'].std(ddof=0)
			df['Strk'] = df['Strikes']/df['Pitches'] #calculates strike rate
			df['zStrk'] = (df['Strk'] - df['Strk'].mean())/df['Strk'].std(ddof=0)
			df['zFBv'] = (df['FBv'] - df['FBv'].mean())/df['FBv'].std(ddof=0)
			df['zAge'] = (df['Age'] - df['Age'].mean())/df['Age'].std(ddof=0)
			df['zPace'] = (df['Pace'] - df['Pace'].mean())/df['Pace'].std(ddof=0)
			df['Luck'] = (df['ERA-'] - df['xFIP-'])/20 #I do the calculation here becuase it helps when checking if the value meets the threshold or not
			df['KN%'] = df['KN%'].fillna(0)
			df['zFBv'][df['zFBv'] < 0] = 0 #replaces values. These throw warnings for no reason because Pandas can't act like R without throwing a goddamn fit
			df['zAge'][df['zAge'] < 0] = 0
			df['Luck'][df['Luck'] < 0] = 0
			df['zFBv'][df['zFBv'] > 2] = 2
			df['zAge'][df['zAge'] > 2] = 2
			df['Luck'][df['Luck'] > 1] = 1
			df['NERD'] = (-df['zxFIP-'] * 2) + -(df['zSwStr%'] / 2) + (df['zStrk'] / 2) + df['zFBv'] + df['zAge'] + (-df['zPace']/2) + df['Luck'] + (df['KN%'] * 5) #base parts of NERD
			df['NERD'] = ((df['NERD'] - min(list(df['NERD']))) / (max(list(df['NERD'])) - min(list(df['NERD'])))) * 10 #I use feature scaling instead of adding a constant in order to get a more consistent scale of values
			self.df = df
			self.year = year
		else:
			raise ValueError('No pitchers qualified for that year\'s leaderboard! Please try again.')

	def pitcher_nerd_score(self,player_name):
		pitcher_df = self.df
		if (len(pitcher_df) >= 26) & (player_name in list(pitcher_df['Name'])): #checks if there are more than 25 pitchers on the list *and* player is on the list.
			return(float(pitcher_df[pitcher_df['Name']==player_name]['NERD']))
		else: #If pitcher does not currently qualify, checks their stats from last season
			pitcher_lb = Pitcher_Leaderboard(str(self.year - 1)) #initializes new Leaderboard object from previous year
			pitcher_df = pitcher_lb.df
			if (len(pitcher_df) >= 26) & (player_name in list(pitcher_df['Name'])): #checks if there are more than 25 pitchers on the list *and* player is on the list.
				return(float(pitcher_df[pitcher_df['Name']==player_name]['NERD']))
			else:
				return(5) #Five is the default score for debuting players.
