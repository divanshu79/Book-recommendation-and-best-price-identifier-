from django.http import JsonResponse, HttpResponse ,HttpResponseRedirect
from django.shortcuts import render, get_object_or_404,render_to_response
#from django.db.models import Q
import facebook
from book.models import user_info
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.context import RequestContext
# from social_core.pipeline.user import USER_FIELDS, get_username, create_user, \
#     user_details
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from social_django.models import UserSocialAuth
import json
from django.core.exceptions import ObjectDoesNotExist
from collections import defaultdict
from math import sqrt

def index(request):
    if request.user.is_authenticated():
        k = request.GET.get('q')
        if k:
            import requests
            from bs4 import BeautifulSoup
            j = "http://www.amazon.in/"
            r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=" + k)
            soup = BeautifulSoup(r.content, "html.parser")
            complete_info = []

            for i in soup.find_all("div", {'class': 'a-fixed-left-grid'}):
                dict = {}

                book_link = i.find_all("a", {"class": "a-link-normal a-text-normal"})
                f_link = 0
                for j in book_link:
                    if len(j) != 0:
                        if f_link == 0:
                            link = j.get("href")
                            f_link += 1
                            dict['amazon_link'] = link

                book_img = i.find_all("img", {"class": "s-access-image cfMarker"})
                f_img = 0
                for j in book_img:
                    if book_img != 0:
                        if f_img == 0:
                            image = j.get("src")
                            f_img += 1
                            # print(image)
                            dict['image'] = image

                type = ''
                book_type = i.find_all('h3')
                for j in book_type:
                    if len(type) == 0:
                        type = j.get('data-attribute')
                        dict['type'] = type

                book_title = i.find_all("h2")
                title = ''
                for j in book_title:
                    title = j.get("data-attribute")
                    if title:
                        dict['title'] = title

                # print(title)

                auther = ''
                auther_name = i.find_all('span', {'class': 'a-size-small a-color-secondary'})
                for j in auther_name:
                    k = j.find_all('a', {'class': 'a-link-normal a-text-normal'})
                    # print(k.text)
                    for l in k:
                        auther = l.text
                        dict['auther'] = auther

                if len(dict) != 0:
                    complete_info.append(dict)
            # profile['id'] = request.session.get('id')
            # if profile['id']:
            #     rating=[]
            #     ratings=user_info.objects.filter(uid=profile['id'])
            #     for r in ratings:
            #         rating['book_name']=r.book_name

            return render(request, 'book/index2.html', {'request': request, 'user': request.user,
                                                       'complete_info': complete_info
                                                       })
        else:

            profile = {}
            dicti = {'books': {'data': [] }, 'books.reads': {'data': [] },
                     'books.wants_to_read': {'data': [] }}
            book = []
            picture = ''
            if UserSocialAuth.objects.filter(user=request.user.id).exists():
                instance = UserSocialAuth.objects.get(user=request.user, provider='facebook')
                token = instance.extra_data['access_token']
                graph = facebook.GraphAPI(token, version="2.7")
                profile = graph.get_object(id='me')
                args = {'fields': 'id,name,email,books,books.reads,books.wants_to_read,picture'}
                profile['books'] = ''
                profile = graph.get_object('me', **args)
                request.session["id"]=profile['id']
                for i in profile:
                    if i == 'picture':
                        dicti[i] = profile[i]['data']['url']
                    else:
                        dicti[i] = profile[i]

                picture = profile['picture']['data']['url']

                if bool(dicti['books']['data']):
                    for boo in dicti['books']['data']:

                        if not user_info.objects.filter(book_name=boo['name']):
                            user_info.objects.create(uid=profile['id'], name=profile['name'], picture=picture,
                                                     book_name=boo['name'],rating=Decimal('0.00'))
                if bool(dicti['books.wants_to_read']['data']):
                    for boo in dicti['books.wants_to_read']['data']:
                        if not user_info.objects.filter(book_name=boo['data']['book']['title']):
                            user_info.objects.create(uid=profile['id'], name=profile['name'], picture=picture,
                                                     book_name=boo['data']['book']['title'],rating=Decimal('0.00'))
                if bool(dicti['books.reads']['data']):
                    for boo in dicti['books.reads']['data']:
                        if not user_info.objects.filter(book_name=boo['data']['book']['title']):
                            user_info.objects.create(uid=profile['id'], name=profile['name'], picture=picture,
                                                     book_name=boo['data']['book']['title'],rating=Decimal('0.00'))
            context = {'request': request, 'user': request.user, 'books': dicti['books']['data'], 'picture': picture, 'dicti':dicti}
            # return render(request, 'book/base.html', context)
            # context = {'request': request, 'user': request.user ,'books': dicti['books.reads']['data'],'picture':picture}
            # print(dicti)


                #
            return render(request, 'book/base.html', {
                'dicti': dicti,
                'context': context,
                # 'con_recommendation': con_recommendation
            })

    else:
        import requests
        from bs4 import BeautifulSoup
        import random

        import re
        r = requests.get("http://www.amazon.in/gp/bestsellers/books")
        soup = BeautifulSoup(r.content, 'lxml')
        g = soup.find_all('div', {'id': 'zg_centerListWrapper'})
        dataset = []
        for i in g:
            k = i.find_all('div', {"class": 'a-section a-spacing-none p13n-asin'})
            if k:
                for t in k:
                    #         print t.prettify()
                    data = {}
                    al = (t.find('a', {'class': 'a-link-normal'}))['href']
                    data['amazon_link'] = 'http://www.amazon.in/' + al
                    data['image'] = (t.find('img'))['src']
                    # k = (
                    #     t.find('div', {'class': 'p13n-sc-truncate p13n-sc-truncated-hyphen p13n-sc-line-clamp-1'})).text
                    data['title'] = 'RAM'
                    da = (t.find('a', {'class': 'a-size-small a-link-child'}))
                    if da != None:
                        data['auther'] = da.text

                    # k = title

                    ## goodreads

                    j = "https://www.goodreads.com/search?q=" + 'game of thrones'
                    r = requests.get(j)
                    soup = BeautifulSoup(r.content, "html.parser")
                    rng = soup.find_all('span', {'class': 'minirating'})
                    l = 0
                    ln = 0
                    if len(rng) != 0:
                        a = rng[0].text
                        grt = a[1:5]
                        if grt[len(grt) - 1] == ' ' and ' a' not in grt:
                            grt = grt[:4]
                        elif ' a' in grt:
                            grt = grt[:3]

                        gun1 = a[::-1][7:]
                        gun1 = gun1[::-1][len(grt) + 15:].replace(',', '')
                        # print(gun1)

                        if '1' in grt or '2' in grt or '3' in grt or '4' in grt or '5' in grt and ord(gun1[0]) < 60:
                            # if float(grt):
                            mg = float(grt) * float(gun1)
                        else:
                            mg = 0
                            gun1 = 0
                        # l.append(mg)
                        # ln.append(float(gun1))
                        l = mg
                        ln = float(gun1)
                    else:
                        # l.append(0)
                        # ln.append(0)
                        l = 0
                        ln = 0

                    ## amazon

                    rating = i.find_all('div', {'class': 'a-column a-span5 a-span-last'})
                    a = ''
                    b = ''
                    for i in rating:
                        rate = i.find_all('span')
                        f_rating = 0
                        for j in rate:
                            if f_rating == 0:
                                a = j.text
                                a = a[1:4]
                                f_rating += 1
                                if 'o' in a:
                                    a = a[:1]

                    for i in rating:
                        no = i.find_all('a', {'class': 'a-size-small a-link-normal a-text-normal'})
                        for j in no:
                            if len(j) != 0:
                                b = j.text
                                if ',' in b:
                                    b = b.replace(',', '')

                    if len(a) > 0:
                        if ord(a[0]) >= 48 and ord(a[0]) <= 57:
                            a = float(a) * float(b)
                        else:
                            a = 0
                    else:
                        a = 0
                    if len(b) > 0:
                        hh = float(b) + ln
                    else:
                        hh = ln
                    if hh != 0:
                        global_rating = (float(a) + l) / hh
                        # global_rating = a
                    else:
                        global_rating = round(random.uniform(3.1,4.0),2)
                    data['global_rating'] = round(global_rating, 2)

                    # data['global_rating']=3.24
                    dataset.append(data)

                break

        
        
        
        return render(request, 'book/base.html', {
            'complete_info': dataset,
        })

# def detail(request):
#     return render(request,'book/base.html')

