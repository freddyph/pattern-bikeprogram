from decimal import InvalidOperation
import bikeclass
import json
import time
import requests
from geopy import distance
from datetime import datetime
import time
from itertools import cycle
#print(time.time())

#API-länkar
bike_id = "61a8af7803d845a108c5377b"
user_id = "619f6ee3d0b6c914a2b58514"
link = "http://localhost:1337/"
cykel = requests.get(link+"bikes/"+bike_id).json()
user = requests.get(link+"users/"+user_id).json()
stad = requests.get(link+"cities").json()
priser = requests.get(link+"prices").json()

#Kunduppgifter
global status_batteri
kundens_id = user["user"]["_id"]
balans_konto = user["user"]["balance"]
status_batteri =int(cykel["bike"]["battery_status"])

#Kostnadsuppgifter
pristariff = priser["prices"][0]["price_per_minute"]
tid_per_km = 3
startkostnad = priser["prices"][0]["starting_fee"]
straffavgift = priser["prices"][0]["penalty_fee"]
avdrag_bra_parkering = priser["prices"][0]["discount"]
travel_time = balans_konto / pristariff


#Tidspunkter
starttid = ""
kontroll_tid = ""
sluttid = ""

#Skapa fil
try:
    f = open(bike_id, "x")
except:
    f = open(bike_id, "a")
f.write("User-id: "+user_id+"\n")
#f.close

def print_menu():
    """Meny program"""
    print("\n=========== CYKELNS PROGRAM ===========")
    print("\nVälkommen", user["user"]["firstname"], "vad vill du göra?")
    print("\nDu har ", travel_time(balans_konto, status_batteri, pristariff), "minuter kvar att åka")
    print("\nVad vill du göra?")
    print("1.",bike_status())
    print("2. Ange var du vill åka (lat/long)")
    print("3. Starta resa")
    print("4. Avsluta resa")
    print("5. Avsluta programmet")

def travel_time(balans_konto, status_batteri, pristariff):
    """Program för uträkningar av batteri, kostnad och balans"""
    räckvidd_batteri = int(status_batteri) *1.2
    #räckvidd_batteri = 40.0
    travel_time = balans_konto / pristariff
    if räckvidd_batteri > travel_time:
        return travel_time
    else:
        return räckvidd_batteri

def change_bike_status():
    """Ändra status på cykeln"""
    if cykel["bike"]["bike_status"] == "available":
        print("\nSätter cykeln som upptagen")
        cykel["bike"]["bike_status"] = "unavailable"
        starttid = datetime.now()
        print(starttid)
        #return starttid
        
    elif cykel["bike"]["bike_status"] == "unavailable":
        print("\nSätter cykeln som ledig")
        cykel["bike"]["bike_status"] = "available"
        sluttid = datetime.now()
        print(sluttid)
        #return sluttid

def bike_status():
    #print(cykel["bike"]["bike_status"])
    if cykel["bike"]["bike_status"] == "unavailable":
         return "Stäng av cykeln"
    if cykel["bike"]["bike_status"] == "available":
         return "Starta cykeln"
    else:
        return "Något är fel" 

def travel_kor():
    """Hanterar koordinater och räknar ut sträckor & tidsåtgång"""
    i = 0
    #print(stad)
    while i < stad["count"]:
        if cykel["bike"]["city_id"] == stad["cities"][i]["_id"]:
            nuvarande_stad = stad["cities"][i]["name"]
            f.write("Nuvarande stad: "+ nuvarande_stad+"\n")
            nuvarande_kord = stad["cities"][i]["coordinates"]
            nw_lat = stad["cities"][i]["coordinates"]["northwest"]["lat"]
            nw_long = stad["cities"][i]["coordinates"]["northwest"]["long"]
            se_lat = stad["cities"][i]["coordinates"]["southeast"]["lat"]
            se_long = stad["cities"][i]["coordinates"]["southeast"]["long"]
            #print(stad["cities"][i]["coordinates"]["southeast"])fff
        i+=1
    print("\nDina nuvarande koordinater:") 
    print("Lat:",cykel["bike"]["coordinates"]["lat"])
    print("Long:",cykel["bike"]["coordinates"]["long"])
    f.write("Nuvarande koordinater: "+ str(cykel["bike"]["coordinates"]["lat"])+","+str(cykel["bike"]["coordinates"]["long"])+"\n")
    print("Var vill du åka?")
    
    lat = float(input("Lat(ange mellan " +str(nw_lat) + " och "+ str(se_lat)+") "))
    while lat > nw_lat or lat < se_lat:
        print("Fel koordinat")
        lat = float(input("Lat(ange mellan " +str(nw_lat) + " och "+ str(se_lat)+") "))
    print("Lat satt till:", lat)
    
    long = float(input("Long(ange mellan "+ str(se_long) + " och " + str(nw_long)+") "))
    if long > se_long  or long < nw_long:
        print("Fel koordinat")
        long = float(input("Long(ange mellan "+ str(se_long) + " och " + str(nw_long)+") "))
    else:
        print("Long satt till:", long)
    new_location = (lat, long)
    old_location = (cykel["bike"]["coordinates"]["lat"], cykel["bike"]["coordinates"]["long"])
    sträcka = distance.distance(new_location, old_location).km
    print(f"Den inlagda sträcka är {sträcka:.1f} km lång")
    tidsåtgång = sträcka * tid_per_km
    print(f"Beräknas ta ungefär {tidsåtgång:.1f} minuter att åka")


def resa(value = True):
    """För resor"""
    global kontroll_tid
    global status_batteri
    status_batteri += 1.2

    while value:
        kontroll_tid = datetime.now()
        status_batteri -= 1.2
        if status_batteri < 10:
            print(f"Du har bara {status_batteri:.1f} % kvar")
        #avsluta = input("Vill du avsluta resan? ")
        #if avsluta == "J" or "j":
        #    value=False
        #else:
        time.sleep(10)
        if status_batteri < 0.2:
            avsluta_resa_slut()
        
        
    #Skicka batteristatus
    #Skicka hastighet
    #Kontrollera batteristatus
    #Kontrolla balansen
    #Om under 10, skicka varning
    #Om 0, avsluta programmet

def avsluta_resa_slut():
    """Används när batteriet eller saldot är 0"""
    print("Batteriet är slut / Du har slut på pengar")
    print("Din resa avslutas och du debiteras för den tid du använt cykeln.")
    exit()

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
            #starttid = start_tid()
            print(starttid)
        elif option == 2:
            travel_kor()
        elif option == 3:
            resa(True)
        elif option == 4:
            resa(False)
        elif option == 5:
            print('Avslutar cykelns program')
            exit()
        else:
            print('Du måste ange ett nummer!')