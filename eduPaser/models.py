#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging  
import logging.handlers  

from urlparse import urlparse

### Classes

# @note:设置抓取规则
class ParseRule:
	def __init__(self):
		# @param tag:要抓取的目标标签
		self.tag = ''
		# {	
		# 	'class':True, true或者false表示是否含有此标签
		#	'width':'21%'，标签为具体值则表示仅当标签=值时抓取
		#   'class':['class1','class2'], 标签为列表时表示仅当标签值为列表中的值才成立
		#}
		self.attrDict = {}

class ItemBase:
	def __init__(self,url=None,name=None,eng=None):
		self.url = url or ''
		self.name = name or ''
		# www.[xxx.edu.cn]
		self.eng_name = urlparse(self.url).netloc[4:] or eng
		self.done = False
		self.rule = ParseRule()
	def to_json(self):
		return json.dumps(self.__dict__,indent=4,sort_keys=True)


class Academy(ItemBase):
	def __init__(self,url=None,name=None,eng=None):
		ItemBase.__init__(self,url,name,eng)

class College(ItemBase):
	def __init__(self,url=None,name=None,eng=None):
		ItemBase.__init__(self,url,name,eng)
		self.academies = list()
		self.academiesUrl = ''

class China211:
	def __init__(self,url=None,cols=None):
		self.url = url or ''
		self.colleges = cols or list()

_l_classes = {
	"China211":China211,
	"College":College,
	"Academy":Academy,
	"ParseRule":ParseRule
}

### Serialize
def unserialize_object(d):
	clsname = d.pop('__classname__', None)
	if clsname:
		cls = _l_classes[clsname]
		 # Make instance without calling __init__
		obj = cls()
		for key, value in d.items():
			setattr(obj, key, value)
		return obj
	else:
		return d

def serialize_instance(obj):
	d = { '__classname__' : obj.__class__.__name__ }
	d.update(vars(obj))
	return d

def obj_to_json(obj):
	return json.dumps(obj,indent=4,sort_keys=True,default=serialize_instance,ensure_ascii=False)

def obj_from_file(filename):
	with open(filename,'rb') as fp:
		return json.loads(fp.read(),object_hook=unserialize_object)

def obj_to_file(obj,filepath):
	with open(filepath,'wb') as fp:
		fp.write(obj_to_json(obj))
		fp.close()

