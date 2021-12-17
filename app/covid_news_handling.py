#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

import json
from newsapi import NewsApiClient
from app.logger import logging

#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Main Specification Project---------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Data Caching ----------------------------------------------------------
#---------------------------------------------------------------------------------------------------

#Create a cache for requested data from the NEWS API, this stops the app from calling the NEWS API
#request at every refresh of the app
NEWS_API_REQUEST_CACHE = {}
#Function checks if there is data cached in the COVID_API_REQUEST_CACHE
def news_API_request_cached(covid_terms, force_update=False):
    """
    Summary of news_API_request_cache

    Parameters:
        -   Covid Terms (defined in config.json file)
        -   Defult parameter set to: Covid COVID-19 coronavirus

        If cache is NOT empty (mainly for non-forced updates)
            returns data from cache
        IF cache is empty
            request live data
            returns live data and saves to cache

    """
    key = (covid_terms)
    #If cache is found and there is no scheduled update to be executed, cached data is loaded
    logging.info("Checking for cached data")
    if key in NEWS_API_REQUEST_CACHE and not force_update:
        logging.info("found cached data")
        return NEWS_API_REQUEST_CACHE[key]
    #Otherwise live data is requested, loaded and then cached
    else:
        logging.info("Requesting live data")
        try:
            live_news_data = news_API_request(covid_terms)
        except:
            logging.error("Exception occurred", exc_info=True)
        NEWS_API_REQUEST_CACHE[key] = live_news_data
        return live_news_data
#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Data Caching ----------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Covid News Extraction -------------------------------------------------
#---------------------------------------------------------------------------------------------------

#Live Data Access Function with parammeters covid terms
#(defult values set to Covid COVID-19 coronavirus)
def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    """
    Summery of news_API_request

    Parameters:
        -   Covid Terms (defined in config.json file)
        -   Defult parameter set to: Covid COVID-19 coronavirus

        First an API key is extracted from the config file

        The API is then initiated

        returns articles via the API request
        (other parameters can be used, please see API documentation in README)

    """
    #Create an empty dictionary to store our API key, accessible from the config file
    args_news_api_key = {}
    #First we extract our API key stored on our config file and assign to a variable
    with open("app/static/json/config.json", encoding="utf-8") as config_file:
        config_parameters_local = json.load(config_file)
    news_api_key = config_parameters_local.get("news_api_key")
    #We store our API key, if there are any, in a dictionary defined above
    if news_api_key:
        args_news_api_key['api_key'] = news_api_key
    #Initializing the open API with our API KEY
    news_api = NewsApiClient(**args_news_api_key)
    #Getting the data from the API as a nested dictionary
    try:
        all_article_data = news_api.get_everything(q=covid_terms,
                                        sources='bbc-news,the-verge',
                                        domains='bbc.co.uk,techcrunch.com',
                                        language='en',
                                        sort_by='relevancy',
                                        page=2)
    except:
        logging.error("Exception occurred", exc_info=True)

    return all_article_data

#---------------------------------------------------------------------------------------------------

#Create an empty list to store all new data
news = []
#Create an empty list to store all news articles that are removed by the user
deleted_articles = []
def update_news(force_update=False):
    """
    Summary of update_news

    Parameters: none
    (initally set to not be triggered unless a force update is)

    Arguments for news_API_request are extracted from the config file, which are then
    used to call the API.

    returns news articles from API and appends to empty list news
    """
    #Create an empty dictionary to store our custom covid terms, accessible from the config file
    args_covid_terms = {}
    #First we extract our Custom covid terms stored on our config file and assign to a variable
    with open("app/static/json/config.json", encoding="utf-8") as config_file:
        config_parameters_local = json.load(config_file)
    custom_covid_terms = config_parameters_local.get("custom_covid_terms")
    #We store our custom covid terms, if there are any, in a dictionary defined above
    args_covid_terms["covid_terms"] = custom_covid_terms
    #We call our API request, filtering the data using the stored custom covid terms or defult
    #values if no custom terms exist
    news_articles = \
        news_API_request_cached(**args_covid_terms, force_update=force_update)['articles']
    #For each article in our news list we used the base format to append the article to
    #our News list
    for item in news_articles:
        update_news_item = {
            'title': item['title'],
            'content': item['description']
        }
        news.append(update_news_item)
        logging.info("News articles have been found and added")
        #The news list is then merged into the main updates list in our backend
#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Covid News Extraction -------------------------------------------------
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Main Specification Project---------------------------------------------
#---------------------------------------------------------------------------------------------------
