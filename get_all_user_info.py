#!/usr/bin/python
#-*- coding:utf-8 -*-
from selenium import webdriver
import csv
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
pd.set_option('display.max_columns',None) #set the display size
import time
start = time.time()
fail = 0

def getUser(tup):
    print("now open "+tup[2])
    driver.get(tup[2])

    #规定更多的层级
    time.sleep(2)
    try:
        more_txt = driver.find_element_by_xpath("//div[@class='PCD_person_info']/a")
        more_txt.click()
        fail = 0
    except:
        fail = 1
        return None

    datarow=pd.DataFrame()
    datarow["user_id"]=[tup[1]]
    datarow["user_name"]=[tup[0]]
    datarow["url"] = [tup[2]]

    time.sleep(1)
    try:
        datarow["province and city"]=[driver.find_element_by_xpath("//span[contains(text(),'所在地')]/following-sibling::*").text]
    except:
        datarow["province and city"]=None

    #所在地：
    #注意 这个ul是自动生成的 所以li的数量每个用户都不相同
    #所以需要用关键词的next sibling来定位更为准确
    try:
        datarow["birthday(age)"]=[driver.find_element_by_xpath("//span[contains(text(),'生日')]/following-sibling::*").text]
    except:
        datarow["birthday(age)"]=None
    try:
        datarow["description"]=[driver.find_element_by_xpath("//span[contains(text(),'简介')]/following-sibling::*").text]
    except:
        datarow["description"]=None
    try:
        datarow["gender"]=[driver.find_element_by_xpath("//span[contains(text(),'性别')]/following-sibling::*").text]
    except:
        datarow["gender"]=None
    try:
        datarow["follows_count"]=[driver.find_element_by_xpath("//span[contains(text(),'关注')]/preceding-sibling::strong").text]
    except:
        datarow["follows_count"]=None
    try:
        datarow["followers_count"]=[driver.find_element_by_xpath("//span[contains(text(),'粉丝')]/preceding-sibling::strong").text]
    except:
        datarow["followers_count"]=None
    try:
        datarow["weibos_count"]=[driver.find_element_by_xpath("//span[contains(text(),'微博')]/preceding-sibling::strong").text]
    except:
        datarow["weibos_count"]=None

    try:
        datarow["created_at"] = [driver.find_element_by_xpath("//span[contains(text(),'注册时间')]/following-sibling::*").text]
    except:
        datarow["created_at"] = None

    print(datarow)

    return datarow


driver = webdriver.Chrome('/Users/chaidominic/Downloads/chromedriver')
driver.get('https://huati.weibo.cn/discovery/super?extparam=ctg1_166')


# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

#找到所有的超级话题
time.sleep(2)
super_topics =driver.find_elements_by_xpath("//em[@class='super_name txt-cut']")

for each_topic in super_topics:
    print(each_topic.text)


#对于每一个超级话题，采集所有帖子
#移动版的下拉之后加载不出来全部的微博
#获取张云雷的超级话题页面的网址 解析后转到网页版
super_topics[3].click()
current_url = driver.current_url
title = driver.title
print(current_url)
print(title)

Users_feature = ["user_id", "user_name",
                     "province and city", "birthday(age)", "description",
                     "url",
                     #"domain",  # 个性化域名
                     "gender",

                     "followers_count",  # 粉丝数
                     "follows_count",  # 关注数
                     "weibos_count",  # 微博数
                     #"favourites_count",  # 收藏数

                      "created_at" #"following","allow_all_act_msg","geo_enabled","verified",
                     # "allow_all_comment", #是否允许所有人对我的微博进行评论，true：是，false：否
                     #"bi_followers_count",
                     #"博主类型", "影响力信息", "昨日微博阅读数", "近期微博阅读数", "昨日互动数", "近期粉丝增量"
                     ]
dfu = pd.DataFrame(columns=Users_feature)

# 新开一个窗口，通过执行js来新开一个窗口

super_index_id=current_url.split('containerid=',1)[1].split('&',1)[0]

url_list=["https://weibo.com/p/"+super_index_id+"/super_index"]
for i in range(2,24):
    url_list.append("https://weibo.com/p/10080828e924294c96b3bdf91723df198835bd/super_index?page="+str(i))

#获取张云雷网页版的超级话题之下的所有发帖的用户 最关键的是用户ID

user_list=[]
SCROLL_PAUSE_TIME = 3
for each_url in url_list:
    driver.get(each_url)
    time.sleep(2)
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    users = driver.find_elements_by_xpath("//a[@class='W_f14 W_fb S_txt1']")
    for eachuser in users:
        tup=(eachuser.text,eachuser.get_attribute('usercard'),eachuser.get_attribute('href'))
        user_list.append(tup)
        print(len(user_list))

print(user_list)
print("the number of users is ")
print(len(user_list))

for each in user_list:
    print(each)
    #注意你写两次函数 就是调用两次函数 也就是对多出来一倍的时间用来check if
    if fail==0:
        dfu = pd.concat([dfu, getUser(each)], axis=0, ignore_index=False,sort=True)
print("the dfu is ")
print(dfu)


encoding = 'utf-8'
dfu.to_csv('Users'+str(super_topics[2])+'.csv', encoding=encoding)

end = time.time()
running_time = end-start
print("running time:")
print(running_time)


#driver.close()
