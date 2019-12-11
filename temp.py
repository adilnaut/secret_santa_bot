import requests
url = "https://api.jsonbin.io/b/5df0a111bc5ffd0400977abc"
  # url = 'https://api.jsonbin.io/b/<BIN_ID>'
headers = {'Content-Type': 'application/json', 'secret-key': '$2b$10$R248o3.U5BEnIlPpNDFs.uERh/ui3h4oD/xLYz6Cbi2DTr.RrM52y',}
data = {"data": "shit"}

req = requests.put(url, json=data, headers=headers)
print(req.text)
