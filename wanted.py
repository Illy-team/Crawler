import pandas as pd
from pandas import json_normalize
from bs4 import BeautifulSoup
import re
import requests
import json
import pymysql

conn = pymysql.connect(host='', port=3306, user='', password='', db='', charset='utf8')
cur = conn.cursor()

# IT: https://www.wanted.co.kr/api/chaos/navigation/v1/results?1706798483752&job_group_id=518&years=-1&locations=all&country=kr&job_sort=job.recommend_order

main_url = "https://www.wanted.co.kr/api/chaos/navigation/v1/results?1706186671919&years=-1&locations=all&country=kr&job_sort=job.recommend_order&limit=100"
main_res = json.loads(requests.get(main_url).text)
for e in main_res["data"]:
    detail_url = f'https://www.wanted.co.kr/api/chaos/jobs/v1/{e["id"]}/details'
    res = json.loads(requests.get(detail_url).text)
    result = {}
    result["host_name"] = res["job"]["company"]["name"]
    result["image"] = res["job"]["company"]["logo_img"]["origin"]
    result["title"] = res["job"]["detail"]["position"]
    # dup_sql = "select count(event_id) from event where title like '{}' and host_name like '{}';".format(result["title"], result["host_name"])
    # dup = cur.execute(dup_sql)
    # print(result["title"],dup_sql)
    # if dup > 0:
    #     print("duplicated!")
    #     continue
    result["category"] = res["job"]["category_tag"]["parent_tag"]["text"]
    if res["job"]["due_time"]:
        result["apply_date"] = res["job"]["due_time"]
    else:
        result["apply_date"] = "상시채용"
    result["tasks"] = res["job"]["detail"]["main_tasks"]
    result["requirements"] = res["job"]["detail"]["requirements"].replace('\'', '')
    result["preferred"] = res["job"]["detail"]["preferred_points"]
    result["link"] = "https://www.wanted.co.kr/wd/" + str(e["id"])
    print(e["id"])
    
    
    import csv

    # 파일이랑 헤더는 미리 준비
    headers = list(result.keys())
    with open("event-job.csv", 'a') as file:
        csv_writer = csv.DictWriter(file, fieldnames=headers)
        csv_writer.writerow(result)

    try:
        sql = f"""INSERT INTO event (type, host_name, image, title, category, apply_date, tasks, requirement, preferred, link) 
                    values ("JOB", '{result["host_name"]}', '{result["image"]}', '{result["title"]}', '{result["category"]}', 
                    '{result["apply_date"]}', '{result["tasks"]}', '{result["requirements"]}', '{result["preferred"]}', '{result["link"]}');"""
        cur.execute(sql)
        conn.commit()
    except:
        continue
cur.close()
conn.close()
