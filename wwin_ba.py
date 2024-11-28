from selenium import webdriver
from selenium.webdriver.edge import options
from selenium.webdriver.edge import service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime
import numpy as np

# driver = webdriver.Edge(r'C:\\Users\\PC\\OneDrive\\Desktop\\prjcts\\WEBSCRAPPER\\driver\\msedgedriver.exe')
# # C:\Users\PC\OneDrive\Desktop\prjcts\WEBSCRAPPER\driver

# driver.get('https://google.rs')

options = Options()
options.add_argument("start-maximized")
# options.add_argument("--headless")
options.add_experimental_option("detach", True)
# options.add_argument("headless")
# options.add_argument("window-size=1920,1080")
# options.add_experimental_option("headless", True)
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://wwin.com/en/")


driver.find_element("id", "navSport").click()

# Wait 1 second to load element and make it clickable. Should find better way to write this kind of s*it.
time.sleep(2) 

# Turn off live betting.
# Iskljuci uzivo ponudu.
# driver.find_elements(By.CSS_SELECTOR, ".sport-sidebar__options-live-toggle")[1].click()

time.sleep(1)

date = driver.find_elements(By.CSS_SELECTOR,".sport-overview__header-wrapper .msports__calendar-display__date")[0].text
# print(date)

# sport_overview = driver.find_elements()

Competition = []
Time = []
Match_HomeTeam = []
Match_AwayTeam = []
Odds = []
Odd__BTS_Yes = []
Odd__BTS_No = []
x = []
y = []
# xy = ""

TwoDimensionArray = []

sport_events__wrapper = driver.find_elements(By.CLASS_NAME, "sport-events__wrapper > div")

for i in sport_events__wrapper:
    if i.get_attribute("class") == "headmarket__v2":
        # Save Current Competition
        currentCompetition = i.find_element(By.CSS_SELECTOR,".headmarket__title__v2__wrapper").text
    if i.get_attribute("class") == "live-match__hov single-match__prematch":
        # Find Time When Match Begins
        Time.append(i.find_element(By.CSS_SELECTOR, ".live-match-date__time").text)
        # Find Home Team Name
        Match_HomeTeam.append(i.find_element(By.CSS_SELECTOR, ".live-name-v__home").text)
        # Find Away Team Name
        Match_AwayTeam.append(i.find_element(By.CSS_SELECTOR, ".live-name-v__away").text)
        # Save Odds For The Match In This Order [1, X, 2, 1X, X2, 12]
        tempOdds = i.find_element(By.CSS_SELECTOR, ".live-match__odd").text.split("\n")
        if ( len ( tempOdds ) > 5):
            Odds.append(tempOdds)
        else :
            Odds.append(['_1_', '_X_', '_2_', '_1X_', '_X2_', '_12_'])
        Competition.append(currentCompetition)

# Variable Odds contains odds for all matches where Odds[0] contains six odds (1, X, 2, 1X, X2, 12) for first match, Odds[1] for 
# second match, Odds[2] for third match, etc. Idea is to make Array[number of matches][number of odds(which is six)] to
# Array[number of odds][number of matches], where 1st row contains all odds for home team win which is represent by character 1,
# 2nd row for draw - X, etc.So, we can use transpose of matrix where transpose is function which swap rows and column in matrix.

Odds_Directly = np.array(Odds)
Odds_Directly = Odds_Directly.transpose()

FinalResult = {
    "Competition": Competition,
    "Time": Time,
    "Home": Match_HomeTeam,
    "Away": Match_AwayTeam,
    "1": Odds_Directly[0],
    "X": Odds_Directly[1],
    "2": Odds_Directly[2],
    "1X": Odds_Directly[3],
    "X2": Odds_Directly[4],
    "12": Odds_Directly[5],
}

# print(Odds)

df = pd.DataFrame.from_dict(FinalResult)
# df.to_excel('Wwin.xlsx')

now = datetime.now()
dt_string = now.strftime("%d%m%Y%H%M%S")
# print(dt_string)

df.to_excel("Wwin_BA_"+dt_string+".xlsx")