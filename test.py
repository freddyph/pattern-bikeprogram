import time
import json
import json
starttime = time.time()
#while True:
#    print("tick")
#    time.sleep(10.0 - ((time.time() - starttime) % 10.0))
import requests
#print(time.time())
bike_id = "61a8af7803d845a108c5377b"
stad = "http://localhost:1337/cities/"
response = requests.get(stad)
cyklar = "http://localhost:1337/bikes/"
#print(response.json())
stader = response.json()
response2 = requests.get(cyklar+bike_id)
se_cyklar = response2.json()
nuvarande_stad = ""
nuvarande_kord = ""
nw_lat = ""
nw_long = ""
se_lat = ""
se_long = ""
#print(se_cyklar["bike"]["city_id"])
#print(stader["cities"][0]["name"])
#print(stader["count"])
i = 0
while i < stader["count"]:
    if se_cyklar["bike"]["city_id"] == stader["cities"][i]["_id"]:
        nuvarande_stad = stader["cities"][i]["name"]
        nuvarande_kord = stader["cities"][i]["coordinates"]
        nw_lat = stader["cities"][i]["coordinates"]["northwest"]["lat"]
        nw_long = stader["cities"][i]["coordinates"]["northwest"]["long"]
        se_lat = stader["cities"][i]["coordinates"]["southeast"]["lat"]
        se_long = stader["cities"][i]["coordinates"]["southeast"]["long"]
        print(stader["cities"][i]["coordinates"]["southeast"])
    i+=1
print(nw_lat)


