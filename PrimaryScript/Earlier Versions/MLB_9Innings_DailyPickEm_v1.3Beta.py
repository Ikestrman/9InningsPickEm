import statsapi
import datetime
import numpy as np
import pandas as pd
import json
import re
import requests
from icecream import ic

ic(requests)

FiveThirtyEightFrame = pd.read_csv('https://projects.fivethirtyeight.com/mlb-api/mlb_elo_latest.csv')

date = input("Enter date (e.g., 08/01/2021): ")

print('*****')
print('*****processing...*****')
print('*****')
print('Title:')
print('---')

dt = date
month, day, year = (int(x) for x in dt.split('/'))
ans = datetime.date(year, month, day)

# -----Adding FiveThirtyEight Apr.26
onlyTodayGamesFrame = FiveThirtyEightFrame[
    (FiveThirtyEightFrame["date"] == ans.strftime("%Y" + "-" + "%m" + "-" + "%d"))]
onlyTodayGamesFrame = onlyTodayGamesFrame[['date', 'team1', 'team2', 'rating_prob1', 'rating_prob2']]

teamAbbreviationReplacers = {
    'ARI': 'Arizona Diamondbacks',
    'ATL': 'Atlanta Braves',
    'BAL': 'Baltimore Orioles',
    'BOS': 'Boston Red Sox',
    'CHC': 'Chicago Cubs',
    'CHW': 'Chicago White Sox',
    'CIN': 'Cincinnati Reds',
    'CLE': 'Cleveland Indians',
    'COL': 'Colorado Rockies',
    'DET': 'Detroit Tigers',
    'FLA': 'Miami Marlins',
    'HOU': 'Houston Astros',
    'KCR': 'Kansas City Royals',
    'ANA': 'Los Angeles Angels',
    'LAD': 'Los Angeles Dodgers',
    'MIL': 'Milwaukee Brewers',
    'MIN': 'Minnesota Twins',
    'NYM': 'New York Mets',
    'NYY': 'New York Yankees',
    'OAK': 'Oakland Athletics',
    'PHI': 'Philadelphia Phillies',
    'PIT': 'Pittsburgh Pirates',
    'SDP': 'San Diego Padres',
    'SFG': 'San Francisco Giants',
    'SEA': 'Seattle Mariners',
    'STL': 'St. Louis Cardinals',
    'TBD': 'Tampa Bay Rays',
    'TEX': 'Texas Rangers',
    'TOR': 'Toronto Blue Jays',
    'WSN': 'Washington Nationals'}

onlyTodayGamesFrame['team1'].replace(teamAbbreviationReplacers, inplace=True)
onlyTodayGamesFrame['team2'].replace(teamAbbreviationReplacers, inplace=True)
# -----

# ----
def determine_if_doubleheader():
    if singleAwayProbValueAsPercentage is not None:
        return singleAwayProbValueAsPercentage
    else:
        return multipleAwayProbValueAsPercentage
# ----

params = {
    "sportId": 1,
    "date": date,
    "hydrate": "probablePitcher(note)",
}
schedule = statsapi.get("schedule", params)
gamesThatDay = schedule["dates"][0]["games"]

probablePitcherIds = []
probablePitcherIds.extend([str(x['teams']['away'].get('probablePitcher', {}).get('id', None)) for x in gamesThatDay])
probablePitcherIds.extend([str(x['teams']['home'].get('probablePitcher', {}).get('id', None)) for x in gamesThatDay])
probablePitcherIds = [x for x in probablePitcherIds if x != "None"]

peopleParams = {
    "personIds": ",".join(probablePitcherIds),
    "hydrate": f"stats(group=[pitching],type=[season],season=2021)",
    "fields": "people,id,fullName,stats,splits,stat,gamesPitched,gamesStarted,era,inningsPitched,wins,losses,saves,saveOpportunities,holds,blownSaves,whip,completeGames,shutouts",
}
pitcherStats = statsapi.get("people", peopleParams)

