import sqlite3
from django.shortcuts import render, get_object_or_404, redirect

def index(request):
    return render(request, "home.html")


def car_list(request):
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('SELECT * FROM Car ORDER BY RANDOM() LIMIT 100')
    car_data = [row for row in cursor]

    # Get the manufacturers list
    manufacturers = list(set(row[1] for row in car_data))

    selected_manufacturer = request.GET.get('manufacturer', '')  # Get the selected manufacturer from GET parameters

    # If a manufacturer is selected, filter the data
    filtered_data = car_data
    if selected_manufacturer:
        filtered_data = [row for row in car_data if row[1] == selected_manufacturer]

    conn.close()

    context = {
        "car_data": filtered_data,
        "manufacturers": manufacturers,
        "selected_manufacturer": selected_manufacturer,
    }
    return render(request, "car_list.html", context)


def car_confirm_delete(request, car_id):
    conn = sqlite3.connect('Full_Car_Database.db')

    # Fetch data from the Car table
    car_cursor = conn.execute('SELECT * FROM Car WHERE car_id=?', (car_id,))
    car_data = car_cursor.fetchone()

    # Check if the car_id exists in the database
    if not car_data:
        return render(request, "error.html", {"error_message": "Car not found"})

    conn.close()

    if request.method == 'POST':
        # Perform the deletion from the database
        conn = sqlite3.connect('Full_Car_Database.db')
        conn.execute('DELETE FROM Car WHERE car_id=?', (car_id,))
        conn.commit()
        conn.close()

        # Redirect to the car_list view after successful deletion
        return redirect('car_list')

    context = {
        "object": {
            "car_id": car_data[0],
            "manufacturer": car_data[1],
            "model": car_data[2],
            "year": car_data[3],
        }
    }

    return render(request, "car_confirm_delete.html", context)

def home(request):
    return render(request, "home.html")

def car_detail_by_id(request, car_id):
    conn = sqlite3.connect('Full_Car_Database.db')

    # Fetch data from the Car table
    car_cursor = conn.execute('SELECT * FROM Car WHERE car_id=?', (car_id,))
    car_data = car_cursor.fetchone()

    # Check if the car_id exists in the database
    if not car_data:
        return render(request, "error.html", {"error_message": "Car not found"})

    # Fetch data from the CarAttributes table
    car_attributes_cursor = conn.execute('SELECT * FROM CarAttributes WHERE car_id=?', (car_id,))
    car_attributes_data = car_attributes_cursor.fetchone()

    # Fetch data from the CarHistory table
    car_history_cursor = conn.execute('SELECT * FROM CarHistory WHERE car_id=?', (car_id,))
    car_history_data = car_history_cursor.fetchone()

    # Fetch data from the Dealer table
    dealer_cursor = conn.execute('SELECT * FROM Dealer WHERE car_id=?', (car_id,))
    dealer_data = dealer_cursor.fetchone()

    # Fetch data from the Price table
    price_cursor = conn.execute('SELECT * FROM Price WHERE car_id=?', (car_id,))
    price_data = price_cursor.fetchone()

    conn.close()

    # Prepare the context with data from all the tables
    context = {
        "object": {
            "car_id": car_data[0],
            "manufacturer": car_data[1],
            "model": car_data[2],
            "year": car_data[3],
            "mileage": car_attributes_data[1],
            "engine": car_attributes_data[2],
            "transmission": car_attributes_data[3],
            "drivetrain": car_attributes_data[4],
            "fuel_type": car_attributes_data[5],
            "mpg": car_attributes_data[6],
            "exterior_color": car_attributes_data[7],
            "interior_color": car_attributes_data[8],
            "accidents_or_damage": car_history_data[1],
            "one_owner": car_history_data[2],
            "personal_use_only": car_history_data[3],
            "seller_name": dealer_data[1],
            "seller_rating": dealer_data[2],
            "driver_rating": dealer_data[3],
            "driver_reviews_num": dealer_data[4],
            "price_drop": price_data[1],
            "price": price_data[2],
        }
    }

    return render(request, "car_detail.html", context)

