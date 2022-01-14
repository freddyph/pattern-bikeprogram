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
from decouple import config

LINK = config('SERVER')
SUM = []
API_KEY = config('JWT_SECRET')
headers = {'x-access-token': API_KEY}
#print(API_KEY)

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
    print("2. Avsluta programmet")

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
        response = requests.post(LINK+'users/register', json =skapa_data, headers=headers)
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
        response = requests.get(LINK+'cities/stations/'+stad, headers=headers).json()
        parkering = kontroll_plats_parkering(lat,long,response)
        laddning = kontroll_plats_laddstation(lat,long,response)
        skapa_data = {
            "city_id": stad,
            "bike_status": "available",
            "battery_status": "100",
            "charge_id": laddning,
            "parking_id": parkering,
            "lat": lat,
            "long": long

        }
        response = requests.post(LINK+'bikes', json=skapa_data, headers=headers)
        SUM.append(response)
        i += 1
    print("\n"+str(antal)+" cyklar har skapats")

def välja_stad():
    """Enkel funktion för att välja stad."""
    print("Du kan välja mellan följande städer:\n")
    print("1. Karlskrona")
    print("2. Stockholm")
    print("3. Karlstad")
    städer = {
        1: "61a76026bb53f131584de9b1",
        2: "61a7603dbb53f131584de9b3",
        3: "61a8fd85ea20b50150945887"
    }

    try:
        val = int(input("Välj stad: "))
        return städer[val]
    except: # pylint: disable=bare-except
        print("Felaktig stad")
        val = int(input("Välj stad: "))
        return städer[val]

def starta_resan(user_id,bike_id,start_latitude,start_longitude):
    """Starta resa"""
    starta_resa = {
        "user_id": user_id,
        "bike_id": bike_id,
        "start_coordinates":{
            "lat":start_latitude,
            "long":start_longitude
        }
    }
    resa = requests.post(LINK+'trips/', json =starta_resa, headers=headers).json()
    id_resan = resa['startedTrip']['_id']
    return id_resan

def avsluta_resa(id_resan,stop_lat,stop_long):
    """Avsluta en resa"""
    print("Din resa avslutas.")
    avsluta_resan ={
        "stop_coordinates": {
            "lat": stop_lat,
            "long": stop_long
        }
    }
    #print(avsluta_resan)
    response = requests.patch(LINK+'trips/end/'+id_resan, json =avsluta_resan, headers=headers)
    SUM.append(response)
#kontroller_stad = LINK+"cities/stations/"+"61a76026bb53f131584de9b1"
#parkeringar = requests.get(kontroller_stad,headers=headers).json()
#print(parkeringar)
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
#print(kontroll_plats_laddstation(56.164191, 15.585593, parkeringar))
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
#skapa_data_cyklar("61a76026bb53f131584de9b1")
def kontroll_tid_batteri_saldo(tid,batteri,kostnad,saldo):
    """Kontroll för att ev avsluta resa"""
    if batteri < 10:
        print("Varning din batterinivå är under 10%")
    if tid <= 0 or batteri < 1.2 or saldo < kostnad:
        return True
    return False

def calculate_trip(priser, minuter, parkering=None, laddning=None):
    """Räkna ut kostnad för användning"""
    #print(priser)
    pris_per_minut = priser["prices"][0]["price_per_minute"]
    start_avgift = priser["prices"][0]["starting_fee"]
    straffavgift = priser["prices"][0]["penalty_fee"]
    avdrag_bra_parkering = priser["prices"][0]["discount"]
    if minuter > 0:
        summa = start_avgift
        summa += pris_per_minut * minuter
        if parkering is not None or laddning is not None:
            summa -= avdrag_bra_parkering
        else:
            summa += straffavgift
    else:
        summa = 0
    #slutsumma = balans - summa
    return summa

def uppdatera_cykel(
    status_batteri,
    lat,
    long,
    bike_id,
    hastighet,
    distans,
    pris,
    charge_id,
    parking_id):
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

    response = requests.patch(LINK+'bikes/'+bike_id, json =uppdatera_cykeln, headers=headers)
    print(response)
    SUM.append(response)

