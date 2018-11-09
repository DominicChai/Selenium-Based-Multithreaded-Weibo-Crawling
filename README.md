# Selenium-Based-Multithreaded-Weibo-Crawling
Use Python Selenium and BeautifulSoup architecture to develop dynamic multi-thread data crawlers, collect big data(GB-level) of Weibo.com(A big social network web in China) 

# Requirements
1. python>=3.4.0 and pycharm on MacOS
2. selenium = 3.14.0
3. threadpool = 1.3.2


# Installation
python3.4 -m pip install -r requirements.txt --upgrade


# Dependencies

In order to run this project, please download chrome driver from (https://sites.google.com/a/chromium.org/chromedriver/downloads) and refer to it in your code before using selenium

# Notes
1. Since this research project is still being worked, a demo for crawling all the users information is showed in get_all_user_info.py, a demo for crawling all the reposts, comments and likes of one weibo is showed in get_all_info_of_one_weibo.py
2. As a demo, only csv files are stored as output
3. Due to the consideration for privacy, the login usernames and passwords are omitted, please register and create your own account/accounts and then crawl the data, in the code we assume each thread is supported by a login user, if you have more username-password pool and enough CPU, you can create more threads and crawl data faster