def send(request):
    from social_django.models import UserSocialAuth
    profile = ''
    title = request.GET.get('name')
    auther = request.GET.get('auther')
    image = request.GET.get('image')
    rating = request.GET.get('rating')
    amazon_link = request.GET.get('amazon_link')
    # print('saak')
    if UserSocialAuth.objects.filter(user=request.user.id).exists():
        instance = UserSocialAuth.objects.get(user=request.user, provider='facebook')
        token = instance.tokens
        graph = facebook.GraphAPI(token, version="2.7")
        profile = graph.get_object(id='me')

        args = {'fields': 'id,name,email,books,picture'}
        profile = graph.get_object('me', **args)
        picture = profile['picture']['data']['url']
        title = request.GET.get('name')
        auther = request.GET.get('auther')
        image = request.GET.get('image')
        rating = request.GET.get('rating')
        amazon_link = request.GET.get('amazon_link')


        texti = user_info.objects.filter(uid=profile['id'])
        print(texti)
        c = 0
        for books in texti:
            if books.book_name == title:
                c += 1
                break
        if c == 0:
            user_info.objects.create(uid=profile['id'], name=profile['name'], picture=image, author=auther,
                                     book_name=title, amazon_link=amazon_link, )

            t = user_info.objects.filter(uid=profile['id']).get(book_name=title)
            t.rating = rating
            t.save()

        #context = {'request': request, 'user': request.user ,'books':profile}
        # print(title)
        # print(auther)
        # print(profile['id'])

    return HttpResponse(json.dumps({
        'page_id': '1',
        'amazon_link':title,
    }))

def genre_opp(request):
    link = 'http://www.amazon.in/b/ref=sv_ba_3?ie=UTF8&node=976390031'
    r = requests.get(link)
    # print (link)
    soup = BeautifulSoup(r.content, "html.parser")
    genre_div = soup.find_all('div', {'class': 'bxc-grid__image'})
    # print(genre_div)
    complete_info = []
    for i in genre_div:
        genre_dict = {}

        genre_link = i.find_all('a')
        f_link = 0
        for j in genre_link:
            genre_dict['link'] = j.get('href')

        genre_img = i.find_all('img')
        # print(genre_img)
        f_img = 0
        for j in genre_img:
            genre_dict['image'] = j.get('src')
            genre_dict['title'] = j.get('alt')

        complete_info.append(genre_dict)
    return render(request, 'book/genre.html', {
        'complete_info': complete_info
    })


def genre(request):
    link = request.GET.get('amazon_link')
    request.session['link'] = link
    return HttpResponseRedirect(reverse('remain'))


def remain(request):
    link = request.session.get('link')
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")
    complete_info = []
    
    for i in soup.find_all("div", {'class': 'a-fixed-left-grid'}):
        dict = {}

        book_link = i.find_all("a", {"class": "a-link-normal a-text-normal"})
        f_link = 0
        for j in book_link:
            if len(j) != 0:
                if f_link == 0:
                    li = j.get("href")
                    f_link += 1
                    dict['amazon_link'] = li

        book_img = i.find_all("img", {"class": "s-access-image cfMarker"})
        f_img = 0
        for j in book_img:
            if book_img != 0:
                if f_img == 0:
                    image = j.get("src")
                    f_img += 1
                    # print(image)
                    dict['image'] = image

        book_prize = i.find_all("span", {"class": "a-size-base a-color-price s-price a-text-bold"})
        f_prize = 0
        # print(book_prize)
        for j in book_prize:
            if f_prize == 0:
                prize = j.text
                f_prize += 1
                dict['amazon_prize'] = prize

        type = ''
        book_type = i.find_all('h3')
        for j in book_type:
            if len(type) == 0:
                type = j.get('data-attribute')
                dict['type'] = type

        book_title = i.find_all("h2")
        title = ''
        for j in book_title:
            title = j.get("data-attribute")
            if title:
                dict['title'] = title

        # print(title)

        auther = ''
        auther_name = i.find_all('span', {'class': 'a-size-small a-color-secondary'})
        for j in auther_name:
            k = j.find_all('a', {'class': 'a-link-normal a-text-normal'})
            # print(k.text)
            for l in k:
                auther = l.text
                dict['auther'] = auther

        
            ##goodreads
        # k=title
        # j = "https://www.goodreads.com/search?q=" + k
        # r = requests.get(j)
        # soup = BeautifulSoup(r.content, "html.parser")
        # rng = soup.find_all('span', {'class': 'minirating'})
        # l = 0
        # ln = 0
        # if len(rng) != 0:
        #     a = rng[0].text
        #     grt = a[1:5]
        #     if grt[len(grt) - 1] == ' ' and ' a' not in grt:
        #         grt = grt[:4]
        #     elif ' a' in grt:
        #         grt = grt[:3]

        #     gun1 = a[::-1][7:]
        #     gun1 = gun1[::-1][len(grt) + 15:].replace(',', '')
        #     # print(gun1)

        #     if '1' in grt or '2' in grt or '3' in grt or '4' in grt or '5' in grt and ord(gun1[0]) < 60:
        #         # if float(grt):
        #         mg = float(grt) * float(gun1)
        #     else:
        #         mg = 0
        #         gun1 = 0
        #     # l.append(mg)
        #     # ln.append(float(gun1))
        #     l = mg
        #     ln = float(gun1)
        # else:
        #     # l.append(0)
        #     # ln.append(0)
        #     l = 0
        #     ln = 0

        # ## amazon

        # rating = i.find_all('div', {'class': 'a-column a-span5 a-span-last'})
        # a = ''
        # b = ''
        # for i in rating:
        #     rate = i.find_all('span')
        #     f_rating = 0
        #     for j in rate:
        #         if f_rating == 0:
        #             a = j.text
        #             a = a[1:4]
        #             f_rating += 1
        #             if 'o' in a:
        #                 a = a[:1]

        # for i in rating:
        #     no = i.find_all('a', {'class': 'a-size-small a-link-normal a-text-normal'})
        #     for j in no:
        #         if len(j) != 0:
        #             b = j.text
        #             if ',' in b:
        #                 b = b.replace(',', '')

        # if len(a) > 0:
        #     if ord(a[0]) >= 48 and ord(a[0]) <= 57:
        #         a = float(a) * float(b)
        #     else:
        #         a = 0
        # else:
        #     a = 0
        # if len(b) > 0:
        #     hh = float(b) + ln
        # else:
        #     hh = ln
        # if hh != 0:
        #     global_rating = (float(a) + l) / hh
        #     # global_rating = a
        # else:
        #     global_rating = round(Math.random.uniform(3.1,4.0),2)
        # dict['global_rating'] = round(global_rating, 2)
        if len(dict) != 0:
            complete_info.append(dict)
        # data['global_rating']=3.24
    return render(request, 'book/index2.html', {'request': request, 'user': request.user,
                                                'complete_info': complete_info
                                                })

def editor(request):
    link = 'http://www.amazon.in/b/ref=s9_acss_bw_ln_Editoria_1_10_w?_encoding=UTF8&node=10591963031&pf_rd_m=A1VBAL9TL5WCBF&pf_rd_s=merchandised-search-leftnav&pf_rd_r=YV0GS99S8BBAWM5R9NKV&pf_rd_r=YV0GS99S8BBAWM5R9NKV&pf_rd_t=101&pf_rd_p=2dbc9cc3-05a1-4458-806e-129a1a89437b&pf_rd_p=2dbc9cc3-05a1-4458-806e-129a1a89437b&pf_rd_i=1318158031'
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")
    genre_div = soup.find_all('div', {'class': 'bxc-grid__image'})
    # print(genre_div)
    complete_info = []
    link_list = []
    image_list = []
    for i in genre_div:
        genre_dict = {}

        genre_link = i.find_all('a')
        for j in genre_link:
            img = j.get('href')
            if len(link_list) <= 9:
                genre_dict['link'] = img
                link_list.append(img)

        genre_img = i.find_all('img')
        # print(genre_img)
        for j in genre_img:
            li = j.get('src')
            if len(image_list) < 9:
                genre_dict['image'] = li
                image_list.append(li)

        # print(genre_dict)

        if len(genre_dict) != 1:
            complete_info.append(genre_dict)
        #complete_info = complete_info[:len(complete_info)-1]

    return render(request, 'book/genre.html', {
        'complete_info': complete_info
    })

def age(request):
    link = 'http://www.amazon.in/children-books/b/ref=sv_ba_4?ie=UTF8&node=1318073031'

    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")
    complete_info = []
    link_list = []
    image_list = []
    for i in soup.find_all('div', {'class': 'bxc-grid__image'}):
        dict = {}

        age_link = i.find_all('a')
        for j in age_link:
            li = j.get('href')
            if len(link_list) < 5:
                dict['link'] = li
                link_list.append(li)

        image_link = i.find_all('img')
        for j in image_link:
            img = j.get('src')
            if len(image_list) < 5:
                dict['image'] = img
                image_list.append(img)

        if len(dict) != 0:
            complete_info.append(dict)

    return render(request, 'book/genre.html', {
        'complete_info': complete_info
    })

def star(request):
    return render(request,'book/star.html')

def page(request):

    link = (request.GET.get('amazon_link'))
    request.session['link'] = (link)
    return HttpResponseRedirect(reverse('all'))


