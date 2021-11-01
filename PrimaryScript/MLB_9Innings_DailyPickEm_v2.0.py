firstDoubleHeaderAwayProb = 0
secondDoubleHeaderAwayProb = 0
firstDoubleHeaderHomeProb = 0
secondDoubleHeaderHomeProb = 0
singleAwayProbValueAsPercentage = 0

def PickEmAsAFunction(date):
    #All line breaks have been manually added as '<br>' tags throughout this script, which is only necessary if this is being rendered in HTML (as is the case with the Flask app)

    import sys
    import io
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    import statsapi
    import datetime
    import numpy as np
    import pandas as pd
    import re
    import requests
    import json

    FiveThirtyEightFrame = pd.read_csv('https://projects.fivethirtyeight.com/mlb-api/mlb_elo_latest.csv')

    print('<strong>Instructions: Any non-bolded text below will be used for the Reddit post unless otherwise noted. See other specific directions below.</strong><br>')
    print('<h3>Title:</h3>')

    dt = date
    year, month, day = (int(x) for x in dt.split('-'))
    ans = datetime.date(year, month, day)
    dtFormatted = (str(month).zfill(2) + "/" + str(day).zfill(2) + "/" + str(year))

    onlyTodayGamesFrame = FiveThirtyEightFrame[
        (FiveThirtyEightFrame["date"] == ans.strftime("%Y" + "-" + "%m" + "-" + "%d"))]
    onlyTodayGamesFrame = onlyTodayGamesFrame[['date', 'team1', 'team2', 'rating_prob1', 'rating_prob2']]

    teamAbbreviationReplacers = {
        'ARI': 'Arizona Diamondbacks', 'ATL': 'Atlanta Braves', 'BAL': 'Baltimore Orioles', 'BOS': 'Boston Red Sox',
        'CHC': 'Chicago Cubs', 'CHW': 'Chicago White Sox', 'CIN': 'Cincinnati Reds', 'CLE': 'Cleveland Indians',
        'COL': 'Colorado Rockies', 'DET': 'Detroit Tigers', 'FLA': 'Miami Marlins', 'HOU': 'Houston Astros',
        'KCR': 'Kansas City Royals', 'ANA': 'Los Angeles Angels', 'LAD': 'Los Angeles Dodgers', 'MIL': 'Milwaukee Brewers',
        'MIN': 'Minnesota Twins', 'NYM': 'New York Mets', 'NYY': 'New York Yankees', 'OAK': 'Oakland Athletics',
        'PHI': 'Philadelphia Phillies', 'PIT': 'Pittsburgh Pirates', 'SDP': 'San Diego Padres', 'SFG': 'San Francisco Giants',
        'SEA': 'Seattle Mariners', 'STL': 'St. Louis Cardinals', 'TBD': 'Tampa Bay Rays', 'TEX': 'Texas Rangers',
        'TOR': 'Toronto Blue Jays', 'WSN': 'Washington Nationals'}

    teamCityRemovedReplacers = {
        'Arizona Diamondbacks': 'Diamondbacks', 'Atlanta Braves': 'Braves', 'Baltimore Orioles': 'Orioles', 'Boston Red Sox': 'Red Sox',
        'Chicago Cubs': 'Cubs', 'Chicago White Sox': 'White Sox', 'Cincinnati Reds': 'Reds', 'Cleveland Indians': 'Indians',
        'Colorado Rockies': 'Rockies', 'Detroit Tigers': 'Tigers', 'Miami Marlins': 'Marlins', 'Houston Astros': 'Astros',
        'Kansas City Royals': 'Royals', 'Los Angeles Angels': 'Angels', 'Los Angeles Dodgers': 'Dodgers', 'Milwaukee Brewers': 'Brewers',
        'Minnesota Twins': 'Twins', 'New York Mets': 'Mets', 'New York Yankees': 'Yankees', 'Oakland Athletics': 'Athletics',
        'Philadelphia Phillies': 'Phillies', 'Pittsburgh Pirates': 'Pirates', 'San Diego Padres': 'Padres', 'San Francisco Giants': 'Giants',
        'Seattle Mariners': 'Mariners', 'St. Louis Cardinals': 'Cardinals', 'Tampa Bay Rays': 'Rays', 'Texas Rangers': 'Rangers',
        'Toronto Blue Jays': 'Blue Jays', 'Washington Nationals': 'Nationals'}

    onlyTodayGamesFrame['team1'].replace(teamAbbreviationReplacers, inplace=True)
    onlyTodayGamesFrame['team2'].replace(teamAbbreviationReplacers, inplace=True)

    # Initially creating variables (as non-None) so they exist before they are called in a function
    global firstDoubleHeaderAwayProb
    global secondDoubleHeaderAwayProb
    global firstDoubleHeaderHomeProb
    global secondDoubleHeaderHomeProb
    global singleAwayProbValueAsPercentage

    # ----
    def determine_prob_if_doubleheader_away():
        if singleAwayProbValueAsPercentage is not None:
            return singleAwayProbValueAsPercentage
        else:
            global firstDoubleHeaderAwayProb
            global secondDoubleHeaderAwayProb
            if firstDoubleHeaderAwayProb is not None:
                print("<h4>Today has a double header</h4><br>")
                firstDoubleHeaderAwayProbProcessed = firstDoubleHeaderAwayProb
                firstDoubleHeaderAwayProbAsPercentage = ("{:.0%}".format(float(firstDoubleHeaderAwayProbProcessed)))
                firstDoubleHeaderAwayProb = None
                return firstDoubleHeaderAwayProbAsPercentage
            else:
                if firstDoubleHeaderAwayProb is None and secondDoubleHeaderAwayProb != 0:
                    secondDoubleHeaderAwayProbAsPercentage = ("{:.0%}".format(float(secondDoubleHeaderAwayProb)))
                    firstDoubleHeaderAwayProb = 0
                    secondDoubleHeaderAwayProb = 0
                    return secondDoubleHeaderAwayProbAsPercentage
                else:
                    pass

    def determine_prob_if_doubleheader_home():
        if singleHomeProbValueAsPercentage is not None:
            return singleHomeProbValueAsPercentage
        else:
            global firstDoubleHeaderHomeProb
            global secondDoubleHeaderHomeProb
            if firstDoubleHeaderHomeProb is not None:
                firstDoubleHeaderHomeProbProcessed = firstDoubleHeaderHomeProb
                firstDoubleHeaderHomeProbAsPercentage = ("{:.0%}".format(float(firstDoubleHeaderHomeProbProcessed)))
                firstDoubleHeaderHomeProb = None
                return firstDoubleHeaderHomeProbAsPercentage
            else:
                secondDoubleHeaderHomeProbAsPercentage = ("{:.0%}".format(float(secondDoubleHeaderHomeProb)))
                firstDoubleHeaderHomeProb = 0
                secondDoubleHeaderHomeProb = 0
                return secondDoubleHeaderHomeProbAsPercentage
    # ----
    def round_start_time(convertedTimestamp):
        functionTimeStamp = convertedTimestamp

        startTimeAfterHour = (functionTimeStamp % 3600)

        checkForGameStartRounding = functionTimeStamp % 3600

        if checkForGameStartRounding < 1800:
            roundedGameStartTime = functionTimeStamp - (functionTimeStamp % 3600)
        else:
            roundedGameStartTime = (3600 - checkForGameStartRounding) + functionTimeStamp
        
        return roundedGameStartTime
    # ----
    def get_single_city_weather(weatherUrl, StartTime, TimePlusOne, TimePlusTwo, HomeTeamName): 
        singleCityFunctionUrl = weatherUrl
        singleCityWeatherResponse = requests.get(singleCityFunctionUrl)
        singleCityFullWeatherData = singleCityWeatherResponse.json()
        singleTeamHourStart = 0
        singleTeamHourPlusOne = 0
        singleTeamHourPlusTwo = 0

        for hour in singleCityFullWeatherData['hourly']:
            if hour['dt'] == StartTime:
                singleTeamHourStart = float(hour['pop'])
                singleTeamHourStartPercent = "{:.0%}".format(hour['pop'])
            else:
                pass

            if hour['dt'] == TimePlusOne:
                singleTeamHourPlusOne = float(hour['pop'])
                singleTeamHourPlusOnePercent = "{:.0%}".format(hour['pop'])
            else:
                pass

            if hour['dt'] == TimePlusTwo:
                singleTeamHourPlusTwo = float(hour['pop'])
                singleTeamHourPlusTwoPercent = "{:.0%}".format(hour['pop'])
            else:
                pass

        if (singleTeamHourStart + singleTeamHourPlusOne + singleTeamHourPlusTwo) > 1.05: #Only takes teams with an average that will be greater than 35%
            singleTeamHourlyPrecipAverage = ((singleTeamHourStart + singleTeamHourPlusOne + singleTeamHourPlusTwo)/3)
            singleTeamHourlyPrecipAveragePercent = "{:.0%}".format(singleTeamHourlyPrecipAverage)
            print(HomeTeamName + ": " + str(singleTeamHourlyPrecipAveragePercent))
            print(" --- Hourly Breakdown: " + singleTeamHourStartPercent + ", " + singleTeamHourPlusOnePercent + ", " + singleTeamHourPlusTwoPercent)
            print("<br>")
        else:
            pass

    params = {
        "sportId": 1,
        "date": date,
        "hydrate": "probablePitcher(note)",
    }
    schedule = statsapi.get("schedule", params)
    
    try: #This try/except will check to verify that day's scheduled is not an empty list (i.e., no games); an empty list will terminate the script gracefully noting the lack of games
        gamesThatDay = schedule["dates"][0]["games"]
    except IndexError as e: 
        return str("There are no games scheduled for the selected date. Please return to the /home page and choose a different game day (upcoming games can be perused on mlb.com).")

    probablePitcherIds = []
    probablePitcherIds.extend([str(x['teams']['away'].get('probablePitcher', {}).get('id', None)) for x in gamesThatDay])
    probablePitcherIds.extend([str(x['teams']['home'].get('probablePitcher', {}).get('id', None)) for x in gamesThatDay])
    probablePitcherIds = [x for x in probablePitcherIds if x != "None"]

    peopleParams = {
        "personIds": ",".join(probablePitcherIds),
        "hydrate": f"stats(group=[pitching],type=[season],season=2021)",
        "fields": "people,id,fullName,stats,splits,stat,gamesPitched,gamesStarted,era,inningsPitched,wins,losses,saves,saveOpportunities,holds,blownSaves,whip,completeGames,shutouts",
    }
    try: #This try/except will allow the script to keep processing if the statsapi.get("people", peopleParams) were to return a 400 (no known people info that day at the endpoint) instead of terminating the script
        pitcherStats = statsapi.get("people", peopleParams)
    except ValueError as e:
        pitcherStats = {}

    stadiumsUrl = "https://raw.githubusercontent.com/Ikestrman/SourceFiles/main/ManualJSON-Stadiums.json"
    stadiumsResponse = requests.get(stadiumsUrl)
    stadiumsData = json.loads(stadiumsResponse.text)
    stadiumsDf = pd.json_normalize(data=stadiumsData['teams'])
    stadiumsDf["StartTime"] = np.nan
    stadiumsDf["weatherUrl"] = np.nan
    api_key = "REDACTED"

    table = "|**Matchup and Team Records**|**Probable Pitchers (Season ERA)**|**Estimated Win Probability**|<br>"
    table += "|:-----|:-----|:--|<br>"
    for game in gamesThatDay:
        try:
            contextMetrics = statsapi.get("game_contextMetrics", {"gamePk": game["gamePk"]})
        except ValueError as e:
            contextMetrics = {}

        singleAwayProbRow = onlyTodayGamesFrame[
            (onlyTodayGamesFrame.date == ans.strftime("%Y" + "-" + "%m" + "-" + "%d")) & (
                        onlyTodayGamesFrame.team2 == game["teams"]["away"]['team']['name'])]
        singleAwayProbValueAsArray = singleAwayProbRow['rating_prob2'].values

        if np.count_nonzero(singleAwayProbValueAsArray) > 1:
            for x in np.nditer(singleAwayProbValueAsArray, flags=['external_loop']):
                if firstDoubleHeaderAwayProb is not None:
                    firstDoubleHeaderAwayProb = x[1]
                else:
                    pass

                secondDoubleHeaderAwayProb = x[0]
                singleAwayProbValueAsPercentage = None
        else:
            singleAwayProbValueAsDecimal = re.sub('[\[\]]', '', np.array_str(singleAwayProbValueAsArray))
            try:
                singleAwayProbValueAsPercentage = ("{:.0%}".format(float(singleAwayProbValueAsDecimal)))
            except ValueError as e:
                singleAwayProbValueAsPercentage = "Postponed?"

        singleHomeProbRow = onlyTodayGamesFrame[
            (onlyTodayGamesFrame.date == ans.strftime("%Y" + "-" + "%m" + "-" + "%d")) & (
                        onlyTodayGamesFrame.team1 == game["teams"]["home"]['team']['name'])]
        singleHomeProbValueAsArray = singleHomeProbRow['rating_prob1'].values

        if np.count_nonzero(singleHomeProbValueAsArray) > 1:
            for x in np.nditer(singleHomeProbValueAsArray, flags=['external_loop']):
                if firstDoubleHeaderHomeProb is not None:
                    firstDoubleHeaderHomeProb = x[1]
                else:
                    pass

                secondDoubleHeaderHomeProb = x[0]
                singleHomeProbValueAsPercentage = None
        else:
            singleHomeProbValueAsDecimal = re.sub('[\[\]]', '', np.array_str(singleHomeProbValueAsArray))
            try:
                singleHomeProbValueAsPercentage = ("{:.0%}".format(float(singleHomeProbValueAsDecimal)))
            except ValueError as e:
                singleHomeProbValueAsPercentage = "Postponed?"

        awayProbPitcherId = game["teams"]["away"].get("probablePitcher", {}).get("id", None)
        if awayProbPitcherId:
            awayProbPitcherStr = game["teams"]["away"]["probablePitcher"]["fullName"]
            awayProbPitcherStats = next(
                (x.get("stats", [{}])[0].get("splits", [{}])[0].get("stat") for x in pitcherStats["people"] if
                 x["id"] == awayProbPitcherId), None)
            if awayProbPitcherStats:
                awayProbPitcherStr += f" ({awayProbPitcherStats['era']})"
        else:
            awayProbPitcherStr = "TBD"
        homeProbPitcherId = game["teams"]["home"].get("probablePitcher", {}).get("id", None)
        if homeProbPitcherId:
            homeProbPitcherStr = game["teams"]["home"]["probablePitcher"]["fullName"]
            homeProbPitcherStats = next(
                (x.get("stats", [{}])[0].get("splits", [{}])[0].get("stat") for x in pitcherStats["people"] if
                 x["id"] == homeProbPitcherId), None)
            if homeProbPitcherStats:
                homeProbPitcherStr += f" ({homeProbPitcherStats['era']})"
        else:
            homeProbPitcherStr = "TBD"

        #Section added to prep addition of weather script
        homeTeamName = game["teams"]["home"]["team"]["name"]
        singleGameStartTime = game["gameDate"]

        # Extract values and convert to UTC time; matching OpenWeatherMap API formatting 
        utc_singleGameStartTime = datetime.datetime.strptime(singleGameStartTime, '%Y-%m-%dT%H:%M:%SZ')
        convertedTimestamp = int((utc_singleGameStartTime - datetime.datetime(1970, 1, 1)).total_seconds())
        convertedRoundedTimestamp = round_start_time(convertedTimestamp)

        #Populate stadium json dataframe with the rounded timestamp, plus 1 and 2 hours after the rounded game start time
        stadiumsDf.loc[stadiumsDf["Name"] == homeTeamName, 'StartTime'] = convertedRoundedTimestamp
        stadiumsDf["Start+1hr"] = stadiumsDf["StartTime"] + 3600
        stadiumsDf["Start+2hr"] = stadiumsDf["StartTime"] + 7200

        stadiumsDf.loc[stadiumsDf["Name"] == homeTeamName, 'weatherUrl'] = 'https://api.openweathermap.org/data/2.5/onecall?lat=' + stadiumsDf["Metadata.Lat"].astype(str) + '&lon=' + stadiumsDf["Metadata.Long"].astype(str) + '&exclude=current,daily,minutely&appid=' + str(api_key)

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
            f"{determine_prob_if_doubleheader_away()} / {determine_prob_if_doubleheader_home()}"  
            "|<br>"
        )

    ###Poll Preparation###
    #Get the 5 highest home and away team probabilities
    onlyTodayGamesFrameSorted = onlyTodayGamesFrame.nlargest(5, ['rating_prob1'])
    onlyTodayGamesFrameAwaySorted = onlyTodayGamesFrame.nlargest(5, ['rating_prob2'])

    #Swap probability and team columns of away frame (in preparation for merge)
    onlyTodayGamesFrameAwaySorted[['rating_prob1','rating_prob2']] = onlyTodayGamesFrameAwaySorted[['rating_prob2','rating_prob1']]
    onlyTodayGamesFrameAwaySorted[['team1','team2']] = onlyTodayGamesFrameAwaySorted[['team2','team1']]

    #Combine home and away heaviest favorites
    allSortedFrames = [onlyTodayGamesFrameSorted, onlyTodayGamesFrameAwaySorted]
    combinedTodayGamesFrameSorted = pd.concat(allSortedFrames)

    #Clean column and team names, remove cities
    combinedTodayGamesFrameSorted = combinedTodayGamesFrameSorted.rename(columns={'team1': "Favorite", "team2": 'Underdog', 'rating_prob1': 'FavoriteProb', 'rating_prob2': 'UnderdogProb'})
    combinedTodayGamesFrameSorted['Favorite'].replace(teamCityRemovedReplacers, inplace=True)
    combinedTodayGamesFrameSorted['Underdog'].replace(teamCityRemovedReplacers, inplace=True)

    #Sort by heaviest favorites
    combinedTodayGamesFrameSorted = combinedTodayGamesFrameSorted.sort_values(by=['FavoriteProb'],ascending=False)

    ###Post Body Preparation ###
    print("Daily Pick'Em Thread | " + ans.strftime("%A") + ", " + dtFormatted + " Game day<br><br>")
    print('<h3>Post Body:</h3>Welcome back to another Pick’Em thread!<br>&nbsp;  <br>')
    print("This post can be used to discuss your picks for " + dtFormatted + ". If you have any feedback or suggestions on improving the thread further, drop a comment below or [message the moderators](https://www.reddit.com/message/compose?to=%2Fr%2FMLB_9Innings).  <br>&nbsp;  <br>")
    print("Don't forget: picks must be submitted during the twelve-hour window before Noon EDT on game day, you can only make one selection per day, and missed days count as losses, so choose wisely and don't delay!  <br>&nbsp;  <br>")
    print("*Games for " + ans.strftime("%A") + ", " + dtFormatted +":*  <br>&nbsp;  <br>")
    print(table)
    print("&nbsp;  <br>")
    print("1. All columns are Away / Home. Records are typically current as-of the time of posting, and do not always contain the matchup results from the day of posting.  <br>")
    print("2. A **bolded matchup** means that there is a chance of Precipitation greater than 35% in a non-domed stadium at the time of this post.  <br>")
    print("3. An *italicized matchup* means that it is Game 2 of a doubleheader, which for Pick'Em purposes will not be applicable (only Game 1 is counted, but Game 2 is still included above so that you can be aware that Game 1 will be 7 innings, and that pitching management may be different than a non-doubleheader game day).  <br>")
    print("4. Probable pitchers and stats sourced from [mlb.com](https://www.mlb.com/) (via the [MLB-StatsAPI](https://pypi.org/project/MLB-StatsAPI/)); weather data soured from the [OpenWeather One Call API](https://openweathermap.org/api/one-call-api).  <br>")
    print("5. Estimated chance of winning percentages sourced from [FiveThirtyEight’s 2021 MLB Game Predictions](https://projects.fivethirtyeight.com/2021-mlb-predictions/games/), an [ELO-based](https://fivethirtyeight.com/features/how-our-mlb-predictions-work/), easy to understand ratings system.  <br>&nbsp;  <br>")
    print("Details such as probable pitchers, winning odds, and match certainty are subject to change. Note that cancelled games (weather or otherwise) are automatically counted as correct guesses.  <br><br>")
    print('---<br><strong>Copy and paste the above text into a the post body (using markdown mode), the below choices into the poll, and manually bold teams listed in the weather report data below.</strong><h3>Poll Options, with heaviest 538 favorites ranked first (watch for doubleheaders):</h3>')

    ###Poll Numbers###
    for index, row in combinedTodayGamesFrameSorted.iterrows():
        print(row['Favorite'] + ' over ' + row['Underdog'] + "<br>")

    print("Other/I just want the results -- discuss in the comments!")

    ###Weather Values###
    homeTeamOnlyFrame = stadiumsDf[stadiumsDf["weatherUrl"].notna()]
    homeTeamOnlyFrame = homeTeamOnlyFrame.rename(columns={'Metadata.Impacted by Rain': 'RainImpacts'})

    print("<h3>Teams with potential weather delays:</h3>")
    for index, row in homeTeamOnlyFrame.iterrows():
        if row["RainImpacts"] == True:
            get_single_city_weather(row["weatherUrl"], row["StartTime"], row["Start+1hr"], row["Start+2hr"], row["Name"])
        else:
            pass
    print("<strong>If there are no teams with percentages directly above this line, no matchups need to be bolded. Note: This will only display values if matchups are < 48 hours away.</strong>")
    
    #Putting the old stream back in place (first line), returning a string containing the entire contents of the buffer (second line) before printing, closing, and returning the str for main.py
    sys.stdout = old_stdout
    whatWasPrinted = buffer.getvalue()
    buffer.close()
    return whatWasPrinted

#PickEmAsAFunction()

if __name__ == "__main__":
    PickEmAsAFunction()