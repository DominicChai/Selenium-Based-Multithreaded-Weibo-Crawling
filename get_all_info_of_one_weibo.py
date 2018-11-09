#!/usr/bin/python
#-*- coding:utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
import random
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import os
pd.set_option('display.max_columns',None) #set the display size

def time_sleep():
    downbound=10
    upperbound=20
    division=10
    time.sleep(random.randint(downbound, upperbound)/division)



def login(tup,index):

    try:
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        #加入header 作为伪装的帽子
        dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"


        driver = webdriver.Chrome('/Users/chaidominic/Downloads/chromedriver',desired_capabilities=dcap)
        driver.get('https://passport.weibo.cn/signin/login?entry=mweibo&r=https%3A%2F%2Fweibo.cn%2Fu%2F1916035273&backTitle=%CE%A2%B2%A9&vt=')
        time.sleep(2)
        driver.find_element_by_link_text('第三方帐号').click()
        driver.find_element_by_link_text('QQ帐号登录').click()
        time.sleep(1)
        #driver.find_element_by_xpath("//a[contains(text(),'帐号密码登录')]").click()
        #找不到
        body = driver.find_element_by_xpath("//body")
        print("find it")
        print(body.size)
        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_to_element_with_offset(body, 460, 365)
        action.click()
        action.perform()
        time.sleep(2)

        # fill in qq

        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_to_element_with_offset(body, 450, 190)
        action.click().key_down(tup[0]).perform()

        # fill in pwd

        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_to_element_with_offset(body, 450, 245)
        action.click().key_down(tup[1]).perform()

        # login
        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_to_element_with_offset(body, 450, 300)
        action.click().perform()

        time.sleep(3)
    except:
        global index_set
        index_set.add(index)

    #time.sleep(2)
    #body = driver.find_element_by_xpath("//body")
    #print("find it")
    #print(body.size)
    #action = webdriver.common.action_chains.ActionChains(driver)
    #action.move_to_element_with_offset(body, 525, 250)
    #action.click()
    #action.perform()
    #time.sleep(10) #设置10是为了等待当前进程池里的所有线程登陆了
    return driver
    #登陆成功



def getweibo(driver,uid,each_wb_id):

    datarow_wb = pd.DataFrame()
    datarow_wb['user_id'] = [uid]
    datarow_wb['weibo_text'] = [driver.find_element_by_xpath("//div[@class='c']//div//span[@class='ctt']").text]
    datarow_wb['weibo_id'] = [each_wb_id]
    datarow_wb['time'] = [driver.find_element_by_xpath("//span[@class='ct']").text]
    repost=driver.find_element_by_xpath("//div/span/a[starts-with(text(),'转发')]").text
    if repost!='转发':
        datarow_wb['repost_count'] = [repost.split('[')[1].split(']')[0]]
    else:
        datarow_wb['repost_count'] = [0]

    comment=driver.find_element_by_xpath("//div/span/a[starts-with(text(),'评论')]").text
    if comment!='评论':
        datarow_wb['comment_count'] = [comment.split('[')[1].split(']')[0]]
    else:
        datarow_wb['comment_count'] = [0]

    like=driver.find_element_by_xpath("//div/span[contains(text(),'赞')]").text

    # 被点击过后的a就变成了span
    if like!='赞':
        datarow_wb['like_count'] = [like.split('[')[1].split(']')[0]]
    else:
        datarow_wb['like_count']=[0]

    return datarow_wb
def getlike(like_div,uid,each_wb_id):
    datarow_lk=pd.DataFrame()
    user = like_div.find_element_by_xpath("./a[@href]")

    #print(user.get_attribute('href'))
    #print(user.text)
    #print(like_div.find_element_by_xpath("./span[@class='ct']").text)


    datarow_lk['weibo_id']=[each_wb_id]
    datarow_lk['uid']=[uid]
    datarow_lk['like_uid']=[user.get_attribute('href')]
    datarow_lk['time']=[like_div.find_element_by_xpath("./span[@class='ct']").text]
    #print(datarow_lk)
    return datarow_lk


def getcomment(comment_div, each_wb_id):
    datarow_ct = pd.DataFrame()
    datarow_ct["weibo_id"]=[each_wb_id]

    user = comment_div.find_element_by_xpath("./a[@href]")
    #print(user.get_attribute('href'))
    #print(user.text)
    #print(comment_div.find_element_by_xpath("./span[@class='ctt']").text)
    #tm = comment_div.find_element_by_xpath("./span[@class='ct']")
    #print(tm.text)
    datarow_ct["commentor_id"]=[user.get_attribute('href')]
    datarow_ct["comment"]=[comment_div.find_element_by_xpath("./span[@class='ctt']").text]
    datarow_ct["comment_time"]=[comment_div.find_element_by_xpath("./span[@class='ct']").text]

    return datarow_ct