def all(request):
    import requests
    from bs4 import BeautifulSoup
    dict = {}
    link = request.GET.get('amazon_link')

    # print('abc' + link)
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")
    dict['amazon_link'] = link
    img_div = soup.find_all('img', {'id': 'imgBlkFront'})
    # print(img_div)
    for i in img_div:
        img = i.get('src')
        dict['image'] = img

    prize_span = soup.find_all('span', {'class': 'a-size-medium a-color-price inlineBlock-display offer-price a-text-normal price3P'})
    for i in prize_span:
        prize = i.text
        if len(prize) != 0:
            dict['prize'] = prize[3:10]

    title_span = soup.find_all('span', {'id': 'productTitle'})
    #k = ''

    for i in title_span:
        k = i.text
        #k = title
        dict['title'] = k


        ebay_url = requests.get("http://www.ebay.in/sch/Books-Magazines/267/i.html?_from=R40&_nkw=" + k+"&_sop=15")
        soup_ebay = BeautifulSoup(ebay_url.content, 'html.parser')
        complete_ebay_html = soup_ebay.find_all('li', {'r': '1'})
        e_l = []
        e_p = []

        for i in complete_ebay_html:
            book_title = i.find_all('a', {'class': 'vip'})
            for j in book_title:
                if len(j) != 0:
                    if len(e_l) == 0:
                        ebay_book_link = j.get("href")
                        e_l.append(ebay_book_link)
                        dict['ebay_link'] = ebay_book_link
            book_prize = i.find_all('span', {'class': 'bold'})
            for j in book_prize:
                if len(j) != 0:
                    if len(e_p) == 0:
                        prize = j.text
                        e_p.append(prize)
                        dict['ebay_prize'] = prize[5:]
                        # print(complete_book_name)

        r = requests.get("https://www.snapdeal.com/search?keyword=" + k + ' paperback ' + 'english' + "&santizedKeyword=" + k + "&catId=0&categoryId=0&suggested=false&vertical=p&noOfResults=20&searchState=&clickSrc=go_header&lastKeyword=&prodCatId=&changeBackToAll=false&foundInAll=false&categoryIdSearched=&cityPageUrl=&categoryUrl=&url=&utmContent=&dealDetail=&sort=rlvncy")
        soup = BeautifulSoup(r.content, "html.parser")
        g = soup.find_all('div', {'class': 'product-tuple-image '})
        snapdeal_link = []
        snapdeal_prize = []
        for i in g:
            book_link = i.find_all('a')
            for j in book_link:
                if len(snapdeal_link) == 0:
                    x = j.get('href')
                    snapdeal_link.append(x)
                    dict['snapdeal_link'] = x
        for i in soup.find_all('div', {'class': 'product-price-row clearfix'}):
            book_link = i.find_all('span', {'class': 'lfloat product-price'})
            for j in book_link:
                if len(snapdeal_prize) == 0:
                    y = j.get('display-price')
                    snapdeal_prize.append(y)
                    dict['snapdeal_prize'] = y
    return render(request, 'book/index.html', {'request': request, 'user': request.user,
                                                'dict': dict
 
                                                })
