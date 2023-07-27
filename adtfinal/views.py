import sqlite3
from django.shortcuts import render, get_object_or_404, redirect
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Set the Agg backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def index(request):
    return render(request, "home.html")

def about_view(request):
    # Add any logic or data retrieval you need for the about page here
    return render(request, 'about.html')

def car_list(request):
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('SELECT * FROM Car ORDER BY RANDOM() LIMIT 1000')
    car_data = [row for row in cursor]

    # Get the manufacturers and models lists
    manufacturers = sorted(list(set(row[1] for row in car_data)))
    selected_manufacturer = request.GET.get('manufacturer', '')

    if selected_manufacturer:
        models = sorted(list(set(row[2] for row in car_data if row[1] == selected_manufacturer)))
    else:
        models = []

    # Get the selected filters from GET parameters
    selected_year = request.GET.get('year', '')
    selected_model = request.GET.get('model', '')

    # If manufacturer is selected, filter data
    filtered_data = car_data
    if selected_manufacturer:
        filtered_data = [row for row in car_data if row[1] == selected_manufacturer]

    # If year is selected, filter data
    if selected_year:
        filtered_data = [row for row in filtered_data if str(row[3]) == selected_year]

    # If model is selected, filter data
    if selected_model:
        filtered_data = [row for row in filtered_data if row[2] == selected_model]

    conn.close()

    context = {
        "car_data": filtered_data,
        "manufacturers": manufacturers,
        "selected_manufacturer": selected_manufacturer,
        "models": models,
        "selected_year": selected_year,
        "selected_model": selected_model,
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
            "accidents_or_damage" : bool(int.from_bytes(car_history_data[1], byteorder='big')),
            "one_owner" : bool(int.from_bytes(car_history_data[2], byteorder='big')),
            "personal_use_only" : bool(int.from_bytes(car_history_data[3], byteorder='big')),
            "seller_name": dealer_data[1],
            "seller_rating": dealer_data[2],
            "driver_rating": dealer_data[3],
            "driver_reviews_num": dealer_data[4],
            "price_drop": price_data[1],
            "price": price_data[2],
        }
    }

    return render(request, "car_detail.html", context)



def generate_graph1():
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('''
        SELECT Car.year, COUNT(Car.year), AVG(Price.price)
        FROM Car
        INNER JOIN Price 
        ON Car.car_id = Price.car_id
        WHERE Car.year >= 2000
        GROUP BY Car.year;
        ''')

    colnames = cursor.description #column names
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])
    df_yr = pd.DataFrame(cursor.fetchall(), columns=colnames_list)

    #Plot the results
    import matplotlib.pyplot as plt
    plt.plot(df_yr['year'], df_yr['AVG(Price.price)'])
    plt.xlabel('Age of Car (Year Built)')
    plt.ylabel('Average Price')
    

    # Save the plot to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    # Encode the image as base64 and convert it to a data URI
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    image_data_uri = f"data:image/png;base64,{image_base64}"

    conn.close()

    return image_data_uri
    
