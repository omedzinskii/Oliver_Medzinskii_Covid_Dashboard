#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

from datetime import datetime, timedelta, date
import json
import pandas as pd
import more_itertools as mit
from uk_covid19 import Cov19API
from app.logger import logging

from app.covid_news_handling import update_news

#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Preliminary Functions -------------------------------------------------
#---------------------------------------------------------------------------------------------------

#Covid 19 static test data file, accessed from config.json and assigned to variable
try:
    with open("app/static/json/config.json", encoding="utf-8") as config_file:
        test_data_file = json.load(config_file)
        logging.info(f"Trying to load test file:{test_data_file}")
        covid_19_test_data = test_data_file.get("test_data_file")
except:
    logging.error("Exception occurred", exc_info=True)
#---------------------------------------------------------------------------------------------------

#Function to ingest file and returns a list of strings for the rows in the file
def parse_csv_data(csv_filename):
    """
    Summary of parse_csv_data

    Parameters:
        -   csv_filename (test csv file found in config.json)

        The file is converted to a dataframe
        returns a list of stings for the rows in the file
    """

    #Converts file to dataframe and then returns a list of strings for the rows in the file
    data_frame_1 = pd.read_csv(csv_filename)
    logging.info("File has been ingested")
    return [data_frame_1.columns.values] + data_frame_1.values.tolist()
#---------------------------------------------------------------------------------------------------

#Function to process data stored in a file and extract required data metrics as a tuple
def process_covid_csv_data(covid_csv_data):

    """
    Summary of process_covid_csv_data

    Parameters:
        -   covid_csv_data (csv data)

        The data is converted to a dataframe

        Data from the data frame can then be extracted using pandas module

        returns a tuple of 3 data points
        (last7days_cases, current_hospital_cases, total_deaths)

    """

    #Convert data into dataframe and remove headings
    data_frame_2 = pd.DataFrame(covid_csv_data[1:],columns=covid_csv_data[0])
    #-----------------------------------------------------------------------------------------------
    #Access column with new cases data and filter for the top 9 rows, as these include data for the
    #last 7 days, We disregard the first data entry as its incomplete
    new_cases_column = data_frame_2.iloc[2:9]["newCasesBySpecimenDate"]
    #Using pandas '.sum()' function we add all values ('.sum' function automatically ignores NaN
    #values)
    last7days_cases = new_cases_column.sum()
    #----------------------------------------------------------------------------------------------
    #Using pandas to find the current number of hospital cases, which is the first value in the
    #hospitalCases column
    current_hospital_cases = data_frame_2.iloc[0]['hospitalCases']
    #----------------------------------------------------------------------------------------------
    #Access column with cumulative deaths to find total deaths
    total_deaths_column = data_frame_2["cumDailyNsoDeathsByDeathDate"]
    #Using first_valid_index to find the top cumulative death value as this will be the total
    #number of deaths to date
    total_deaths = total_deaths_column.loc[total_deaths_column.first_valid_index()]
    #----------------------------------------------------------------------------------------------
    #Return a tuple of the 3 data metrics we wanted to extract
    logging.info("Data has been extracted")
    return last7days_cases, current_hospital_cases, total_deaths

#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Preliminary Functions -------------------------------------------------
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Main Specification Project---------------------------------------------
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Data Caching ----------------------------------------------------------
#---------------------------------------------------------------------------------------------------

#Create a cache for requested data from the COVID API, this stops the app from calling the COVID API
#request at every refresh of the app
COVID_API_REQUEST_CACHE = {}

#Function checks if there is data cached in the COVID_API_REQUEST_CACHE
def covid_API_request_cached(location="Exeter", location_type="ltla", force_update=False):
    """
    Summary of covid_API_request_cache

    Parameters:
        -   Location and Location type (extracted from config.json)
        -   Defult paramters set to Exeter and LTLA

        If cache is NOT empty (mainly for non-forced updates)
            returns data from cache
        IF cache is empty
            request live data
            returns live data and saves to cache

    """

    key = (location,location_type)

    #If cache is found and there is no scheduled update to be executed, cached data is loaded
    logging.info("Checking for cached data")
    if key in COVID_API_REQUEST_CACHE and not force_update:
        logging.info("found cached data")
        return COVID_API_REQUEST_CACHE[key]

    #Otherwise live data is requested, loaded and then cached
    else:
        logging.info("Requesting live data")
        try:
            live_data = covid_API_request(location,location_type)
        except:
            logging.error("Exception occurred", exc_info=True)
        COVID_API_REQUEST_CACHE[key] = live_data
        return live_data
