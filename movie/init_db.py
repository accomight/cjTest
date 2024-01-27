import random
import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

client = MongoClient("localhost", 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbjungle


def insert_all():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
    }
    data = requests.get(
        "https://search.daum.net/search?w=tot&q=%EC%98%81%ED%99%94", headers=headers
    )

   
    soup = BeautifulSoup(data.text, "html.parser")

    
    movies = soup.select("ol.type_plural.list_exact.movie_list > li")

    
    for movie in movies:
        # movie 안에 a 가 있으면,
        # (조건을 만족하는 첫 번째 요소, 없으면 None을 반환한다.)
        tag_element = movie.select_one(".wrap_cont > .info_tit > a")
        if not tag_element:
            print("error in title")
            continue
        title = tag_element.text 

        tag_element = movie.select_one("div.wrap_cont > dl:nth-child(4) > dd")
        if not tag_element:
            print("error in opendate : "+title)
            continue
        open_date = tag_element.text
        try:
            (open_year, open_month, open_day) = [
                int(element) for element in open_date[:-1].split(".")
            ]
        except ValueError:
            print("error in date : "+ title)
            continue
        
        tag_element = movie.select_one("div.wrap_cont > dl:nth-child(5) > dd")
        if not tag_element:
            print("error in viewer : "+ title)
            continue
        viewers = tag_element.findChild(string=True, recursive=False)
        viewers = int("".join([c for c in viewers if c.isdigit()]))
        
        def get_naver_search_images(query):
            url = f"https://search.naver.com/search.naver?query={query}&tbm=isch"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            data = requests.get(url, headers=headers)

            soup = BeautifulSoup(data.text, "html.parser")
            images = soup.select_one(
                "div.cm_content_area._cm_content_area_info > div > div.detail_info > a > img"
            )["src"]
            
            return images
        try : 
            poster_url=get_naver_search_images(title)
        except TypeError as e:
            print("error in images : "+ title)
            continue
        
    
        tag_element = movie.select_one(".wrap_thumb > a")
        if not tag_element: 
            print("error in href : "+ title)
            continue
        info_url = tag_element["href"]
        if not info_url:
            print("error in info : " + title)
            continue
        info_url = "https://movie.daum.net/search" + info_url

       
        found = list(db.movies.find({"title": title}))
        if found:
            continue

        # 좋아요를 random 으로 정한다 [0, 100)
        likes = random.randrange(0, 100)

        doc = {
            "title": title,
            "open_year": open_year,
            "open_month": open_month,
            "open_day": open_day,
            "viewers": viewers,
            "poster_url": poster_url,
            "info_url": info_url,
            "likes": likes,
            "trashed": False,
        }
        db.movies.insert_one(doc)
        print(
            "완료: ",
            title,
            open_year,
            open_month,
            open_day,
            viewers,
            poster_url,
            info_url,
        )


if __name__ == "__main__":
    # 기존의 movies 콜렉션을 삭제하기
 db.movies.drop()

    # 영화 사이트를 scraping 해서 db 에 채우기
 insert_all()
