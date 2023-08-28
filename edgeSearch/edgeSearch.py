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

#TODO: use chrome alongside with edge, pyautogui seems like a crude but easy solution
phoneUserAgent = "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 EdgA/113.0.1774.63"
edgeOptions = Options()
edgeOptions.add_argument('--log-level=3')
edgeOptions.add_experimental_option("detach", True)
#edgeOptions.add_argument("auto-open-devtools-for-tabs")
pcDriver = webdriver.Edge(options=edgeOptions)
pcDriver.maximize_window()

pcMaxPoints = 150
mobileMaxPoints = 100
pointsPerSearch = 5

def login(driver):
    driver.get('https://login.microsoftonline.com/')

#TODO:
#   Need a check for entertainment quiz (7 questions) <- this might be done, but will need to check once the quiz pops up in tasks
def clickButton(driver, method: By, path):
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
    panes = pcDriver.find_element(By.XPATH, '//*[@id="ListOfQuestionAndAnswerPanes"]')
    progress = panes.find_elements(By.CSS_SELECTOR, 'div')
    extract = progress[-1].get_attribute('innerText')[1:-1].split('of')
    numbers = [int(extract[0].strip()), int(extract[1].strip())]
    
    return numbers

# Warpspeed and supersonic quizzes
def specialQuiz():
    try:
        clickButton(pcDriver, By.XPATH, '//*[@id="rqStartQuiz"]')
    except NoSuchElementException:
        print('Element not found, quiz was likely already started')
    curPoints = int(pcDriver.find_element(By.CLASS_NAME, 'rqECredits').get_attribute('innerText'))
    maxPoints = int(pcDriver.find_element(By.CLASS_NAME, 'rqMCredits').get_attribute('innerText'))
    option = 0
    while curPoints < maxPoints:
        if clickButton(pcDriver, By.XPATH, f'//*[@id="rqAnswerOption{option}"]'):
            newPoints = int(pcDriver.find_element(By.CLASS_NAME, 'rqECredits').get_attribute('innerText'))
            
            if curPoints != newPoints: 
                option = 0
                curPoints = newPoints
            else:
                option += 1
        else:
            print("Submit button not found in specialQuiz, stopping quiz")
            break

# returns false if quiz failed, true otherwise
def abcQuiz():
    try:
        progress = wqIsolateNumbers()
    except:
        print("Quitting abcQuiz")
        return False

    curQuestion = progress[0]
    maxQuestion = progress[1]
    
    while curQuestion <= maxQuestion:
        if clickButton(pcDriver, By.CLASS_NAME, 'wk_choicesInstLink'):
            time.sleep(2)
            if clickButton(pcDriver, By.XPATH, f'//*[@id="nextQuestionbtn{curQuestion-1}"]') and curQuestion != maxQuestion:
                time.sleep(2)
                updateProgress = wqIsolateNumbers()
                curQuestion = updateProgress[0]
            else:
                print("Submit button not found in abcQuiz, stopping quiz")
                break
        else:
            print("Choice button not found in abcQuiz, stopping quiz")
            break
        
    return True
        
    
def doDailySets():
    pcDriver.get('https://rewards.bing.com/?signin=1')
    daily = pcDriver.find_elements(By.XPATH, "//*[@id='daily-sets']/mee-card-group[1]/div/mee-card")
    pcDriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    extra = pcDriver.find_elements(By.XPATH, '//*[@id="more-activities"]/div/mee-card')
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
            pcDriver.switch_to.window(pcDriver.window_handles[newWindow])
            
            if 'warpspeed quiz' in text[1] or 'supersonic quiz' in text[1] or 'turbocharge quiz' in text[1]:
                specialQuiz()
            elif 'poll' in text[1]:
                if not clickButton(pcDriver, By.ID, f'btoption{random.randint(0, 1)}'):
                    print("Poll button not found")
            elif 'test your smarts' in text[1] or 'show what you know' in text[1] or 'a, b, or c' in text[1] or 'quiz' in text[2]:
                abcQuiz()
            
            pcDriver.switch_to.window(pcDriver.window_handles[0]) 
            newWindow += 1
        

def getCap():
    pcDriver.get('https://rewards.bing.com/')
    pcDriver.find_element(By.XPATH, '//*[@id="dailypointColumnCalltoAction"]').click()
    pcCap = pcMaxPoints - int(pcDriver.find_element(By.XPATH, '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[1]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.split("/")[0].strip())
    mobileCap = mobileMaxPoints - int(pcDriver.find_element(By.XPATH, '//*[@id="userPointsBreakdown"]/div/div[2]/div/div[2]/div/div[2]/mee-rewards-user-points-details/div/div/div/div/p[2]').text.split("/")[0].strip())
    
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
    searches = []

    while len(searches) < cap/pointsPerSearch:
        suggestion = keywords[random.randint(0, len(keywords)-1)]
        if suggestion not in searches:
            searches.append(suggestion)
    
    return searches

def searchLoop(driver, cap=0):
    searchBar = driver.find_element(By.ID, "sb_form_q")
    searches = generateString(cap)

    print("Searching ", len(searches))
    print("Searches: ", searches)
    
    points = 0
    searchCounter = 0
    while points < cap:
        searchBar = driver.find_element(By.ID, "sb_form_q")
        
        try:
            searchBar.clear()
        except StaleElementReferenceException:
            searchBar = driver.find_element(By.ID, "sb_form_q")
            searchBar.clear()
        time.sleep(0.2)
        try: 
            searchBar.send_keys(searches[searchCounter])
            searchBar.submit()
        except StaleElementReferenceException:
            searchBar = driver.find_element(By.ID, "sb_form_q")
            searchBar.send_keys(searches[searchCounter])
            searchBar.submit()
        
        points += pointsPerSearch # += 5
        searchCounter += 1

# Menu button
# //*[@id="mHamburger"] 
# Signin button
# //*[@id="hb_s"]
def initMobile(mobileCap):
    edgeOptions.add_argument(f'--user-agent={phoneUserAgent}')
    phoneDriver = webdriver.Edge(options=edgeOptions)
    login(phoneDriver)
    phoneDriver.get('https://bing.com')
    clickButton(phoneDriver, By.ID, 'mHamburger')
    clickButton(phoneDriver, By.ID, 'hb_s')
    searchLoop(phoneDriver, mobileCap)

# hotkeys are for turning mobile mode on and off
def doSearch(pcCap, mobileCap):
    searchLoop(pcDriver, pcCap)
    # pyautogui.hotkey('ctrl', 'shift', 'i')
    # time.sleep(1)
    # pyautogui.hotkey('ctrl', 'shift', 'm')
    initMobile(mobileCap)

if __name__ == "__main__":
    login(pcDriver)
    doDailySets()
    
    pcAvailPoints, mobileAvailPoints = getCap()
    while pcAvailPoints != 0 or mobileAvailPoints != 0:
        pcDriver.get('https://bing.com')
        doSearch(pcAvailPoints, mobileAvailPoints)    
        pcAvailPoints, mobileAvailPoints = getCap()
        
    pcDriver.get('https://rewards.bing.com/')
    pcDriver.find_element(By.XPATH, '//*[@id="dailypointColumnCalltoAction"]').click()