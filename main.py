import time, requests, re
import base64
from QRCode2Terminal import transfer
import xml.dom.minidom
import json

session = requests.session()
# this is intend to get uuid
url = 'https://login.wx.qq.com/jslogin'
params = {
    'appid': 'wx782c26e4c19acffb',
    'redirect_uri': 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage',
    'fun': 'new',
    'lang': 'en_US',
    '_': int(time.time())
}
print("Fetching UUID...")
r = session.get(url, params=params)
# print('content:%s' % r.text)

regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";'
data = re.search(regx, r.text)
if data and data.group(1) == '200':
    uuid = data.group(2)
# print(uuid)
print("Fetching QRCode...")
# get QRCode
url = 'https://login.weixin.qq.com/qrcode/' + uuid
r = session.get(url, stream=True)
print("Saving QRCode...")

with open('QRCode.jpg', 'wb') as f:
    f.write(r.content)

print("Scan the QRCode below to login:")
transfer('QRCode.jpg')


def get_login_info(s):
    baseRequest = {}
    for node in xml.dom.minidom.parseString(s).documentElement.childNodes:
        if node.nodeName == 'skey':
            baseRequest['Skey'] = node.childNodes[0].data.encode('utf8')
        elif node.nodeName == 'wxsid':
            baseRequest['Sid'] = node.childNodes[0].data.encode('utf8')
        elif node.nodeName == 'wxuin':
            baseRequest['Uin'] = node.childNodes[0].data.encode('utf8')
        elif node.nodeName == 'pass_ticket':
            baseRequest['DeviceID'] = node.childNodes[0].data.encode('utf8')
    return baseRequest


while 1:
    url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login'
    params = {
        'loginicon': 'true',
        'uuid': uuid,
        'tip': '0',
        '_': int(time.time())
    }
    r = session.get(url, params=params)

    regx = r'window.code=(\d+);'
    data = re.search(regx, r.text)
    if not data: continue
    if data.group(1) == '200':
        print("Login Successful, fetching user data...")
        regx = r'window.code=200;\nwindow.redirect_uri="(\S+?)";'
        redirectUri = re.search(regx, r.text)

        baseRequest = get_login_info(baseRequestText)

        url = '%s/webwxinit?r=%s' % (redirectUri, int(time.time()))
        data = {
            'BaseRequest': baseRequest,
        }
        headers = {'ContentType': 'application/json; charset=UTF-8'}
        r = session.post(url, data=json.dumps(data), headers=headers)
        dic = json.loads(r.content.decode('utf-8', 'replace'))

        print('Log in as %s' % dic['User']['NickName'])
        break
    elif data.group(1) == '201':

        print("Scanned. Requesting to login...")
        regx = r'window.code=201;window.userAvatar = \'data:img/jpg;base64,(\S+?)\';'
        data = re.search(regx, r.text)
        imgdata = base64.b64decode(data.group(1))
        with open('Avatar.jpg', 'wb') as f:
            f.write(imgdata)

        continue
    elif data.group(1) == '408':
        continue

print("Login Successful")
