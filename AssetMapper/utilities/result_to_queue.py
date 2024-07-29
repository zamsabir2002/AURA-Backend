import os
import json
from AssetMapper.utilities.publish_message import publish_message


def publish_result_to_queue():
    if os.path.exists('./result.json'):
        with open("result.json", "r+") as file:
            data = json.load(file)

    for each in data['scan']:
        print("Host --> ", each.get('addresses').get('ipv4'))
        publish_message(message=each, queue='result_queue')
