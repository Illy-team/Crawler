import pandas as pd
import numpy as np
import uuid
import json
import time
import requests
import csv

df = pd.read_csv('./event-contest.csv')

api_url = ""
secret_key = ""

for i in range(len(df[' image'])):
  print(i)
  image_url = df[' image'][i]

  request_json = {
      'images': [
          {
              'format': 'jpg',
              'name': 'demo',
              'url': image_url
          }
      ],
      'requestId': str(uuid.uuid4()),
      'version': 'V2',
      'timestamp': int(round(time.time() * 1000))
  }

  payload = json.dumps(request_json).encode('UTF-8')
  headers = {
    'X-OCR-SECRET': secret_key,
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", api_url, headers=headers, data = payload)

  try:
    json_res = json.loads(response.text)['images']
    text = ""
    for field in json_res[0]['fields']:
        text += field['inferText'] + " "
    # print(text)

    csv_res = {}
    csv_res["link"] = image_url
    csv_res["ocr_result"] = text

    header = ["link", "ocr_result"]
    with open("contest_ocr_result.csv", 'a') as file:
      csv_writer = csv.DictWriter(file, fieldnames=header)
      csv_writer.writerow(csv_res)
  except:
    continue
