import tweepy
import mlbgame
from secrets import *
from pitcher_nerd_score import *
from team_nerd_score import *
import datetime
import subprocess
import codecs
from time import *
import pause
import ipdb
import imgkit

path_wkthmltoimage = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
config = imgkit.config(wkhtmltoimage=path_wkthmltoimage)
options = {
	"disable-local-file-access":""
}

while True:
	#authentication
	try:
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_secret)
		api = tweepy.API(auth)
		print('Authenticated without issue!')
	except:
		print('Error with Authentication!')
	#ipdb.set_trace()
	now = datetime.datetime.now()
	try:
		p_leaderboard = PitcherLeaderboard(now.year) #creates pitcher leaderboard
		t_leaderboard = TeamLeaderboard(now.year) #creates team leaderboard
	except:
		try:
			p_leaderboard = PitcherLeaderboard(int(now.year) - 1) #creates pitcher leaderboard
			t_leaderboard = TeamLeaderboard(int(now.year) - 1) #creates team leaderboard
		except:
			print("Error occured in generating leaderboards!")
			pass

 	#Posts information regarding NERD scores for the day
	try:
		games = []
		for game in mlbgame.day(now.year,now.month,now.day): #iterates through the games in nerd_bot
			if game.home_team == 'D-backs': #MLB gameday formatting is pretty stupid, idk why they have "D-Backs" here
				game.home_team  = 'Diamondbacks' #like seriously, no other site abbreviates just "d-backs"
			elif game.away_team == 'D-backs': #how important is it to have team names less than 10 characters?
				game.away_team = 'Diamondbacks' #f****** stupid.
			game.home_team_NERD = int(round(t_leaderboard.team_nerd_score(game.home_team),0)) #NERD score calculations
			try:
				game.home_pitcher_NERD = int(round(p_leaderboard.pitcher_nerd_score(game.p_pitcher_home),0))
			except: #double contigency built in, just in case something borks with the built in class method for pitcher_ned_score
				game.home_pitcher_NERD = int(5)
			game.away_team_NERD = int(round(t_leaderboard.team_nerd_score(game.away_team),0))
			try:
				game.away_pitcher_NERD = int(round(p_leaderboard.pitcher_nerd_score(game.p_pitcher_away),0))
			except:
				game.away_pitcher_NERD = int(5)
			game.total_NERD = int(round(((game.home_team_NERD + game.home_pitcher_NERD + game.away_pitcher_NERD + game.away_team_NERD)/4),0))
			games = games + [game]

		games = sorted(games, key=lambda x: x.total_NERD, reverse=True) #sorts by NERD for games
	except:
		print('WARNING! Error occured in scraping.')
		pass

	#Posts NERD Scores for the day
	try:
		days_games = pd.DataFrame() #puts scoreoard into a dataframe
		days_games['Home P'] = [game.p_pitcher_away for game in games]
		days_games['Home Team']  = [game.home_team for game in games]
		days_games['H_SP'] = [game.away_pitcher_NERD for game in games]
		days_games['H_TM'] = [game.home_team_NERD for game in games]
		days_games['GM'] = [game.total_NERD for game in games]
		days_games['A_TM'] = [game.away_team_NERD for game in games]
		days_games['A_SP'] = [game.home_pitcher_NERD for game in games]
		days_games['Away Team'] = [game.away_team for game in games]
		days_games['Away P'] = [game.p_pitcher_home for game in games]
		days_games['Game Time'] = [game.game_start_time for game in games]
		days_games.to_html("todays_table.html",index = False) #writes to an HTML table for conversion to image
		f=codecs.open("todays_table.html", 'r')
		new_html = f.read()
		f.close()
		f = codecs.open('todays_table.html','w')
		new_html = '''<html>
		<head>
		<style>
		table{
			max-width: 1000px;
			background-color: #fff;
			margin: 0 auto;
			font-family: Lato,Arial;
			font-size: 12px;
			line-height: 1.5;
			color: #000;
			background-color: #f0f0f0;
			margin: 0;
			padding: 0;
		}
		</style>
		<link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">
		</head>''' + new_html + '</html>' #adds styling to HTML table
		f.write(new_html)
		f.close()
		imgkit.from_url('todays_table.html', 'todays_table.png',config=config, options=  options)
		body = 'Top games for today by NERD\n'
		body += '%s (%s) vs. %s (%s), %s ET (NERD: %d)\n' % (str(days_games['Home Team'].iloc[0]),str(days_games['Home P'].iloc[0]),str(days_games['Away Team'].iloc[0]),str(days_games['Away P'].iloc[0]),str(days_games['Game Time'].iloc[0]),int(days_games['GM'].iloc[0]))
		body += '%s (%s) vs. %s (%s), %s ET (NERD: %d)\n' % (str(days_games['Home Team'].iloc[1]),str(days_games['Home P'].iloc[1]),str(days_games['Away Team'].iloc[1]),str(days_games['Away P'].iloc[1]),str(days_games['Game Time'].iloc[1]),int(days_games['GM'].iloc[1]))
		body += '%s (%s) vs. %s (%s), %s ET (NERD: %d)\n' % (str(days_games['Home Team'].iloc[2]),str(days_games['Home P'].iloc[2]),str(days_games['Away Team'].iloc[2]),str(days_games['Away P'].iloc[2]),str(days_games['Game Time'].iloc[2]),int(days_games['GM'].iloc[2]))
	except:
		print("Unable to generate game table image!")
		pass

	try:
		# api.update_with_media('todays_table.png',body) #posts tweet
		top_game_already_posted = True
		print('Posted today\'s game table.')
		# sleep(900) #wait 15 minutes for next tweet
	except:
		print('Unable to post today\'s game table.')
		# sleep(900)

	#Shows top NERD scores for pitchers

	pitcher_df = p_leaderboard.df.sort_values(by=['NERD'],ascending=False) #Puts pitchers into leaderboard, NERD leaders
	pitcher_df = pitcher_df.reset_index(drop=True)
	pitcher_df = pitcher_df[['Name','NERD']]
	pitcher_df['NERD'] = pitcher_df['NERD'].round(0)
	pitcher_df['NERD'] = pd.to_numeric(pitcher_df['NERD'],downcast = 'signed')
	pitcher_df = pitcher_df.head(19)
	pitcher_df.to_html("pitcher_leaders.html",index=False) #this chunk also writes the table into an IMAGE
	f=codecs.open("pitcher_leaders.html", 'r')
	new_html = f.read()
	f.close()
	f = codecs.open('pitcher_leaders.html','w')
	new_html = '''<html>
	<head>
		<style>
		table{
			max-width: 1000px;
			background-color: #fff;
			margin: 0 auto;
			font-family: Lato,Arial;
			font-size: 12px;
			line-height: 1.5;
			color: #000;
			background-color: #f0f0f0;
			margin: 0;
			padding: 0;
		}
		</style>
	<link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">
	</head>''' + new_html + '</html>'
	f.write(new_html)
	f.close()
	imgkit.from_url('pitcher_leaders.html','pitchers_table.png',config=config)
	body = 'Top pitchers by NERD - %d/%d/%d \n' % (now.month,now.day,now.year)
	body += '%s - %d\n' % (pitcher_df.iloc[0]['Name'],pitcher_df.iloc[0]['NERD'])
	body += '%s - %d\n' % (pitcher_df.iloc[1]['Name'],pitcher_df.iloc[1]['NERD'])
	body += '%s - %d\n' % (pitcher_df.iloc[2]['Name'],pitcher_df.iloc[2]['NERD'])
	body += '%s - %d\n' % (pitcher_df.iloc[3]['Name'],pitcher_df.iloc[3]['NERD'])
	body += '%s - %d\n' % (pitcher_df.iloc[4]['Name'],pitcher_df.iloc[4]['NERD'])

	try:
		# api.update_with_media('pitchers_table.png',body)
		print('Posted today\'s pitchers table.')
		# sleep(900)
	except:
		print('Unable to post today\'s pitchers table.')
		# sleep(900)

	#this last chunk puts NERD values for teams together
	team_df = t_leaderboard.df.sort_values(by=['NERD'],ascending=False)
	team_df = team_df.reset_index(drop=True)
	team_df = team_df[['Team','NERD']]
	team_df['NERD'] = team_df['NERD'].round(0)
	team_df['NERD'] =  pd.to_numeric(team_df['NERD'],downcast = 'signed')
	team_df.to_html("team_leaders.html", index=False)
	f=codecs.open("team_leaders.html", 'r')
	new_html = f.read()
	f.close()
	f = codecs.open('team_leaders.html','w')
	new_html = '''<html>
	<head>
			<style>
			table{
				max-width: 1000px;
				background-color: #fff;
				margin: 0 auto;
				font-family: Lato,Arial;
				font-size: 12px;
				line-height: 1.5;
				color: #000;
				background-color: #f0f0f0;
				margin: 0;
				padding: 0;
			}
			</style>
	<link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">
	</head>''' + new_html + '</html>'
	f.write(new_html)
	f.close()
	imgkit.from_url('team_leaders.html', 'team_table.png',config=config)
	body = 'Top teams by NERD - %d/%d/%d \n' % (now.month,now.day,now.year)
	body += '%s - %d\n' % (team_df.iloc[0]['Team'],team_df.iloc[0]['NERD'])
	body += '%s - %d\n' % (team_df.iloc[1]['Team'],team_df.iloc[1]['NERD'])
	body += '%s - %d\n' % (team_df.iloc[2]['Team'],team_df.iloc[2]['NERD'])
	body += '%s - %d\n' % (team_df.iloc[3]['Team'],team_df.iloc[3]['NERD'])
	body += '%s - %d\n' % (team_df.iloc[4]['Team'],team_df.iloc[4]['NERD'])

	try:
		# api.update_with_media('team_table.png',body)
		print('Posted today\'s team table.')
	except:
		print('Unable to post today\'s team table.')

	#goes through games to check for when games start
	game_times = [datetime.datetime.strptime(time,'%I:%M %p') - datetime.timedelta(minutes=10) for time in list(days_games['Game Time'])]
	game_times = [game_time.replace(year=now.year) for game_time in game_times]
	game_times = [game_time.replace(month=now.month) for game_time in game_times]
	game_times = [game_time.replace(day=now.day) for game_time in game_times]
	days_games['Game Time'] = game_times
	days_games = days_games.sort_values(by=['Game Time'])
	game_times = sorted(game_times)
	days_games = days_games.reset_index(drop=True)
	print(days_games)
	for index,row in days_games.iterrows(): #This posts NERD scores when games are about to begin
		print('Waiting for %s vs. %s to start' % (str(days_games['Home Team'].iloc[index]) , str(days_games['Away Team'].iloc[index])))
		pause.until(game_times[index])
		body = '%s (%s) vs. %s (%s) about to start - NERD Game Score of %d' % (str(days_games['Home Team'].iloc[index]),str(days_games['Home P'].iloc[index]),str(days_games['Away Team'].iloc[index]),str(days_games['Away P'].iloc[index]),days_games['GM'].iloc[index])
		#api.update_status(body)

	#pauses running until new day
	new_day = now + datetime.timedelta(days=1)
	new_day = new_day.replace(hour=10)
	new_day = new_day.replace(minute=5)
	print('Sleeping until ' + str(new_day))
	pause.until(new_day)
