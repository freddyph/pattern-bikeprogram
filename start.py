import bikeclass
import json
import time
import requests
#print(time.time())
bike_id = "bikes/61a8af7803d845a108c5377b"
link = "http://localhost:1337/"
cykel = requests.get(link+bike_id).json()
user = requests.get(link+"users/619f6ee3d0b6c914a2b58514").json()
stad = requests.get(link+"cities").json()
kundens_id = user["user"]["_id"]
balans_konto = user["user"]["balance"]
status_batteri =cykel["bike"]["battery_status"]
pristariff = 2
travel_time = balans_konto / pristariff
#bike_status = bike_status()

def print_menu():
    print("\n=========== CYKELNS PROGRAM ===========")
    print("\nVälkommen", user["user"]["firstname"], "vad vill du göra?")
    print("\nDu har ", travel_time, "minuter kvar att åka")
    print("\nVad vill du göra?")
    print("1.",bike_status())
    print("2. Ange var du vill åka (lat/long)")
    print("3. Ange hur lång tid(ungefär) du vill åka")
    print("4. Avsluta programmet")

def change_bike_status():
    if cykel["bike"]["bike_status"] == "free":
        print("\nSätter cykeln som upptagen")
        #print(cykel["bike"]["bike_status"])
        cykel["bike"]["bike_status"] = "in_use"
        #print(cykel["bike"]["bike_status"])
        #r = requests.patch(link+bike_id, cykel)
        #print(r)
        #print(cykel)
    elif cykel["bike"]["bike_status"] == "in_use":
        print("\nSätter cykeln som ledig")
        #print(cykel["bike"]["bike_status"])
        cykel["bike"]["bike_status"] = "free"
        #print(cykel["bike"]["bike_status"])
        #r = requests.patch(link+bike_id, cykel)
        #print(r)
        #print(cykel)

def bike_status():
    #print(cykel["bike"]["bike_status"])
    if cykel["bike"]["bike_status"] == "in_use":
         return "Stäng av cykeln"
    if cykel["bike"]["bike_status"] == "free":
         return "Starta cykeln"
    else:
        return "Något är fel" 

def travel_kor():
    i = 0
    #print(stad)
    while i < stad["count"]:
        if cykel["bike"]["city_id"] == stad["cities"][i]["_id"]:
            nuvarande_stad = stad["cities"][i]["name"]
            nuvarande_kord = stad["cities"][i]["coordinates"]
            nw_lat = stad["cities"][i]["coordinates"]["northwest"]["lat"]
            nw_long = stad["cities"][i]["coordinates"]["northwest"]["long"]
            se_lat = stad["cities"][i]["coordinates"]["southeast"]["lat"]
            se_long = stad["cities"][i]["coordinates"]["southeast"]["long"]
            #print(stad["cities"][i]["coordinates"]["southeast"])
        i+=1
    print("\nDina nuvarande koordinater:") 
    print("Lat:",cykel["bike"]["coordinates"]["lat"])
    print("Long:",cykel["bike"]["coordinates"]["long"])
    print("Var vill du åka?")
    
    lat = int(input("Lat(ange mellan " +str(nw_lat) + " och "+ str(se_lat)+") "))
    while lat < nw_lat or lat > se_lat:
        print("Fel koordinat")
        lat = int(input("Lat(ange mellan " +str(nw_lat) + " och "+ str(se_lat)+") "))
    print("Lat satt till:", lat)
    
    long = input("Long(ange mellan ",se_long, "och", nw_long)
    if long < se_long  or long > nw_long:
        print("Fel koordinat")
    else:
        print("Long satt till:", long)

def val3():
     print('Handle option \'Option 3\'')

if __name__=='__main__':
    while(True):
        print_menu()
        option = ''
        try:
            option = int(input('Gör ett val: '))
        except:
            print('Du angav inte en giltig siffra ...')
        #Kontrollera val
        if option == 1:
            change_bike_status()
            bike_status()
        elif option == 2:
            travel_kor()
        elif option == 3:
            val3()
        elif option == 4:
            print('Avslutar cykelns program')
            exit()
        else:
            print('Du måste ange ett nummer!')