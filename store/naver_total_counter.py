import requests
from bs4 import BeautifulSoup

target = "모터"
web_url = "https://search.naver.com/search.naver?sm=top_hty&fbm=0&ie=utf8&query=" + target
req = requests.get(web_url)
soup = BeautifulSoup(req.text, 'html.parser')
result = soup.find_all('p', class_="title_desc title_desc_v2")
print(result[0].text)
