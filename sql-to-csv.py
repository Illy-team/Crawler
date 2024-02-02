import pandas as pd
import pymysql

# MySQL 연결
conn = pymysql.connect(host='', port=3306, user='', password='', db='', charset='utf8')
cursor = conn.cursor()

# SQL 쿼리
sql_query = 'SELECT * FROM event where type=\'CONTEST\''

# SQL 쿼리 실행 및 결과 가져오기
cursor.execute(sql_query)
result = cursor.fetchall()

# 컬럼 이름 가져오기
columns = [column[0] for column in cursor.description]

# 결과를 DataFrame으로 변환
data_frame = pd.DataFrame(result, columns=columns)

# CSV 파일로 저장
csv_filename = 'contest-output.csv'
data_frame.to_csv(csv_filename, index=False)

# 연결 종료
cursor.close()
conn.close()

print(f'Table data exported to {csv_filename}')
