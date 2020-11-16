# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
from time import sleep
import mysql.connector


# database/mysql setup, specify the database name with login credentials.
cnx = mysql.connector.connect(user="root", password="nivlek0", host="127.0.0.1", database="ebay_and_taobao")
cur = cnx.cursor()

# this is a function to add comments into database
def insert_comments(user_id, user_name, comment, reply):
    try:
        # to insert data into a database
        # step 1: write a query, specify the info to be inserted: sellerId, sellerName, comments, and reply
        query = "INSERT INTO taobao_records (seller_id, seller_name, commentText, reply) VALUES (%d, '%s', '%s', '%s')" %(user_id, user_name, comment, reply)
        # step 2: execute the query
        cur.execute(query)
        cnx.commit()
        # after the commit, data should be inserted into database already
    except:
        print "insert comment error"


# this function is to get the data(seller id, seller username) info on seller's page.
# meanwhile, insert seller info(username, userlevel, levelnum) into database.
# the data are found by finding the corresponding tags on the page.
def insert_user(driver):
    # 1, get seller'name
    try:
        username = driver.find_element_by_class_name("tb-shop-seller").find_element_by_tag_name("dd").text
    except:
        print "username error"

    # 2, get the seller/shop ranking level(userlevel in the code)
    userlevel = ""
    levelnum = 0

    # here initially we don't know what the user level the seller has.
    # there're three levels: cap, blue, red
    # in order to find the level of the seller, we need to check if we can find the symbol of each level.
    # if level=cap
    try:
        # let's try to find cap by finding the symbol: .tb-shop-rank.tb-rank-cap
        level = driver.find_element_by_css_selector(".tb-shop-rank.tb-rank-cap")
        # if here we have no error, that means we found cap, which means the ranking level of the seller is cap. 
        # assign user level to variable "cap".
        userlevel = "cap"
        # after the assignment, it goes to the next step (line 59)
        # [IMPORTANT ALER! we have an assumption: the seller level can have only one of these "cap", "blue", "red"
        # so even the userlevel is assigned here, when it goes to the next step, it will hit except and do nothing and the userlevel will not be changed.]
        now we have user level = "cap", 
    except:
        # if finding the level cap got error, the code breaks before assigning userLevel = "cap" and goes here
        # then we will continue to find if the seller's page has blue on the next step (line 59)
        pass

    # if level=blue
    try:
        level = driver.find_element_by_css_selector(".tb-shop-rank.tb-rank-blue")
        userlevel = "blue"
    except:
        pass

    # if level=red
    try:
        level = driver.find_element_by_css_selector(".tb-shop-rank.tb-rank-red")
        userlevel = "red"
    except:
        pass

    # 3, get level number
    try:
        i_tag = level.find_elements_by_tag_name("i")
        levelnum = len(i_tag)
    except:
        pass

    # store the info we fetch (seller_name, userlevel, levelnum) into database
    # sql INSERT
    try:
        query = "INSERT INTO taobao_seller (seller_name, prestige, prestige_num) VALUES ('%s', '%s', %d)" %(username, userlevel, levelnum)
        # print query
        cur.execute(query)
        cnx.commit()
    except:
        print "insert error"

    # the seller id would be automatically generated when the seller info was inserted
    # here we get the seller id of the seller from our database by executing "select" query
    query = ("SELECT seller_id FROM taobao_seller WHERE seller_name='%s'" %username)
    # print query
    cur.execute(query)
    seller_id = int(cur.fetchone()[0])
    return seller_id, username


def subpage(driver, href):
    # open a new page by pressing "command" + "t"
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
    # go the seller's page url
    driver.get(href)
    # let the system wait for 5 seconds to pretend this is a human. 
    sleep(5)

    # to check reviews on the seller's page
    click_flag = 0
    try:
        # try to find reviews and click into it, if we find it, click-flags = 1, it means we mark it as clicked.
        driver.find_element_by_class_name("J_ReviewsCount").click()
        click_flag = 1
    except:
        pass

    try:
        # if we didn't click into "reviews", we click into anchor.(another alternate review section I guess)
        if click_flag == 0:
            driver.find_element_by_class_name("tb-tab-anchor").click()
    except:
        pass

    sleep(5)
    try:
        # check if exist bad comments
        bad_comments_num = driver.find_element_by_xpath("//li[@data-kg-rate-filter-val='-1']/label/span").text
        print bad_comments_num
        if bad_comments_num != "(0)":
            # good comments
            # driver.find_element_by_xpath("//li[@data-kg-rate-filter-val='1']").click()
            # bad comments
            driver.find_element_by_xpath("//li[@data-kg-rate-filter-val='-1']").click()
            sleep(5)
            bad_comments = driver.find_elements_by_class_name("tb-rev-item")
            print len(bad_comments)
            flag = 0
            user_id = 0
            user_name = ""
            # check the bad comments
            for bad_comment in bad_comments:
                # print bad_comment.find_element_by_tag_name("div").text
                try:
                    reply = bad_comment.find_element_by_class_name("reply").text
                    if (flag == 0): # add addition
                        user_id, user_name = insert_user(driver)
                        print user_id, user_name
                        flag = 1
                    comment = bad_comment.find_element_by_tag_name("div").text
                    insert_comments(user_id, user_name, comment, reply)
                except:
                    pass

            sleep(4)
    except:
        pass

    sleep(2)
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')
    sleep(2)





def main():
    # use firefox
    driver = webdriver.Firefox()

    # open taobao page
    driver.get("https://www.taobao.com")

    # wait for 10 sec to make sure the page is fully loaded
    sleep(10)

    # get to search a bunch of keywords in taobao
    driver.get("https://s.taobao.com/search?q=%E5%B7%A7%E5%85%8B%E5%8A%9B&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.50862.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20160331")
    sleep(2)

    # do what a human do, to click a link
    driver.find_element_by_xpath("//a[@data-value='renqi-desc']").click()
    sleep(2)
    url_pattern = re.compile(r".*taobao\.com\/item\.htm\?id=*")

    # we are on page 1, in programming language, no matter what language, we count numbers always starting from 0 instead of 1
    counter = 0
    sleep(2)

    # in programming language, 1 == true, so this while loop keeps running and won't stop until it get a error.
    # in this case, only when there's no next button on the page, which means we're already on the last page.
    while 1:
        try:
            driver.find_element_by_css_selector(".icon.icon-btn-next-2").click()
            sleep(2)
            
            # seems like the J_ClickStat is something that can help us to get a list of sellers.
            a = driver.find_elements_by_class_name("J_ClickStat")
            # once we have a list of sellers, we iterate/go through each seller, and click into the seller's page
            for item in a:
                # get the link to the seller's page
                href = item.get_attribute("href")
                # count how many sellers we've checked
                counter += 1

                # we want to double check if the link we got is a seller's page link. it needs a match to our seller url pattern.
                # if it matches and it's a seller's page link. 
                if url_pattern.match(href) and counter%2 == 0:
                    # go to a page and get seller's info
                    subpage(driver, href)


        except:
            pass
    # close your browser and everything's done! Yay!
    driver.close()

if __name__ == '__main__':
    # this is the main function that you let your computer know where is the first line of code to read.
    main()
