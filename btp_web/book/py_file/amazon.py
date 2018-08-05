import requests
from bs4 import BeautifulSoup
from collections import defaultdict
k = request.GET.get("q")
j = "http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords="+k
r = requests.get(j)
soupp = BeautifulSoup(r.content, "html.parser")
#print(soupp)

g = soupp.find_all('div',{'class':'pagnHy'})
li = [j]
for i in g:
    page_no_link = i.find_all('a')
    for j in page_no_link:
        l = j.get('href')
        l = "http://www.amazon.in"+ l
        li.append(l)
li = li[:len(li)-1]
#print(li)
items = defaultdict(list)
link_list = []
title_list = []
img_list = []
prize_list = []
name_list = []
for k in li:
    url_html = requests.get(k)
    soup = BeautifulSoup(url_html.content,"html.parser")

    for i in soup.find_all("li"):
        book_title = i.find_all("h2")
        f_title = 0
        for j in book_title:
            if len(j) != 0:
                if f_title == 0:
                    title = j.get("data-attribute")
                    f_title += 1
                    title_list.append(title)


        book_link = i.find_all("a",{"class":"a-link-normal a-text-normal"})
        f_link = 0
        for j in book_link:
            #print(j.text)
            if len(j) != 0:
                if f_link == 0:
                    link = j.get("href")
                    f_link += 1
                    link_list.append(link)
                    items[title].append(link)


        book_img = i.find_all("img",{"class":"s-access-image cfMarker"})
        f_img = 0
        for j in book_img:
            if book_img != 0:
                if f_img == 0:
                    image = j.get("src")
                    f_img += 1
                    img_list.append(image)
                    items[title].append(image)


        book_prize = i.find_all("span",{"class":"a-size-base a-color-price s-price a-text-bold"})
        f_prize = 0
        #print(book_prize)
        for j in book_prize:
            if f_prize == 0:
                prize = j.text
                f_prize += 1
                prize_list.append(prize)
                items[title].append(prize)

        auther_name = i.find_all('span',{'class':'a-size-small a-color-secondary'})
        for j in auther_name:
            k = j.find_all('a',{'class':'a-link-normal a-text-normal'})
            for l in k:
                name_list.append(l.text)
                items[title].append(l.text)
##print(len(prize_list))
##print(len(img_list))
##print(len(link_list))
##print(len(title_list))
##print(name_list)

#print(items)