def uppdatera_saldo(user_id,saldo):
    """Uppdatera batteri och position"""
    uppdatera_saldot = [
        {"propName": "balance", "value": saldo}
    ]
    response = requests.patch(LINK+'users/'+user_id, json =uppdatera_saldot, headers=headers)
    SUM.append(response)
#uppdatera_saldo("61df210bacfddbc5a47a3aa6",63)
def hämta_lat(bike_id):
    """Hämta latitud"""
    cykel = requests.get(LINK+"bikes/"+bike_id, headers=headers).json()
    lat = cykel["bike"]["coordinates"]["lat"]
    return lat
def avslutning_cykel(
    status_batteri,
    lat,
    long,
    bike_id,
    hastighet,
    distans,
    pris,
    charge_id,
    parking_id):
    """Uppdatera batteri och position"""
    uppdatera_cykeln = [
        {"propName": "battery_status", "value": status_batteri},
        {"propName": "coordinates", "value": {"lat":lat, "long": long}},
        {"propName": "charge_id", "value": charge_id},
        {"propName": "parking_id", "value": parking_id},
        {"propName": "latest_trip", "value":
        {"average_speed":hastighet,
        "distance": distans,
        "price": pris,
        "charge_id": charge_id,
        "parking_id": parking_id}}
    ]

    response = requests.patch(LINK+'bikes/'+bike_id, json =uppdatera_cykeln, headers=headers)
    print(response)
    SUM.append(response)

def hämta_long(bike_id):
    """Hämta longitud"""
    cykel = requests.get(LINK+"bikes/"+bike_id, headers=headers).json()
    long = cykel["bike"]["coordinates"]["long"]
    return long

def travel_time(pristariff,cykel_id,person_id):
    """Program för uträkningar av batteri, kostnad och balans"""
    cykel = requests.get(LINK+"bikes/"+cykel_id, headers=headers).json()
    status_batteri = float(cykel["bike"]["battery_status"])

    user = requests.get(LINK+"users/"+person_id, headers=headers).json()
    balans_konto = user["user"]["balance"]

    räckvidd_batteri = int(status_batteri) *1.2
    #räckvidd_batteri = 40.0
    rese_tid = balans_konto / pristariff
    return min(räckvidd_batteri,rese_tid)

