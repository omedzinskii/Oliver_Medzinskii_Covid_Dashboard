## Advanced Details

This python project implements various python libraries and self-created modules. The aim of this section 
is to give a deeper understanding of how the modules work and the logic behind it. This can also be found 
in the documentation folder inside the app. 

#### The modules I plan to discuss are:
- Covid Data and News handlers (specifically caching)
- The views
- The logger 

It is important to remember the directory structure stipulated above. The way I have packaged the app, 
means that it can be run from a single file, so understanding of these module functionalities are 
completely optional.

In addition to this, the code contain inline comments that will aid in your understanding of the 
modules

### Covid Data and News handlers

These handlers are used to pre-process variables we want loaded into the UI. For example you will 
notice a function in the covid_data_handler.py module called process_local_data that takes in 
parameters from the configuration file and returns a local infection rate. Any of the function 
called "process ..." are data processing function. 

In both handlers I have implemented a caching system. Why? well this caching system allows for 
many benefits. As our application is on a regular refresh every 60 seconds, the caching means we
don’t need to call the API request function at every refresh. We simply check if there is data in 
the cache and if there is, then we load it, otherwise we get live data. This is as we only really 
need to call the API request when a user schedules a FORCED DATA UPDATE. The diagram below shows 
this in more detail.

![caching](caching.png)

For the actual scheduling aspect, what I have is the same function for both handlers. Essentially,
they check for the user input parameters (update interval and update name). It will then append 
a list item; if it’s a news update it goes in the news list and if it’s a data update it goes in 
the covid data list. The lists are then merged in views.py and rendered on the template. 

To learn more on the python schedule module click [here](https://docs.python.org/3/library/sched.html)

### Views

The views module is like the glue between everything. It connect the front end to all the back end 
processes. Simply put it is used for running the python modules, Accessing user input data and 
sending them to the backend as well as rending everything on the HTML template.

### Logger 

The logger is a small python module that essentially formats the data that we try log. You will 
notice in the other modules code, statements such as:

```
logging.error("error message" **args)
```

These log messages will be stored on an external file called app.log as well as be printed in the 
console, as this is how I’ve set the logger up. This will help you track what and when functions 
are being executed and if any errors occur. 

## Unit Testing and DTC

A series of tests have been implemented in the app to allow for the softwares reliability and longevity 
to be at a higher standard. The tests help to maintain the softwares lifecycle. Each unit test is used
to make sure a function is working. They follow a simple structure of 

1. Arrange - the environment for the test is initialised 
2. Act - a function/feature is executed 
3. Assert - The result of the execution is compared to the actual result

A additional python module was created, run_tests.py. This runs the unit tests at a regular interval 
of 48 hours. This is part of the DTC(see next paragraph) to ensure the software reliability.

### DTC - deployment test cycle 

During development a deployment test cycle was used to ensure full functionality of the application.

- Pre-Deployment
    During phase 1 implementation of testing individual functions as they are created using the unit tests. 
    An example of the tests running in phase 1:

![caching](testing_phase1.png)

- Deployment 
    Proper live deployment was not made, however after completion the app was given a full run through of the 
    tests again to check full functionality
- Post-Deployment 
    Any remaining bugs were fixed 

NOTE: implementing a full software development life cycle would involve repeating these stages, with 
more user testing and a proper deployment phase