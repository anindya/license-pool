import requests
import json
import time

res = requests.get('http://localhost:5000/licenses')
licenses = json.loads(res.text)


def request(uname, password, cid):
    res = requests.post('http://localhost:5000/license/request',
                        json={'username': uname,
                              'password': password,
                              'container_id': cid})
    return res


res = request('Emma', 'abcd', 'foo')
assert res.status_code == 200
res = request('Emma', 'abcd', 'bar')
assert res.status_code == 403
res = request('John', 'efgh', 'baz')
assert res.status_code == 200
res = request('John', 'efgh', 'boom')
assert res.status_code == 200
res = request('John', 'efgh', 'oops')
assert res.status_code == 403
time.sleep(10)
res = request('Emma', 'abcd', 'spam')
assert res.status_code == 200