def add_car(request):
    if request.method == 'POST':
        manufacturer = request.POST.get('manufacturer')
        model = request.POST.get('model')
        year = request.POST.get('year')
        mileage = request.POST.get('mileage')
        engine = request.POST.get('engine')
        transmission = request.POST.get('transmission')
        drivetrain = request.POST.get('drivetrain')
        fuel_type = request.POST.get('fuel_type')
        mpg = request.POST.get('mpg')
        exterior_color = request.POST.get('exterior_color')
        interior_color = request.POST.get('interior_color')
        accidents_or_damage = request.POST.get('accidents_or_damage')
        one_owner = request.POST.get('one_owner')
        personal_use_only = request.POST.get('personal_use_only')
        seller_name = request.POST.get('seller_name')
        seller_rating = request.POST.get('seller_rating')
        driver_rating = request.POST.get('driver_rating')
        driver_reviews_num = request.POST.get('driver_reviews_num')
        price_drop = request.POST.get('price_drop')
        price = request.POST.get('price')

        conn = sqlite3.connect('Full_Car_Database.db')
        cursor = conn.execute('INSERT INTO Car (manufacturer, model, year) VALUES (?, ?, ?)', (manufacturer, model, year))
        cursor = conn.execute('INSERT INTO Carattributes (mileage, engine, transmission, drivetrain, fuel_type, mpg, exterior_color, interior_color) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (mileage, engine, transmission, drivetrain, fuel_type, mpg, exterior_color, interior_color))
        cursor = conn.execute('INSERT INTO Carhistory (accidents_or_damage, one_owner, personal_use_only) VALUES (?, ?, ?)', (accidents_or_damage, one_owner, personal_use_only))
        cursor = conn.execute('INSERT INTO Dealer (seller_name, seller_rating, driver_rating, driver_reviews_num) VALUES (?, ?, ?, ?)', (seller_name, seller_rating, driver_rating, driver_reviews_num))
        cursor = conn.execute('INSERT INTO Price (price_drop, price) VALUES (?, ?)', (price_drop, price))
        conn.commit()

        return redirect('car_list')

    return render(request, 'add_car.html')


def car_update(request, car_id):
    if request.method == 'POST':
        manufacturer = request.POST.get('manufacturer')
        model = request.POST.get('model')
        year = request.POST.get('year')
        mileage = request.POST.get('mileage')
        engine = request.POST.get('engine')
        transmission = request.POST.get('transmission')
        drivetrain = request.POST.get('drivetrain')
        fuel_type = request.POST.get('fuel_type')
        mpg = request.POST.get('mpg')
        exterior_color = request.POST.get('exterior_color')
        interior_color = request.POST.get('interior_color')
        accidents_or_damage = request.POST.get('accidents_or_damage')
        one_owner = request.POST.get('one_owner')
        personal_use_only = request.POST.get('personal_use_only')
        seller_name = request.POST.get('seller_name')
        seller_rating = request.POST.get('seller_rating')
        driver_rating = request.POST.get('driver_rating')
        driver_reviews_num = request.POST.get('driver_reviews_num')
        price_drop = request.POST.get('price_drop')
        price = request.POST.get('price')

        conn = sqlite3.connect('Full_Car_Database.db')
        cursor = conn.execute('UPDATE Car SET manufacturer=?, model=?, year=? WHERE car_id=?', (manufacturer, model, year, car_id))
        cursor = conn.execute('UPDATE CarAttributes SET mileage=?, engine=?, transmission=?, drivetrain=?, fuel_type=?, mpg=?, exterior_color=?, interior_color=? WHERE car_id=?', (mileage, engine, transmission, drivetrain, fuel_type, mpg, exterior_color, interior_color, car_id))
        cursor = conn.execute('UPDATE CarHistory SET accidents_or_damage=?, one_owner=?, personal_use_only=? WHERE car_id=?', (accidents_or_damage, one_owner, personal_use_only, car_id))
        cursor = conn.execute('UPDATE Dealer SET seller_name=?, seller_rating=?, driver_rating=?, driver_reviews_num=? WHERE car_id=?', (seller_name, seller_rating, driver_rating, driver_reviews_num, car_id))
        cursor = conn.execute('UPDATE Price SET price_drop=?, price=? WHERE car_id=?', (price_drop, price, car_id))

        conn.commit()
        return redirect('car_list')

    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('SELECT * FROM Car WHERE car_id=?', (car_id,))
    car_data = cursor.fetchone()

    return render(request, 'car_update.html', {'car_data': car_data, 'car_id': car_id})

def generate_graph2():
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('''
        SELECT Car.manufacturer, COUNT(Car.manufacturer), AVG(Price.price)
        FROM Car
        INNER JOIN Price 
        ON Car.car_id = Price.car_id
        WHERE Car.year == 2022
        GROUP BY Car.manufacturer
        ORDER BY AVG(Price.price) DESC
        LIMIT 10;
        ''')

    colnames = cursor.description #column names
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])

    df_man = pd.DataFrame(cursor.fetchall(), columns=colnames_list)

    plt.figure(figsize=(10,5))
    plt.bar(df_man['manufacturer'], df_man['AVG(Price.price)'])
    plt.xlabel('Manufacturer')
    plt.ylabel('Average Price')
    

    # Save the plot to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    # Encode the image as base64 and convert it to a data URI
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    image_data_uri = f"data:image/png;base64,{image_base64}"

    conn.close()

    return image_data_uri

def generate_graph3():
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('''
        SELECT Car.manufacturer, AVG(CarAttributes.mileage)
        FROM Car
        INNER JOIN CarAttributes
        ON Car.car_id = CarAttributes.car_id
        GROUP BY Car.manufacturer;
        ''')

    colnames = cursor.description #column names
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])

    df_man = pd.DataFrame(cursor.fetchall(), columns=colnames_list)

    plt.figure(figsize=(10,5))
    plt.bar(df_man['manufacturer'], df_man['AVG(CarAttributes.mileage)'])
    plt.xlabel('Manufacturer')
    plt.xticks(rotation=90)
    plt.ylabel('Average Mileage')
    

    # Save the plot to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    # Encode the image as base64 and convert it to a data URI
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    image_data_uri = f"data:image/png;base64,{image_base64}"

    conn.close()

    return image_data_uri

def image_page(request):
    graph1 = generate_graph1()
    graph2 = generate_graph2()
    graph3 = generate_graph3()

    context = {"graph1": graph1, "graph2": graph2, "graph3": graph3}
    return render(request, "image_page.html", context)