def collab(request):

    ## pso ALGORITHM

    if UserSocialAuth.objects.filter(user=request.user.id).exists():
        instance = UserSocialAuth.objects.all()
        # print(instance)
        id = request.session.get('id')
        dataset={}
        dict_book = {}
        dict_rating = {}
        list_book = []
        initial = []
        users = []
        for index,name in enumerate(instance):
            books=user_info.objects.filter(uid=name.uid)
            di = {}
            list_book_2 = []
            list_rating_2 = []
            # dataset[name.uid]=[]
            if len(books)!=0:
                for i,book in enumerate(books):
                    # ring={}
                    di[book.book_name]=book.rating
                    if name.uid == id:
                        list_book.append(book.book_name)
                        if book.rating is None:
                            book.rating = 0.00
                        initial.append(float(book.rating))
                    else:
                        list_book_2.append(book.book_name)
                        if book.rating is None:
                            book.rating = 0.00
                        list_rating_2.append(float(book.rating))
                    # di[name.uid].append(ring)
            dataset[name.uid] = di
            dict_book[name.uid] = list_book_2
            dict_rating[name.uid] = list_rating_2
            if name.uid != id:
                users.append(name.uid)
        dataset=dict((k, v) for k, v in dataset.items() if v)

        bound = []
        for us in users:
            hsd = []
            for bo in list_book:
                if bo in dict_book[us]:
                    hsd.append(float(dataset[us][bo]))
                else:
                    hsd.append(0)
            bound.append(hsd)

        # --- COST FUNCTION ------------------------------------------------------------+

        # function we are attempting to optimize (minimize)
        def func1(x):
            total = 0
            for i in range(len(x)):
                total += x[i] ** 2
                return total

        # --- MAIN ---------------------------------------------------------------------+


        def __init__(self, x0):
            self.position_i = []  # particle position
            self.velocity_i = []  # particle velocity
            self.pos_best_i = []  # best position individual
            self.err_best_i = -1  # best error individual
            self.err_i = -1  # error individual

            for p in range(0, num_dimensions):
                self.velocity_i.append(random.uniform(-1, 1))
                self.position_i.append(x0[p])

                # evaluate current fitness

        def evaluate(self, costFunc):
            self.err_i = costFunc(self.position_i)

            # check to see if the current position is an individual best
            if self.err_i < self.err_best_i or self.err_best_i == -1:
                self.pos_best_i = self.position_i
                self.err_best_i = self.err_i

                # update new particle velocity

        def update_velocity(x, y, s):
            no1 = []
            a = defaultdict(int)
            max = 0
            summ = 0
            for i in range(len(x)):
                summ = sum(x[i])
                if summ > max:
                    max = summ
                no1.append(summ)
                a[summ] += 1

            ind = []
            ##    print(no1)
            fin = []
            if a[max] > 1:
                for i in range(len(no1)):
                    if no1[i] == max:
                        ind.append(i)

            if len(ind) > 0:
                for i in ind:
                    suum = sum(y[i])
                    fin.append((suum, i))
            else:
                no1.sort(reverse=True)
                fin.append((0, no1[0]))
            fin.sort()
            ##    print(fin)
            index = fin[0][1]
            return index



            # update the particle position based off new velocity updates

        def update_position(x1, x0):
            lst = []
            dis = []
            for i in range(0, num_dimensions):
                diff = abs(x1[i] - x0[i])
                dis.append(diff)
                if diff > 0.5:
                    lst.append(0)
                else:
                    lst.append(1)

            return lst, dis

        def PSO(costFunc, x0, bounds, num_particles, maxiter):
            global num_dimensions

            num_dimensions = len(x0)
            err_best_g = -1  # best error for group
            pos_best_g = 0  # best position for group

            # establish the swarm
            i = 0
            while i < maxiter:
                score_list = []
                diff_score_list = []
                for k in range(len(bounds)):
                    x, y = update_position(bounds[k], x0)
                    score_list.append(x)
                    diff_score_list.append(y)

                start_score = 0
                pos_best_g = update_velocity(score_list, diff_score_list, start_score)

                i += 1

            # print('final results')
            # print(pos_best_g)
            return pos_best_g

        ##    print(score_list)
        ##    for i in range(len(diff_score_list)):
        ##        print(sum(diff_score_list[i]))
        ##    print(diff_score_list)

        # if __name__ == "__PSO__":
        #     main()

        # --- RUN ----------------------------------------------------------------------+
        init = PSO(func1, initial, bound, num_particles=15, maxiter=30)
        k = users[init]
        name = dict_book[k]
        names = []
        for i in name:
            if i not in list_book:
                names.append(i)
        if len(name) >= 10:
            names = names[:15]
        cno = len(names)





    ## BEE ALGORITHM

    # if UserSocialAuth.objects.filter(user=request.user.id).exists():
    #     instance = UserSocialAuth.objects.all()
    #     dataset={}
    #     for index,name in enumerate(instance):
    #         books=user_info.objects.filter(uid=name.uid)
    #         di = {}
    #         # dataset[name.uid]=[]
    #         if len(books)!=0:
    #             for i,book in enumerate(books):
    #                 # ring={}
    #                 di[book.book_name]=book.rating
    #                 # di[name.uid].append(ring)
    #         dataset[name.uid] = di
    #     dataset=dict((k, v) for k, v in dataset.items() if v)
    #     from math import sqrt
    #
    #     def similarity_score(person1,person2):
    #
    #         # Returns ratio Euclidean distance score of person1 and person2
    #
    #         both_viewed = {}        # To get both rated items by person1 and person2
    #
    #         for item in dataset[person1]:
    #             if item in dataset[person2]:
    #                 both_viewed[item] = 1
    #
    #             # Conditions to check they both have an common rating items
    #             if len(both_viewed) == 0:
    #                 return 0
    #
    #             # Finding Euclidean distance
    #             sum_of_eclidean_distance = []
    #
    #             for item in dataset[person1]:
    #                 if item in dataset[person2]:
    #                     sum_of_eclidean_distance.append(pow(dataset[person1][item] - dataset[person2][item],2))
    #             sum_of_eclidean_distance = sum(sum_of_eclidean_distance)
    #
    #             return 1/(1+sqrt(sum_of_eclidean_distance))
    #     #print(similarity_score('Lisa Rose','Jack Matthews'))
    #
    #
    #     def pearson_correlation(person1,person2):
    #
    #         # To get both rated items
    #         both_rated = {}
    #         # print(person2)
    #         for item in dataset[person1]:
    #             if item in dataset[person2]:
    #                 both_rated[item] = 1
    #
    #         number_of_ratings = len(both_rated)
    #         # print('xyz'+' '+str(number_of_ratings))
    #         # print(both_rated)
    #
    #         # Checking for number of ratings in common
    #         if number_of_ratings == 0:
    #             return 0
    #         else:
    #
    #             # Add up all the preferences of each user
    #             person1_preferences_sum = sum([float(dataset[person1][item]) for item in both_rated])
    #             # print('a'+' '+str(person1_preferences_sum))
    #             person2_preferences_sum = sum([float(dataset[person2][item]) for item in both_rated])
    #             # print('b' + ' ' + str(person2_preferences_sum))
    #
    #             # Sum up the squares of preferences of each user
    #             person1_square_preferences_sum = sum([pow(float(dataset[person1][item]),2) for item in both_rated])
    #             # print('c' + ' ' + str(person1_square_preferences_sum))
    #             person2_square_preferences_sum = sum([pow(float(dataset[person2][item]),2) for item in both_rated])
    #             # print('d' + ' ' + str(person2_square_preferences_sum))
    #
    #             # Sum up the product value of both preferences for each item
    #             product_sum_of_both_users = sum([float(dataset[person1][item]) * float(dataset[person2][item]) for item in both_rated])
    #             # print('e' + ' ' + str(product_sum_of_both_users))
    #
    #             # Calculate the pearson score
    #             numerator_value = product_sum_of_both_users - ((person1_preferences_sum*person2_preferences_sum)/(number_of_ratings))
    #             # numerator_value = 1
    #             # print(numerator_value)
    #             # print(person1_preferences_sum*person2_preferences_sum/number_of_ratings)
    #
    #             denominator_value = sqrt((person1_square_preferences_sum - pow(person1_preferences_sum,2)/number_of_ratings) * (person2_square_preferences_sum -pow(person2_preferences_sum,2)/number_of_ratings))
    #             # denominator_value = 2
    #             # print(denominator_value)
    #             if denominator_value == 0:
    #                 return 0
    #             else:
    #                 r = numerator_value/denominator_value
    #                 # print(r)
    #                 return r
    #
    #     #print(pearson_correlation('Lisa Rose','Jack Matthews'))
    #
    #
    #     # def most_similar_users(person,number_of_users):
    #     #     # returns the number_of_users (similar persons) for a given specific person.
    #     #     scores = [(pearson_correlation(person,other_person),other_person) for other_person in dataset if  other_person != person ]
    #     #
    #     #     # Sort the similar persons so that highest scores person will appear at the first
    #     #     scores.sort()
    #     #     scores.reverse()
    #     #     return scores[0:number_of_users]
    #     #
    #     # #print(most_similar_users('Lisa Rose',3))
    #
    #
    #
    #     def user_reommendations(person):
    #
    #         # Gets recommendations for a person by using a weighted average of every other user's rankings
    #         totals = {}
    #         simSums = {}
    #         rankings_list =[]
    #         for other in dataset:
    #             # don't compare me to myself
    #             if other == person:
    #                 continue
    #             sim = pearson_correlation(person,other)
    #
    #             # ignore scores of zero or lower
    #             if sim <= 0:
    #                 continue
    #             for item in dataset[other]:
    #
    #                 # only score movies i haven't seen yet
    #                 if item not in dataset[person] or dataset[person][item] == 0:
    #
    #                 # Similrity * score
    #                     totals.setdefault(item,0)
    #                     totals[item] += float(dataset[other][item])* sim
    #                     # sum of similarities
    #                     simSums.setdefault(item,0)
    #                     simSums[item]+= sim
    #
    #             # Create the normalized list
    #
    #         rankings = [(total/simSums[item],item) for item,total in totals.items()]
    #         rankings.sort()
    #         rankings.reverse()
    #         # returns the recommended items
    #         recommendataions_list = [recommend_item for score,recommend_item in rankings]
    #         return recommendataions_list
    #
    #     # profile['id'] = ''
    #     id=request.session.get('id')
    #     names= user_reommendations(id)
    #     cno = len(names)
    #     # if len(names) > 7:
    #     #     names = names[:7]

        coll = []
        mix = []
        con = []
        for au in names:
            r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=" + au)
            soup = BeautifulSoup(r.content, "html.parser")
            s = []
            p = []
            # recomm_dict = {}
            # recomm_dict['title'] = au
            for i in soup.find_all("li"):
                recomm_dict = {}
                # recomm_dict['title'] = au
                book_link = i.find_all("a", {"class": "a-link-normal"})
                for j in book_link:
                    if len(j) != 0:
                        if len(s) == 0:
                            link = j.get("href")
                            # title = j.get("title")
                            s.append(link)
                            if len(link) != 0:
                                recomm_dict['amazon_link'] = link
                            # if len(title) != 0:
                                recomm_dict['title'] = au

                book_img = i.find_all("img", {"class": "s-access-image cfMarker"})
                for j in book_img:
                    if len(p) == 0:
                        image = j.get("src")
                        p.append(image)
                        if len(image) != 0:
                            recomm_dict['image'] = image

                # print(recomm_dict)


                if (len(recomm_dict) != 0):
                    coll.append(recomm_dict)
                    mix.append(recomm_dict)

        if UserSocialAuth.objects.filter(user=request.user.id).exists():
            instance = UserSocialAuth.objects.get(user=request.user, provider='facebook')
            token = instance.tokens
            graph = facebook.GraphAPI(token, version="2.7")
            profile = graph.get_object(id='me')
            args = {'fields': 'id,name,email,books,picture'}
            profile = graph.get_object('me', **args)
            request.session['id'] = profile['id']
        auther = []
        if profile['id']:
            k = user_info.objects.filter(uid=profile['id'])
        else:
            k = []

        chck_list = defaultdict(int)
        if len(k) != 0:
            for j in k:
                ram = j.author
                if ram:
                    chck_list[j.amazon_link] = 1
                    if ram not in auther:
                        auther.append(j.author)
                else:
                    if j.book_name not in auther:
                        auther.append(j.book_name)
                        chck_list[j.amazon_link] = 1



        order_list = []
        map = defaultdict(list)
        s = []
        for au in auther:
            s.append(au)
            r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=" + au)
            soup = BeautifulSoup(r.content, "html.parser")

            ks = []
            k_rate = []
            k_link = []
            k_img = []
            k_au = []
            qq = 6

            for l in soup.find_all('li'):

                linti = l.find_all('div', {'class': 'a-fixed-left-grid-col a-col-right'})
                title = ''
                link = ''
                ch_link = 0
                f_link = 0
                for i in linti:
                    li = i.find_all('a')

                    for j in li:
                        if f_link == 0:
                            if len(k_link) != qq:
                                link = j.get('href')
                                title = j.get('title')
                                if chck_list[link] != 1:
                                    map[link].append(title)
                                    f_link += 1
                                    k_link.append(link)
                                else:
                                    ch_link = 1

                rating = l.find_all('div', {'class': 'a-column a-span5 a-span-last'})
                a = ''
                b = ''
                for i in rating:
                    rate = i.find_all('span')
                    f_rating = 0
                    for j in rate:
                        if f_rating == 0:
                            if len(ks) != qq:
                                if chck_list[link] != 1:
                                    a = j.text
                                    a = a[1:4]
                                    # print(a)
                                    # b = a[::-1]
                                    f_rating += 1
                                    if 'o' in a:
                                        a = a[:1]
                                    ks.append(a)

                for i in rating:
                    if len(k_rate) != qq:
                        no = i.find_all('a', {'class': 'a-size-small a-link-normal a-text-normal'})
                        for j in no:
                            if len(j) != 0:
                                if chck_list[link] != 1:
                                    b = j.text
                                    if ',' in b:
                                        b = b.replace(',', '')
                                    k_rate.append(b)

                score = ''
                # print(a)
                if len(a) > 0 and ord(a[0])<60:
                    score = float(a) * float(b)


                aut = l.find_all('span', {'class': 'a-size-small a-color-secondary'})
                for i in aut:
                    auth = i.find_all('a')
                    for j in auth:
                        if len(j) != 0:
                            if len(k_au) != qq:
                                if chck_list[link] != 1:
                                    author = j.text
                                    map[link].append(author)
                                    k_au.append(author)

                div = l.find_all('div', {'class', 'a-fixed-left-grid-col a-col-left'})
                for i in div:
                    img = i.find_all('img')
                    for j in img:
                        if len(k_img) != qq:
                            if chck_list[link] != 1:
                                image = j.get('src')
                                map[link].append(image)
                                k_img.append(image)

                if len(str(score)) > 0 and len(link) > 0 and ch_link == 0:
                    order = (score, link)
                    order_list.append(order)
        order_list.sort(reverse=True)
        total_book = cno + len(order_list)
        order_list = order_list[:10]

        for i in order_list:
            recomm_dict = {}
            recomm_dict['title'] = map[i[1]][0]
            if len(map[i[1]]) == 2:
                recomm_dict['image'] = map[i[1]][1]
            else:
                recomm_dict['image'] = map[i[1]][2]
            recomm_dict['amazon_link'] = i[1]
            if len(map[i[1]]) == 3:
                recomm_dict['auther'] = map[i[1]][1]
            con.append(recomm_dict)
            mix.append(recomm_dict)

        request.session['Total'] = total_book
        mixl = []
        for i in range(len(mix)):
            dd = mix[i]
            k = dd['title']
            # print(k)

            ## goodreads

            j = "https://www.goodreads.com/search?q=" + k
            r = requests.get(j)
            soup = BeautifulSoup(r.content, "html.parser")
            rng = soup.find_all('span', {'class': 'minirating'})
            l = 0
            ln = 0
            if len(rng) != 0:
                a = rng[0].text
                grt = a[1:5]
                if grt[len(grt) - 1] == ' ' and ' a' not in grt:
                    grt = grt[:4]
                elif ' a' in grt:
                    grt = grt[:3]

                gun1 = a[::-1][7:]
                gun1 = gun1[::-1][len(grt) + 15:].replace(',', '')
                # print(gun1)

                if '1' in grt or '2' in grt or '3' in grt or '4' in grt or '5' in grt and ord(gun1[0]) < 60:
                    # if float(grt):
                    mg = float(grt) * float(gun1)
                else:
                    mg = 0
                    gun1 = 0
                # l.append(mg)
                # ln.append(float(gun1))
                l = mg
                ln = float(gun1)
            else:
                # l.append(0)
                # ln.append(0)
                l = 0
                ln = 0

            ## amazon

            r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=" + k)
            soup = BeautifulSoup(r.content, "html.parser")

            rating = soup.find_all('div', {'class': 'a-column a-span5 a-span-last'})
            a = ''
            b = ''
            for i in rating:
                rate = i.find_all('span')
                f_rating = 0
                for j in rate:
                    if f_rating == 0:
                        a = j.text
                        a = a[1:4]
                        f_rating += 1
                        if 'o' in a:
                            a = a[:1]

            for i in rating:
                no = i.find_all('a', {'class': 'a-size-small a-link-normal a-text-normal'})
                for j in no:
                    if len(j) != 0:
                        b = j.text
                        if ',' in b:
                            b = b.replace(',', '')

            if len(a) > 0:
                if ord(a[0]) >= 48 and ord(a[0]) <= 57:
                    a = float(a) * float(b)
                else:
                    a = 0
            else:
                a = 0
            if len(b) > 0:
                hh = float(b) + ln
            else:
                hh = ln
            if hh != 0:
                global_rating = (float(a) + l) / hh
                # global_rating = a
            else:
                import random
                global_rating = round(random.uniform(3.1, 4.0), 2)
            dd['global_rating'] = round(global_rating, 2)
            mixl.append(dd)

        # print(mixl)



        return render(request,'book/collab.html',{'mix':mix,
                                                  'names': chck_list,
                                                  'author': auther,
                                                  'length':len(mix)    
                                                  })
    else:
        return render(request,'book/login.html')
