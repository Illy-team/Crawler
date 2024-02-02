import re
import pymysql
import requests
from bs4 import BeautifulSoup

conn = pymysql.connect(host='', port=3306, user='', password='', db='', charset='utf8')
cur = conn.cursor()

# 전체: https://www.contestkorea.com/sub/list.php?displayrow=12&int_gbn=2&Txt_sGn=1&Txt_key=all&Txt_word=&Txt_bcode=&Txt_code1=&Txt_aarea=&Txt_area=&Txt_sortkey=a.int_sort&Txt_sortword=desc&Txt_host=&Txt_tipyn=&Txt_comment=&Txt_resultyn=&Txt_actcode=&page=
# IT: https://www.contestkorea.com/sub/list.php?int_gbn=1&Txt_bcode=030510001

# int_gbn = 1: 공모전, int_gbn = 2: 대외활동
for i in range(1, 10):
    main_url = f'https://www.contestkorea.com/sub/list.php?displayrow=12&int_gbn=1&Txt_sGn=1&Txt_key=all&Txt_word=&Txt_bcode=&Txt_code1=&Txt_aarea=&Txt_area=&Txt_sortkey=a.int_sort&Txt_sortword=desc&Txt_host=&Txt_tipyn=&Txt_comment=&Txt_resultyn=&Txt_actcode=&page={i}'
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(main_url, headers=headers)
    soup = BeautifulSoup(res.content.decode('utf-8', 'replace'), 'html.parser')

    list_crawl = soup.select('#frm > div > div.list_style_2 > ul > li > div.title')

    for div in list_crawl:
        sub_link = div.find('a')['href']   
        print(sub_link) 
        url = 'https://www.contestkorea.com/sub/' + sub_link
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content.decode('utf-8', 'replace'), 'html.parser')
        
        try:
            result = {}
            result["title"] = soup.select('#wrap > div.container.list_wrap > div.left_cont > div.view_cont_area > div.view_top_area.clfx > h1')[0].text
            result["image"] = "https://www.contestkorea.com" + soup.select('#wrap > div.container.list_wrap > div.left_cont > div.view_cont_area > div.view_top_area.clfx > div.clfx > div.img_area > div > img')[0]['src']
            trs = soup.select('tr')
            result["host_name"] = trs[0].select('td')[0].text.strip().replace("\t", "")
            result["category"] = trs[1].select('td')[0].text.strip().replace("\t", "")
            result["requirements"] = trs[2].select('td')[0].text.strip().replace("\t", "")
            result["apply_date"] = trs[3].select('td')[0].text.strip().replace("\t", "")
            result["activity_date"] = trs[4].select('td')[0].text.strip().replace("\t", "")
            try:
                result["link"] = trs[7].select('td')[0].find('a')['href']
            except:
                result["link"] = ""
                        
            import csv

            # 파일이랑 헤더는 미리 준비
            header = ["title", "image", "host_name", "category", "requirements", "apply_date", "activity_date", "link"]
            with open("event-activity.csv", 'a') as file:
                csv_writer = csv.DictWriter(file, fieldnames=header)
                csv_writer.writerow(result)
                        
            sql = f"""INSERT INTO event (type, host_name, image, title, category, apply_date, requirement, link, activity_date) 
                values ("CONTEST", '{result["host_name"]}', '{result["image"]}', '{result["title"]}', '{result["category"]}', 
                '{result["apply_date"]}', '{result["requirements"]}', '{result["link"]}', '{result["activity_date"]}');"""
            cur.execute(sql)
            conn.commit()
        except:
            continue

cur.close()
conn.close()
