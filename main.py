import os
import sys
import time
import pathlib
from tqdm.auto import tqdm
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
import requests
from bs4 import BeautifulSoup

sleepamt = 1

def download_video(url):
    if url is None:
        return
    download_bttn="/html/body/span/label/input"
    time.sleep(sleepamt)
    #page = requests.get(url)
    options = Options()
    #options.add_argument('--headless')
    options.add_argument('--log-level=3')
    #driver = webdriver.Chrome(options=chromeOptions)
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    try:
        driver.get(url)
    except Exception as e:
        print(e)
        print(url)
        print("AN ERROR HAS OCCURRED. URL IS BUSTED")
        return

    delay = 7 # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, download_bttn)))
        print ("Page is ready!")
        time.sleep(2)
    except TimeoutException:
        print ("Loading took too much time!")

    driver.find_element(By.XPATH, download_bttn).click()

    ul = driver.find_element(By.XPATH,' /html/body/span/label/ul')
    c = ul.find_elements(By.XPATH, './child::*')

    current = 0
    largest = None
    for each in c:
        if float(each.text.split(' ')[1].split(' ')[0].lstrip('(')) >= current:
            largest = each
            current = float(each.text.split(' ')[1].split(' ')[0].lstrip('('))
        #print(each.text.split(' ')[1].split(' ')[0].lstrip('('))
    #print("large", largest)
    print("Largest file is: ",current, "Resolution",largest.text.split(' ')[0].rstrip(' '))
    #largest.click()
    #print("done url", largest.find_elements(By.XPATH, './child::*')[0].get_attribute('href'))
    storage = str(largest.find_elements(By.XPATH, './child::*')[0].get_attribute('href'))
    time.sleep(1)
    driver.quit()
    return  storage
    #print(r.html.url)


def download_page(url):
    time.sleep(sleepamt)
    page = requests.get(url)

    soup = BeautifulSoup(page.text, 'html.parser')

    # Gets title of episode
    title = soup.find(class_='data')
    title_parsed = title.find_all('h1')
    print("Found:",title_parsed[0].contents[0])
    conf_title=title_parsed[0].contents[0]

    spl = "Episode"
    base="./Hentai/"
    spllist = str(conf_title).split(spl)
    for each in spllist:
        try:
            print(each.replace(":",""))
            spllist[spllist.index(each)] = each.replace(":","")
        except Exception as e:
            print(e)
        try:
            spllist[spllist.index(each)] = each.replace("/","")
        except Exception as e:
            print(e)
    if not os.path.exists(base):
        os.mkdir(base)
    if not os.path.exists(base + spllist[0].rstrip(' ')+'/'):
        os.mkdir(base + spllist[0].rstrip(' ')+'/')
    if not len(spllist) >= 2:
        spllist.append('1')
    if os.path.exists(base + spllist[0].rstrip(' ')+'/' + spllist[0].rstrip(' ')+ " Episode "+ spllist[1]+".mp4"):
        print("Already seen skipping...")
        return



    # Gets tags associated with video

    tags_parsed = soup.find_all('a')
    taglist=[]
    for each in tags_parsed:
        try:
            #print(each)
            if each.get('rel')[0] == 'tag'  :
                #print(str(each.contents[0]).lstrip().rstrip())
                taglist.append(str(each.contents[0]).lstrip().rstrip())
        except Exception as e:
            pass

        #else:
            #print("not",each)
    # Gets embedded url for downloading
    url = soup.find(class_='sbox fixidtab')
    url_parsed= url.attrs["data"]

    if not url_parsed is None:
        validlink = download_video(url_parsed)

    file_managment(conf_title, validlink, taglist)
    return
def genre_scrape(url):
    time.sleep(sleepamt)
    page = requests.get(url)

    soup = BeautifulSoup(page.text, 'html.parser')
    episode_list = soup.find_all('a', href=True)
    cleaned=[]
    loop = True
    cnt=1
    loops = 3
    while cnt != loops:
        while loop:
            for each in episode_list:
                if "hentaihaven.red/hentai/" in each['href']:
                    cleaned.append(each['href'])
            pages = soup.find_all(class_='pagination')
            last = str(str(pages[0].text).split(' ')[3])[0]
            #print('last',last, str(pages[0].text).split(' ')[1])
            if int(last) == int(str(pages[0].text).split(' ')[1]):
                loop=False
            else:
                #current page number plus 1
                p1= int(str(pages[0].text).split(' ')[1]) + 1
                change = url.rstrip('/')+ '/page/' + str(p1)
                page = requests.get(change)
                soup = BeautifulSoup(page.text, 'html.parser')
                episode_list = soup.find_all('a', href=True)
                for each in cleaned:
                    print(each)
        cnt += 1
    cleaned = list(set(cleaned))
    for each in cleaned:
        download_page(each)

def file_managment(title, url, tags):
    spl = "Episode"

    base="./Hentai/"

    spllist = title.split(spl)
    if not os.path.exists(base):
        os.mkdir(base)
    if not os.path.exists(base + spllist[0].rstrip(' ')+'/'):
        os.mkdir(base + spllist[0].rstrip(' ')+'/')

    print("Downloading: ", spllist[0].rstrip(' ') + "/" + spllist[0].rstrip(' ')+ " Episode "+ spllist[1]+".mp4")

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(base+spllist[0].rstrip(' ') + "/" + spllist[0].rstrip(' ')+ " Episode "+ spllist[1]+".mp4", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    f = open(base+spllist[0].rstrip(' ') + "/" + "Episode "+ spllist[1]+".txt", "a")
    for each in tags:
        f.write(each + '\n')
    f.close()
    return
def search_scrape(url):
    time.sleep(sleepamt)
    page = requests.get(url)

    soup = BeautifulSoup(page.text, 'html.parser')
    episode_list = soup.find_all('a', href=True)
    cleaned=[]
    for each in episode_list:
        if "hentaihaven.red/hentai/" in each['href']:
            cleaned.append(each['href'])

    # This will download the videos to disk
    print("I have", len(cleaned), "items to download.")
    for each in cleaned:
        download_page(each)

# BEGIN ON INITAL START
os.environ['WDM_LOG_LEVEL'] = '0'


# gets input from commandline
input_len = len(sys.argv)
argv = sys.argv
if input_len == 1:
    link=input("Give me link: ")
else:
    link=sys.argv[-1]

# Parses the url link determines if its a valid link.

if "hentaihaven.red/hentai/" in link:
    download_page(link)
elif "htstreaming.com" in link:
    download_video(link)
elif "hentaihaven.red/?s=" in link:
    search_scrape(link)
elif "hentaihaven.red/genre" in link:
    genre_scrape(link)

else:
    print("Unknown video")


