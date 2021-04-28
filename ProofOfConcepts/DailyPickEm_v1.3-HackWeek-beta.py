import statsapi
import datetime
import numpy as np
import pandas as pd
import re

FiveThirtyEightFrame = pd.read_csv('https://projects.fivethirtyeight.com/mlb-api/mlb_elo_latest.csv')

date = input("Enter date (e.g., 08/01/2021): ")

dt = date
month, day, year = (int(x) for x in dt.split('/'))    
ans = datetime.date(year, month, day)

#-----Adding FiveThirtyEight Apr.26
onlyTodayGamesFrame = FiveThirtyEightFrame[(FiveThirtyEightFrame["date"] == ans.strftime("%Y"+"-"+"%m"+"-"+"%d"))]
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
#-----

params = {
    "sportId": 1,
    "date": date,
    "hydrate": "probablePitcher(note)",
}
schedule = statsapi.get("schedule", params)
gamesThatDay = schedule["dates"][0]["games"]

probablePitcherIds = []
probablePitcherIds.extend([str(x['teams']['away'].get('probablePitcher', {}).get('id',None)) for x in gamesThatDay])
probablePitcherIds.extend([str(x['teams']['home'].get('probablePitcher', {}).get('id',None)) for x in gamesThatDay])
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
#----- More from Apr 26
    singleAwayProbRow = onlyTodayGamesFrame[(onlyTodayGamesFrame.date == ans.strftime("%Y"+"-"+"%m"+"-"+"%d")) & (onlyTodayGamesFrame.team2 == game["teams"]["away"]['team']['name'])]
    singleAwayProbValueAsArray = singleAwayProbRow['rating_prob2'].values

    if np.count_nonzero(singleAwayProbValueAsArray) > 1:
        print("Today has a double header")
        np.array_split(singleAwayProbValueAsArray, 1)
    else:
        singleAwayProbValueAsDecimal = re.sub('[\[\]]', '', np.array_str(singleAwayProbValueAsArray))
        singleAwayProbValueAsPercentage = ("{:.0%}".format(float(singleAwayProbValueAsDecimal)))

    singleHomeProbRow = onlyTodayGamesFrame[(onlyTodayGamesFrame.date == ans.strftime("%Y"+"-"+"%m"+"-"+"%d")) & (onlyTodayGamesFrame.team1 == game["teams"]["home"]['team']['name'])]
    singleHomeProbValueAsArray = singleHomeProbRow['rating_prob1'].values
    
    if np.count_nonzero(singleAwayProbValueAsArray) > 1:
        print("Today has a double header")
        np.array_split(singleAwayProbValueAsArray, 1)
    else:
        singleHomeProbValueAsDecimal = re.sub('[\[\]]', '', np.array_str(singleHomeProbValueAsArray))
        singleHomeProbValueAsPercentage = ("{:.0%}".format(float(singleHomeProbValueAsDecimal)))
#--------
    #awayWinProb = contextMetrics.get("awayWinProbability", "-")
    #homeWinProb = contextMetrics.get("homeWinProbability", "-")
    awayProbPitcherId = game["teams"]["away"].get("probablePitcher", {}).get("id", None)
    if awayProbPitcherId:
        awayProbPitcherStr = game["teams"]["away"]["probablePitcher"]["fullName"]
        awayProbPitcherStats = next((x.get("stats", [{}])[0].get("splits", [{}])[0].get("stat") for x in pitcherStats["people"] if x["id"] == awayProbPitcherId), None)
        if awayProbPitcherStats:
            awayProbPitcherStr += f" ({awayProbPitcherStats['era']})"  # Include other stats from this URL, if you want (others can be included in the fields param above, remove the fields param from the URL to see all available): https://statsapi.mlb.com/api/v1/people?personIds=545333&hydrate=stats(group=[pitching],type=[season],season=2020)&fields=people,id,fullName,stats,splits,stat,gamesPitched,gamesStarted,era,inningsPitched,wins,losses,saves,saveOpportunities,holds,blownSaves,whip,completeGames,shutouts
    else:
        awayProbPitcherStr = "TBD"
    homeProbPitcherId = game["teams"]["home"].get("probablePitcher", {}).get("id", None)
    if homeProbPitcherId:
        homeProbPitcherStr = game["teams"]["home"]["probablePitcher"]["fullName"]
        homeProbPitcherStats = next((x.get("stats", [{}])[0].get("splits", [{}])[0].get("stat") for x in pitcherStats["people"] if x["id"] == homeProbPitcherId), None)
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
        f"{singleAwayProbValueAsPercentage} / {singleHomeProbValueAsPercentage}"  # Win probabilities - this does not always seem to be available.
        "|\n"
    )

    
print("*Games for " + ans.strftime("%A") + ", " + date +":*")
print(table)