def getrepost(repost_div,each_wb_id):
    datarow_rp = pd.DataFrame()
    reposter=repost_div.find_element_by_xpath("./a[@href]")
    datarow_rp['weibo_id']=[each_wb_id]
    datarow_rp["repostor_id"]=[reposter.get_attribute('href')]
    datarow_rp["repost_comment"]= [repost_div.text]
    datarow_rp["repost_time"] = [repost_div.find_element_by_xpath("./span[@class='ct']").text]

    return datarow_rp


qq=[('username','pws')] #Ommited here as stated in Notes

global index_set
index_set=set([0,1,2,3,4])
def get_all_wclr_and_store(uid,folder_name):
    global index_set
    #单独占用一份资源'

    if index_set!=set([]):
        index = index_set.pop()
    else: #没有资源了
        return None

    driver = login(qq[index],index)
    print("now use :")
    print(qq[index])

    #对于每一个用户 创建一组csv文件
    dfw = pd.DataFrame(columns=Weibo_feature)
    dfc = pd.DataFrame(columns=Comment_feature)
    dfrp = pd.DataFrame(columns=Repost_feature)
    dfl = pd.DataFrame(columns=Like_features)

    #open user main page
    driver.get('https://weibo.cn/u/'+uid)
    page = driver.find_element_by_xpath("//form[@method='post']").text
    try:
        page_number = int(page.split('/',1)[1].split('页',1)[0])
    except:
        page_number=1

    print("page number is")
    print(page_number)

    #选取前21条weibo
    if page_number>3:
        page_number=3


    url_list=['https://weibo.cn/u/'+uid]
    for i in range(2,page_number+1):
        url_list.append('https://weibo.cn/u/'+uid+'?page='+str(i))

    #每一个url都是一页微博
    #note：再打开某一个微博的时候 要在新的handle打开 爬取结束之后再关掉

    weibo_id_li=[]
    for url in url_list:
        time_sleep()
        driver.get(url)
        weibos = driver.find_elements_by_xpath("//div[@class='c']")
        for weibo in weibos:
            if weibo.get_attribute('id')!='':
                weibo_id_li.append(weibo.get_attribute('id').split('_',1)[1])


    print(weibo_id_li)
    print("total number of weibo is:")
    print(len(weibo_id_li))
    #weibo_id_li 一个用户的所有微博的ID 可以访问所有微博的网页


    #weibo_id_li=[weibo_id_li[0]] #只选取一个weibo

    for each_wb_id in weibo_id_li:

        driver.get("https://weibo.cn/attitude/" + each_wb_id + "?#attitude")

        datarow_wb = getweibo(driver, uid, each_wb_id)
        print(datarow_wb)
        dfw = pd.concat([dfw, datarow_wb], axis=0, ignore_index=False, sort=True)

        try:
            attitude_page = driver.find_element_by_xpath("//div[@id='pagelist']//form[@method='post']").text
            attitude_page_number = int(attitude_page.split('/', 1)[1].split('页', 1)[0])
            print(attitude_page_number)

            attitude_url_li = ["https://weibo.cn/attitude/" + each_wb_id + "?#attitude"]
            for i in range(2, int(attitude_page_number) + 1):
                attitude_url_li.append("https://weibo.cn/attitude/" + each_wb_id + "?&page=" + str(i))
        except:
            attitude_url_li = ["https://weibo.cn/attitude/" + each_wb_id + "?#attitude"]
        print("the len of lk li is: ")
        print(len(attitude_url_li))

        #attitude_url_li=[attitude_url_li[0]]

        for each_attitude_url in attitude_url_li:
            time_sleep()
            driver.get(each_attitude_url)
            all_likes_div = driver.find_elements_by_xpath("//div[@class='c']")[1:-1]
            for like_div in all_likes_div:
                try:
                    datarow_lk = getlike(like_div,uid, each_wb_id)
                    # print(datarow_lk)
                    dfl = pd.concat([dfl, datarow_lk], axis=0, ignore_index=False, sort=True)

                except:
                    pass


        driver.get("https://weibo.cn/comment/"+each_wb_id+"?#rt")
        time.sleep(1)


        try:
            comment_page= driver.find_element_by_xpath("//div[@id='pagelist']//form[contains(@action,'/comment/')]").text
            print(comment_page)
            comment_page_number = int(comment_page.split('/', 1)[1].split('页', 1)[0])


            comment_url_li = ["https://weibo.cn/comment/"+each_wb_id+"?#rt"]
            for i in range(2, int(comment_page_number) + 1):
                comment_url_li.append("https://weibo.cn/comment/" + each_wb_id + "?&page=" + str(i))



        except:
            comment_url_li = ["https://weibo.cn/comment/" + each_wb_id + "?#rt"]
        print("the len of cm li is :")
        print(len(comment_url_li))

        #comment_url_li=[comment_url_li[0]]
        #所有评论的url 评论有很多页

        #遍历每一页的评论 采集 每一页的所有评论

        for each_comment_url in comment_url_li:
            time_sleep()
            driver.get(each_comment_url)
            all_comment_div = driver.find_elements_by_xpath("//div[@class='c']")[1:-1]
            for comment_div in all_comment_div:
                try:
                    datarow_ct = getcomment(comment_div, each_wb_id)
                    #print(datarow_ct)
                    dfc = pd.concat([dfc, datarow_ct], axis=0, ignore_index=False, sort=True)
                except:
                    pass



        driver.get("https://weibo.cn/repost/" + each_wb_id + "?#rt")
        time.sleep(1)
        try:
            repost_page = driver.find_element_by_xpath("//div[@id='pagelist']//form[contains(@action,'/repost/')]").text
            print(repost_page)
            repost_page_number = int(repost_page.split('/', 1)[1].split('页', 1)[0])

            repost_url_li = ["https://weibo.cn/repost/" + each_wb_id + "?#rt"]
            for i in range(2, int(repost_page_number) + 1):
                repost_url_li.append("https://weibo.cn/repost/" + each_wb_id + "?&page=" + str(i))
            print(repost_url_li)
        except:
            repost_url_li = ["https://weibo.cn/repost/" + each_wb_id + "?#rt"]

        print("the len of rp li is")
        print(len(repost_url_li))

        #repost_url_li = [repost_url_li[0]]

        for each_repost_url in repost_url_li:
            time_sleep()
            #if random.randint(1, upperbound) == 1:
            #time.sleep(random.randint(1,5)/10)
            #else:
                #pass
            driver.get(each_repost_url)
            all_repost_div = driver.find_elements_by_xpath("//div[@class='c']")[1:-1]
            for repost_div in all_repost_div:
                try:

                    datarow_rp = getrepost(repost_div, each_wb_id)
                    #print(datarow_rp)
                    dfrp = pd.concat([dfrp, datarow_rp], axis=0, ignore_index=False, sort=True)

                except:
                    pass

    encoding = 'utf-8'
    if dfw.shape[0]!=0:
        dfw.to_csv('./'+folder_name+'/Weibos of uid='+uid+'.csv', encoding=encoding)
    if dfc.shape[0] != 0:
        dfc.to_csv('./'+folder_name+'/Comment of uid='+uid+'.csv', encoding=encoding)
    if dfrp.shape[0] != 0:
        dfrp.to_csv('./'+folder_name+'/Relation of reposted of uid='+uid+'.csv', encoding=encoding)
    if dfl.shape[0]!=0:
        dfl.to_csv('./'+folder_name+'/Like of uid='+uid+'.csv', encoding=encoding)

    #归还qq账号
    index_set.add(index)

