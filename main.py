# coding:utf-8
import time, requests, re
import base64
from QRCode2Terminal import transfer
import xml.dom.minidom
import json
import random
import Utils


class TChat(object):
    def __init__(self):
        self.session = requests.session()
        self.base_url = ''  # https://wx.qq.com/cgi-bin/mmwebwx-bin
        self.device_id = 'e' + repr(random.random())[2:17]
        self.pass_ticket = ''
        self.appid = 'wx782c26e4c19acffb'
        self.uuid = ''
        self.skey = ''
        self.lang = 'en_US'

        self.myself = []

        self.member_list = []
        self.member_count = 0
        self.friends = []  # 好友
        self.group_chats = []  # 群聊
        self.group_members = []  # 群聊成员
        self.public_members = []  # 公众号
        self.special_member = []  # 特殊账号，比如自己？文件传输列表
        self.SpecialUsers = ['newsapp', 'fmessage', 'filehelper', 'weibo',
                             'qqmail', 'fmessage', 'tmessage', 'qmessage',
                             'qqsync', 'floatbottle', 'lbsapp', 'shakeapp',
                             'medianote', 'qqfriend', 'readerapp', 'blogapp',
                             'facebookapp', 'masssendapp', 'meishiapp',
                             'feedsapp',
                             'voip', 'blogappweixin', 'weixin',
                             'brandsessionholder', 'weixinreminder',
                             'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c',
                             'officialaccounts', 'notification_messages',
                             'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil',
                             'userexperience_alarm', 'notification_messages']

    def generate_login_request(self, s):
        # <error>
        #   <ret>0</ret>
        #   <message></message>
        #   <skey>@crypt_4f1677ff_3236b80cdaaa06710da6b2ad6917349f</skey>
        #   <wxsid>iDI/SxtExtCyVb/t</wxsid>
        #   <wxuin>1149368840</wxuin>
        #   <pass_ticket>5Zhsx6n4aNAoNSOZJdfQTFRDwmy2vLtArB3u8koRPZpyUjophsDmwqT5%2B2V03ffb</pass_ticket>
        #   <isgrayscale>1</isgrayscale>
        # </error>
        baseRequest = {}
        for node in xml.dom.minidom.parseString(s).documentElement.childNodes:
            # 这里encode后是b''（byte类型），需要转string，才能转json
            if node.nodeName == 'skey':
                self.skey = node.childNodes[0].data
                # print(self.skey)
                baseRequest['Skey'] = self.skey.encode('utf-8').decode("utf-8")
            elif node.nodeName == 'wxsid':
                baseRequest['Sid'] = node.childNodes[0].nodeValue.encode(
                    'utf-8').decode("utf-8")
            elif node.nodeName == 'wxuin':
                baseRequest['Uin'] = node.childNodes[0].nodeValue.encode(
                    'utf-8').decode("utf-8")
            elif node.nodeName == 'pass_ticket':
                self.pass_ticket = node.childNodes[0].data
                # print(self.pass_ticket)
        baseRequest['DeviceID'] = self.device_id
        return baseRequest

    def get_contacts(self):
        print("Get contact list...")
        # 获取联系人 get 下面的url
        # https://wx.qq.com/cgi-bin/mmwebwx-bin/
        # webwxgetcontact?
        # lang=en_US&
        # pass_ticket=U1witxoZqHhEt6hZ41WmOBX1l4HuSYDQtEzJznEDiRc9I6PhhbYO%252Bc0F%252Fb5QS5bO&
        # r=1522216295421&
        # seq=0&
        # skey=@crypt_4f1677ff_be8ace8324ec8323e81a743374124649

        url = self.base_url + '/webwxgetcontact'
        params = {
            'lang': self.lang,
            'pass_ticket': self.pass_ticket,
            'r': int(time.time()),
            'seq': 0,
            'skey': self.skey
        }
        # r = requests.session().get(url, params=params)
        # url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?r=%s&seq=0&skey=%s' \
        #                                             % (int(time.time()),
        #                                               self.skey)
        headers = {
            'ContentType': 'application/json; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        }

        # 总算get成功了，之前的代码是requests.session().get()
        # 创建了新的session导致无法获得内容...哎...低级错误
        r = self.session.get(url, params=params)
        dic = json.loads(r.content.decode('utf-8', 'replace'))
        if dic == '':
            print("获取好友失败")
            return

        self.member_count = dic['MemberCount']
        self.member_list = dic['MemberList']

        member_list = self.member_list[:]
        for i in range(len(self.member_list) - 1, -1, -1):
            member = member_list[i]
            if member['VerifyFlag'] & 8 != 0:  # 公众号
                member_list.remove(member)
                self.public_members.append(member)
            elif member['UserName'] in self.SpecialUsers:  # 特殊账号
                member_list.remove(member)
                self.special_member.append(member)
            elif '@@' in member['UserName']:  # 群聊
                member_list.remove(member)
                self.group_chats.append(member)
            elif member['UserName'] == self.myself['UserName']:
                member_list.remove(member)
        self.member_list = member_list
        self.member_count = len(self.member_list)
        print('%s%s' % ("好友数", self.member_count))

    def start(self):
        # this is intend to get uuid
        url = 'https://login.wx.qq.com/jslogin'
        params = {
            'appid': self.appid,
            'redirect_uri': 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage',
            'fun': 'new',
            'lang': self.lang,
            '_': int(time.time())
        }
        print("Fetching UUID...")
        r = self.session.get(url, params=params)
        # print('content:%s' % r.text)

        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";'
        data = re.search(regx, r.text)
        if data and data.group(1) == '200':
            self.uuid = data.group(2)
        # print(uuid)
        print("Fetching QRCode...")
        # get QRCode
        url = 'https://login.weixin.qq.com/qrcode/' + self.uuid
        r = self.session.get(url, stream=True)
        print("Saving QRCode...")

        with open('QRCode.jpg', 'wb') as f:
            f.write(r.content)

        print("Scan the QRCode below to login:")
        transfer('QRCode.jpg')

        while 1:
            url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login'
            params = {
                'loginicon': 'true',
                'uuid': self.uuid,
                'tip': '0',
                '_': int(time.time())
            }
            r = self.session.get(url, params=params)

            regx = r'window.code=(\d+);'
            data = re.search(regx, r.text)
            if not data: continue
            if data.group(1) == '200':
                print("Login Successful")
                regx = r'window.redirect_uri="(\S+?)";'
                redirectUri = re.search(regx, r.text).group(1)
                # print(redirectUri)
                # https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=AVyHuLRlIIvHFBq6lsDYJbZP@qrticket_0&uuid=oebf1lmzzw==&lang=en_US&scan=1522203397
                r = self.session.get(redirectUri, allow_redirects=False)

                baseRequestText = r.text

                self.base_url = redirectUri[:redirectUri.rfind('/')]
                # https://wx.qq.com/cgi-bin/mmwebwx-bin

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

        print("fetching user data...")
        baseRequest = self.generate_login_request(baseRequestText)
        # 抓包知道需要把request post给下面链接
        # https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-1784026806&pass_ticket=6TpKtmY8x6iQ5%252FgcLYDRoO6tXLDgRb36GvQ%252FkMT04INxO4Ai%252B0Za%252FOpYyq2vQnND
        url = '%s/webwxinit?r=%s' % (self.base_url, int(time.time()))
        data = {
            'BaseRequest': baseRequest,
        }
        headers = {'ContentType': 'application/json; charset=UTF-8'}
        r = self.session.post(url, data=json.dumps(data), headers=headers)
        # print(r.text)
        dic = json.loads(r.content.decode('utf-8', 'replace'))
        # print(dic)
        self.myself = dic['User']
        print('%s%s' % (Utils.get_greetings(), self.myself['NickName']))

        self.get_contacts()


if __name__ == '__main__':
    tchat = TChat()
    tchat.start()
