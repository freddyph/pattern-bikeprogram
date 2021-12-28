from decimal import InvalidOperation
from os import stat
import bikeclass
import json
import time
import requests
from geopy import distance
from datetime import datetime
import time
#from itertools import cycle
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
global balans_konto
kundens_id = user["user"]["_id"]
balans_konto = user["user"]["balance"]
status_batteri =float(cykel["bike"]["battery_status"])
#status_batteri = 0.2

#Kostnadsuppgifter
pris_per_minut = priser["prices"][0]["price_per_minute"]
start_avgift = priser["prices"][0]["starting_fee"]
straffavgift = priser["prices"][0]["penalty_fee"]
avdrag_bra_parkering = priser["prices"][0]["discount"]
travel_time = balans_konto / pris_per_minut


#Tidspunkter
starttid = ""
kontroll_tid = ""
sluttid = ""




def uppdatera_balans():
    user = requests.get(link+"users/"+user_id).json()
    balans_konto = user["user"]["balance"]
    return balans_konto

def uppdatera_batteri(bike_id):
    cykel = requests.get(link+"bikes/"+bike_id).json()
    return float(cykel["bike"]["battery_status"])

def print_menu():
    #balans_konto = uppdatera_balans()
    #print(balans_konto)
    """Meny program"""
    print("\n=========== CYKELNS PROGRAM ===========")
    print("\nVälkommen", user["user"]["firstname"], "vad vill du göra?")
    print("\nDu har ", travel_time(pris_per_minut), "minuter kvar att åka")
    print("\nNuvarande batterinivå är: {:.0f} %".format(uppdatera_batteri(bike_id)))
    print("\nVad vill du göra?")
    print("1.",bike_status())
    print("2. Starta resa")
    print("3. Avsluta resa")
    print("4. Avsluta resa & programmet")

def travel_time(pristariff):
    """Program för uträkningar av batteri, kostnad och balans"""
    cykel = requests.get(link+"bikes/"+bike_id).json()
    status_batteri = float(cykel["bike"]["battery_status"])
    
    user = requests.get(link+"users/"+user_id).json()
    balans_konto = user["user"]["balance"]

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

def starta_resan(start_tid, lat, long):
    start_tid_fixad =json.dumps(start_tid, indent=4, sort_keys=True, default=str)
    starta_resa = [
        {"propName": "user_id", "value": str(user_id)},
        {"propName": "bike_id", "value": bike_id},
        {"propName": "start_time", "value": start_tid_fixad},
        {"propName": "lat", "value": lat},
        {"propName": "lat", "value": long}
        ]
    r = requests.post('http://localhost:1337/trips/', json =starta_resa)
    fixed = r.json()
    id_resan = fixed['startedTrip']['_id']
    #print(id_resan)
    return id_resan

def stoppa_resa(id_resan, lat, long, pris, slut_tid_fixad):

    hastighet = 15
    gamla = (lat, long)
    new_lat = lat + 10
    new_long = long + 5
    nya = (new_lat, new_long)
    sträcka = distance.distance(nya, gamla).km
    #pris = 56
    stoppa_resa = [
        {"propName": "average_speed", "value": hastighet},
        {"propName": "distance", "value": sträcka},
        {"propName": "price", "value": pris},
        {"propName": "stop_time", "value": slut_tid_fixad},
        {"propName": "lat", "value": new_lat},
        {"propName": "long", "value": new_long}
        ]
    r2 = requests.patch('http://localhost:1337/trips/end/'+id_resan, json =stoppa_resa)
    print(r2.content)

