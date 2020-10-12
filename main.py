from bs4 import BeautifulSoup  # scrape data
from urllib.request import urlopen, Request  # get and post requests using url
from urllib.error import URLError   # report errors occured
import mechanize  # backend browser
import os
import shutil
import zipfile
import pdfkit  # for creating pdf
import sys  # for sys.exit()
from flask import Flask, flash, redirect, render_template, request, url_for, jsonify, send_from_directory, send_file
app = Flask(__name__)

to_return = {}

@app.route('/')
def index():
   return render_template('index.html')


@app.route('/form-0', methods=['POST'])
def page_input():
   global to_return

   page = request.form['pageno']
   
   headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
   url = "https://www.codeforces.com/problemset/page/" + page

   to_return = {}
   req = Request(url=url, headers=headers)
   try:
      response = urlopen(req)
   except URLError as e:
      if hasattr(e, 'reason'):
         to_return['has_error'] = True
         to_return['error'] = "Failed to reach server. <br/>Reason: <code>{}</code>".format(e.reason)
         return to_return
      elif hasattr(e, 'code'):
         to_return['has_error'] = True
         to_return['error'] = "The server couldn't fulfill the request. <br /> Error code: <code>{}</code>".format(e.code)
         return to_return
   else:
      data = response.read()
      to_return['has_error'] = False
      to_return['error'] = ""

      soup = BeautifulSoup(data, features="lxml")
      problems = soup.find('table', class_="problems").find_all('tr')
      to_return['problems'] = []
      for i in range(1, len(problems)):
         curr_prob = {}
         curr_prob['id'] = problems[i].a.string.strip()
         curr_prob['name'] = problems[i].div.a.string.strip()
         curr_prob['link'] = "https://codeforces.com" + str(problems[i].a.get('href'))
         to_return['problems'].append(curr_prob)

      return to_return


@app.route('/download', methods=['POST'])
def download_problems():
   global to_return

   # Clearing download directory for new downloads
   folder = "./downloads"
   for file in os.listdir(folder):
      file_path = os.path.join(folder, file)
      if os.path.isfile(file_path) or os.path.islink(file_path):
         os.unlink(file_path)
      elif os.path.isdir(file_path):
         shutil.rmtree(file_path)

   # Getting list of indices of problems to download
   download_list = [int(x) for x in request.form['prob_indices'].split(',')]

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

   zip_probs = zipfile.ZipFile('./downloads/zipped_problems.zip', 'w')
   # print(download_list)
   for prob_indx in download_list:
      pdfName = to_return['problems'][int(prob_indx)]['id'] + ". " + to_return['problems'][int(prob_indx)]['name'] + '.pdf'

      # opening and saving questions.
      br = mechanize.Browser()
      br.set_handle_robots(False)
      br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
      prob_url = to_return['problems'][int(prob_indx)]['link']
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
      pdfkit.from_string(html, os.path.join(folder, pdfName), options=options)
      zip_probs.write(os.path.join(folder, pdfName), pdfName, compress_type = zipfile.ZIP_DEFLATED)

   zip_probs.close()

   try:
      return send_file('./downloads/zipped_problems.zip', attachment_filename='zipped_problems.zip')
   except Exception as e:
      return str(e)

if __name__ == '__main__':
   app.run(debug = True)
