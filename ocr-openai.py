import os
from openai import OpenAI
import pymysql


model_engine = "gpt-3.5-turbo"
client = OpenAI(
    # This is the default and can be omitted
    api_key="",
)


# csv 파일 가져오기
import csv
my_dict = {}
with open("contest_ocr_result.csv", 'r') as file:
    reader = csv.reader(file)
    for link, text in reader:
        my_dict[link] = text


conn = pymysql.connect(host='', port=3306, user='', password='', db='', charset='utf8')
cur = conn.cursor()

N = len(list(my_dict.values()))
# N = 1
for i in range(N):
    link = list(my_dict.keys())[i]
    ocr = list(my_dict.values())[i]

    prompt = ocr + "\n 이 텍스트에서 지원자격, 우대사항 을 뽑아서 '지원자격:' , '우대사항:' 이렇게 적어줘"
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model_engine,
    )

    res = chat_completion.choices[0].message.content
    # "지원자격:"과 "우대사항:" 사이의 값을 가져오기
    requirement_start_index = res.find("지원자격:") + len("지원자격:")
    requirement_end_index = res.find("우대사항:")
    requirement = res[requirement_start_index:requirement_end_index].strip().replace("\'", "")

    # "우대사항:" 이후의 값을 가져오기
    preferred_start_index = res.find("우대사항:") + len("우대사항:")
    preferred = res[preferred_start_index:].strip().replace("\'", "")

    print(i)
    sql = f"update event set requirement='{requirement}', preferred='{preferred}' where image like '{link}'"
    cur.execute(sql)
    conn.commit()
    
cur.close()
conn.close()