#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Data Caching ----------------------------------------------------------
#---------------------------------------------------------------------------------------------------

#Live Data Access Function with parammeters location and location type (defult values set to Exeter
#and ltla)
def covid_API_request(location="Exeter",location_type="ltla"):
    """
    Summary of covid_API_request

    Parameters:
        -   Location and Location type (extracted from config.json)
        -   Defult paramters set to Exeter and LTLA

        First location filters are set for the API
        Then the structure is set for how we want data returned from the API

        The API is then initiated

        Data is requested as a dataframe

        Returns a conversion of the data from a dataframe to a dictionary

    """

    #Location parameters for pre-filtering data
    location_filter = [
        f'areaName={location}',
        f'areaType={location_type}'
    ]

    #The structure, in terms of metrics, in which we wish to receive the response
    cases_and_deaths = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "hospitalCases": "hospitalCases",
        "cumDailyNsoDeathsByDeathDate":"cumDailyNsoDeathsByDeathDate",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumCasesByPublishDate": "cumCasesByPublishDate",
        "newDeaths28DaysByDeathDate": "newDeaths28DaysByDeathDate",
        "cumDeaths28DaysByDeathDate": "cumDeaths28DaysByDeathDate"
    }

    #Initializing the open API with our parameters
    try:
        api = Cov19API(filters=location_filter, structure=cases_and_deaths)

        #Getting the data from the API as a pandas dataframe
        covid_data = api.get_dataframe()

        #Converting the data from a dataframe to a nested dictionary and returning the dictionary
        #dadict => shorthand form for data_as_a_dictionary
        daadict = covid_data.to_dict()
    except:
        logging.error("Exception occurred", exc_info=True)
    return daadict

#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Data Management Functions ---------------------------------------------
#---------------------------------------------------------------------------------------------------

#Function to process the data requested with local parameters

def process_local_data(force_update=False):

    """
    Summary of process_local_data

    Parameters: None
    (initally set to not be triggered unless a force update is)

    Arguments for the API request are extracted from the config file, which are then
    used to call the API.

    returns a tuple for local_infection_rate,local_location_name

    """

    #Create an empty dictionary to store local location parameters, accessible from the config file
    args_location_local = {}

    #First we extract our local location parameters stored on our config file and assign to
    #variables
    with open("app/static/json/config.json", encoding='utf-8') as config_file:
        config_parameters_local = json.load(config_file)
    local_location_name = config_parameters_local.get("location_local")
    local_location_type = config_parameters_local.get("locationType_local")

    #We store our location parameters, if there are any, in a dictionary defined above
    if local_location_name and local_location_type:
        args_location_local["location"]=local_location_name
        args_location_local["location_type"]=local_location_type

    #We call our API_request function to get local data using either the defult parameters or our
    #config file parameters.
    #The config file takes precedence over defult values.
    #Local data is then requested and cached
    local_data = covid_API_request_cached(**args_location_local, force_update=force_update)
    #-----------------------------------------------------------------------------------------------
    #From the local_data we extract the newCasesByPublishDate data
    local_new_cases_data=local_data["newCasesByPublishDate"]
    #We can then take the lastest 7 day cases using more-itertools functions
    local_cases_last_7_days = mit.take(7,local_new_cases_data.values())
    #We can then find the infection rate by dividing the total cases in the past 7 days by 7.
    #Rounding our answer to 2 decimal places and adding unis to make it more clear.
    local_infection_rate = str(round((sum(local_cases_last_7_days)/7),2)) + " cases per day"

    #We can then return the rate and location to be then used when rendering the HTML template
    logging.info("Managed to process local data")
    return local_infection_rate,local_location_name
#---------------------------------------------------------------------------------------------------