table = "|**Matchup and Team Records**|**Probable Pitchers (Season ERA)**|**Estimated Win Probability**|\n"
table += "|:-----|:-----|:--|\n"
for game in gamesThatDay:
    try:
        contextMetrics = statsapi.get("game_contextMetrics", {"gamePk": game["gamePk"]})
    except ValueError as e:
        contextMetrics = {}
    # ----- More from Apr 26
    singleAwayProbRow = onlyTodayGamesFrame[
        (onlyTodayGamesFrame.date == ans.strftime("%Y" + "-" + "%m" + "-" + "%d")) & (
                    onlyTodayGamesFrame.team2 == game["teams"]["away"]['team']['name'])]
    singleAwayProbValueAsArray = singleAwayProbRow['rating_prob2'].values

    if np.count_nonzero(singleAwayProbValueAsArray) > 1:
        #print(singleAwayProbValueAsArray.ite)
        for x in np.nditer(singleAwayProbValueAsArray):
            #print(x)
        #    singleAwayProbValueAsDecimal = re.sub('[\[\]]', '', np.array_str(np.ndarray(key)))
            multipleAwayProbValueAsPercentage = ("{:.0%}".format(float(x)))
            #print("The multiple value is: " + multipleAwayProbValueAsPercentage)
            singleAwayProbValueAsPercentage = None
    else:
        singleAwayProbValueAsDecimal = re.sub('[\[\]]', '', np.array_str(singleAwayProbValueAsArray))
        singleAwayProbValueAsPercentage = ("{:.0%}".format(float(singleAwayProbValueAsDecimal)))

    singleHomeProbRow = onlyTodayGamesFrame[
        (onlyTodayGamesFrame.date == ans.strftime("%Y" + "-" + "%m" + "-" + "%d")) & (
                    onlyTodayGamesFrame.team1 == game["teams"]["home"]['team']['name'])]
    singleHomeProbValueAsArray = singleHomeProbRow['rating_prob1'].values

    if np.count_nonzero(singleHomeProbValueAsArray) > 1:
        print("Today has a double header")
        for key in singleHomeProbValueAsArray:
            #print(key)
            # singleAwayProbValueAsDecimal = re.sub('[\[\]]', '', np.array_str(np.ndarray(key)))
            singleHomeProbValueAsPercentage = ("{:.0%}".format(float(key)))
    else:
        singleHomeProbValueAsDecimal = re.sub('[\[\]]', '', np.array_str(singleHomeProbValueAsArray))
        singleHomeProbValueAsPercentage = ("{:.0%}".format(float(singleHomeProbValueAsDecimal)))
    # --------



    # awayWinProb = contextMetrics.get("awayWinProbability", "-")
    # homeWinProb = contextMetrics.get("homeWinProbability", "-")
    awayProbPitcherId = game["teams"]["away"].get("probablePitcher", {}).get("id", None)
    if awayProbPitcherId:
        awayProbPitcherStr = game["teams"]["away"]["probablePitcher"]["fullName"]
        awayProbPitcherStats = next(
            (x.get("stats", [{}])[0].get("splits", [{}])[0].get("stat") for x in pitcherStats["people"] if
             x["id"] == awayProbPitcherId), None)
        if awayProbPitcherStats:
            awayProbPitcherStr += f" ({awayProbPitcherStats['era']})"  # Include other stats from this URL, if you want (others can be included in the fields param above, remove the fields param from the URL to see all available): https://statsapi.mlb.com/api/v1/people?personIds=545333&hydrate=stats(group=[pitching],type=[season],season=2020)&fields=people,id,fullName,stats,splits,stat,gamesPitched,gamesStarted,era,inningsPitched,wins,losses,saves,saveOpportunities,holds,blownSaves,whip,completeGames,shutouts
    else:
        awayProbPitcherStr = "TBD"
    homeProbPitcherId = game["teams"]["home"].get("probablePitcher", {}).get("id", None)
    if homeProbPitcherId:
        homeProbPitcherStr = game["teams"]["home"]["probablePitcher"]["fullName"]
        homeProbPitcherStats = next(
            (x.get("stats", [{}])[0].get("splits", [{}])[0].get("stat") for x in pitcherStats["people"] if
             x["id"] == homeProbPitcherId), None)
        if homeProbPitcherStats:
            homeProbPitcherStr += f" ({homeProbPitcherStats['era']})"  # Include other stats from this URL, if you want (others can be included in the fields param above, remove the fields param from the URL to see all available): https://statsapi.mlb.com/api/v1/people?personIds=545333&hydrate=stats(group=[pitching],type=[season],season=2020)&fields=people,id,fullName,stats,splits,stat,gamesPitched,gamesStarted,era,inningsPitched,wins,losses,saves,saveOpportunities,holds,blownSaves,whip,completeGames,shutouts
    else:
        homeProbPitcherStr = "TBD"
    table += (
        "|"
        f"{game['teams']['away']['team']['name']}"
        f" ({game['teams']['away']['leagueRecord']['wins']}-{game['teams']['away']['leagueRecord']['losses']}"
        f"{'-' + game['teams']['away']['leagueRecord']['ties'] if game['teams']['away']['leagueRecord'].get('ties') else ''})"
        " @ "
        f"{game['teams']['home']['team']['name']}"
        f" ({game['teams']['home']['leagueRecord']['wins']}-{game['teams']['home']['leagueRecord']['losses']}"
        f"{'-' + game['teams']['home']['leagueRecord']['ties'] if game['teams']['home']['leagueRecord'].get('ties') else ''})"
        "|"
        f"{awayProbPitcherStr} / {homeProbPitcherStr}"
        "|"
        f"{determine_if_doubleheader()} / {singleHomeProbValueAsPercentage}"  # Win probabilities - this does not always seem to be available.
        "|\n"
    )

