#This program was written to test pulling in stadium data (manually entered into a JSON) into a Pandas Dataframe, 
#then select specific information about particular stadiums based on a variable. (In this case, the variable is 
#selecting the Chicago White Sox and Chicago Cubs, but ideally this would be adjusted based on whichever teams are
#the home team on a given date.

import requests
import json
import pandas as pd
import numpy as np

stadiumsUrl = "https://raw.githubusercontent.com/Ikestrman/SourceFiles/main/ManualJSON-Stadiums.json"

stadiumsResponse = requests.get(stadiumsUrl)
stadiumsData = json.loads(stadiumsResponse.text)
###Note: This creates a dict (stadiumsData) with a key (teams) with all other information included as the value.

stadiumsDf = pd.json_normalize(data=stadiumsData['teams'])

stadiumsDf.columns

homeTeamsThatDay = ['Chicago Cubs', 'Chicago White Sox']

table = "This is a table:"

for team in homeTeamsThatDay:
    latitudes = stadiumsDf.loc[stadiumsDf['Name'].isin(homeTeamsThatDay)]
    #longitudes = stadiumsDf[team]['Metadata.Long']
    
    table += (
        "\n|"
        f"{latitudes}"
        "|\n"
    )

print(table)

###Example Output: 

#This is a table:
#|                Name      Metadata.ballpark  Metadata.Lat  Metadata.Long     Metadata.Impacted by Rain  
#4       Chicago Cubs          Wrigley Field     41.948574     -87.655333     True   
#5  Chicago White Sox  Guaranteed Rate Field     41.830166     -87.633806     True  ||