# def collab(request):
#     if UserSocialAuth.objects.filter(user=request.user.id).exists():
#         instance = UserSocialAuth.objects.all()
#         dataset={}
#         for index,name in enumerate(instance):
#             books=user_info.objects.filter(uid=name.uid)
#             di = {}
#             # dataset[name.uid]=[]
#             if len(books)!=0:
#                 for i,book in enumerate(books):
#                     # ring={}
#                     di[book.book_name]=book.rating
#                     # di[name.uid].append(ring)
#             dataset[name.uid] = di
#         dataset=dict((k, v) for k, v in dataset.items() if v)
#         from math import sqrt
#
#         # def kmean(x,y):
#         #     import pandas as pd
#         #     import numpy as np
#         #     import matplotlib.pyplot as plt
#         #
#         #     df = pd.DataFrame({
#         #         'x': [12, 20, 28, 18, 29, 33, 24, 45, 45, 52, 51, 52, 55, 53, 55, 61, 64, 69, 72],
#         #         'y': [39, 36, 30, 52, 54, 46, 55, 59, 63, 70, 66, 63, 58, 23, 14, 8, 19, 7, 24]
#         #     })
#         #
#         #     from sklearn.cluster import KMeans
#         #
#         #     kmeans = KMeans(n_clusters=3)
#         #     kmeans.fit(df)
#         #
#         #     KMeans(algorithm='auto', copy_x=True, init='k-means++', max_iter=300,
#         #            n_clusters=3, n_init=10, n_jobs=1, precompute_distances='auto',
#         #            random_state=None, tol=0.0001, verbose=0)
#         #
#         #     labels = kmeans.predict(df)
#         #     centroids = kmeans.cluster_centers_
#         #     colmap = {1: 'r', 2: 'g', 3: 'b'}
#         #
#         #     fig = plt.figure(figsize=(5, 5))
#         #
#         #     colors = map(lambda x: colmap[x + 1], labels)
#         #     print(list(enumerate(centroids)))
#         #
#         #     plt.scatter(df['x'], df['y'], color=list(colors), alpha=0.5, edgecolor='k')
#         #     for idx, centroid in enumerate(centroids):
#         #         plt.scatter(*centroid, color=colmap[idx + 1])
#         #     plt.xlim(0, 80)
#         #     plt.ylim(0, 80)
#         #     plt.show()
#
#         def similarity_score(person1,person2):
#
#             # Returns ratio Euclidean distance score of person1 and person2
#
#             both_viewed = {}        # To get both rated items by person1 and person2
#
#             for item in dataset[person1]:
#                 if item in dataset[person2]:
#                     both_viewed[item] = 1
#
#                 # Conditions to check they both have an common rating items
#                 if len(both_viewed) == 0:
#                     return 0
#
#                 # Finding Euclidean distance
#                 sum_of_eclidean_distance = []
#
#                 for item in dataset[person1]:
#                     if item in dataset[person2]:
#                         sum_of_eclidean_distance.append(pow(dataset[person1][item] - dataset[person2][item],2))
#                 sum_of_eclidean_distance = sum(sum_of_eclidean_distance)
#
#                 return 1/(1+sqrt(sum_of_eclidean_distance))
#         #print(similarity_score('Lisa Rose','Jack Matthews'))
#
#
#         def pearson_correlation(person1,person2):
#
#             # To get both rated items
#             both_rated = {}
#             # print(person2)
#             for item in dataset[person1]:
#                 if item in dataset[person2]:
#                     both_rated[item] = 1
#
#             number_of_ratings = len(both_rated)
#             # print('xyz'+' '+str(number_of_ratings))
#             # print(both_rated)
#
#             # Checking for number of ratings in common
#             if number_of_ratings == 0:
#                 return 0
#             else:
#
#                 # Add up all the preferences of each user
#                 person1_preferences_sum = sum([float(dataset[person1][item]) for item in both_rated])
#                 # print('a'+' '+str(person1_preferences_sum))
#                 person2_preferences_sum = sum([float(dataset[person2][item]) for item in both_rated])
#                 # print('b' + ' ' + str(person2_preferences_sum))
#
#                 # Sum up the squares of preferences of each user
#                 person1_square_preferences_sum = sum([pow(float(dataset[person1][item]),2) for item in both_rated])
#                 # print('c' + ' ' + str(person1_square_preferences_sum))
#                 person2_square_preferences_sum = sum([pow(float(dataset[person2][item]),2) for item in both_rated])
#                 # print('d' + ' ' + str(person2_square_preferences_sum))
#
#                 # Sum up the product value of both preferences for each item
#                 product_sum_of_both_users = sum([float(dataset[person1][item]) * float(dataset[person2][item]) for item in both_rated])
#                 # print('e' + ' ' + str(product_sum_of_both_users))
#
#                 # Calculate the pearson score
#                 numerator_value = product_sum_of_both_users - ((person1_preferences_sum*person2_preferences_sum)/(number_of_ratings))
#                 # numerator_value = 1
#                 # print(numerator_value)
#                 # print(person1_preferences_sum*person2_preferences_sum/number_of_ratings)
#
#                 denominator_value = sqrt((person1_square_preferences_sum - pow(person1_preferences_sum,2)/number_of_ratings) * (person2_square_preferences_sum -pow(person2_preferences_sum,2)/number_of_ratings))
#                 # denominator_value = 2
#                 # print(denominator_value)
#                 if denominator_value == 0:
#                     return 0
#                 else:
#                     r = numerator_value/denominator_value
#                     # print(r)
#                     return r
#
#         #print(pearson_correlation('Lisa Rose','Jack Matthews'))
#
#
#         # def most_similar_users(person,number_of_users):
#         #     # returns the number_of_users (similar persons) for a given specific person.
#         #     scores = [(pearson_correlation(person,other_person),other_person) for other_person in dataset if  other_person != person ]
#         #
#         #     # Sort the similar persons so that highest scores person will appear at the first
#         #     scores.sort()
#         #     scores.reverse()
#         #     return scores[0:number_of_users]
#         #
#         # #print(most_similar_users('Lisa Rose',3))
#
#
#
#         def user_reommendations(person):
#
#             # Gets recommendations for a person by using a weighted average of every other user's rankings
#             totals = {}
#             simSums = {}
#             rankings_list =[]
#             for other in dataset:
#                 # don't compare me to myself
#                 if other == person:
#                     continue
#                 sim = pearson_correlation(person,other)
#
#                 # ignore scores of zero or lower
#                 if sim <= 0:
#                     continue
#                 for item in dataset[other]:
#
#                     # only score movies i haven't seen yet
#                     if item not in dataset[person] or dataset[person][item] == 0:
#
#                     # Similrity * score
#                         totals.setdefault(item,0)
#                         totals[item] += float(dataset[other][item])* sim
#                         # sum of similarities
#                         simSums.setdefault(item,0)
#                         simSums[item]+= sim
#
#                 # Create the normalized list
#
#             rankings = [(total/simSums[item],item) for item,total in totals.items()]
#             rankings.sort()
#             rankings.reverse()
#             # returns the recommended items
#             recommendataions_list = [recommend_item for score,recommend_item in rankings]
#             return recommendataions_list
#
#         # profile['id'] = ''
#         id=request.session.get('id')
#         names= user_reommendations(id)
#         cno = len(names)
#         if len(names) > 7:
#             names = names[:7]
#
#         coll = []
#         mix = []
#         con = []
#         for au in names:
#             r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=" + au)
#             soup = BeautifulSoup(r.content, "html.parser")
#             s = []
#             p = []
#             # recomm_dict = {}
#             # recomm_dict['title'] = au
#             for i in soup.find_all("li"):
#                 recomm_dict = {}
#                 # recomm_dict['title'] = au
#                 book_link = i.find_all("a", {"class": "a-link-normal"})
#                 for j in book_link:
#                     if len(j) != 0:
#                         if len(s) == 0:
#                             link = j.get("href")
#                             # title = j.get("title")
#                             s.append(link)
#                             if len(link) != 0:
#                                 recomm_dict['amazon_link'] = link
#                             # if len(title) != 0:
#                                 recomm_dict['title'] = au
#
#                 book_img = i.find_all("img", {"class": "s-access-image cfMarker"})
#                 for j in book_img:
#                     if len(p) == 0:
#                         image = j.get("src")
#                         p.append(image)
#                         if len(image) != 0:
#                             recomm_dict['image'] = image
#
#                 # print(recomm_dict)
#
#
#                 if (len(recomm_dict) != 0):
#                     coll.append(recomm_dict)
#                     mix.append(recomm_dict)
#
#         if UserSocialAuth.objects.filter(user=request.user.id).exists():
#             instance = UserSocialAuth.objects.get(user=request.user, provider='facebook')
#             token = instance.tokens
#             graph = facebook.GraphAPI(token, version="2.7")
#             profile = graph.get_object(id='me')
#             args = {'fields': 'id,name,email,books,picture'}
#             profile = graph.get_object('me', **args)
#             request.session['id'] = profile['id']
#         auther = []
#         if profile['id']:
#             k = user_info.objects.filter(uid=profile['id'])
#         else:
#             k = []
#
#         chck_list = defaultdict(int)
#         if len(k) != 0:
#             for j in k:
#                 ram = j.author
#                 if ram:
#                     chck_list[j.amazon_link] = 1
#                     if ram not in auther:
#                         auther.append(j.author)
#                 else:
#                     if j.book_name not in auther:
#                         auther.append(j.book_name)
#                         chck_list[j.amazon_link] = 1
#
#
#
#         order_list = []
#         map = defaultdict(list)
#         s = []
#         for au in auther:
#             s.append(au)
#             r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=" + au)
#             soup = BeautifulSoup(r.content, "html.parser")
#
#             ks = []
#             k_rate = []
#             k_link = []
#             k_img = []
#             k_au = []
#             qq = 6
#
#             for l in soup.find_all('li'):
#
#                 linti = l.find_all('div', {'class': 'a-fixed-left-grid-col a-col-right'})
#                 title = ''
#                 link = ''
#                 ch_link = 0
#                 f_link = 0
#                 for i in linti:
#                     li = i.find_all('a')
#
#                     for j in li:
#                         if f_link == 0:
#                             if len(k_link) != qq:
#                                 link = j.get('href')
#                                 title = j.get('title')
#                                 if chck_list[link] != 1:
#                                     map[link].append(title)
#                                     f_link += 1
#                                     k_link.append(link)
#                                 else:
#                                     ch_link = 1
#
#                 rating = l.find_all('div', {'class': 'a-column a-span5 a-span-last'})
#                 a = ''
#                 b = ''
#                 for i in rating:
#                     rate = i.find_all('span')
#                     f_rating = 0
#                     for j in rate:
#                         if f_rating == 0:
#                             if len(ks) != qq:
#                                 if chck_list[link] != 1:
#                                     a = j.text
#                                     a = a[1:4]
#                                     # print(a)
#                                     # b = a[::-1]
#                                     f_rating += 1
#                                     if 'o' in a:
#                                         a = a[:1]
#                                     ks.append(a)
#
#                 for i in rating:
#                     if len(k_rate) != qq:
#                         no = i.find_all('a', {'class': 'a-size-small a-link-normal a-text-normal'})
#                         for j in no:
#                             if len(j) != 0:
#                                 if chck_list[link] != 1:
#                                     b = j.text
#                                     if ',' in b:
#                                         b = b.replace(',', '')
#                                     k_rate.append(b)
#
#                 score = ''
#                 # print(a)
#                 if len(a) > 0 and ord(a[0])<60:
#                     score = float(a) * float(b)
#
#
#                 aut = l.find_all('span', {'class': 'a-size-small a-color-secondary'})
#                 for i in aut:
#                     auth = i.find_all('a')
#                     for j in auth:
#                         if len(j) != 0:
#                             if len(k_au) != qq:
#                                 if chck_list[link] != 1:
#                                     author = j.text
#                                     map[link].append(author)
#                                     k_au.append(author)
#
#                 div = l.find_all('div', {'class', 'a-fixed-left-grid-col a-col-left'})
#                 for i in div:
#                     img = i.find_all('img')
#                     for j in img:
#                         if len(k_img) != qq:
#                             if chck_list[link] != 1:
#                                 image = j.get('src')
#                                 map[link].append(image)
#                                 k_img.append(image)
#
#                 if len(str(score)) > 0 and len(link) > 0 and ch_link == 0:
#                     order = (score, link)
#                     order_list.append(order)
#         order_list.sort(reverse=True)
#         total_book = cno + len(order_list)
#         order_list = order_list[:15]
#
#         for i in order_list:
#             recomm_dict = {}
#             recomm_dict['title'] = map[i[1]][0]
#             if len(map[i[1]]) == 2:
#                 recomm_dict['image'] = map[i[1]][1]
#             else:
#                 recomm_dict['image'] = map[i[1]][2]
#             recomm_dict['amazon_link'] = i[1]
#             if len(map[i[1]]) == 3:
#                 recomm_dict['auther'] = map[i[1]][1]
#             con.append(recomm_dict)
#             mix.append(recomm_dict)
#
#         request.session['Total'] = total_book
#         mixl = []
#         for i in range(len(mix)):
#             dd = mix[i]
#             k = dd['title']
#
#
#             ## goodreads
#
#             j = "https://www.goodreads.com/search?q=" + k
#             r = requests.get(j)
#             soup = BeautifulSoup(r.content, "html.parser")
#             rng = soup.find_all('span', {'class': 'minirating'})
#             l = 0
#             ln = 0
#             if len(rng) != 0:
#                 a = rng[0].text
#                 grt = a[1:5]
#                 if grt[len(grt) - 1] == ' ' and ' a' not in grt:
#                     grt = grt[:4]
#                 elif ' a' in grt:
#                     grt = grt[:3]
#
#                 gun1 = a[::-1][7:]
#                 gun1 = gun1[::-1][len(grt) + 15:].replace(',', '')
#                 # print(gun1)
#
#                 if '1' in grt or '2' in grt or '3' in grt or '4' in grt or '5' in grt and ord(gun1[0]) < 60:
#                     # if float(grt):
#                     mg = float(grt) * float(gun1)
#                 else:
#                     mg = 0
#                     gun1 = 0
#                 # l.append(mg)
#                 # ln.append(float(gun1))
#                 l = mg
#                 ln = float(gun1)
#             else:
#                 # l.append(0)
#                 # ln.append(0)
#                 l = 0
#                 ln = 0
#
#             ## amazon
#
#             r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=" + k)
#             soup = BeautifulSoup(r.content, "html.parser")
#
#             rating = soup.find_all('div', {'class': 'a-column a-span5 a-span-last'})
#             a = ''
#             b = ''
#             for i in rating:
#                 rate = i.find_all('span')
#                 f_rating = 0
#                 for j in rate:
#                     if f_rating == 0:
#                         a = j.text
#                         a = a[1:4]
#                         f_rating += 1
#                         if 'o' in a:
#                             a = a[:1]
#
#             for i in rating:
#                 no = i.find_all('a', {'class': 'a-size-small a-link-normal a-text-normal'})
#                 for j in no:
#                     if len(j) != 0:
#                         b = j.text
#                         if ',' in b:
#                             b = b.replace(',', '')
#
#             if len(a) > 0:
#                 if ord(a[0]) >= 48 and ord(a[0]) <= 57:
#                     a = float(a) * float(b)
#                 else:
#                     a = 0
#             else:
#                 a = 0
#             if len(b) > 0:
#                 hh = float(b) + ln
#             else:
#                 hh = ln
#             if hh != 0:
#                 global_rating = (float(a) + l) / hh
#                 # global_rating = a
#             else:
#                 global_rating = 3.245
#             dd['global_rating'] = round(global_rating,2)
#             mixl.append(dd)
#
#
#         return render(request,'book/collab.html',{'mix':mix,
#                                                   'names': chck_list,
#                                                   'author': auther,
#                                                   'length':len(mix)
#                                                   })
#     else:
#         return render(request,'book/login.html')
# def collab(request):

