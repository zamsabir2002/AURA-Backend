import os
import json

if os.path.exists('./result.json'):
    # try:
    with open("result.json", "r+") as file:
        data = json.load(file)

# print(data)
for i in data['scan']:
    print(i)
    print(json.dumps(i))
    print('\n\n')
