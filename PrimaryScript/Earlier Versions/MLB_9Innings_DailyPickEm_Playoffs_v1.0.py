import statsapi
import datetime

date = input("Enter date (e.g., 08/01/2020): ")
#presentThread = input("Paste in the link for today's Pick'Em game thread: ")
print('*****')
print('*****processing...*****')
print('*****')
print('Title:')
print('---')

dt = date
month, day, year = (int(x) for x in dt.split('/'))    
ans = datetime.date(year, month, day)

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
    "hydrate": f"stats(group=[pitching],type=[season],season=2020)",
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
    awayWinProb = contextMetrics.get("awayWinProbability", "-")
    homeWinProb = contextMetrics.get("homeWinProbability", "-")
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
        f"{awayWinProb}% / {homeWinProb}%"  # Win probabilities - this does not always seem to be available.
        "|\n"
    )

    
print("Daily Pick'Em Thread | " + ans.strftime("%A") + ", " + date + " Game day | Playoff Edition")
print('---')
print("Welcome back to another playoff edition Pick’Em thread!")
print("&nbsp;")
print(" ")
print("This post can be used to discuss your picks for " + date + ". If you have any feedback or suggestions on improving the thread further, drop a comment below or [message the moderators](https://www.reddit.com/message/compose?to=%2Fr%2FMLB_9Innings).")
print("&nbsp;")
print(" ")
print("Here's the [2020 Playoff Bracket](https://imgur.com/a/TpZ5ovI) -- make sure to select a game **in each league** (if both AL and NL games are being played), as you can pick one from each and the rewards from correctly chosen playoff games are cumulative rather than streak-based.  ")
print("&nbsp;")
print("  ")
print("Don't forget: picks must be submitted during the twelve-hour window before Noon EDT on game day, so choose wisely and don't delay!  ")
print("&nbsp;")
print("  ")
print("*Games for " + ans.strftime("%A") + ", " + date +":*")
print("  ")
print("## National League:  ")
print("  ")
print("|**Matchup and Team Records**|**Probable Pitchers (Season ERA)**|**Estimated Win Probability**|")
print("|:-----|:-----|:--|")
print("&nbsp;")
print("  ")
print("## American League:  ")
print("  ")
print(table)
print("&nbsp;")
print("  ")
print("1. All columns are Away / Home. Records are current as-of the time of posting, and do not contain the current day’s matchup results.  ")
print("2. A **bolded matchup** means that there is a chance of Precipitation greater than 35% in a non-domed stadium at the time of this post.  ")
print("3. An *italicized matchup* means that the game will only be played if necessary, pending the results of a game not yet complete at the time of this post.  ")
print("4. Probable pitchers, stats, and weather data sourced from [mlb.com](https://www.mlb.com/) (via the [MLB-StatsAPI](https://pypi.org/project/MLB-StatsAPI/) and [Swish Analytics](https://swishanalytics.com/mlb/weather)).  ")
print("5. Estimated chance of winning percentages sourced from [FiveThirtyEight’s 2020 MLB Game Predictions](https://projects.fivethirtyeight.com/2020-mlb-predictions/games/).  ")
print("6. Playoff bracket used with permission from u/DrBadassPhD.")
print("&nbsp;")
print("  ")
print("Our thoughts go out to all individuals affected by the COVID-19 pandemic, and we hope for full recoveries for the players and staff infected. We will try to include updates as information is made known; however, there is obviously a great deal of uncertainty, so details such as probable pitchers, winning odds, and match certainty are (even more than usual) subject to change. Note that cancelled games (weather or other reasons) are automatically counted as correct guesses, but not all games have been included as available selections (due to cancellations and late-rescheduling).  ")
#print("&nbsp;")
#print("  ")
#print("For discussion regarding today's in-progress games, see [yesterday's Pick’Em thread](" + presentThread + ").  ")
print('*****')
print('*****')
print('*****')
print('Copy and Paste the above text into a Reddit post, and manually add in the projected Winning Percentages and any weather data.')
input('Press the Enter key to exit')