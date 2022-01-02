"""
Samling av funktioner.
"""
import random as rand
from datetime import datetime
import time as t
from geopy import distance
import requests
import names

LINK = "http://localhost:1337/v1/"
SUM = []

#Funktioner simulering

def print_menu_simulering():
    """Meny program"""
    print("\n=========== SIMULERINGSPROGRAM ===========")
    print("\nVälkommen, vad vill du göra?")
    print("1. Skapa personer & cyklar")
    print("2. Simulera")
    print("3. Avsluta programmet")

def skapa_data_personer(stad):
    """Funktion för att skapa x antal personer"""
    #print(stad)
    antal = int(input("\nHur många personer vill du skapa? "))
    i = 0
    while i < antal:
        förnamn = names.get_first_name()
        efternamn = names.get_last_name()
        email = förnamn + "."+ efternamn +"@gmail.com"
        password ="pass"
        phone = "12345"
        payment_method = "monthly"
        card_information = "123445"
        balance = rand.randint(10,300)
        account_status = "active"
        skapa_data = {
            "firstname": förnamn,
            "lastname": efternamn,
            "email": email,
            "password": password,
            "phone": phone,
            "payment_method": payment_method,
            "card_information": card_information,
            "balance": balance,
            "account_status": account_status,
            "city": stad
        }
        response = requests.post(LINK+'users/register', json =skapa_data)
        SUM.append(response)
        i += 1
        
        
    print("\n"+str(antal)+" personer har skapats")

def skapa_data_cyklar(stad):
    """Funktion för att skapa cyklar i specifik stad"""
    antal = int(input("\nHur många cyklar vill du skapa? "))
    i = 0
    while i < antal:
        if stad == "61a76026bb53f131584de9b1":
            lat = round(rand.uniform(56.193013, 56.152144),6)
            long = round(rand.uniform(15.559232, 15.634511),6)

        elif stad == "61a7603dbb53f131584de9b3":
            lat = round(rand.uniform(59.343886, 59.310522),6)
            long = round(rand.uniform(18.026826, 18.099825),6)

        elif stad == "61a8fd85ea20b50150945887":
            lat = round(rand.uniform(59.390921, 59.364795),6)
            long = round(rand.uniform(13.466531, 13.541185),6)

        else:
            print("Felaktigt stadsid")

        skapa_data = {
            "city_id": stad,
            "bike_status": "available",
            "battery_status": "100",
            "lat": lat,
            "long": long

        }
        response = requests.post(LINK+'bikes', json=skapa_data)
        SUM.append(response)
        i += 1
    print("\n"+str(antal)+" cyklar har skapats")

def välja_stad():
    """Enkel funktion för att välja stad."""
    print("Du kan välja mellan följande städer:\n")
    print("1. Karlskrona")
    print("2. Stockholm")
    print("3. Karlstad")
    val = int(input("Välj stad: "))
    if val == 1:
        return "61a76026bb53f131584de9b1"
    if val == 2:
        return "61a7603dbb53f131584de9b3"
    if val == 3:
        return "61a8fd85ea20b50150945887"

def starta_resan(user_id,bike_id,lat,long):
    """Starta resa"""
    starta_resa = {
        "user_id": user_id,
        "bike_id": bike_id,
        "start_coordinates":{
            "lat":lat,
            "long":long
        }

        }

    response = requests.post(LINK+'trips/', json =starta_resa)
    fixed = response.json()
    id_resan = fixed['startedTrip']['_id']
    #print(id_resan)
    return id_resan

def avsluta_resa(id_resan,lat,long,summa):
    """Avsluta en resa"""
    avsluta_resan ={
        "stop_coordinates": {
            "lat": lat,
            "long": long
        },
        "price": summa

        }
    print(avsluta_resan)
    response = requests.patch(LINK+'trips/end/'+id_resan, json =avsluta_resan)
    SUM.append(response)

