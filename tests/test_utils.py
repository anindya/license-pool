import requests
import json

res = requests.get('http://localhost:5000/licenses')
licenses = json.loads(res.text)

res = requests.post('http://localhost:5000/license/request',
                    json={'username': 'Emma',
                          'password': 'abcd',
                          'container_id': 'foo'})


def request(uname, password, cid):
    res = requests.post('http://localhost:5000/license/request',
                        json={'username': uname,
                              'password': password,
                              'container_id': cid})
    return res


res = request('Emma', 'abcd', 'foo')
res = request('Emma', 'abcd', 'bar')

res = request('John', 'efgh', 'baz')
res = request('John', 'efgh', 'foobar')
res = request('John', 'efgh', 'boom')
res = request('John', 'efgh', 'oops')
