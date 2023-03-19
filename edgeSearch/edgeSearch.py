from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from pytrends.request import TrendReq
from keywords import keywords
import time
import random

edgeOptions = Options()
edgeOptions.add_argument('--log-level=3')
edgeOptions.add_experimental_option("detach", True) 
driver = webdriver.Edge(options=edgeOptions)
driver.maximize_window()

#FIXME:
#   Warpspeed broken
#   Only does the sequence once
#   Needs a check to see if question is complete
#   Need a check for entertainment quiz (7 questions), do a check for #of questions and base for loop off that
def doQuiz(isWarpspeed):
    buttonX = 364
    buttonY = 994
    
    if isWarpspeed:
        time.sleep(3)
        for i in range(0,3):
            time.sleep(2)
            choices = driver.find_elements(By.CLASS_NAME, "rq_button")
            for choice in choices:
                try:
                    driver.execute_script("arguments[0].click()",choice)
                except Exception:
                    break
    else:
        for i in range(0,3):
            time.sleep(0.5)
            driver.find_element(By.XPATH, f"//*[@id='QuestionPane{i}']/div[1]/div[2]/a[1]/div/div").click()
            time.sleep(0.5)
            driver.find_element(By.XPATH, f"//*[@id='nextQuestionbtn{i}']").click()

#TODO:
#   Ability to do additional tasks
#   Login check
#   backlog: check if tasks has been done, if it has been skip it
#FIXME:
#   Poll button is not clickable for some reason
def doDailySets():
    driver.get('https://rewards.bing.com/?signin=1')
    rewards = driver.find_elements(By.XPATH, "//*[@id='daily-sets']/mee-card-group[1]/div/mee-card")
    newWindow = 1
    
    for reward in rewards:
        text = reward.text.lower()
        reward.click()
        driver.switch_to.window(driver.window_handles[newWindow])
        time.sleep(0.5)
        #driver.find_element(By.XPATH, "html").click() #FIXME: a tag not being found
        try:
           driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/span/a").click()
        except Exception:
            print("No login needed")
        print(f"Current reward: {text}")
        if "quiz" in text:
            if "warpspeed" in text:
                doQuiz(True)
            else:
                doQuiz(False)
        elif "poll" in text:
            choice = driver.find_element(By.XPATH, "//*[@id='btoption0']")
            driver.execute_script("argument[0].click()", choice)
        
        time.sleep(0.5)
        driver.switch_to.window(driver.window_handles[0])
        newWindow += 1
        

# implement search with pytrends
def generateString():
    pytrends = TrendReq(hl='en-US', tz=360)
    searches = []

    while len(searches) < 60:
        suggestions = pytrends.suggestions(keyword=keywords[random.randint(0, len(keywords))])
        for suggestion in suggestions:
            if (not suggestion["title"] in searches):
                searches.append(suggestion["title"])
    
    return searches
    

# TODO:
#   Mobile searches, opening phone view in dev console triggers it
def doSearch():
    driver.get('https://bing.com')
    cap = 300
    searchBar = driver.find_element(By.ID, "sb_form_q")
    searches = generateString()

    points = 0
    searchCounter = 0
    while points < cap:
        searchBar = driver.find_element(By.ID, "sb_form_q")
        searchBar.clear()
        searchBar.send_keys(searches[searchCounter])
        searchBar.submit()
        time.sleep(random.randint(1,3)/10)
        points += 5
        searchCounter += 1

def login():
    driver.get('https://login.microsoftonline.com/')
        
        
if __name__ == "__main__":
    doSearch()
    edgeOptions.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1')
    driver = webdriver.Edge(options=edgeOptions)
    doSearch()