def kontroll_plats(lat, long, stad):
    """Kontrollera om en plats är laddstation eller parkering"""
    stad = LINK+"cities/stations/"+stad
    parkeringar = requests.get(stad).json()
    i = 0
    while i < len(parkeringar["stations"]["charge_stations"]):
        se_lat = parkeringar["stations"]["charge_stations"][i]["coordinates"]["southeast"]["lat"]
        nw_lat = parkeringar["stations"]["charge_stations"][i]["coordinates"]["northwest"]["lat"]
        is_between_lat = se_lat <= lat <= nw_lat
        nw_long = parkeringar["stations"]["charge_stations"][i]["coordinates"]["northwest"]["long"]
        se_long = parkeringar["stations"]["charge_stations"][i]["coordinates"]["southeast"]["long"]
        is_between_long = nw_long <= long <= se_long
        if is_between_lat and is_between_long:
            return "bra"
        i+=1
    i = 0
    while i < len(parkeringar["stations"]["parking_stations"]):
        se_lat = parkeringar["stations"]["parking_stations"][i]["coordinates"]["southeast"]["lat"]
        nw_lat = parkeringar["stations"]["parking_stations"][i]["coordinates"]["northwest"]["lat"]
        is_between_lat =  se_lat <= lat <= nw_lat
        nw_long = parkeringar["stations"]["parking_stations"][i]["coordinates"]["northwest"]["long"]
        se_long = parkeringar["stations"]["parking_stations"][i]["coordinates"]["southeast"]["long"]
        is_between_long =  nw_long <= long <= se_long
        if is_between_lat and is_between_long:
            return "bra"
        i+=1

def calculate_trip(minuter, plats="none"):
    """Räkna ut kostnad för användning"""
    #Kostnadsuppgifter
    priser = requests.get(LINK+"prices").json()
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
    return summa

def uppdatera_cykel(status_batteri,lat,long,bike_id):
    """Uppdatera batteri och position"""
    uppdatera_cykeln = [
        {"propName": "battery_status", "value": status_batteri},
        {"propName": "coordinates", "value": {"lat":lat, "long": long}}
    ]
    response = requests.patch(LINK+'bikes/'+bike_id, json =uppdatera_cykeln)
    SUM.append(response)

def hämta_lat(bike_id):
    """Hämta latitud"""
    cykel = requests.get(LINK+"bikes/"+bike_id).json()
    lat = cykel["bike"]["coordinates"]["lat"]
    return lat

def hämta_long(bike_id):
    """Hämta longitud"""
    cykel = requests.get(LINK+"bikes/"+bike_id).json()
    long = cykel["bike"]["coordinates"]["long"]
    return long

def slumpa_riktning(lat,long,bike_id):
    """Slumpa riktning på cykeln"""
    cykel = requests.get(LINK+'bikes/'+bike_id).json()
    status_batteri =float(cykel["bike"]["battery_status"])
    antal = rand.randint(1,11)
    i = 0
    while i < antal:
        slumpat = rand.randint(0,3)
        if slumpat == 0:
            lat=hämta_lat(bike_id)
            long=hämta_long(bike_id)
            lat += 0.001
            lat = round(lat,6)
            status_batteri -= 1.2
            t.sleep(1)
            uppdatera_cykel(status_batteri,lat,long, bike_id)
        elif slumpat == 1:
            lat=hämta_lat(bike_id)
            long=hämta_long(bike_id)
            lat -= 0.001
            lat = round(lat,6)
            status_batteri -= 1.2
            t.sleep(1)
            uppdatera_cykel(status_batteri,lat,long, bike_id)
        elif slumpat == 2:
            lat=hämta_lat(bike_id)
            long=hämta_long(bike_id)
            long -= 0.001
            long = round(long,6)
            status_batteri -= 1.2
            t.sleep(1)
            uppdatera_cykel(status_batteri,lat,long, bike_id)
        elif slumpat == 3:
            lat=hämta_lat(bike_id)
            long=hämta_long(bike_id)
            long += 0.001
            long = round(long,6)
            status_batteri -= 1.2
            t.sleep(1)
            uppdatera_cykel(status_batteri,lat,long, bike_id)
        i += 1

