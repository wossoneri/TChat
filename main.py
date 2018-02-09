# coding: utf-8
'''
加载wx.qq.com
https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=en_US&_=1517476962227
获得QRCode
https://login.weixin.qq.com/qrcode/gZSSoMN-ag==
手机扫码,会发出这个请求,同时获取头像.对比多次扫码,
https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=IbAMLNnpmQ==&tip=0&r=-1417447152&_=1517540888786
https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=YdWkJdywMg==&tip=0&r=-1417728230&_=1517541164415
odY6Upuzmw==
头像
data:img/jpg;base64,/9j/4AAQSk......
手机点确定
https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=AVALV95BS7SD2ohqqqViU76_@qrticket_0&uuid=IbAMLNnpmQ==&lang=en_US&scan=1517540902&fun=new&version=v2
'''

import time, requests, re
import platform, os, subprocess
import base64
from QRCode2Terminal import transfer
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
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
# 关于stream参数,http://docs.python-requests.org/zh_CN/latest/user/advanced.html
# 默认情况下，当你进行网络请求后，响应体会立即被下载。
# 你可以通过 stream 参数覆盖这个行为，推迟下载响应体直到访问 Response.content 属性
# 这个过程其实就是仅有响应头被下载下来了，连接保持打开状态，因此允许我们根据条件获取内容
with open('QRCode.jpg', 'wb') as f:
    f.write(r.content)
#
# if platform.system() == 'Darwin':
#     subprocess.call(['open', 'QRCode.jpg'])
# elif platform.system() == 'Linux':
#     subprocess.call(['xdg-open', 'QRCode.jpg'])
# else:
#     os.startfile('QR.jpg')
print("Scan the QRCode below to login:")
transfer('QRCode.jpg')


# since we get the QRCode, try scan code request
# https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid=IbAMLNnpmQ==&tip=0&r=-1417447152&_=1517540888786





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
        # 'r': 'en_US',
        '_': int(time.time())
    }
    r = session.get(url, params=params)
    # print('content:%s' % r.text)

    regx = r'window.code=(\d+);'
    # regx = r'window.code=(\d+);window.userAvatar = \'data:img/jpg;base64,(\S+?)\';'
    data = re.search(regx, r.text)
    if not data: continue
    if data.group(1) == '200':
        print("Login Successful, fetching user data...")
        regx = r'window.code=200;\nwindow.redirect_uri="(\S+?)";'
        redirectUri = re.search(regx, r.text)
        # print(data.group(1))

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
        # print(data.group(2))
        regx = r'window.code=201;window.userAvatar = \'data:img/jpg;base64,(\S+?)\';'
        data = re.search(regx, r.text)
        imgdata = base64.b64decode(data.group(1))
        with open('Avatar.jpg', 'wb') as f:
            f.write(imgdata)

        continue
    elif data.group(1) == '408':
        # print("QRCode is out of date.")
        # print("Refreshing QRCode...")
        continue

print("Login Successful")

# window.code = 201;
# window.userAvatar = 'data:img/jpg;base64,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';

# window.code=200;
# window.redirect_uri="https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?
# ticket=AZ6hFlXeb1SAg-C_NftGa4gL@qrticket_0&uuid=4cw2LLtMrA==&lang=en_US&scan=1517556902";












# 练手项目https://zhuanlan.zhihu.com/p/30434565
# https://zhuanlan.zhihu.com/p/22675429
# http://python.jobbole.com/84918/
# http://python.jobbole.com/89004/
