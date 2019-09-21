from bs4 import BeautifulSoup
import urllib.request,requests
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}

def convspc_chars(char):
    spec_chars=list("!@#$%^&*()+,/`:;'[]{}")
    if char in spec_chars:
        return '%'+str(hex(ord(char)))[2:]
    else:
        return char

'''def takeQuery():
    searchkey = input("enter search key:").strip().split(' ')
    searchkey = [key for key in searchkey if key != '']
    #spec_chars = list("!@#$%^&*()+,/`:;'[]{}")
    searchkey = '+'.join([''.join(map(convspc_chars, e)) for e in searchkey])
    return searchkey'''

def is_url_ok(url):
    try:
        return 200 == requests.head(url).status_code
    except Exception:
        return False

def url_scrape(searchkey):
    url = 'https://www.youtube.com/results?search_query=' + searchkey

    req = urllib.request.Request(url=url, headers=headers)

    page = urllib.request.urlopen(req)

    soup = BeautifulSoup(page, 'html.parser')

    titles = []
    ytb_feat = ['YouTube Home', 'Upload', 'Home', 'Trending', 'Subscriptions', 'Get YouTube Premium', 'Library',
                'History',
                'Music', 'Sports', 'Gaming', 'Movies', 'TV Shows', 'News', 'Live', 'Spotlight', '360° Video',
                'Browse channels',
                'Search for Last hour', 'Search for Today', 'Search for This week', 'Search for This month',
                'Search for This year',
                'Search for Video', 'Search for Channel', 'Search for Playlist', 'Search for Movie', 'Search for Show',
                'Search for Short (< 4 minutes)', 'Search for Long (> 20 minutes)', 'Search for Live', 'Search for 4K',
                'Search for HD', 'Search for Subtitles/CC', 'Search for Creative Commons', 'Search for 360°',
                'Search for VR180',
                'Search for 3D', 'Search for HDR', 'Search for Location', 'Search for Purchased', 'Sort by upload date',
                'Sort by view count', 'Sort by rating']
    #print(len(ytb_feat))
    a = soup.find_all('a')
    for i in range(len(a)):
        try:
            temp = a[i]['title']
            if 'http' not in temp and temp not in ytb_feat:
                titles.append(temp)
        except Exception:
            pass

    #print(len(titles), titles)

    titles = titles[:len(titles) - 1]

    urls = []
    for link in a:
        temp = link.get('href')
        if '/watch?' not in temp:
            continue
        else:
            if 'https://www.youtube.com' + temp not in urls:
                if(is_url_ok('https://www.youtube.com' + temp)):
                    urls.append('https://www.youtube.com' + temp)
                else:
                    continue


    embed_urls = [url.replace('watch?v=', 'embed/') for url in urls]
    return embed_urls,titles,urls

from flask import Flask,request
from string import Template
app=Flask(__name__)

@app.route('/')
def search():
    a='''<head><title>Search Page</title></head><body style="background-color:#181919"><br><br><center><h1 style="color:white">Enter Your Search Query Below!</h1><form action="/results" method="post">
    <input type="text" name="search"><br><br>
    <input type="submit" value="Search!">
</form></center></body>'''

    return a

@app.route('/results', methods=['POST'])
def results():
    home_title="<head><title>Youtube Search</title><style>body{background-color: #acb0b7}</style></head><h1>Your Results are here!</h1><br><br>"
    player=Template(
        '<iframe width="967" height="544" src="${url}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
    )

    title_template = Template(
        '<h2>${title_name}</h2><h3>video unavailable?<a href=${alturl} target="_blank">here</a><h3>'
    )

    Skey=request.form['search']
    if(Skey=='' or Skey==None):
        return '''<br><br><br><br><head><title>Error Page</title></head><body style="background-color:#2c2d2d"><br><br><center><h1 style="color:white">Please Enter a valid search query :(</h1>'''

    searchkey = Skey.strip().split(' ')
    searchkey = [key for key in searchkey if key != '']
    # spec_chars = list("!@#$%^&*()+,/`:;'[]{}")
    searchkey = '+'.join([''.join(map(convspc_chars, e)) for e in searchkey])

    urls,titles,alturls=url_scrape(searchkey)
    urls_and_titles=[]
    for i in range(len(urls)):
        try:
            urls_and_titles.append((urls[i], titles[i], alturls[i]))
        except Exception:
            continue
    #urls_and_titles=list(zip(urls,titles))
    final_template=''
    for url,title,alturl in urls_and_titles:
        final_template+=player.substitute(url=url)+'<br>'+title_template.substitute(title_name=title,alturl=alturl)+'<br><br>'

    return '<center>'+home_title+final_template+'</center>'

if __name__=='__main__':
    app.run(debug=True, use_reloader=True)
