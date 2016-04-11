# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
from time import sleep
import mysql.connector



cnx = mysql.connector.connect(user="root", password="nivlek0", host="127.0.0.1", database="ebay_and_taobao")
cur = cnx.cursor()


def insert_comments(user_id, user_name, comment, reply):
    try:
        query = "INSERT INTO taobao_records (seller_id, seller_name, commentText, reply) VALUES (%d, '%s', '%s', '%s')" %(user_id, user_name, comment, reply)
        # print query
        cur.execute(query)
        cnx.commit()
    except:
        print "insert comment error"


def insert_user(driver):
    try:
        username = driver.find_element_by_class_name("tb-shop-seller").find_element_by_tag_name("dd").text
    except:
        print "username error"

    userlevel = ""
    levelnum = 0
    # if level=cap
    try:
        level = driver.find_element_by_css_selector(".tb-shop-rank.tb-rank-cap")
        userlevel = "cap"
    except:
        pass

    # if level=red
    try:
        level = driver.find_element_by_css_selector(".tb-shop-rank.tb-rank-blue")
        userlevel = "blue"
    except:
        pass

    # if level=red
    try:
        level = driver.find_element_by_css_selector(".tb-shop-rank.tb-rank-red")
        userlevel = "blue"
    except:
        pass

    # get levelnum
    try:
        i_tag = level.find_elements_by_tag_name("i")
        levelnum = len(i_tag)
    except:
        pass

    # print seller_name, userlevel, levelnum
    #sql INSERT
    try:
        query = "INSERT INTO taobao_seller (seller_name, prestige, prestige_num) VALUES ('%s', '%s', %d)" %(username, userlevel, levelnum)
        # print query
        cur.execute(query)
        cnx.commit()
    except:
        print "insert error"


    query = ("SELECT seller_id FROM taobao_seller WHERE seller_name='%s'" %username)
    # print query
    cur.execute(query)
    seller_id = int(cur.fetchone()[0])
    return seller_id, username


def subpage(driver, href):
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
    driver.get(href)
    sleep(5)
    click_flag = 0
    try:
        driver.find_element_by_class_name("J_ReviewsCount").click()
        click_flag = 1
    except:
        pass

    try:
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
    driver = webdriver.Firefox()
    driver.get("https://www.taobao.com")
    sleep(10)
    driver.get("https://s.taobao.com/search?q=%E5%B7%A7%E5%85%8B%E5%8A%9B&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.50862.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20160331")
    sleep(2)
    driver.find_element_by_xpath("//a[@data-value='renqi-desc']").click()
    sleep(2)
    url_pattern = re.compile(r".*taobao\.com\/item\.htm\?id=*")
    counter = 0
    sleep(2)
    while 1:
        try:
            driver.find_element_by_css_selector(".icon.icon-btn-next-2").click()
            sleep(2)

            a = driver.find_elements_by_class_name("J_ClickStat")
            for item in a:
                href = item.get_attribute("href")
                counter += 1
                if url_pattern.match(href) and counter%2 == 0:
                    subpage(driver, href)


        except:
            pass
    driver.close()

if __name__ == '__main__':
    main()
