import requests
import json
import datetime

def get_train_list():
    try:
        response = requests.get("https://www.irctc.co.in/eticketing/trainList").text
        # Removing leading and trailing double quotes
        trimmed_response = response.strip('"')
        # Splitting the string into a list of train details
        train_dict = {}
        for detail in trimmed_response.split('","'):
            train_number, train_name = detail.split(' - ', 1)
            train_dict[train_number] = train_name
        return train_dict
    except Exception as E:
        print("Error fetching train data:", E)
        return {}

def get_current_timestamp():
    return int(datetime.datetime.now().timestamp() * 1000)

def get_train_details(train_number):
    url = f"https://www.irctc.co.in/eticketing/protected/mapps1/trnscheduleenquiry/{train_number}"
    headers = {'greq': str(get_current_timestamp())}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            train_name = data['trainName']
            stations = [f"{station['stationName']}({station['stationCode']})" for station in data['stationList']]
            return train_name, stations
        else:
            return None, None
    except Exception as E:
        print(f"Error fetching train details for {train_number}: {E}")
        return None, None

def get_available_seats(train_number, boarding_station, journey_date):
    url = "https://www.irctc.co.in/online-charts/api/trainComposition"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "trainNo": str(train_number),
        "jDate": str(journey_date),
        "boardingStation": str(boarding_station)
    }
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code} during seat availability check")
            return {}
    except Exception as E:
        print(f"Error fetching available seats: {E}")
        return {}

def total_seats_by_class(seat_data):
    try:
        if 'cdd' not in seat_data:
            print("No 'cdd' key found in the data.")
            return {}
        elif seat_data['cdd'] == None and seat_data['error'] == 'Chart not prepared':
            print("Chart not prepared")
            return {}
        else:
            class_vacancies = {}
            for coach in seat_data['cdd']:
                class_code = coach['classCode']
                vacant_berths = coach['vacantBerths']
                class_vacancies[class_code] = class_vacancies.get(class_code, 0) + vacant_berths

            return class_vacancies
    except Exception as E:
        print("Error processing seat data:", E)
        return {}


def main():
    train_number = input("Enter train number: ")
    train_name, stations = get_train_details(train_number)
    if not train_name:
        print("Train not found!")
        return
   
    print(f"Train Number and Name: {train_number} - {train_name}")
    print("Stations:", ", ".join(stations))
   
    boarding_station = input("Enter boarding station code: ")
    journey_date = input("Enter journey date (YYYY-MM-DD): ")
   
    seats_available = get_available_seats(train_number, boarding_station, journey_date)
    seats_by_class_dict = total_seats_by_class(seats_available)
    if seats_by_class_dict != {}:
        print("Available seats by class:")
        for class_name, seats in seats_by_class_dict.items():
            print(f"{class_name}: {seats}")
           
    else:
        print("No seats available or error in fetching details.")

if __name__ == "__main__":
    main()