#Function to process the data requested with national parameters
def process_national_data(force_update=False):
    """
    Summary of process_national_data

    Parameters: None
    (initally set to not be triggered unless a force update is)

    Arguments for the API request are extracted from the config file, which are then
    used to call the API.

    returns national_infection_rate, current_hospital_cases_national,
    total_deaths_national, national_location_name

    """

    #Create an empty dictionary to store national location parameters, accessible from the config
    #file
    args_location_national = {}

    #First we extract our national location parameters stored on our config file and assign to
    #variables
    with open("app/static/json/config.json", encoding='utf-8') as config_file:
        config_parameters_national = json.load(config_file)
    national_location_name = config_parameters_national.get("location_national")
    national_location_type = config_parameters_national.get("locationType_national")

    #We store our location parameters, if there are any, in a dictionary defined above
    if national_location_name and national_location_type:
        args_location_national["location"]=national_location_name
        args_location_national["location_type"]=national_location_type

    #We call our API_request function to get national data using either the defult parameters or
    #our config file parameters.The config file takes precedence over defult values.
    #National data is then requested and cached
    national_data = covid_API_request_cached(**args_location_national, force_update=force_update)
    #-----------------------------------------------------------------------------------------------
    #The data column is assigned to a variable to be used when rendering the HTML template
    case_dates = national_data["date"]
    #We want to extract 3 key data points for the national data:
    #7 day infection rate, current hospital cases and total deaths
    #-----------------------------------------------------------------------------------------------
    #7-day-infection-rate
    #From the national_data we extract the newCasesByPublishDate data
    national_new_cases_data = national_data["newCasesByPublishDate"]
    #We can then take the lastest 7 day cases using more-itertools functions
    national_cases_last_7_days = mit.take(7,national_new_cases_data.values())
    #We can then find the infection rate by dividing the total cases in the past 7 days by 7.
    #Rounding our answer to 2 decimal places and adding units to make it more clear.
    national_infection_rate = str(round((sum(national_cases_last_7_days)/7),2)) + " cases per day"
    #-----------------------------------------------------------------------------------------------
    #current-hospital-cases
    #From the national data we extract the hospitalCases
    hospital_cases_data = national_data["hospitalCases"]
    #Convert to a list and replace nan values with 0
    hospital_cases_data_list = [0 if x != x else x for x in list(hospital_cases_data.values())]
    #We can find the index of the first non-zero value
    latest_hospital_case_index = \
        (next((i for i, x in enumerate(hospital_cases_data_list) if x!=0), None))
    #We can extract the current KNOWN hospital cases and the date using the index found and our
    #variable case_dates
    current_hospital_cases_national = str(hospital_cases_data.get(latest_hospital_case_index))\
        + " cases on " + str(case_dates.get(latest_hospital_case_index))
    #-----------------------------------------------------------------------------------------------
    #total-deaths
    #From the national data we extract the cumulative number of deaths
    cumulative_death_data = national_data["cumDailyNsoDeathsByDeathDate"]
    #convert to a list and replace nan values with 0
    cumulative_death_data_list = [0 if x != x else x for x in list(cumulative_death_data.values())]
    #We can find the index of the first non-zero value
    cumulative_death_data_index = \
        (next((i for i, x in enumerate(cumulative_death_data_list) if x!=0), None))
    #We can extract the current KNOWN total death toll and the date using the index found and our
    #variable case_dates
    total_deaths_national = str(cumulative_death_data.get(cumulative_death_data_index)) \
        + " deaths recorded by " + str(case_dates.get(cumulative_death_data_index))

    #We then return a tuple of our metrics that we want rendered on the UI
    logging.info("Managed to process national data")
    return national_infection_rate, current_hospital_cases_national, \
        total_deaths_national, national_location_name

#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Data Management Functions ---------------------------------------------
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Automated Updates Functions -------------------------------------------
#---------------------------------------------------------------------------------------------------

#Create an empty list to store all the covid data update requests
updates = []

