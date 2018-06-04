import asyncio
import aiohttp
import async_timeout
from utils import funcs
import json
import urllib

class MSFace():

	def __init__(self,**kwargs):
		self.app_key = kwargs.pop("key")
		self.session = aiohttp.ClientSession()
		self.base_url = "https://westus.api.cognitive.microsoft.com/face/v1.0" #Put API url here (it varies from region to region)
		self.base_headers = {"Ocp-Apim-Subscription-Key":self.app_key,"Content-Type":"application/json"}

	async def http_post(self, url, **kwargs):
		isjson = kwargs.pop("json",False)
		headers = kwargs.pop("headers",{})
		params = kwargs.pop("params",{})
		try:
			with async_timeout.timeout(10):
				async with self.session.post(url,headers=headers,data=params) as resp:
					data = (await resp.read()).decode("utf-8")
					if isjson:
						data = json.loads(data)
					return data
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
			return False

	async def http_get(self, url, **kwargs):
		headers = kwargs.pop("headers",{})
		json = kwargs.pop("json",False)
		try:
			with async_timeout.timeout(10):
				async with self.session.get(url,headers=headers) as resp:
					if json:
						data = json.loads(await resp.text())
					else:
						data = await resp.read()
					return data
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
			return False

	async def detect(self,url,**kwargs):
		landmarks = kwargs.pop("landmarks",True)
		faceid = kwargs.pop("ids",False)
		attributes = kwargs.pop("attributes","")
		params = {"url":url}
		urlparams = {"returnFaceLandmarks":str(landmarks).lower(),"returnFaceId":str(faceid).lower()}
		if attributes:
			params["returnFaceAttributes"] = attributes
		if urlparams:
			urlparams = "?" + urllib.parse.urlencode(urlparams)
		else:
			urlparams = ""
		resp = await self.http_post(self.base_url+"/detect"+urlparams,headers=self.base_headers,params=json.dumps(params),json=True)
		return resp
