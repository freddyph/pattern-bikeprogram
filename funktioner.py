#!/usr/bin/env python3
"""
Samling av funktioner.
"""
import random as rand
from datetime import datetime
import time as t
#from geopy import distance
import requests
import names

LINK = "http://localhost:1337/v1/"
SUM = []

def print_menu_simulering():
    """Meny program"""
    print("\n=========== SIMULERINGSPROGRAM ===========")
    print("\nVälkommen, vad vill du göra?")
    print("1. Skapa personer & cyklar")
    print("2. Simulera")
    print("3. Avsluta programmet")

def print_menu():
    """Meny program"""
    print("\n=========== CYKELNS PROGRAM ===========")
    print("\nVälkommen, vad vill du göra?")
    print("\nVad vill du göra?")
    print("1. Starta resa")
    print("2. Avsluta resa & programmet")

def skapa_data_personer(stad):
    """Funktion för att skapa x antal personer"""
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
    elif val == 2:
        return "61a7603dbb53f131584de9b3"
    elif val == 3:
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
    resa = requests.post(LINK+'trips/', json =starta_resa).json()
    id_resan = resa['startedTrip']['_id']
    return id_resan

def avsluta_resa(id_resan,lat,long):
    """Avsluta en resa"""
    avsluta_resan ={
        "stop_coordinates": {
            "lat": lat,
            "long": long
        }
    }
    print(avsluta_resan)
    response = requests.patch(LINK+'trips/end/'+id_resan, json =avsluta_resan)
    SUM.append(response)

def kontroll_plats_laddstation(lat, long, parkeringar):
    """Kontrollera om en plats är en laddstation"""
    i = 0
    while i < len(parkeringar["stations"]["charge_stations"]):
        se_lat = parkeringar["stations"]["charge_stations"][i]["coordinates"]["southeast"]["lat"]
        nw_lat = parkeringar["stations"]["charge_stations"][i]["coordinates"]["northwest"]["lat"]
        is_between_lat = se_lat <= lat <= nw_lat
        nw_long = parkeringar["stations"]["charge_stations"][i]["coordinates"]["northwest"]["long"]
        se_long = parkeringar["stations"]["charge_stations"][i]["coordinates"]["southeast"]["long"]
        is_between_long = nw_long <= long <= se_long
        if is_between_lat and is_between_long:
            return parkeringar["stations"]["charge_stations"][i]["_id"]
        i+=1

def kontroll_plats_parkering(lat, long, parkeringar):
    """Kontrollera om en plats är en parkering"""
    i = 0
    while i < len(parkeringar["stations"]["parking_stations"]):
        se_lat = parkeringar["stations"]["parking_stations"][i]["coordinates"]["southeast"]["lat"]
        nw_lat = parkeringar["stations"]["parking_stations"][i]["coordinates"]["northwest"]["lat"]
        is_between_lat =  se_lat <= lat <= nw_lat
        nw_long = parkeringar["stations"]["parking_stations"][i]["coordinates"]["northwest"]["long"]
        se_long = parkeringar["stations"]["parking_stations"][i]["coordinates"]["southeast"]["long"]
        is_between_long =  nw_long <= long <= se_long
        if is_between_lat and is_between_long:
            return parkeringar["stations"]["parking_stations"][i]["_id"]
        i+=1

def kontroll_tid_batteri_saldo(tid,batteri,saldo,id_resan,lat,long):
    """Kontroll för att ev avsluta resa"""
    if tid < 0 or batteri < 1.2 or saldo < 0:
        avsluta_resa(id_resan,lat,long)
        print("Avslutar resa")

def calculate_trip(priser, minuter, parkering=None, laddning=None):
    """Räkna ut kostnad för användning"""
    pris_per_minut = priser["prices"][0]["price_per_minute"]
    start_avgift = priser["prices"][0]["starting_fee"]
    straffavgift = priser["prices"][0]["penalty_fee"]
    avdrag_bra_parkering = priser["prices"][0]["discount"]
    summa = start_avgift
    summa += pris_per_minut * minuter
    if parkering is not None or laddning is not None:
        summa -= avdrag_bra_parkering
    else:
        summa += straffavgift
    return summa