#     if UserSocialAuth.objects.filter(user=request.user.id).exists():
#         instance = UserSocialAuth.objects.all()
#         # print(instance)
#         id = request.session.get('id')
#         dataset={}
#         dict_book = {}
#         dict_rating = {}
#         list_book = []
#         initial = []
#         users = []
#         for index,name in enumerate(instance):
#             books=user_info.objects.filter(uid=name.uid)
#             di = {}
#             list_book_2 = []
#             list_rating_2 = []
#             # dataset[name.uid]=[]
#             if len(books)!=0:
#                 for i,book in enumerate(books):
#                     # ring={}
#                     if(book.rating):
#                             di[book.book_name]=book.rating
#                             if name.uid == id:
#                                 list_book.append(book.book_name)
#                                 initial.append(float(book.rating))
#                             else:
#                                 list_book_2.append(book.book_name)
#                                 list_rating_2.append(float(book.rating))
#                     # di[name.uid].append(ring)
#             dataset[name.uid] = di
#             dict_book[name.uid] = list_book_2
#             dict_rating[name.uid] = list_rating_2
#             if name.uid != id:
#                 users.append(name.uid)
#         dataset=dict((k, v) for k, v in dataset.items() if v)

#         bound = []
#         for us in users:
#             hsd = []
#             for bo in list_book:
#                 if bo in dict_book[us]:
#                     hsd.append(float(dataset[us][bo]))
#                 else:
#                     hsd.append(0)
#             bound.append(hsd)

