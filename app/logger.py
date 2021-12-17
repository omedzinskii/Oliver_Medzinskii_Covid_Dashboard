#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import logging
#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Imports ---------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#-------- OPEN ------------- Main Specification Project---------------------------------------------
#---------------------------------------------------------------------------------------------------
#Configurations for logging 
logging.basicConfig(
    format='%(levelname)s - %(asctime)s - %(message)s',
    level=logging.DEBUG,
    filename='app.log',
    filemode='a'
)
#Hooking up logger to the console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
console.setFormatter(formatter)
#Add the output to console for logger
logging.getLogger().addHandler(console)
def get_logger():
    """
    Summary of get_logger
    
    returns a logger
    """
    return logging.getLogger("CovidAppLogger")
#---------------------------------------------------------------------------------------------------
#-------- CLOSED ----------- Main Specification Project---------------------------------------------
#---------------------------------------------------------------------------------------------------
