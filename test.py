import os
import json

# if os.path.exists('./result.json'):
#     # try:
#     with open("result.json", "r+") as file:
#         data = json.load(file)

# # print(data)
# for i in data['scan']:
#     print(i)
#     print(json.dumps(i))
#     print('\n\n')


# import requests

# url = 'https://jsonkeeper.com/b/1BUZ'

# response = requests.get(url, verify=False)
# data = response.json()

# print(data)

# with open('result2.json', 'w') as f:
#     json.dump(data, f, indent=4)

import os
import json

if os.path.exists('./result.json'):
    with open("result.json", "r+") as file:
        data = json.load(file)
print(data['scan'])
for each_asset in data['scan']:
    pass