print("Daily Pick'Em Thread | " + ans.strftime("%A") + ", " + date + " Game day")
print('---')
print("Welcome back to another Pick???Em thread!")
print("&nbsp;")
print(" ")
print("This post can be used to discuss your picks for " + date + ". If you have any feedback or suggestions on improving the thread further, drop a comment below or [message the moderators](https://www.reddit.com/message/compose?to=%2Fr%2FMLB_9Innings).")
print("&nbsp;")
print(" ")
print("Don't forget: picks must be submitted during the twelve-hour window before Noon EDT on game day, you can only make one selection per day, and missed days count as losses, so choose wisely and don't delay!  ")
print("&nbsp;")
print("  ")
print("*Games for " + ans.strftime("%A") + ", " + date +":*")
print("&nbsp;")
print("  ")
print(table)
print("&nbsp;")
print("  ")
print("1. All columns are Away / Home. Records are typically current as-of the time of posting, and do not contain the matchup results from the day of posting.  ")
print("2. A **bolded matchup** means that there is a chance of Precipitation greater than 35% in a non-domed stadium at the time of this post.  ")
print("3. An *italicized matchup* means that it is Game 2 of a doubleheader, which for Pick'Em purposes will not be applicable (only Game 1 is counted, but Game 2 is still included above so that you can be aware that Game 1 will be 7 innings, and that pitching management may be different than a non-doubleheader game day).  ")
print("4. Probable pitchers, stats, and weather data sourced from [mlb.com](https://www.mlb.com/) (via the [MLB-StatsAPI](https://pypi.org/project/MLB-StatsAPI/) and [Swish Analytics](https://swishanalytics.com/mlb/weather)).  ")
print("5. Estimated chance of winning percentages sourced from [FiveThirtyEight???s 2021 MLB Game Predictions](https://projects.fivethirtyeight.com/2021-mlb-predictions/games/), an [ELO-based](https://fivethirtyeight.com/features/how-our-mlb-predictions-work/), easy to understand ratings system.  ")
print("&nbsp;")
print("  ")
print("Details such as probable pitchers, winning odds, and match certainty are subject to change. Note that cancelled games (weather or otherwise) are automatically counted as correct guesses.  ")
print('*****')
print('*****')
print('*****')
print('Copy and Paste the above text into a Reddit post, and manually add in the projected Winning Percentages and any weather data.')
input('Press the Enter key to exit')