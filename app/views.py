#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
from app import app

import sched
from requests.api import get

from flask import request, render_template
from app.covid_data_handler import process_local_data, process_national_data, \
    schedule_covid_updates, updates
from app.covid_news_handling import news, update_news, deleted_articles

from app.logger import logging

#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Main Specification Project---------------------------------------------
#---------------------------------------------------------------------------------------------------

#Initiate schedulers
user_update_sched = sched.scheduler()
logging.info("Starting up scheduler")

#Start up news module
update_news()

#App route for running the code on URL/index
#Defining backend functionality of the app running on the given URL
@app.route("/index")
def index():

    print(news)

    print(deleted_articles)

    #Start up of the scheduler
    user_update_sched.run(blocking=False)

    #Variable linking to favicon, title and the title logo
    favicon = "/static/images/favicon.png"
    title = "Your Covid-19 Data Updates"
    title_img = "titleimage.png"

    #Linking variables to data extracted in covid_data_handler.py module
    local_infection_rate,local_location_name = process_local_data()
    national_infection_rate, current_hospital_cases_national, \
        total_deaths_national, national_location_name = process_national_data()

    #Requesting arguments in URL based of user input
    #UP => Update I => Interval N => Name
    upi = request.args.get("update")
    upn = request.args.get("two")

    #Requestion arguments for checkboxes in the UI
    sched_update_repeats = request.args.get("repeat")
    sched_update_covid_data = request.args.get("covid-data")
    sched_update_news = request.args.get("news")

    #Depending on the parameters the user inputs, independent scheduling of events will run

    if upi and upn != None:
        if sched_update_covid_data == 'covid-data':
            schedule_covid_updates('covid-data', user_update_sched, upi,upn, sched_update_repeats=="repeat")
        if sched_update_news == 'news':
            schedule_covid_updates('news', user_update_sched, upi,upn, sched_update_repeats=="repeat")

    #Requesting args to see if a user tries to remove a widget item
    update_to_remove = request.args.get("update_item")
    news_to_remove = request.args.get("notif")


    #If a user clicks the cross on a toast widget it is deleted
    for update_item in updates:
        if update_item['title'] == update_to_remove:
           updates.remove(update_item)

    for news_item in news:
        for deleted_item in deleted_articles:
            if deleted_item == news_item:
                news.remove(news_item)
        if news_item['title'] == news_to_remove:
           news.remove(news_item)
           deleted_articles.append(news_item)

    #Return statement to load data and infomation for the user
    return render_template(
        "index.html",
        title = title,
        local_7day_infections = local_infection_rate,
        location = local_location_name,
        national_7day_infections = national_infection_rate,
        hospital_cases = current_hospital_cases_national,
        deaths_total = total_deaths_national,
        nation_location = national_location_name,
        news_articles = news,
        updates = updates,
        image = title_img,
        favicon = favicon
        )
#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Main Specification Project---------------------------------------------
#---------------------------------------------------------------------------------------------------
