#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from urlparse import urlparse

### Classes
class ItemBase:
	def __init__(self,url=None,name=None,eng=None):
		self.url = url or ''
		self.name = name or ''
		# www.[xxx.edu.cn]
		self.eng_name = urlparse(self.url).netloc[4:] or eng
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


classes = {
	"China211":China211,
	"College":College,
	"Academy":Academy
}

### Serialize
def unserialize_object(d):
	clsname = d.pop('__classname__', None)
	if clsname:
		cls = classes[clsname]
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

def china211_to_json(obj):
	return json.dumps(obj,indent=4,sort_keys=True,default=serialize_instance,ensure_ascii=False)

def china211_from_file(filename):
	with open(filename,'rb') as fp:
		return json.loads(fp.read(),object_hook=unserialize_object)

