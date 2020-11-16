from bs4 import BeautifulSoup
import urllib2
import mysql.connector
import re

#database/mysql setup, specify the database name with login credentials.
cnx = mysql.connector.connect(user="root", password="nivlek0", host="127.0.0.1", database="ebay_and_taobao")
cur = cnx.cursor()

#this is a function to get the ebay url from a page.
def url_maker(page):
    skc = 48*page
    base_url = "http://www.ebay.com/sch/i.html?_from=R40&_sacat=0&_dmd=2&_nkw=chocolate&_pgn=%d&_skc=%d&rt=nc" %(page, skc)
    print base_url
    return base_url

def seller_page_parse(html):
    soup = BeautifulSoup(html, "html.parser")
    seller = soup.find("span", attrs={"class": "mbg-nw"}).contents
    grade = soup.find("span", attrs={"class": "mbg-l"}).get_text()
    searchRst = re.search("[0-9]+", grade)
    seller_rate = searchRst.group(0)

    try:
        seller = seller[0].decode()
        print seller
        feedback = soup.find_all("tr", attrs={"class", "fbOuterAddComm"})
        if len(feedback) != 0:
            print "enter"
            try:
                query = ("INSERT INTO ebay_seller (seller_name, seller_rate) VALUES ('%s', %s);" %(seller, seller_rate))
                print query
                cur.execute(query)
                cnx.commit()
            except:
                pass

            query = ("SELECT seller_id FROM ebay_seller WHERE seller_name='%s'" %seller)
            cur.execute(query)
            seller_id = int(cur.fetchone()[0])

            for fee in feedback:
                feedbackSoup = BeautifulSoup(str(fee), "html.parser")
                userFeedback = feedbackSoup.find_all("td")[1].contents[0].decode()
                print userFeedback
                sellerReply = fee.next_sibling.find("span").contents[0].decode()
                print sellerReply

                itemName = fee.next_sibling.next_sibling.find_all("td")[1].contents[0].decode()
                print itemName

                price = fee.next_sibling.next_sibling.find_all("td")[2].contents[0].decode()
                print price
                try:
                    query = ("INSERT INTO ebay_records (seller_id, seller_name, commentText, reply) VALUES (%d, '%s', '%s', '%s');" %(seller_id, seller, userFeedback, sellerReply))
                    cur.execute(query)
                    cnx.commit()
                except:
                    pass
    except:
        pass


def item_page_parse(html):
    soup = BeautifulSoup(html, "html.parser")

    si_content = soup.find("div", attrs={"class": "si-content"})
    si_soup = BeautifulSoup(str(si_content), "html.parser")
    ahref = si_soup.find("span", attrs={"class": "mbg-l"}).a["href"] + "&which=negative&interval=365&items=200"
    print ahref
    # ahref = "http://feedback.ebay.com/ws/eBayISAPI.dll?ViewFeedback2&userid=qiang1989zhi&iid=231656958135&de=off&items=200&which=negative&interval=365&_trkparms=negative_365"
    html = urllib2.urlopen(ahref).read()
    seller_page_parse(html)


def search_page_parse(html):
    soup = BeautifulSoup(html, "html.parser")
    lis = soup.find_all("li", attrs={"class": "sresult gvresult"})
    for li in lis:
        lihtml = str(li)
        lisoup = BeautifulSoup(lihtml, "html.parser")
        link = lisoup.find("div", attrs={"class": "gvtitle"}).h3.a["href"]
        print link
        try:
            html = urllib2.urlopen(link).read()
            item_page_parse(html)
        except:
            pass


def main():
    count = 500
    page = 0
    while count>0:
        try:
            url = url_maker(page)
            html = urllib2.urlopen(url).read()
            search_page_parse(html)
            page += 1
        except:
            pass

if __name__ == '__main__':
    main()
