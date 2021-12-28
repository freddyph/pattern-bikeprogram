import requests
import names

link = "http://localhost:1337/"

def print_menu():
    """Meny program"""
    print("\n=========== SIMULERINGSPROGRAM ===========")
    print("\nVälkommen, vad vill du göra?")
    print("1. Simulera")
    print("2. Avsluta programmet")

def simulera():
    stad = requests.get(link+"cities").json()
    print(stad["cities"][1])
    #print(names.get_first_name())
    pass

def skapa_data_personer(stad):
    antal = int(input("Hur många vill du skapa?"))
    i = 0
    while i < antal: 
        förnamn = names.get_first_name()
        efternamn = names.get_last_name()
        email = förnamn + "."+ efternamn +"@gmail.com"
        password ="pass"
        phone = "12345"
        payment_method = "monthly"
        card_information = "123445"
        balance = 99
        account_status = "active"
        city = stad
        skapa_data = [
            {"propName": "firstname", "value": förnamn},
            {"propName": "lastname", "value": efternamn},
            {"propName": "email", "value": email},
            {"propName": "password", "value": password},
            {"propName": "phone", "value": phone},
            {"propName": "payment_method", "value": payment_method},
            {"propName": "card_information", "value": card_information},
            {"propName": "balance", "value": balance},
            {"propName": "account_status", "value": account_status},
            {"propName": "city", "value": city}
        ]
    #r = requests.post('http://localhost:1337/bikes/'+bike_id, json =uppdaterad_cykel)
        print(skapa_data)
        i += 1


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
            #simulera()
            stad = "61a76026bb53f131584de9b1"
            skapa_data_personer(stad)
        elif option == 2:
            print('Avslutar simuleringsprogrammet')
            exit()
        else:
            print('Du måste ange ett nummer!')