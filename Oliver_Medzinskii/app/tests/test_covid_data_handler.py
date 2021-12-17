#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import pytest
from app.covid_data_handler import COVID_API_REQUEST_CACHE, covid_19_test_data,\
    covid_API_request_cached, covid_API_request, process_covid_csv_data, parse_csv_data, \
        process_local_data, process_national_data, update_cached_data, schedule_covid_updates
from app.views import user_update_sched
#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#-------- OPEN ----------- UnitTests ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def test_parse_csv_data():
    #variable that links the test data and conversion function aboves
    data_to_test = parse_csv_data(covid_19_test_data)
    #assert test to check length is 639
    assert len(data_to_test) == 639
#---------------------------------------------------------------------------------------------------
def test_process_covid_csv_data():
    #link test variables to values derived from function
    last7days_cases, current_hospital_cases, total_deaths = \
        process_covid_csv_data(parse_csv_data(covid_19_test_data))
    #assert tests to check values were correctly extracted and processed
    assert last7days_cases == 240299
    assert current_hospital_cases == 7019
    assert total_deaths == 141544
#---------------------------------------------------------------------------------------------------
def test_covid_API_request_cached():
    #check if cache is empty
    covid_cache = COVID_API_REQUEST_CACHE
    assert len(covid_cache) == 0
    #execute caching function
    covid_API_request_cached()
    #check if cache now has data
    assert len(covid_cache) > 0
#---------------------------------------------------------------------------------------------------
def test_covid_API_request():
    #execute api request function to get data
    data = covid_API_request()
    #check if the data returned is a dictionary
    assert isinstance(data, dict)
#---------------------------------------------------------------------------------------------------
def test_process_local_data():
    process_local_data()
def test_process_national_data():
    process_national_data()
#---------------------------------------------------------------------------------------------------
def test_update_cached_data():
    update_cached_data("covid-data", user_update_sched ,"22:28", "mock-covid-update","")
#---------------------------------------------------------------------------------------------------
def test_schedule_covid_updates():
    schedule_covid_updates("covid-data", user_update_sched ,"22:29", "mock-covid-update","")
#---------------------------------------------------------------------------------------------------
#-------- CLOSED --------- UnitTests ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
