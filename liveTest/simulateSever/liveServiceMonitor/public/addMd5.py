# -*- coding: utf-8 -*-

import hashlib
import hmac
import base64
import time
from functools import reduce
import string

sTest = "hello"
secret = "123"
# test_dict={}
# test_dict['live_id']="5e0daf373a158c0a3cab9f4e"
# test_dict['user_type']=2
# test_dict['avatar_url']="https://static.17xueba.com/?x-oss-process=image/resize,m_mfit,h_120,w_120/auto-orient,1/quality,q_80"
# #test_dict['ticket']="Ok3loRbPSEQ53OqGCH"
# test_dict['user_id']=12987938
# test_dict['nickname']="测试长度"
# #test_dict['landing_page']="blank"
# #test_dict['from']="asst-web"
# test_dict['app_id']="58eee6ac19b005fec0d848ce"
# test_dict['timestamp']=1577956351252
# test_dict['room_index']=28907
# app_secret = "4911898908f9d03ae7bf913f2ae16cb1"

#计算字符串的md5码
def get_md5_value(src):
	myMd5 = hashlib.md5()
	myMd5.update(src)
	myMd5_Digest = myMd5.hexdigest()
	return myMd5_Digest

#将字符串转换为16进制
def toHex(str1):
	lst = []
	for ch in str1:
		hv = hex(ord(ch)).replace('0x', '')
		if len(hv) == 1:
			hv = '0' + hv
		lst.append(hv)
	return reduce(lambda x, y: x + y, lst)


#签名算法函数hmac_sha256
def addSign(p_dict, app_secret):
	try:
		para_list = []
		for key in sorted(p_dict.keys()):
			if key != 'sign':
				param = "%s=%s" % (key, p_dict[key])
				para_list.append(param)
		content = '&'.join(para_list)

		message = content.encode('utf-8')
		secret = app_secret.encode('utf-8')
		signature = hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()
		return signature
	except Exception as err:
		print(u"签名异常", err)


