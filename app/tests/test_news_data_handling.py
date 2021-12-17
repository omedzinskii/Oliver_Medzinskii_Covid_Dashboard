#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import pytest
from app.covid_news_handling import NEWS_API_REQUEST_CACHE, news_API_request, \
    news_API_request_cached, update_news
#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#-------- OPEN ----------- UnitTests ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def test_news_API_request_cached():
    #Initialise cache object, it will be full as update_news is executed on load of app. 
    #Empty cache and then test its empty, then can call news api request cached function
    news_cache = NEWS_API_REQUEST_CACHE
    assert len(news_cache) == 1
    #check if cache is empty
    news_cache.clear()
    assert len(news_cache) == 0
    #execute caching function
    news_API_request_cached(covid_terms="Covid COVID-19 coronavirus")
    #check if cache now has data
    assert len(news_cache) > 0
#---------------------------------------------------------------------------------------------------
def test_news_API_request():
    #execute api request function to get data
    data = news_API_request()
    #check if the data returned is a dictionary
    assert isinstance(data, dict)
#---------------------------------------------------------------------------------------------------
def test_update_news():
    update_news()
#---------------------------------------------------------------------------------------------------
#-------- CLOSED --------- UnitTests ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