def uppdatera_cykel(
    status_batteri,
    lat,
    long,
    bike_id,
    hastighet,
    distans,
    pris,
    charge_id=None,
    parking_id=None):
    """Uppdatera batteri och position"""
    uppdatera_cykeln = [
        {"propName": "battery_status", "value": status_batteri},
        {"propName": "coordinates", "value": {"lat":lat, "long": long}},
        {"propName": "latest_trip", "value":
        {"average_speed":hastighet,
        "distance": distans,
        "price": pris,
        "charge_id": charge_id,
        "parking_id": parking_id}}
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

def travel_time(pristariff,cykel_id,person_id):
    """Program för uträkningar av batteri, kostnad och balans"""
    cykel = requests.get(LINK+"bikes/"+cykel_id).json()
    status_batteri = float(cykel["bike"]["battery_status"])

    user = requests.get(LINK+"users/"+person_id).json()
    balans_konto = user["user"]["balance"]

    räckvidd_batteri = int(status_batteri) *1.2
    #räckvidd_batteri = 40.0
    rese_tid = balans_konto / pristariff
    if räckvidd_batteri > rese_tid:
        return rese_tid
    else:
        return räckvidd_batteri

def slumpa_riktning(
    person_id,
    bike_id,
    balans_konto,
    id_resan,
    response_resa,
    priser,
    parkeringar,
    parkering,
    laddning):
    """Slumpa riktning på cykeln"""
    cykel = requests.get(LINK+'bikes/'+bike_id).json()
    status_batteri =float(cykel["bike"]["battery_status"])
    stad = cykel["bike"]["city_id"]
    pris_per_minut = priser["prices"][0]["price_per_minute"]
    antal = rand.randint(1,11)
    lat=hämta_lat(bike_id)
    long=hämta_long(bike_id)
    sträcka = 0
    tid = travel_time(pris_per_minut,bike_id,person_id)
    kontroll_tid_batteri_saldo(tid,status_batteri,balans_konto,id_resan,lat,long)
    i = 0
    while i < antal:
        slumpat = rand.randint(0,3)
        if slumpat == 0:
            lat += 0.001
            lat = round(lat,6)
            lat = kontrollera_lat(lat,stad)
            status_batteri -= 1.2
            sträcka += 57
            minuter =räkna_minuter(response_resa)
            hastighet = räkna_och_sätt_medelhastighet(sträcka,minuter)
            pris = calculate_trip(priser, 1)
            kontroll_tid_batteri_saldo(tid,status_batteri,balans_konto,id_resan,lat,long)
            t.sleep(1)
            parkering = kontroll_plats_parkering(lat,long,parkeringar)
            laddning = kontroll_plats_laddstation(lat,long,parkeringar)
            uppdatera_cykel(status_batteri,lat,long, bike_id, hastighet, sträcka, pris,laddning,parkering)
        elif slumpat == 1:
            lat -= 0.001
            lat = round(lat,6)
            lat = kontrollera_lat(lat,stad)
            status_batteri -= 1.2
            sträcka += 57
            minuter =räkna_minuter(response_resa)
            hastighet = räkna_och_sätt_medelhastighet(sträcka,minuter)
            pris = calculate_trip(priser, 1)
            kontroll_tid_batteri_saldo(tid,status_batteri,balans_konto,id_resan,lat,long)
            t.sleep(1)
            parkering = kontroll_plats_parkering(lat,long,parkeringar)
            laddning = kontroll_plats_laddstation(lat,long,parkeringar)
            uppdatera_cykel(status_batteri,lat,long, bike_id, hastighet, sträcka, pris,laddning,parkering)
        elif slumpat == 2:
            long -= 0.001
            long = round(long,6)
            long = kontrollera_long(long,stad)
            status_batteri -= 1.2
            sträcka += 57
            minuter =räkna_minuter(response_resa)
            hastighet = räkna_och_sätt_medelhastighet(sträcka,minuter)
            pris = calculate_trip(priser, 1)
            kontroll_tid_batteri_saldo(tid,status_batteri,balans_konto,id_resan,lat,long)
            t.sleep(1)
            parkering = kontroll_plats_parkering(lat,long,parkeringar)
            laddning = kontroll_plats_laddstation(lat,long,parkeringar)
            uppdatera_cykel(status_batteri,lat,long, bike_id, hastighet, sträcka, pris,laddning,parkering)
        elif slumpat == 3:
            long += 0.001
            long = round(long,6)
            long = kontrollera_long(long,stad)
            status_batteri -= 1.2
            sträcka += 57
            minuter =räkna_minuter(response_resa)
            hastighet = räkna_och_sätt_medelhastighet(sträcka,minuter)
            pris = calculate_trip(priser, 1)
            kontroll_tid_batteri_saldo(tid,status_batteri,balans_konto,id_resan,lat,long)
            t.sleep(1)
            parkering = kontroll_plats_parkering(lat,long,parkeringar)
            laddning = kontroll_plats_laddstation(lat,long,parkeringar)
            uppdatera_cykel(status_batteri,lat,long, bike_id, hastighet, sträcka, pris,laddning,parkering)
        i += 1



def räkna_minuter(response_resa):
    """Räknar ut hur många minuter en resa pågått"""
    start_tid = response_resa["trip"]["start_time"]
    start = datetime.strptime(start_tid, '%Y-%m-%dT%H:%M:%S.%fZ')
    try:
        stop_tid = response_resa["trip"]["stop_time"]
        stop = datetime.strptime(stop_tid, '%Y-%m-%dT%H:%M:%S.%fZ')
        duration = stop-start
    except: # pylint: disable=bare-except
        stop_tid = datetime.now()
        duration = stop_tid-start
    längd_i_sekunder = duration.total_seconds()
    längd_i_minuter = round(längd_i_sekunder/60,0)-60
    längd_i_minuter = max(int(längd_i_minuter),1)
    return längd_i_minuter

def räkna_och_sätt_medelhastighet(sträcka, minuter):
    """Enligt funktionsnamnet."""
    distans_i_km = sträcka/1000
    minuter_av_en_timme = minuter/60
    km_per_timme = distans_i_km / minuter_av_en_timme
    return km_per_timme

def välj_en_person():
    """Slumpa en person baserat på antal i databasen"""
    users = requests.get(LINK+"users/").json()
    antal_användare =users["count"]
    antal_användare -= 1
    utvald = rand.randint(0,antal_användare)
    return users["users"][utvald]["_id"]

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

def kontrollera_lat(lat, stad):
    """Kontroll av latitud i stad"""
    if stad == "61a76026bb53f131584de9b1":
        se_lat = 56.193013
        nw_lat = 56.152144
        if lat >= se_lat:
            return se_lat
        elif lat <= nw_lat:
            return nw_lat
        else:
            return lat
    elif stad == "61a7603dbb53f131584de9b3":
        se_lat = 59.343886
        nw_lat = 59.310522
        if lat >= se_lat:
            return se_lat
        elif lat <= nw_lat:
            return nw_lat
        else:
            return lat
    elif stad == "61a8fd85ea20b50150945887":
        se_lat = 59.390921
        nw_lat = 59.364795
        if lat >= se_lat:
            return se_lat
        elif lat <= nw_lat:
            return nw_lat
        else:
            return lat

#print(kontrollera_lat(59.383555,"61a8fd85ea20b5010945887"))
def kontrollera_long(long, stad):
    """Kontroll av longitud i stad"""
    if stad == "61a76026bb53f131584de9b1":
        se_long = 15.634511
        nw_long = 15.559232
        if long >= se_long:
            return se_long
        elif long <= nw_long:
            return nw_long
        else:
            return long
    elif stad == "61a7603dbb53f131584de9b3":
        se_long = 18.099825
        nw_long = 18.026826
        if long >= se_long:
            return se_long
        elif long <= nw_long:
            return nw_long
        else:
            return long
    elif stad == "61a8fd85ea20b50150945887":
        se_long = 13.541185
        nw_long = 13.466531
        if long >= se_long:
            return se_long
        elif long <= nw_long:
            return nw_long
        else:
            return long

kontroll_tid_batteri_saldo(2,-1,2,"id_resan","lat","long")
#Kontroll bike id
#Kontroll user id
#cykel = requests.get(LINK+"bikes/"+"61a8aec803d845a108c53774").json()
#print(cykel['bike'])
#cykel = {}
#cykel_info ={
#    '_id':	cykel['bike']['_id'],
#    'city_id':	cykel['bike']['city_id'],
#    'charge_id':	cykel['bike']['charge_id'],
#    'parking_id':	cykel['bike']['parking_id'],
#    'bike_status': cykel['bike']['bike_status'],
#    'battery_status':	cykel['bike']['battery_status'],
#    'coordinates': {
#        'lat':	cykel['bike']['coordinates']['lat'],
#        'long': cykel['bike']['coordinates']['long']
#    },
#    'maintenance':	cykel['bike']['maintenance'],
#    'latest_trip': {
#        'average_speed': cykel['bike']['latest_trip']['average_speed'],
#        'distance':	cykel['bike']['latest_trip']['distance'],
#        'price':	cykel['bike']['latest_trip']['price'],
#        'charge_id': cykel['bike']['latest_trip']['charge_id'],
#        'parking_id': cykel['bike']['latest_trip']['parking_id']
#    }
#    }
#print(cykel_info)
#battery_status = cykel_info['battery_status']
#print(cykel_info['battery_status'])
#cykel_info['battery_status'] -= 1.2
#print(cykel_info['battery_status'])
#print(cykel_info)
