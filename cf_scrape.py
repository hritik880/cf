from bs4 import BeautifulSoup  # scrape data
from urllib.request import urlopen, Request  # get and post requests using url
import mechanize  # backend browser
import os  # for arranging into folders and renaming files
import pdfkit  # for creating pdf
import sys # for sys.exit()

print("Page no of problemset whose questions to be downloaded")
print("(should be from 1 to 55)", end=" ")
page = input().strip()

if not os.path.exists("page" + page):
    os.makedirs("page" + page)

list1 = [file for file in os.listdir("./" + "page" + page + "/")]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
url = "https://www.codeforces.com/problemset/page/" + page
req = Request(url=url, headers=headers)
data = urlopen(req).read()

soup = BeautifulSoup(data, features="lxml")

problems = soup.find('table', class_="problems").find_all('tr')
print("\nProb no\t\tName")
for i in range(1, len(problems)):
    print(str(i) + "\t" + problems[i].a.string.strip() + " - " + problems[i].div.a.string.strip())

print("\nTo download all, type 'all'")
print("To download in range, type '<from_prob_no> : <to_prob_no>' eg. 3:7")
print("To download discrete problems, separate prob nos by comma(,)")
print("To download single problem, type prob no", end=" ")

query = input().strip()
print()

to_download = []
if query.lower() == "all":
    to_download = range(1, len(problems))

elif query.find(':') != -1:
    index = query.index(':')
    begin = int(query[ : index].strip())
    end = int(query[index+1 : ].strip())

    if begin < 1 or end >= len(problems):
        print("Error: Invalid range")
        sys.exit()

    to_download = range(begin, end+1)

elif query.find(',') != -1:
    to_download = [int(x.strip()) for x in query.split(",")]

else:
    to_download = [int(query)]

# adjust your page display settings here
options = {
    'quiet': '',
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None
}

# Gets problem's name, code, related_url
for prob_no in to_download:
    if prob_no < 1 or prob_no >= len(problems):
        print(str(prob_no) + ". Error: Invalid prob no")
        continue

    row = problems[prob_no]
    code = row.a.string.strip()
    name = row.div.a.string.strip()
    pdfName = code + " - " + name + '.pdf'

    if (pdfName in list1):
        print (str(prob_no) + ". \"" + pdfName + "\" already exists")
        continue

# opening and saving questions.
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    prob_url = "https://www.codeforces.com" + row.a.get('href')
    response = br.open(prob_url)
    data = response.read()

    bsoup = BeautifulSoup(data, features="lxml")

    css = ""
    for stylesheet in bsoup.find_all('link', rel="stylesheet") :
        css_url = "https:" + stylesheet.get('href')
        br1 = mechanize.Browser()
        br1.set_handle_robots(False)
        br1.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        response1 = br1.open(css_url)
        data1 = response1.read()

        temp = BeautifulSoup(data1, features="lxml")
        css += str(temp)

    css = "<style>" + css + "</style>"
    ques = bsoup.find('div', class_="ttypography")
    ques = str(ques)
    tags = bsoup.find_all('div', class_="roundbox sidebox")[2]
    tags = str(tags)

    html = css + ques + "<div style=\"margin:2em\"></p>" + tags
    pdfkit.from_string(html, pdfName, options=options)
    os.rename(pdfName, "./" + "page" + page + "/" + pdfName)
    print(str(prob_no) + ". \"" + pdfName + "\" downloaded")

print("\nFinished.")
