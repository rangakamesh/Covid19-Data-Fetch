import pymongo
from github import Github
import pandas as pd
import json
import numpy as np
import datetime as ddt
from datetime import datetime

# To interact with azure
import logging
import os


def fetchFromRepository():

  # Get the setting named 'myAppSetting'
  MongoDB = os.environ["MONGODB"]

  # Connecting and authenticating to GitHub
  # No authentication provided, this just limits the number of calls made per hour
  # If you call the api very often use g=Github('your-personal-access-token')
  g= Github()

  # Fetching the csv files contatining the COVID-19 raw data from the source
  # Data Sourced BY : JHU CSSE COVID-19 Data
  # Data Source URL : https://github.com/CSSEGISandData/COVID-19
  repo = g.get_repo("CSSEGISandData/COVID-19")
  cont = repo.get_contents("/csse_covid_19_data/csse_covid_19_daily_reports")
  all_files = []
  for i in range(1,len(cont)):
    url = cont[i].download_url
    #avoiding data before 31st March 2020 since they were not formatted as expected
    if (".csv" in url) and (datetime(int(url[118:122]),int(url[112:114]),int(url[115:117])) > datetime(2020,3,31)):
      all_files.append(url)

  ## Reading the csv files into a pandas data frame
  li = []
  for filename in all_files:
    if ".csv" in filename:
      df = pd.read_csv(filename, index_col=None, header=0)
      li.append(df)
  CovidData = pd.concat(li, axis=0, ignore_index=True)

  #Data Pre-Processing 
  CovidData['Last_Update']= pd.to_datetime(CovidData['Last_Update'])
  CovidData['Incident_Rate'] = CovidData['Incident_Rate'].fillna(CovidData['Incidence_Rate'])
  CovidData['Incident_Rate'] = CovidData['Incident_Rate'].fillna(0)
  CovidData['Case_Fatality_Ratio'] = CovidData['Case_Fatality_Ratio'].fillna(CovidData['Case-Fatality_Ratio'])

  # Extract the Latitude and Longitude
  Lat_Long = pd.DataFrame()
  Lat_Long["Country"] = CovidData["Country_Region"]
  Lat_Long["Lat"] = CovidData["Lat"]
  Lat_Long["Long_"] = CovidData["Long_"]
  Lat_Long = Lat_Long.groupby(["Country"])
  Lat_Long = Lat_Long.first()

  CovidData = CovidData.drop(['FIPS','Admin2','Lat','Long_','Incidence_Rate', 'Case-Fatality_Ratio'], axis=1)

  # Countries
  CountryList = CovidData.Country_Region.unique()

  #Cooking the json objects
  country_wise = []
  for country_value in CountryList:
    country_filter = CovidData[CovidData['Country_Region']==country_value]
    country_filter['Last_Update'] = country_filter['Last_Update'].dt.date
    country_filter = country_filter.groupby(['Country_Region','Last_Update'],as_index=False).agg({'Confirmed': 'sum', 'Deaths': 'sum',  'Recovered': 'sum','Active': 'sum','Incident_Rate': 'first'})

    num = country_filter.loc[:,['Confirmed','Deaths','Recovered']]
    difference = num.diff(axis=0)
    difference['Last'] = country_filter['Last_Update']
    country_filter["New_Cases"]=difference["Confirmed"]
    country_filter["New_Deaths"]=difference["Deaths"]
    country_filter["New_Recoveries"]=difference["Recovered"]

    country_filter["Case_Fatality_Rate"]=country_filter["Deaths"]/country_filter["Confirmed"]
    country_filter["Case_Fatality_Rate"]=country_filter["Case_Fatality_Rate"].replace([np.inf, -np.inf], 0)
    country_filter["Case_Fatality_Rate"]=country_filter["Case_Fatality_Rate"].replace(np.nan, 0)

    country_filter['Last_Update'] = pd.to_datetime(country_filter['Last_Update'])
    country_filter['Last_Update'] = pd.to_datetime(country_filter['Last_Update']).dt.tz_localize('US/Eastern').dt.tz_convert('US/Eastern')


    country_filter['Incident_Rate'] = country_filter['Incident_Rate'].round(4)
    country_filter['Case_Fatality_Rate'] = country_filter['Case_Fatality_Rate'].round(4)
    country_filter.loc[0,['New_Cases','New_Deaths','New_Recoveries']]=0

    temp_json = country_filter.to_dict(orient='records')
    pack_jsons = {
        "country":country_value,
        "latitude" : Lat_Long.loc[country_value].Lat,
        "longitude" : Lat_Long.loc[country_value].Long_,
        "object":temp_json
    }
    country_wise.append(pack_jsons)

  # Connecting to the mongo db
  client = pymongo.MongoClient(MongoDB)
  db = client["covid"]
  col = db["countrywise"]
  col.drop()
  db = client["covid"]
  col = db["countrywise"]

  #inserting the bulk object to db
  insert_return = col.insert_many(country_wise)

  #return to whoever expects
  return 0