def resa(balans_konto):
    """För resor"""
    #global kontroll_tid
    #global status_batteri
    #status_batteri += 1.2
    start_tid = datetime.now()
    lat = cykel["bike"]["coordinates"]["lat"]
    long = cykel["bike"]["coordinates"]["long"]
    status_batteri =float(cykel["bike"]["battery_status"])
    uppdaterad_cykel = [
        {"propName": "battery_status", "value": status_batteri},
        {"propName": "lat", "value": lat},
        {"propName": "lat", "value": long}
    ]
    print("Lat:",lat)
    print("Long:",long)
    id_resa = starta_resan(start_tid,lat,long)
    vädersträck = ["norr", "söder", "öster", "väster"]
    riktning = input("I vilken riktning vill du åka? (norr, söder, öster, väster) (Avsluta med q/Q) ")
    
    while True:
        if status_batteri < 0.2 or balans_konto < 0:
            avsluta_resa_slut()
        if riktning in vädersträck:
            print("Du färdas {}".format(riktning))
            print("Lat:",lat)
            print("Long:",long)
            if riktning == "norr":
                lat += 0.001
                status_batteri -= 1.2
                r = requests.patch('http://localhost:1337/bikes/'+bike_id, json =uppdaterad_cykel)
                print(r)
                print(status_batteri)
            elif riktning == "söder":
                lat -= 0.001
                status_batteri -= 1.2
                r = requests.patch('http://localhost:1337/bikes/'+bike_id, json =uppdaterad_cykel)
                print(r)
                print(status_batteri)
            elif riktning == "öster":
                long += 0.001
                status_batteri -= 1.2
                r = requests.patch('http://localhost:1337/bikes/'+bike_id, json =uppdaterad_cykel)
                print(r)
                print(status_batteri)
            elif riktning == "väster":
                long -= 0.001
                status_batteri -= 1.2
                r = requests.patch('http://localhost:1337/bikes/'+bike_id, json =uppdaterad_cykel)
                print(r)
                #print(status_batteri)
            print("Lat:",lat)
            print("Long:",long)
            print(status_batteri)
            riktning = input("I vilken riktning vill du åka? (norr, söder, öster, väster) (Avsluta med q/Q) ")
            
        elif "q" == riktning or "Q" == riktning:
            slut_tid = datetime.now()
            start_tid_fixad =json.dumps(start_tid, indent=4, sort_keys=True, default=str)
            slut_tid_fixad =json.dumps(slut_tid, indent=4, sort_keys=True, default=str)
            duration = slut_tid-start_tid
            längd_i_sekunder = duration.total_seconds()
            längd_i_minuter = round(längd_i_sekunder/60,1)
            summa = calculate_trip(längd_i_minuter)
            stoppa_resa(id_resa,lat,long,summa,slut_tid_fixad)
            print(status_batteri)
            #print_menu()
            break
        else:
            print("Fel riktning, testa igen")
            riktning = input("I vilken riktning vill du åka? (norr, söder, öster, väster) (Avsluta med q/Q) ")


def calculate_trip(minuter, plats="none"):
    """Räkna ut kostnad för användning"""
    #Kostnadsuppgifter
    pris_per_minut = priser["prices"][0]["price_per_minute"]
    start_avgift = priser["prices"][0]["starting_fee"]
    straffavgift = priser["prices"][0]["penalty_fee"]
    avdrag_bra_parkering = priser["prices"][0]["discount"]
    summa = start_avgift
    summa += pris_per_minut * minuter
    if plats == "bra":
        summa -= avdrag_bra_parkering
    else:
        summa += straffavgift
    #print(summa)
    return summa


def avsluta_resa_slut():
    """Används när batteriet eller saldot är 0"""
    print("Batteriet är slut / Du har slut på pengar")
    print("Din resa avslutas och du debiteras för den tid du använt cykeln.")
    exit()

if __name__=='__main__':
    cykel = requests.get(link+"bikes/"+bike_id).json()
    status_batteri =float(cykel["bike"]["battery_status"])
    print(status_batteri)
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
            resa(balans_konto)
        elif option == 3:
            resa(balans_konto)
        elif option == 4:
            print('Avslutar cykelns program')
            exit()
        else:
            print('Du måste ange ett nummer!')