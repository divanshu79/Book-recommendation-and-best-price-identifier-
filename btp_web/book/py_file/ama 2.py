import requests
from bs4 import BeautifulSoup
k = "Harry-Potter"
j = "http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords="+k
r = requests.get(j)
soup = BeautifulSoup(r.content, "html.parser")

g = soup.find_all('div',{'class':'pagnHy'})
li = [j]
for i in g:
    page_no_link = i.find_all('a')
    for j in page_no_link:
        l = j.get('href')
        l = "http://www.amazon.in"+ l
        li.append(l)
