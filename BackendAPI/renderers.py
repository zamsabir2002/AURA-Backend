from rest_framework import renderers
import json

class UserErrorRenderer(renderers.JSONRenderer):
    charset='utf-8'
    def render(self, data):
        response = ''
        if 'ErrorDetail' in str(data):
            response = json.dumps({'Errors':data})
        else:
            response = json.dumps(data)
        return response