#Function that takes in an updates type, interval, name and forces an update on the UI from live
# accessed data instead of cached data
def update_cached_data(update_type, user_update_sched, update_interval, update_name, repeat):
    """
    Summary of update_cached_data

    Parameters:
        -   update_type: can either be covid-data or news
        -   user_update_schedule: scheduling function defined in views backend
        -   update_interval: time when user wants update executed
        -   update_name: name of the update
        -   repeats: if repeats selected, the function will repeat, else it will be blank

    returns:
        -   an execution to process local and national data
        -   an execution to update news

    after all execultions, scheduled updates are removed from the updates queue

    """
    #We assign the date now of a scheduled update to the date now
    date_now = str(date.today())

    #Using the date now and our update parameters, we can execute the scheduled update, if it is
    #still in the schedule queue. Once it is executed it can then be removed
    for update in updates:
        #For and update, if the title and content match we schedule a run
        if update['title'] == update_name and (update_interval) in update['content'] \
            and date_now in update['content']:
            logging.info("Scheduled run")
            #Then depeneding on the update type, the corresponding function for that given update
            #will be executed.
            #NOTES: News updates are then executed independently to covid data updates
            if update_type == "covid-data":
                try:
                    process_local_data(force_update=True)
                    process_national_data(force_update=True)
                except:
                    logging.error("Exception occurred", exc_info=True)
                updates.remove(update)
                logging.info("Scheduled covid event has completed")
            if update_type == "news":
                try:
                    update_news(force_update=True)
                except:
                    logging.error("Exception occurred", exc_info=True)
                updates.remove(update)
                logging.info("Scheduled news event has completed")

    #If the repeat checkbox was ticked then an update would be repeated at the users input
    #parameters
    if repeat:
        schedule_covid_updates\
            ( update_type, user_update_sched, update_interval, update_name, repeat)
#---------------------------------------------------------------------------------------------------

#Function takes in user input parameters to schedule an update
def schedule_covid_updates\
    ( update_type, user_update_sched, update_interval,update_name, repeat=False):
    """
    Summary of schedule_covid_updates

    Parameters:
        -   update_type: can either be covid-data or news
        -   user_update_schedule: scheduling function defined in views backend
        -   update_interval: time when user wants update executed
        -   update_name: name of the update
        -   repeats: autoset to false

    purpose:
        -   if a covid-data update is requested then a covid data update is sent
            to the schedule queue
        -   if a news update is requested then a news update is sent to the schedule queue

    """

    #First get current time
    now = datetime.now()

    #Split update interval
    update_hour, update_minute = update_interval.split(":")

    #Create new datetime
    future = now.replace(hour=int(update_hour), minute=int(update_minute), second=0)

    #If our datetime is in the past we add 1 day to compensate
    if future < now:
        future = future + timedelta(days=1)

    #We then calculate the delay for the schedule module function used
    delay = (future-now).total_seconds()

    #As a precaution: if updates have the same name, to avoid confusion, the following code
    #will be executed to better manage updates.
    existing = 0
    for item in updates:
        if item['title'] == update_name:
            existing += 1

        if existing > 0:
            update_name = f'{update_name} ({existing + 1})'

    #When a user schedules and update, their parameters are inputted into the above format and
    #append to a list and to be posted on the UI as a toast widget.
    #News updates are then scheduled independently to covid data updates
    #First we check what the update type is
    if update_type == "covid-data":
        #The corresponding update given a base format
        update_covid_item = {
            'title': update_name,
            'content': "Your next data update is scheduled for: " \
                + future.strftime("%Y-%m-%d %H:%M")
        }
        #Then the update is appended to the updates list
        updates.append(update_covid_item)
        logging.info(f"Scheduling a covid_update run in:{delay}")

    if update_type == "news":
        update_news_item = {
            'title': update_name,
            'content': "Your next news update is scheduled for: " \
                + future.strftime("%Y-%m-%d %H:%M")
        }
        updates.append(update_news_item)
        logging.info(f"Scheduling a news run in:{delay}")

    #The parameters are then used to queue a update at the given parameters
    try:
        user_update_sched.enter(delay, 1, update_cached_data, \
            (update_type, user_update_sched, update_interval, update_name, repeat))
    except:
        logging.error("Exception occurred", exc_info=True)

#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Automated Updates Functions -------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Main Specification Project---------------------------------------------
#---------------------------------------------------------------------------------------------------
 
