#!/home/harvey/Python/venvs/xword python

# Web scraping stuff shared by all scrapes

# HTTP for humans
# https://pypi.org/project/requests/
import requests
#from compression import zstd

# Regular expressions lib
# https'://docs.python.org/3/library/re.html
#import re
# Beautiful Soup web scraping lib
# https'://pypi.org/project/beautifulsoup4/
#import bs4


# User Agents from https://www.useragents.me/
#agent = "Mozilla/5.0"
#agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3"

# TfTT now uses zstd compression. Install pyzstd to decompress OR tell it not to compress?
# Python should be able to do gzip & deflate natively

reqheaders = {
    'Accept': "text/html", #,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    # Compression:
    #'Accept-Encoding': "gzip, deflate, br, zstd",
    'Accept-Encoding': "gzip, deflate",
    #'Accept-Encoding': "identity",
    'Accept-Language': "en",
    #'Cache-Control': "max-age=0",
    #'If-Modified-Since': Sat, 16 May 2026 15':41':44 GMT
    #'Priority': "u=0, i",
    #'Referer': "https://timesforthetimes.co.uk",
    #'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126"',
    #'Sec-Ch-Ua-Mobile': '?0',
    #'Sec-Ch-Ua-Platform': '"Linux"',
    #'Sec-Fetch-Dest': 'document',
    #'Sec-Fetch-Mode': 'navigate',
    #'Sec-Fetch-Site': 'cross-site',
    #'Sec-Fetch-User': '?1',
    #'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Connection': 'keep-alive'
    }

def getpage(url, session):
    # Use of a session allows for cookies
    # Session is global and retained unless error
    
    txt = None
    # How many tries should we have? 3: 0..2
    for i in range(3):
        try:
            session = session or requests.Session()
            response = session.get(url=url, headers=reqheaders)
            #print(response.headers)
            # Could detect encoding in headers and decompress here. Or disable compression
            txt = response.text
            print(f"Getpage: ok={response.ok}, status={response.status_code}")
            break
        except Exception as e:
            print("Error in getpage: " + str(e))
            session = None

    return txt
# End getpage ----------------------------------------------------------

"""
# Extract text only parts from HTML
def html2txt(txt):
    # Specify the Parser as lxml
    soup = bs4.BeautifulSoup(txt, features="lxml")
    txt = soup.get_text()
    return txt
# End clean_text
"""
"""
# Remove non-ASCII characters
def cleantext(txt):
    # Remove non-ASCII characters
    # BUT ... there are a few we want to keep. Convert to ASCII?  
    txt = re.sub(r'[^\x00-\x7F]+', '', txt)
    return txt
# End clean_text
"""
