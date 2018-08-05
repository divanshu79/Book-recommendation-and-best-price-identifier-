import requests
from bs4 import BeautifulSoup
k = "Harry-Potter"
j = "http://www.amazon.in/"
r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords="+k)
soup = BeautifulSoup(r.content, "html.parser")

link_list = []
title_list = []
img_list = []
prize_list = []

for i in soup.find_all("li"):
    book_title = i.find_all("h2")
    title = ''
    f_title = 0
    for j in book_title:
        if len(j) != 0:
            if f_title == 0:
                title = j.get("data-attribute")
                f_title += 1
                #title_list.append(title)
    book_link = i.find_all("a",{"class":"a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal"})
    f_link = 0
    #print(book_link)
    for j in book_link:
        #print(j.text)
        if len(j) != 0:
            if f_link == 0:
                link = j.get("href")
                tit = j.get('title')
                #print(tit)
                f_link += 1
                #print(link)
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
            #print(j.text)
            f_prize += 1
    auther_name = i.find_all('span',{'class':'a-size-small a-color-secondary'})
    for j in auther_name:
        k = j.find_all('a',{'class':'a-link-normal a-text-normal'})
##        for l in k:
##            print(j.text)

    type = ''
    book_type = i.find_all('h3')
    for j in book_type:
        if len(type) == 0:
            type = j.get('data-attribute')
            #print(type)

    complete_book_name = title+" " +type
    if len(complete_book_name) != 1:
        title_list.append(complete_book_name)
book_img = i.find_all("img",{"class":"s-access-image cfMarker"})
f_img = 0
for j in book_img:
    if book_img != 0:
        if f_img == 0:
            image = j.get("src")
            f_img += 1
            print(image)
