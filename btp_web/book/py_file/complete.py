import requests
from bs4 import BeautifulSoup
k = "ritu tiwari springer"
j = "http://www.amazon.in/"
r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords="+k)
soup = BeautifulSoup(r.content, "html.parser")

link_list = []
title_list = []
img_list = []
prize_list = []
t = []

for i in soup.find_all("li"):
    book_title = i.find_all("h2")
    title = ''
    f_title = 0
    for j in book_title:
        if len(j) != 0:
            if f_title == 0:
                title = j.get("data-attribute")
                f_title += 1
                t.append(title)
    book_link = i.find_all("a",{"class":"a-link-normal a-text-normal"})
    f_link = 0
    for j in book_link:
        #print(j.text)
        if len(j) != 0:
            if f_link == 0:
                link = j.get("href")
                f_link += 1
                print(link)
    book_img = i.find_all("img",{"class":"s-access-image cfMarker"})
    f_img = 0
    for j in book_img:
        if book_img != 0:
            if f_img == 0:
                image = j.get("src")
                f_img += 1
                print(image)
    book_prize = i.find_all("span",{"class":"a-size-base a-color-price s-price a-text-bold"})
    f_prize = 0
    #print(book_prize)
    for j in book_prize:
        if f_prize == 0:
            print(j.text)
            f_prize += 1
    auther = ''
    auther_name = i.find_all('span',{'class':'a-size-small a-color-secondary'})
    for j in auther_name:
        k = j.find_all('a',{'class':'a-link-normal a-text-normal'})
        for l in k:
            auther = j.text
            print(auther)

    type = ''
    book_type = i.find_all('h3')
    for j in book_type:
        if len(type) == 0:
            type = j.get('data-attribute')
            print(type)

    complete_book_name = title+" " +auther
    if len(complete_book_name) != 1:
        title_list.append(complete_book_name)
        


print(title_list)
for k in title_list:
    k = k[:len(k)-len(auther)]
    ebay_url = requests.get("http://www.ebay.in/sch/Books-Magazines/267/i.html?_from=R40&_nkw="+k)
    soup_ebay = BeautifulSoup(ebay_url.content, "html.parser")
    print(k)
    complete_ebay_html = soup_ebay.find_all('li')
    ebay_link = []
    ebay_prize = []
    for i in complete_ebay_html:
        book_title = i.find_all('a',{'class':'vip'})
        #print(book_title)

        for j in book_title:
            if len(j) != 0:
                if len(ebay_link) == 0:
                    #ebay_book_title = j.text
                    ebay_book_link = j.get("href")
                    #print(ebay_book_link)
                    ebay_link.append(ebay_book_link)


        book_prize = i.find_all('span',{'class':'bold'})
        #book_prize = i.find_all('b')
        #print(book_prize)
        f_prize = 0
        #print(book_title)
        for j in book_prize:
            if j != 0:
                if len(ebay_prize) == 0:
                    prize = j.text
                    ebay_prize.append(prize)

    print(ebay_prize)
    print(ebay_link)

    r = requests.get("https://www.snapdeal.com/search?keyword="+k+"&santizedKeyword=&catId=&categoryId=0&suggested=true&vertical=p&noOfResults=20&searchState=&clickSrc=suggested&lastKeyword=&prodCatId=&changeBackToAll=false&foundInAll=false&categoryIdSearched=&cityPageUrl=&categoryUrl=ALL&url=&utmContent=&dealDetail=&sort=rlvncy")
    soup = BeautifulSoup(r.content, "html.parser")

    g = soup.find_all('div',{'class':'product-tuple-image '})
    snapdeal_link = []
    snapdeal_prize = []

    for i in g:
    #for i in g:
        book_link = i.find_all('a')
        #print(book_link)
        for j in book_link:
            if len(snapdeal_link) == 0:
                snapdeal_link.append(j.get('href'))
    

    for i in soup.find_all('div',{'class':'product-price-row clearfix'}):
        book_link = i.find_all('span',{'class':'lfloat product-price'})
        for j in book_link:
            if len(snapdeal_prize) == 0:
            #print(j.get('display-price'))
                snapdeal_prize.append(j.get('display-price'))
    print(snapdeal_link)
    print(snapdeal_prize)
    







            
