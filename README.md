# NERD-Bot

## What is this?
If you're like me, you miss Carson Cistulli's daily NERD Scores on FanGraphs. While I can hardly hope to match Cistulli's writing ability, I can code passably, so I figured I'd implement a version of Cistulli's NERD Scores easily consumable by the Twitterverse.

## What are NERD Scores?
NERD Scores are an attempt to quantify what games are most enjoyable to watch based on a variety of factors between teams and their starting pitchers. [An exact explanation of the calculation can be found here,](https://www.fangraphs.com/blogs/nerd-scores-return-with-something-not-unlike-a-vengeance/) though this bot has some slight differences in calculation.

## What are those differences?
I tried to be as faithful to the spirit of NERD scores as possible, but I did take two shortcuts.

  1. Instead of using overall pitch velocity, I simply used fastball velocity. Fastball velocity is well correlated to overall velocity, but it's far easier to scrape that value than to calculate overall pitch velocity.
  2. Pitcher and Team NERD Scores as calculated by the bot are [feature scaled](https://en.wikipedia.org/wiki/Feature_scaling) to fit onto a 0-10 scale, whereas the original NERD scores added constants with values between 3.5-4.0. In place of adding those constants, the raw scores are feature scaled.

## How does the bot work?
I tried to mark up the bot as best as I could, but the general way that the bot works is as follows: The bot grabs the probable pitchers for each game that day, calculates NERD scores for each game from the scores for each pitcher and team. The bot then posts the top games of the day, the top NERD pitchers of the season, and the top teams of the season. If there's insufficient data (not enough pitchers qualified or games in the season), NERD calculates scores based on last season's data. Then, 10 minutes before each game, NERD posts a reminder that the game is about to begin and what the NERD score for each game is. When all the teams' data is posted, NERD goes to sleep until the next day, and then the cycle repeats.

## Is the bot -
Woah woah woah, let's cool it with the questions.

## What?
I ain't got all day to sit around and answer your dumb questions.

## But they're just simple questions to give you a chance to explain the bot.
I know, I know, I just have more important stuff to do.

## The people deserve to know the truth.
Jeez, okay Tom Cruise - if you have any more questions, @ me on twitter: @John_Edwards_