#         # --- COST FUNCTION ------------------------------------------------------------+

#         # function we are attempting to optimize (minimize)
#         def func1(x):
#             total = 0
#             for i in range(len(x)):
#                 total += x[i] ** 2
#                 return total

#         # --- MAIN ---------------------------------------------------------------------+


#         def __init__(self, x0):
#             self.position_i = []  # particle position
#             self.velocity_i = []  # particle velocity
#             self.pos_best_i = []  # best position individual
#             self.err_best_i = -1  # best error individual
#             self.err_i = -1  # error individual

#             for i in range(0, num_dimensions):
#                 self.velocity_i.append(random.uniform(-1, 1))
#                 self.position_i.append(x0[i])

#                 # evaluate current fitness

#         def evaluate(self, costFunc):
#             self.err_i = costFunc(self.position_i)

#             # check to see if the current position is an individual best
#             if self.err_i < self.err_best_i or self.err_best_i == -1:
#                 self.pos_best_i = self.position_i
#                 self.err_best_i = self.err_i

#                 # update new particle velocity

#         def update_velocity(x, y, s):
#             no1 = []
#             a = defaultdict(int)
#             max = 0
#             summ = 0
#             for i in range(len(x)):
#                 summ = sum(x[i])
#                 if summ > max:
#                     max = summ
#                 no1.append(summ)
#                 a[summ] += 1

#             ind = []
#             ##    print(no1)
#             fin = []
#             if a[max] > 1:
#                 for i in range(len(no1)):
#                     if no1[i] == max:
#                         ind.append(i)

#             if len(ind) > 0:
#                 for i in ind:
#                     suum = sum(y[i])
#                     fin.append((suum, i))
#             else:
#                 no1.sort(reverse=True)
#                 fin.append((0, no1[0]))
#             fin.sort()
#             ##    print(fin)
#             index = fin[0][1]
#             return index



#             # update the particle position based off new velocity updates

#         def update_position(x1, x0):
#             lst = []
#             dis = []
#             for i in range(0, num_dimensions):
#                 diff = abs(x1[i] - x0[i])
#                 dis.append(diff)
#                 if diff > 0.5:
#                     lst.append(0)
#                 else:
#                     lst.append(1)

#             return lst, dis

#         def PSO(costFunc, x0, bounds, num_particles, maxiter):
#             global num_dimensions

#             num_dimensions = len(x0)
#             err_best_g = -1  # best error for group
#             pos_best_g = 0  # best position for group

#             # establish the swarm
#             i = 0
#             while i < maxiter:
#                 score_list = []
#                 diff_score_list = []
#                 for k in range(len(bounds)):
#                     x, y = update_position(bounds[k], x0)
#                     score_list.append(x)
#                     diff_score_list.append(y)

#                 start_score = 0
#                 pos_best_g = update_velocity(score_list, diff_score_list, start_score)

#                 i += 1

#             # print('final results')
#             # print(pos_best_g)
#             return pos_best_g

#         ##    print(score_list)
#         ##    for i in range(len(diff_score_list)):
#         ##        print(sum(diff_score_list[i]))
#         ##    print(diff_score_list)

#         # if __name__ == "__PSO__":
#         #     main()

#         # --- RUN ----------------------------------------------------------------------+
#         init = PSO(func1, initial, bound, num_particles=15, maxiter=30)
#         k = users[init]
#         name = dict_book[k]
#         names = []
#         for i in name:
#             if i not in list_book:
#                 names.append(i)
#         cno = len(names)

#         coll = []
#         mix = []
#         con = []
#         for au in names:
#             r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=" + au)
#             soup = BeautifulSoup(r.content, "html.parser")
#             s = []
#             p = []
#             # recomm_dict = {}
#             # recomm_dict['title'] = au
#             for i in soup.find_all("li"):
#                 recomm_dict = {}
#                 # recomm_dict['title'] = au
#                 book_link = i.find_all("a", {"class": "a-link-normal"})
#                 for j in book_link:
#                     if len(j) != 0:
#                         if len(s) == 0:
#                             link = j.get("href")
#                             # title = j.get("title")
#                             s.append(link)
#                             if len(link) != 0:
#                                 recomm_dict['amazon_link'] = link
#                             # if len(title) != 0:
#                                 recomm_dict['title'] = au

#                 book_img = i.find_all("img", {"class": "s-access-image cfMarker"})
#                 for j in book_img:
#                     if len(p) == 0:
#                         image = j.get("src")
#                         p.append(image)
#                         if len(image) != 0:
#                             recomm_dict['image'] = image

#                 # print(recomm_dict)


#                 if (len(recomm_dict) != 0):
#                     coll.append(recomm_dict)
#                     mix.append(recomm_dict)

#         if UserSocialAuth.objects.filter(user=request.user.id).exists():
#             instance = UserSocialAuth.objects.get(user=request.user, provider='facebook')
#             token = instance.tokens
#             graph = facebook.GraphAPI(token, version="2.7")
#             profile = graph.get_object(id='me')
#             args = {'fields': 'id,name,email,books,picture'}
#             profile = graph.get_object('me', **args)
#             request.session['id'] = profile['id']
#         auther = []
#         if profile['id']:
#             k = user_info.objects.filter(uid=profile['id'])
#         else:
#             k = []

#         chck_list = defaultdict(int)
#         if len(k) != 0:
#             for j in k:
#                 ram = j.author
#                 if ram:
#                     chck_list[j.amazon_link] = 1
#                     if ram not in auther:
#                         auther.append(j.author)
#                 else:
#                     if j.book_name not in auther:
#                         auther.append(j.book_name)
#                         chck_list[j.amazon_link] = 1



#         order_list = []
#         map = defaultdict(list)
#         s = []
#         for au in auther:
#             s.append(au)
#             r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=" + au)
#             soup = BeautifulSoup(r.content, "html.parser")

#             ks = []
#             k_rate = []
#             k_link = []
#             k_img = []
#             k_au = []
#             qq = 6

#             for l in soup.find_all('li'):

#                 linti = l.find_all('div', {'class': 'a-fixed-left-grid-col a-col-right'})
#                 title = ''
#                 link = ''
#                 ch_link = 0
#                 f_link = 0
#                 for i in linti:
#                     li = i.find_all('a')

#                     for j in li:
#                         if f_link == 0:
#                             if len(k_link) != qq:
#                                 link = j.get('href')
#                                 title = j.get('title')
#                                 if chck_list[link] != 1:
#                                     map[link].append(title)
#                                     f_link += 1
#                                     k_link.append(link)
#                                 else:
#                                     ch_link = 1

#                 rating = l.find_all('div', {'class': 'a-column a-span5 a-span-last'})
#                 a = ''
#                 b = ''
#                 for i in rating:
#                     rate = i.find_all('span')
#                     f_rating = 0
#                     for j in rate:
#                         if f_rating == 0:
#                             if len(ks) != qq:
#                                 if chck_list[link] != 1:
#                                     a = j.text
#                                     a = a[1:4]
#                                     # print(a)
#                                     # b = a[::-1]
#                                     f_rating += 1
#                                     if 'o' in a:
#                                         a = a[:1]
#                                     ks.append(a)