def slumpa_riktning(person_id,
                    cykel_id,
                    balans_konto,
                    id_resan,
                    response_resa,
                    priser,
                    parkeringar,
                    parkering,
                    laddning,minutpris, mini):
    """Slumpa riktning på cykeln"""
    cykel = requests.get(LINK+'bikes/'+cykel_id, headers=headers).json()
    status_batteri =float(cykel["bike"]["battery_status"])
    stad = cykel["bike"]["city_id"]
    #pris_per_minut = info["priser"][0]["price_per_minute"]
    #print(info)
    #print(pris_per_minut)
    #start_avgift = info["prices"][0]["starting_fee"]
    #straffavgift = info["prices"][0]["penalty_fee"]
    minimum_tid =mini
    pris_per_minut = minutpris
    antal = rand.randint(1,11)
    lat=hämta_lat(cykel_id)
    #print(lat)
    long=hämta_long(cykel_id)
    sträcka = 0
    tid = travel_time(pris_per_minut,cykel_id,person_id)
    pris = 0
    if kontroll_tid_batteri_saldo(tid,status_batteri,pris,balans_konto):
        print("Avslutar resa då du har för lite batteri/pengar på ditt saldo")
        avsluta_resa(id_resan,lat,long)
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
            pris = calculate_trip(priser, 1,balans_konto)
            if kontroll_tid_batteri_saldo(tid,status_batteri,pris,balans_konto):
                print("Avslutar resa då du har för lite batteri/pengar på ditt saldo")
                avsluta_resa(id_resan,lat,long)
                parkering = kontroll_plats_parkering(lat,long,parkeringar)
                laddning = kontroll_plats_laddstation(lat,long,parkeringar)
                avslutning_cykel(
                status_batteri,
                lat,
                long,
                cykel_id,
                hastighet,
                sträcka,
                pris,
                laddning,
                parkering)
                break
            t.sleep(3)
            parkering = kontroll_plats_parkering(lat,long,parkeringar)
            laddning = kontroll_plats_laddstation(lat,long,parkeringar)
            uppdatera_cykel(status_batteri,
            lat,long, cykel_id, hastighet, sträcka, pris,laddning,parkering)
        elif slumpat == 1:
            lat -= 0.001
            lat = round(lat,6)
            lat = kontrollera_lat(lat,stad)
            status_batteri -= 1.2
            sträcka += 57
            minuter =räkna_minuter(response_resa)
            hastighet = räkna_och_sätt_medelhastighet(sträcka,minuter)
            pris = calculate_trip(priser, 1,balans_konto)
            if kontroll_tid_batteri_saldo(tid,status_batteri,pris,balans_konto):
                print("Avslutar resa då du har för lite batteri/pengar på ditt saldo")
                avsluta_resa(id_resan,lat,long)
                parkering = kontroll_plats_parkering(lat,long,parkeringar)
                laddning = kontroll_plats_laddstation(lat,long,parkeringar)
                avslutning_cykel(
                status_batteri,
                lat,
                long,
                cykel_id,
                hastighet,
                sträcka,
                pris,
                laddning,
                parkering)
                break
            t.sleep(3)
            parkering = kontroll_plats_parkering(lat,long,parkeringar)
            laddning = kontroll_plats_laddstation(lat,long,parkeringar)
            uppdatera_cykel(status_batteri,
            lat,long, cykel_id, hastighet, sträcka, pris,laddning,parkering)
        elif slumpat == 2:
            long -= 0.001
            long = round(long,6)
            long = kontrollera_long(long,stad)
            status_batteri -= 1.2
            sträcka += 57
            minuter =räkna_minuter(response_resa)
            hastighet = räkna_och_sätt_medelhastighet(sträcka,minuter)
            pris = calculate_trip(priser, 1,balans_konto)
            if kontroll_tid_batteri_saldo(tid,status_batteri,pris,balans_konto):
                print("Avslutar resa då du har för lite batteri/pengar på ditt saldo")
                avsluta_resa(id_resan,lat,long)
                parkering = kontroll_plats_parkering(lat,long,parkeringar)
                laddning = kontroll_plats_laddstation(lat,long,parkeringar)
                avslutning_cykel(
                status_batteri,
                lat,
                long,
                cykel_id,
                hastighet,
                sträcka,
                pris,
                laddning,
                parkering)
                break
            t.sleep(3)
            parkering = kontroll_plats_parkering(lat,long,parkeringar)
            laddning = kontroll_plats_laddstation(lat,long,parkeringar)
            uppdatera_cykel(status_batteri,
            lat,long, cykel_id, hastighet, sträcka, pris,laddning,parkering)
        elif slumpat == 3:
            long += 0.001
            long = round(long,6)
            long = kontrollera_long(long,stad)
            status_batteri -= 1.2
            sträcka += 57
            minuter =räkna_minuter(response_resa)
            hastighet = räkna_och_sätt_medelhastighet(sträcka,minuter)
            pris = calculate_trip(priser, 1,balans_konto)
            if kontroll_tid_batteri_saldo(tid,status_batteri,pris,balans_konto):
                print("Avslutar resa då du har för lite batteri/pengar på ditt saldo")
                avsluta_resa(id_resan,lat,long)
                parkering = kontroll_plats_parkering(lat,long,parkeringar)
                laddning = kontroll_plats_laddstation(lat,long,parkeringar)
                avslutning_cykel(
                status_batteri,
                lat,
                long,
                cykel_id,
                hastighet,
                sträcka,
                pris,
                laddning,
                parkering)
                break
            t.sleep(3)
            parkering = kontroll_plats_parkering(lat,long,parkeringar)
            laddning = kontroll_plats_laddstation(lat,long,parkeringar)
            uppdatera_cykel(status_batteri,
            lat,long, cykel_id, hastighet, sträcka, pris,laddning,parkering)
        i += 1