def räkna_minuter(id_resan):
    """Räknar ut hur många minuter en resa pågått"""
    response = requests.get(LINK+'trips/'+id_resan).json()
    start_tid = response["trip"]["start_time"]
    start = datetime.strptime(start_tid, '%Y-%m-%dT%H:%M:%S.%fZ')
    try:
        stop_tid = response["trip"]["stop_time"]
        stop = datetime.strptime(stop_tid, '%Y-%m-%dT%H:%M:%S.%fZ')
    except: # pylint: disable=bare-except
        stop_tid = datetime.now()
    duration = stop-start
    längd_i_sekunder = duration.total_seconds()
    längd_i_minuter = round(längd_i_sekunder/60,0)
    längd_i_minuter = int(längd_i_minuter)
    return längd_i_minuter

def räkna_och_sätt_sträcka(id_resan):
    """Räknar ut sträckan"""
    response = requests.get(LINK+'trips/'+id_resan).json()
    print(response["trip"]["start_coordinates"])
    start_lat = response["trip"]["start_coordinates"]["lat"]
    start_long = response["trip"]["start_coordinates"]["long"]
    start_koordinater = (start_lat,start_long)
    print(start_koordinater)
    print(response["trip"]["bike_id"])
    bike_id = response["trip"]["bike_id"]
    bike = requests.get(LINK+'bikes/'+bike_id).json()
    print(bike["bike"]["coordinates"])
    stop_koordinater = (bike["bike"]["coordinates"]["lat"],bike["bike"]["coordinates"]["long"])
    print(stop_koordinater)
    sträcka = distance.distance(stop_koordinater, start_koordinater).km
    print(f"Den inlagda sträckan är {sträcka:.1f} km lång")
    sträcka = int(round(sträcka * 1000,0))
    print(f"Den inlagda sträckan är {sträcka} m lång")
    #print(bike["bike"]["latest_trip"]["distance"])
    gammal_sträcka = bike["bike"]["latest_trip"]["distance"]
    print(gammal_sträcka)

    ackumulerad_sträcka = sträcka + gammal_sträcka
    print(ackumulerad_sträcka)
    uppdatera_sträckan = [
        {"propName": "distance", "value": ackumulerad_sträcka}
    ]
    response = requests.patch('http://localhost:1337/trips/'+id_resan, json =uppdatera_sträckan)
    SUM.append(response)
    #return sträcka

###Uppdatera sträckan, så det blir det den totala sträckan, inte sträckan
###på servern.
def räkna_och_sätt_medelhastighet(id_resan, minuter):
    """Enligt funktionsnamnet."""
    response = requests.get(LINK+'trips/'+id_resan).json()
    print(response["trip"]["distance"])
    distans_i_km = response["trip"]["distance"]/1000
    print(distans_i_km)
    minuter_av_en_timme = minuter/60
    print(minuter_av_en_timme)
    km_per_timme = distans_i_km / minuter_av_en_timme
    print(km_per_timme)

#Slumpa en person av alla
def välj_en_person():
    """Slumpa en person baserat på antal i databasen"""
    users = requests.get(LINK+"users/").json()
    antal_användare =users["count"]
    antal_användare -= 1
    utvald = rand.randint(0,antal_användare)
    return users["users"][utvald]["_id"]

#Slumpa en cykel i en specifik stad
def välj_en_cykel_i_stad(stads_lista):
    """Slumpa en cykel baserat på stad"""
    antal = len(stads_lista)
    antal -= 1
    utvald = rand.randint(0,antal)
    return stads_lista[utvald]["_id"]

def skapa_lista_stad(stad):
    """Skapa lista på cyklar för en specifik stad"""
    bikes = requests.get(LINK+"bikes/").json()
    stads_lista = []
    for bike in bikes["bikes"]:
        try:
            if bike["city_id"] == stad:
                stads_lista.append(bike)
        except: # pylint: disable=bare-except
            pass
    return stads_lista
