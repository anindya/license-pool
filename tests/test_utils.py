import requests
import json

res = requests.get('http://localhost:5000/licenses')
licenses = json.loads(res.text)

res = requests.post('http://localhost:5000/license/request',
                    json={'username': 'Emma',
                          'password': 'abcd',
                          'container_id': 'foo'})
