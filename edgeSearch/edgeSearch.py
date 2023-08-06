from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
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

#TODO:
#   Need a check for entertainment quiz (7 questions) <- this might be done, but will need to check once the quiz pops up in tasks
def clickButton(method: By, path):
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((method, path)))
        button = driver.find_element(method, path)
        driver.execute_script("arguments[0].click()", button)
        return True
    except TimeoutException:
        print(f"Button could not be found\nMethod: {method}\nPath: {path}\n")
        return False

# Index when parsed:
#   0: numeric points rewarded
#   1: title of activity
#   2: Info on activity
#   3: Text of the link at the bottom of each reward card
def rewardText(rawText):
    text = rawText.strip().split('\n')
    text[3] = text[3][:len(text[3])-1]
    
    return text

# Grabs '(x of 10)' and converts to [x, 10]
def wqIsolateNumbers():
    panes = driver.find_element(By.XPATH, '//*[@id="ListOfQuestionAndAnswerPanes"]')
    progress = panes.find_elements(By.CSS_SELECTOR, 'div')
    extract = progress[-1].get_attribute('innerText')[1:-1].split('of')
    numbers = [int(extract[0].strip()), int(extract[1].strip())]
    
    return numbers

# Warpspeed and supersonic quizzes
def specialQuiz():
    try:
        clickButton(By.XPATH, '//*[@id="rqStartQuiz"]')
    except NoSuchElementException:
        print('Element not found, quiz was likely already started')
    curPoints = int(driver.find_element(By.CLASS_NAME, 'rqECredits').get_attribute('innerText'))
    maxPoints = int(driver.find_element(By.CLASS_NAME, 'rqMCredits').get_attribute('innerText'))
    option = 0
    while curPoints < maxPoints:
        if clickButton(By.XPATH, f'//*[@id="rqAnswerOption{option}"]'):
            newPoints = int(driver.find_element(By.CLASS_NAME, 'rqECredits').get_attribute('innerText'))
            
            if curPoints != newPoints: 
                option = 0
                curPoints = newPoints
            else:
                option += 1
        else:
            print("Submit button not found in specialQuiz, stopping quiz")
            break

def abcQuiz():
    progress = wqIsolateNumbers()
    curQuestion = progress[0]
    maxQuestion = progress[1]
    
    while curQuestion <= maxQuestion:
        if clickButton(By.CLASS_NAME, 'wk_choicesInstLink'):
            time.sleep(2)
            if clickButton(By.XPATH, f'//*[@id="nextQuestionbtn{curQuestion-1}"]') and curQuestion != maxQuestion:
                time.sleep(2)
                updateProgress = wqIsolateNumbers()
                curQuestion = updateProgress[0]
            else:
                print("Submit button not found in abcQuiz, stopping quiz")
                break
        else:
            print("Choice button not found in abcQuiz, stopping quiz")
            break
        
    
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
            time.sleep(1)
            driver.switch_to.window(driver.window_handles[newWindow])
            
            if 'warpspeed quiz' in text[1] or 'supersonic quiz' in text[1]:
                specialQuiz()
            elif 'poll' in text[1]:
                if not clickButton(By.ID, f'btoption{random.randint(0, 1)}'):
                    print("Poll button not found")
            elif 'test your smarts' in text[1] or 'show what you know' in text[1] or 'a, b, or c' in text[1] or 'quiz' in text[2]:
                abcQuiz()
            
            driver.switch_to.window(driver.window_handles[0]) 
            newWindow += 1
        

def getCap():
    driver.get('https://rewards.bing.com/')
    driver.find_element(By.XPATH, '//*[@id="dailypointColumnCalltoAction"]').click()
    pcCap = pcMaxPoints - int(driver.find_element(By.XPATH, '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.split("/")[0].strip())
    mobileCap = mobileMaxPoints - int(driver.find_element(By.XPATH, '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.split("/")[0].strip())
    
    print("Avaliable Points: ", pcCap, mobileCap)
    
    return pcCap, mobileCap
        

# Generates search using pytrends
# def generateString(cap):
#     pytrends = TrendReq(hl='en-US', tz=360)
#     searches = []

#     while len(searches) < cap/pointsPerSearch:
#         suggestions = pytrends.suggestions(keyword=keywords[random.randint(0, len(keywords)-1)])
#         for suggestion in suggestions:
#             if (not suggestion["title"] in searches) and len(suggestion["title"]) < 10:
#                 searches.append(suggestion["title"])
    
#     return searches

# Searches using a random keyword
def generateString(cap):
    #pytrends = TrendReq(hl='en-US', tz=360)
    searches = []

    while len(searches) < cap/pointsPerSearch:
        #suggestions = pytrends.suggestions(keyword=keywords[random.randint(0, len(keywords)-1)])
        suggestion = keywords[random.randint(0, len(keywords)-1)]
        if suggestion not in searches:
            searches.append(suggestion)
    
    return searches

def searchLoop(cap=0):
    searchBar = driver.find_element(By.ID, "sb_form_q")
    searches = generateString(cap)

    print("Searching ", len(searches))
    print("Searches: ", searches)
    
    points = 0
    searchCounter = 0
    while points < cap:
        searchBar = driver.find_element(By.ID, "sb_form_q")
        while searchBar.get_attribute('value') != '':
            searchBar.clear()
            time.sleep(0.2)  
        searchBar.send_keys(searches[searchCounter])
        searchBar.submit()
        time.sleep(random.randint(1,3)/10)
        points += pointsPerSearch # += 5
        searchCounter += 1

# hotkeys are for turning mobile mode on and off
# done by enabling dev console and using device emulation
def doSearch(pcCap, mobileCap):
    searchLoop(pcCap)
    pyautogui.hotkey('ctrl', 'shift', 'i')
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'shift', 'm')
    searchLoop(mobileCap)
    pyautogui.hotkey('ctrl', 'shift', 'i')
    driver.refresh()
    
if __name__ == "__main__":
    doDailySets()
    
    pcAvailPoints, mobileAvailPoints = getCap()
    while pcAvailPoints != 0 or mobileAvailPoints != 0:
        driver.get('https://bing.com')
        doSearch(pcAvailPoints, mobileAvailPoints)    
        pcAvailPoints, mobileAvailPoints = getCap()
        
    driver.get('https://rewards.bing.com/')
    driver.find_element(By.XPATH, '//*[@id="dailypointColumnCalltoAction"]').click()