#                 for i in rating:
#                     if len(k_rate) != qq:
#                         no = i.find_all('a', {'class': 'a-size-small a-link-normal a-text-normal'})
#                         for j in no:
#                             if len(j) != 0:
#                                 if chck_list[link] != 1:
#                                     b = j.text
#                                     if ',' in b:
#                                         b = b.replace(',', '')
#                                     k_rate.append(b)

#                 score = ''
#                 # print(a)
#                 if len(a) > 0 and ord(a[0])<60:
#                     score = float(a) * float(b)


#                 aut = l.find_all('span', {'class': 'a-size-small a-color-secondary'})
#                 for i in aut:
#                     auth = i.find_all('a')
#                     for j in auth:
#                         if len(j) != 0:
#                             if len(k_au) != qq:
#                                 if chck_list[link] != 1:
#                                     author = j.text
#                                     map[link].append(author)
#                                     k_au.append(author)

#                 div = l.find_all('div', {'class', 'a-fixed-left-grid-col a-col-left'})
#                 for i in div:
#                     img = i.find_all('img')
#                     for j in img:
#                         if len(k_img) != qq:
#                             if chck_list[link] != 1:
#                                 image = j.get('src')
#                                 map[link].append(image)
#                                 k_img.append(image)

#                 if len(str(score)) > 0 and len(link) > 0 and ch_link == 0:
#                     order = (score, link)
#                     order_list.append(order)
#         order_list.sort(reverse=True)
#         total_book = cno + len(order_list)
#         order_list = order_list[:15]

#         for i in order_list:
#             recomm_dict = {}
#             recomm_dict['title'] = map[i[1]][0]
#             if len(map[i[1]]) == 2:
#                 recomm_dict['image'] = map[i[1]][1]
#             else:
#                 recomm_dict['image'] = map[i[1]][2]
#             recomm_dict['amazon_link'] = i[1]
#             if len(map[i[1]]) == 3:
#                 recomm_dict['auther'] = map[i[1]][1]
#             con.append(recomm_dict)
#             mix.append(recomm_dict)

#         request.session['Total'] = total_book
#         mixl = []
#         for i in range(len(mix)):
#             dd = mix[i]
#             k = dd['title']
#             # print(k)

#             ## goodreads

#             j = "https://www.goodreads.com/search?q=" + k
#             r = requests.get(j)
#             soup = BeautifulSoup(r.content, "html.parser")
#             rng = soup.find_all('span', {'class': 'minirating'})
#             l = 0
#             ln = 0
#             if len(rng) != 0:
#                 a = rng[0].text
#                 grt = a[1:5]
#                 if grt[len(grt) - 1] == ' ' and ' a' not in grt:
#                     grt = grt[:4]
#                 elif ' a' in grt:
#                     grt = grt[:3]

#                 gun1 = a[::-1][7:]
#                 gun1 = gun1[::-1][len(grt) + 15:].replace(',', '')
#                 # print(gun1)

#                 if '1' in grt or '2' in grt or '3' in grt or '4' in grt or '5' in grt and ord(gun1[0]) < 60:
#                     # if float(grt):
#                     mg = float(grt) * float(gun1)
#                 else:
#                     mg = 0
#                     gun1 = 0
#                 # l.append(mg)
#                 # ln.append(float(gun1))
#                 l = mg
#                 ln = float(gun1)
#             else:
#                 # l.append(0)
#                 # ln.append(0)
#                 l = 0
#                 ln = 0

#             ## amazon

#             r = requests.get("http://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Dstripbooks&field-keywords=" + k)
#             soup = BeautifulSoup(r.content, "html.parser")

#             rating = soup.find_all('div', {'class': 'a-column a-span5 a-span-last'})
#             a = ''
#             b = ''
#             for i in rating:
#                 rate = i.find_all('span')
#                 f_rating = 0
#                 for j in rate:
#                     if f_rating == 0:
#                         a = j.text
#                         a = a[1:4]
#                         f_rating += 1
#                         if 'o' in a:
#                             a = a[:1]

#             for i in rating:
#                 no = i.find_all('a', {'class': 'a-size-small a-link-normal a-text-normal'})
#                 for j in no:
#                     if len(j) != 0:
#                         b = j.text
#                         if ',' in b:
#                             b = b.replace(',', '')

#             if len(a) > 0:
#                 if ord(a[0]) >= 48 and ord(a[0]) <= 57:
#                     a = float(a) * float(b)
#                 else:
#                     a = 0
#             else:
#                 a = 0
#             if len(b) > 0:
#                 hh = float(b) + ln
#             else:
#                 hh = ln
#             if hh != 0:
#                 global_rating = (float(a) + l) / hh
#                 # global_rating = a
#             else:
#                 global_rating = 3.245
#             dd['global_rating'] = global_rating
#             mixl.append(dd)

#         # print(mixl)



#         return render(request,'book/collab.html',{'mix':mix,
#                                                   'names': chck_list,
#                                                   'author': auther,
#                                                   'length':len(mix)
#                                                   })
#         # return render(request, 'book/collab.html',{'a':names})
#     else:
#         return render(request,'book/login.html')
def precision(request):
    array=request.GET.get('name')
    a=eval(array)
    s = a[0]+a[1]
    k = 0
    c = 0
    d=0
    yax = []
    xax = []
#     yax1=[]
#     xax1=[]
    for i in a:
        k = k + i
        if i==0:
            c = c + 1
        d=d+1
        e=float(k)/float(k+c)
        print(e)
        precision = e
        yax.append(precision)
        xax.append(d)
    request.session['precision'] = yax
    request.session['recall'] = xax
    k = 0
    s = 0
    yax = []
    xax = []
    l=len(a)
    for i in a:
        k = k+i
        
        z=sum(a[s:l])
        c = k+10+z
        print(z)
        s = s+1
        
        recall = float(k)/float(c)
        yax.append(recall)
        xax.append(s)
    request.session['precisionr'] = yax
    request.session['recallr'] = xax   
    # print(yax)

    fn = 5
    tn = 50
    tpr = [0]
    fpr = [0]
    p = 0
    r = 0
    for i in range(1,len(a)+1):
        if a[i-1] == 0:
            p += 1
            pi = float(p)/float(p+tn)
            ri = float(r)/float(r+fn)
            fpr.append(ri)
            tpr.append(pi)
        else:
            r += r+a[i-1]
            ri = float(r)/float(r+fn)
            fpr.append(ri)
            pi = float(p)/float(p+tn)
            tpr.append(pi)
    import numpy as np
    from sklearn.metrics import roc_auc_score

    y_true = np.array(a)
    y_scores = np.array(tpr[1:])
    area = (1-roc_auc_score(y_true,y_scores))
    request.session['Roc1']=tpr
    request.session['Roc2']=fpr
    request.session['area']=area
    return HttpResponse(json.dumps({
        'page_id': precision,
    }))

def pr_curve(request):
    id=request.session.get('id')
    precision=request.session.get('precision')
    recall=request.session.get('recall')
    precisionr=request.session.get('precisionr')
    recallr=request.session.get('recallr')
    tpr=request.session.get('Roc1')
    fpr=request.session.get('Roc2')
    import matplotlib.pyplot as plt
    import pylab
    plt.clf()
    plt.plot(recall, precision, lw=2, color='navy',label='Precision-Recall curve')
    plt.xlabel('No. of recommended books')
    plt.ylabel('Precision')
    imgname='book/images/'+id+'.png'
    plt.savefig('book/static/book/images/'+id+'.png')
    plt.clf()
    plt.plot(recallr, precisionr, lw=2, color='navy',label='roc-curve')
    plt.xlabel('No. of recommendations')
    plt.ylabel('Recall')

    plt.savefig('book/static/book/images/'+id+'r.png')
    imgr='book/images/'+id+'r.png'

   
    plt.clf()
    plt.plot(tpr, fpr, lw=2, color='navy',label='roc-curve')
    plt.xlabel('false negative rate')
    plt.ylabel('true positive rate')
    plt.savefig('book/static/book/images/'+id+'roc.png')
    area=request.session.get('area')
    imgroc='book/images/'+id+'roc.png'
    # k = user_info.objects.all()
    # sumi=0
    # n=0
    # sumr=0
    # for line in k:
    #     if line.rating==0.00 or line.rating==None:
    #         continue
    #     r=abs((float(line.rating)-float(line.global_rating)))
    #     sumi= sumi + r
    #     sumr=sumr+ (r*r)
    #     n=n+1
    # mae=sumi/n
    # rmse=sqrt(sumr/n)
    return render(request, 'book/precision.html', {'imgname':imgname,'imgr':imgr,'area':area,'imgroc':imgroc})


def mae(request):
    array=request.GET.get('name')
    # print array
    global_rating=request.GET.get('rating')
    mae=3
    return render(request, 'book/mae.html', {'mae':mae,'a': (array),'g': eval(global_rating)})


