import sqlite3
from django.shortcuts import render


def index(request):
    return render(request, "home.html")

def car_list(request):
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('''SELECT * FROM (
    SELECT * FROM Car ORDER BY RANDOM() LIMIT 100
) UNION ALL
SELECT * FROM (
    SELECT * FROM Car ORDER BY RANDOM() LIMIT 100
) UNION ALL
SELECT * FROM (
    SELECT * FROM Car ORDER BY RANDOM() LIMIT 100
);''')
    car_data = {}
    for row in cursor:
        manufacturer = row[1]
        if manufacturer in car_data:
            car_data[manufacturer].append(row)
        else:
            car_data[manufacturer] = [row]
    manufacturers = list(car_data.keys())

    selected_manufacturer = request.GET.get('manufacturer', '')  # Get the selected manufacturer from GET parameters

    # If a manufacturer is selected, filter the data
    filtered_data = []
    if selected_manufacturer:
        filtered_data = car_data.get(selected_manufacturer, [])
        # car_data = filtered_data
    conn.close()

    context = {"car_data": filtered_data, "manufacturers": manufacturers, "selected_manufacturer": selected_manufacturer}
    return render(request, "car_list.html", context)

def car_detail(request):
    return render(request, "car_detail.html")

def car_delete(request):
    return render(request, "car_confirm_delete.html")


def default_car_detail(request):
    # Add code to fetch and render the details of a default car here
    return render(request, "car_detail.html")

def home(request):
    return render(request, "home.html")
def car_detail_by_id(request, car_id):  # Renamed the function to car_detail_by_id
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('SELECT * FROM Car WHERE id=?', (car_id,))
    car_data = cursor.fetchone()
    conn.close()

    context = {"object": {
        "manufacturer": car_data[1],
        "model": car_data[2],
        "year": car_data[3],
        "mileage": car_data[4],
        "engine": car_data[5],
        "transmission": car_data[6],
        "drivetrain": car_data[7],
        "fuel_type": car_data[8],
        "mpg": car_data[9],
        "exterior_color": car_data[10],
        "interior_color": car_data[11],
        "accidents_or_damage": car_data[12],
        "one_owner": car_data[13],
        "personal_use_only": car_data[14],
        "seller_name": car_data[15],
        "seller_rating": car_data[16],
        "driver_rating": car_data[17],
        "driver_reviews_num": car_data[18],
        "price_drop": car_data[19],
        "price": car_data[20],
    }}

    return render(request, "car_detail.html", context)