#定义特征
Weibo_feature=["user_id",'user_name',
               'weibo_id','weibo_text',
               'time',#微博的发布时间很关键
                "from",
               "repost_count","comment_count","like_count"]

Comment_feature=["weibo_id","commentor_id","comment","comment_time", \
                 "comment_like_count","re-comment"]


Repost_feature=["weibo_id","repost_user_id","repost_time","repost_comment"]

Like_features = ['weibo_id','uid','like_uid','time']


#建立一个文件夹
current_time = time.strftime("%Y,%m,%d,%H,%M")
folder_name = current_time
os.mkdir('./'+folder_name)

#读取用户群
import pandas as pd
df = pd.read_csv('Users-l1.csv')
print(df.columns)
id = df['user_id'].tolist()
print(id)
id_li=[]
for each in id:
    id_li.append(each.split('=')[1].split('&')[0])
print(id_li)
print(len(id_li))
id_li=list(set(id_li))
print("after set-ilize:")
print(len(id_li))

#对每一个用户，开启一个线程,对于每一个线程，要重新启动一次driver

import threadpool

arg_list=[]

for each in id_li:
    arg_list.append(([each,folder_name],None))

start_time = time.time()
pool = threadpool.ThreadPool(5)


requests = threadpool.makeRequests(get_all_wclr_and_store, arg_list)
[pool.putRequest(req) for req in requests]
pool.wait()
print("exexcute time is:" + str(time.time() - start_time))