#response_resa = requests.get(LINK+'trips/'+"61e1278123fc42346128234d",headers=headers).json()
def räkna_minuter(response_resa):
    """Räknar ut hur många minuter en resa pågått"""
    start_tid = response_resa["trip"]["start_time"]
    start = datetime.strptime(start_tid, '%Y-%m-%dT%H:%M:%S.%fZ')
    try:
        stop_tid = response_resa["trip"]["stop_time"]
        stop = datetime.strptime(stop_tid, '%Y-%m-%dT%H:%M:%S.%fZ')
        duration = stop-start
        längd_i_sekunder = duration.total_seconds()
        längd_i_minuter = round(längd_i_sekunder/60,1)
    except: # pylint: disable=bare-except
        stop_tid = datetime.now()
        duration = stop_tid-start
        längd_i_sekunder = duration.total_seconds()
        längd_i_minuter = round(längd_i_sekunder/60,1)-60
    längd_i_minuter = max(int(längd_i_minuter),1)
    return längd_i_minuter
#print(räkna_minuter(response_resa))

def räkna_och_sätt_medelhastighet(sträcka, minuter):
    """Enligt funktionsnamnet."""
    try:
        distans_i_km = sträcka/1000
        minuter_av_en_timme = minuter/60
        km_per_timme = distans_i_km / minuter_av_en_timme
    except: # pylint: disable=bare-except
        km_per_timme = 0
    return km_per_timme

def välj_en_person():
    """Slumpa en person baserat på antal i databasen"""
    users = requests.get(LINK+"users/", headers=headers).json()
    #print("Användare:",users)
    antal_användare =users["count"]
    antal_användare -= 1
    utvald = rand.randint(0,antal_användare)
    print(users["users"][utvald]["_id"])
    return users["users"][utvald]["_id"]

def välj_en_cykel_i_stad(stads_lista):
    """Slumpa en cykel baserat på stad"""
    #print("Stadslista:",stads_lista)
    antal = len(stads_lista)
    antal -= 1
    utvald = rand.randint(0,antal)
    print(stads_lista[utvald]["_id"])
    return stads_lista[utvald]["_id"]

def skapa_lista_stad(stad):
    """Skapa lista på cyklar för en specifik stad"""
    bikes = requests.get(LINK+"bikes/", headers=headers).json()
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
    värde_lat = lat
    if stad == "61a76026bb53f131584de9b1":
        se_lat = 56.193013
        nw_lat = 56.152144
        if lat >= se_lat:
            värde_lat = se_lat
        if lat <= nw_lat:
            värde_lat = nw_lat

    if stad == "61a7603dbb53f131584de9b3":
        se_lat = 59.343886
        nw_lat = 59.310522
        if lat >= se_lat:
            värde_lat = se_lat
        if lat <= nw_lat:
            värde_lat = nw_lat

    if stad == "61a8fd85ea20b50150945887":
        se_lat = 59.390921
        nw_lat = 59.364795
        if lat >= se_lat:
            värde_lat =se_lat
        if lat <= nw_lat:
            värde_lat =nw_lat
    return värde_lat

def kontrollera_long(long, stad):
    """Kontroll av longitud i stad"""
    värde_long = long
    if stad == "61a76026bb53f131584de9b1":
        se_long = 15.634511
        nw_long = 15.559232
        if long >= se_long:
            värde_long = se_long
        if long <= nw_long:
            värde_long = nw_long

    if stad == "61a7603dbb53f131584de9b3":
        se_long = 18.099825
        nw_long = 18.026826
        if long >= se_long:
            värde_long = se_long
        if long <= nw_long:
            värde_long = nw_long

    if stad == "61a8fd85ea20b50150945887":
        se_long = 13.541185
        nw_long = 13.466531
        if long >= se_long:
            värde_long = se_long
        if long <= nw_long:
            värde_long = nw_long
    return värde_long
