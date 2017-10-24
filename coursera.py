import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup as BS
from selenium.webdriver.support.ui import WebDriverWait as wait
import shutil
import os
import json
import urllib
api_url = "https://api.coursera.org/api/courses.v1?start=0&limit=2890&includes=instructorIds,partnerIds,specializations,s12nlds,v1Details,v2Details&fields=instructorIds,partnerIds,specializations,s12nlds,description"
data = requests.get(api_url).json()

url='https://www.coursera.org/learn/'
slug=[]
for each in data['elements']:
    slug.append(each['slug'])

names=[]
for each in data['elements']:
    names.append(each['name'])

des=[]
for each in data['elements']:
    des.append(each['description'])
browser = webdriver.Firefox()
start_date=[]
level=[]
subjects=[]
prereq=[]
enroll_now_link=[]
price=[]
instr=[]
providers=[]
subtitles=[]
course_language=[]
course_image=[]
reviews=[]
syllabus=[]
Specialization=[]
others_in_Specialization=[]
index=0
for each in slug[:9]:
    browser.get(url + each)
    time.sleep(3)
    enroll_now_link.append(url+each)
    level_flag = 0
    for every in browser.find_elements_by_tag_name('tr'):
        if(every.text.find('Level')==0):
            level.append(every.text[6:])
            level_flag =1
    if(level_flag==0):
        level.append('none')
    special=0
    for every in browser.find_elements_by_tag_name('tr'):
        if(every.text.find('Basic Info')==0):
            if(every.text.find('Specialization')):
                Specialization.append('yes')
                special=1
                browser.find_element_by_xpath("//div[@class='rc-CourseS12nInfo']/span/a").click()
                time.sleep(3)
                browser.switch_to.window(browser.window_handles[1])
                other_courses=browser.find_elements_by_tag_name('h2.course-name.headline-5-text')
                other_courses=[x.text for x in other_courses]
                #if names[index] in other_courses:
                others_in_Specialization.append(other_courses)#.remove(names[index]))
                browser.close()
                #browser.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
                browser.switch_to.window(browser.window_handles[0])
                break


    if(special==0):
        Specialization.append('no')
        others_in_Specialization.append('none')
    try:
        subjects.append(browser.find_elements_by_tag_name("a.link.nostyle")[2].text)
    except:
        subjects.append(browser.find_elements_by_tag_name("a.link.nostyle")[1].text)
    try:
        prereq.append(browser.find_element_by_tag_name("div.target-audience-section").text)
    except:
        prereq.append('none')
    try:
        start_date.append(browser.find_element_by_xpath("//div[@class='startdate.rc-StartDateString.caption-text']").text[7:])
    except:
        start_date.append('always-available')
    
    providers_link = browser.find_elements_by_tag_name("img.creator-logo")
    list_of_providers=[]
    for ix in range(len(providers_link)): 
        pro_dic ={}
        pro_dic['names'] = providers_link[ix].get_attribute('alt')
        logo = providers_link[ix].get_attribute('src')
        urllib.request.urlretrieve(logo ,each+'_provider_'+str(ix))
        pro_dic['logo']= os.getcwd() + '/'+each+'_provider_'+str(ix)
        list_of_providers.append(pro_dic)
    providers.append(list_of_providers)
    
    instr_link = browser.find_elements_by_tag_name('div.instructor-info.bt3-col-xs-8.bt3-col-sm-10')
    instr_photo_link= browser.find_elements_by_tag_name("img.bt3-img-circle")
    list_of_instructors = []
    for ix in range(len(instr_link)):
        instr_dic={}
        instruct_imgs = browser.find_elements_by_tag_name("img.bt3-img-circle")[ix].get_attribute('src')
        urllib.request.urlretrieve(instruct_imgs , each+'_instr_'+str(ix))
        instr_dic['imgs'] = os.getcwd() + '/'+each+'_instr_'+str(ix)
        x = instr_link[ix].text
        try:
            instr_dic['name'] = x[x.index(',')+1 : ]
            instr_dic['details'] = x[10 : x.index(',')]
        except:
            instr_dic['name'] = x
            instr_dic['details'] = 'none'
        list_of_instructors.append(instr_dic)
    instr.append(list_of_instructors)    
    
   
    
    a=browser.find_element_by_tag_name("div.rc-Language").text
    try:
        subtitles.append(a[a.index('Subtitles:')+11:])
    except:
        subtitles.append('none')
    course_language.append(a.split()[0])
   
    cover = browser.find_element_by_tag_name("div.body-container").get_attribute('style')[23:-3]
    urllib.request.urlretrieve(cover,each+'_cover')
    course_image.append(os.getcwd() + '/'+each+'_cover')

    try:
        a=browser.find_elements_by_tag_name("button.cdp-view-all-button")
        a[1].click()
        time.sleep(5)
        a=browser.find_elements_by_tag_name("div.rc-CML.styled")
        reviews.append([every.text for every in a])
        X = browser.find_element_by_tag_name("div.c-modal-x-out")
        X.click()
        time.sleep(3)
    except:
        a=browser.find_elements_by_tag_name("div.rc-CML.review-comment-cml.styled")
        reviews.append([every.text for every in a])

    syllabus.append(browser.find_element_by_tag_name("div.rc-WeekView").text.replace('expand','more info'))

    source = browser.page_source
    soup = BS(source)
    y=soup.find_all("script")
    for z in y:
        if z.get_text().find('window.App')>0:
            cc=str(z.get_text)
            num=cc.find('window.App')
            last=cc.find('window.appName')
            d=cc[num+11:last-6]
            js=json.loads(d)

    fee=''
    cost = js['context']['dispatcher']['stores']['NaptimeStore']['data']['productPrices.v3']
    for a in cost:
        for b in cost[a]:
            if(b=='finalAmount'):
                fee=str(cost[a][b])+' '+str(cost[a]['currencyCode'])
                price.append(fee)
                break
    if(fee==''):
        price.append('free')
    index += 1

d={'title':names[:9],
    'description':des[:9],
    'level':level,
    'subject':subjects,
    'prerequisites':prereq,
    'enroll_now_link':enroll_now_link,
    'price':price,
    'instructors':instr,
    'Providers':providers,
    'subtitles':subtitles,
    'course_language':course_language,
    'course_image':course_image,
    'reviews':reviews,
    'syllabus':syllabus,
    'start date':start_date,
    'Specialization':Specialization,
    'others_in_Specialization':others_in_Specialization
    }
info = pd.DataFrame(data=d)
os.chdir('/home/prashant/Voilas')
info.to_excel('coursera_courses_test.xlsx') 