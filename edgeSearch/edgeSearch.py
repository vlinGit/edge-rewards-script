from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from pytrends.request import TrendReq
from keywords import keywords
import time
import random
import pyautogui

edgeOptions = Options()
edgeOptions.add_argument('--log-level=3')
edgeOptions.add_experimental_option("detach", True) 
#edgeOptions.add_argument("auto-open-devtools-for-tabs")
driver = webdriver.Edge(options=edgeOptions)
driver.maximize_window()
pcMaxPoints = 150
mobileMaxPoints = 100
pointsPerSearch = 5

def login():
    driver.get('https://login.microsoftonline.com/')

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

# Index when parsed:
#   0: numeric points rewarded
#   1: title of activity
#   2: Info on activity
#   3: Text of the link at the bottom of each reward card
def rewardText(rawText):
    text = rawText.strip().split('\n')
    text[3] = text[3][:len(text[3])-1]
    
    return text

def doDailySets():
    driver.get('https://rewards.bing.com/?signin=1')
    daily = driver.find_elements(By.XPATH, "//*[@id='daily-sets']/mee-card-group[1]/div/mee-card")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    extra = driver.find_elements(By.XPATH, '//*[@id="more-activities"]/div/mee-card')
    rewards = daily + extra
    newWindow = 1
    
    for reward in rewards:
        try:
            text = rewardText(reward.text.lower()) # see rewardText() for index explanation 
            try:
                taskIcon = reward.find_element(By.XPATH, './/div/card-content/mee-rewards-daily-set-item-content/div/a/mee-rewards-points/div/div/span[1]')
            except Exception:
                taskIcon = reward.find_element(By.XPATH, './/div/card-content/mee-rewards-more-activities-card-item/div/a/mee-rewards-points/div/div/span[1]')
            taskClass = taskIcon.get_attribute('class')
        except Exception:
            taskClass = ''
        
        if taskClass == 'mee-icon mee-icon-AddMedium': # true if task has not been
            reward.click()
            driver.switch_to.window(driver.window_handles[newWindow])
            
            if 'poll' in text[1]:
                choice = driver.find_element(By.ID, f'btoption{random.randint(0, 1)}')
                driver.execute_script("arguments[0].click();", choice)

            driver.switch_to.window(driver.window_handles[0]) 
            newWindow += 1
        

def getCap():
    driver.get('https://rewards.bing.com/')
    driver.find_element(By.XPATH, '//*[@id="dailypointColumnCalltoAction"]').click()
    pcCap = pcMaxPoints - int(driver.find_element(By.XPATH, '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.split("/")[0].strip())
    mobileCap = mobileMaxPoints - int(driver.find_element(By.XPATH, '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.split("/")[0].strip())
    
    print("Avaliable Points: ", pcCap, mobileCap)
    
    return pcCap, mobileCap

# Grab a random keyword generates a suggested search with pytrends
# Why this way, IDK
def generateString(cap):
    pytrends = TrendReq(hl='en-US', tz=360)
    searches = []

    while len(searches) < cap/pointsPerSearch:
        suggestions = pytrends.suggestions(keyword=keywords[random.randint(0, len(keywords)-1)])
        for suggestion in suggestions:
            if (not suggestion["title"] in searches):
                searches.append(suggestion["title"])
    
    return searches

def searchLoop(cap=0):
    searchBar = driver.find_element(By.ID, "sb_form_q")
    searches = generateString(cap)

    print("Searching ", len(searches))
    print("Searches: ", searches)
    
    points = 0
    searchCounter = 0
    while points <= cap:
        searchBar = driver.find_element(By.ID, "sb_form_q")
        searchBar.clear()
        searchBar.send_keys(searches[searchCounter])
        searchBar.submit()
        time.sleep(random.randint(1,3)/10)
        points += pointsPerSearch # += 5
        searchCounter += 1

def doSearch(pcCap, mobileCap):
    searchLoop(pcCap)
    pyautogui.hotkey('ctrl', 'shift', 'i')
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'shift', 'm')
    searchLoop(mobileCap)
    
if __name__ == "__main__":
    doDailySets()
    pcCap, mobileCap = getCap()
    driver.get('https://bing.com')
    doSearch(pcCap, mobileCap)