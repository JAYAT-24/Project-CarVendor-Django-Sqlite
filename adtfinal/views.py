import sqlite3
from django.shortcuts import render, get_object_or_404, redirect
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Set the Agg backend
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from django.db import connection
from django.core.paginator import Paginator



def index(request):
    return render(request, "home.html")

def about_view(request):
    # Add any logic or data retrieval you need for the about page here
    return render(request, 'about.html')

def home(request):
    return render(request, "home.html")

import sqlite3
from django.core.paginator import Paginator
from django.shortcuts import render

def car_list(request):
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('SELECT c.car_id, c.manufacturer, c.model, c.year, p.price FROM Car c JOIN Price p ON c.car_id = p.car_id')
    car_data = [row for row in cursor]
    # Get the manufacturers list
    manufacturers = sorted(list(set(row[1] for row in car_data)))
    selected_manufacturer = request.GET.get('manufacturer', '')

    # If manufacturer is selected, filter data
    filtered_data = car_data
    if selected_manufacturer:
        filtered_data = [row for row in car_data if row[1] == selected_manufacturer]

    # Get the selected sorting options from GET parameters
    sort_by = request.GET.get('sort_by', '')
    sort_order = request.GET.get('sort_order', '')

    # Sorting data
    if sort_by and sort_order:
        if sort_by == 'year':
            filtered_data = sorted(filtered_data, key=lambda x: x[3], reverse=(sort_order == 'desc'))
        elif sort_by == 'manufacturer':
            filtered_data = sorted(filtered_data, key=lambda x: x[1], reverse=(sort_order == 'desc'))
        elif sort_by == 'price':
            filtered_data = sorted(filtered_data, key=lambda x: x[4] if x[4] else 0, reverse=(sort_order == 'desc'))

    conn.close()

    paginator = Paginator(filtered_data, 50)  # Show 50 cars per page

    page_number = request.GET.get('page')
    car_data = paginator.get_page(page_number)

    context = {
        "car_data": car_data,
        "manufacturers": manufacturers,
        "selected_manufacturer": selected_manufacturer,
        "sort_by": sort_by,
        "sort_order": sort_order,
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
            "accidents_or_damage": bool(int.from_bytes(car_history_data[1], byteorder='big')),
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

import sqlite3
from django.shortcuts import render, redirect

# ... (other view functions you might have) ...

from django.db import transaction

@transaction.atomic
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
        accidents_or_damage = request.POST.get('accidents_or_damage') == 'on'
        one_owner = request.POST.get('one_owner') == 'on'
        personal_use_only = request.POST.get('personal_use_only') == 'on'
        seller_name = request.POST.get('seller_name')
        seller_rating = request.POST.get('seller_rating')
        driver_rating = request.POST.get('driver_rating')
        driver_reviews_num = request.POST.get('driver_reviews_num')
        price_drop = request.POST.get('price_drop')
        price = request.POST.get('price')

        # Convert checkboxes to Python boolean values
        accidents_or_damage = accidents_or_damage == 'on'
        print(accidents_or_damage)
        one_owner = one_owner == 'on'
        print(one_owner)
        personal_use_only = personal_use_only == 'on'
        print(personal_use_only)
        conn = sqlite3.connect('Full_Car_Database.db')
        cursor = conn.execute('INSERT INTO Car (manufacturer, model, year) VALUES (?, ?, ?)', (manufacturer, model, year))
        print(conn.execute("select * from Car where manufacturer = 'j';"))
        new_car_id = cursor.lastrowid

        cursor = conn.execute('INSERT INTO CarAttributes (mileage, engine, transmission, drivetrain, fuel_type, mpg, exterior_color, interior_color, car_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (mileage, engine, transmission, drivetrain, fuel_type, mpg, exterior_color, interior_color, new_car_id))

        cursor = conn.execute('INSERT INTO CarHistory (accidents_or_damage, one_owner, personal_use_only, car_id) VALUES (?, ?, ?, ?)', (accidents_or_damage, one_owner, personal_use_only, new_car_id))

        cursor = conn.execute('INSERT INTO Dealer (seller_name, seller_rating, driver_rating, driver_reviews_num, car_id) VALUES (?, ?, ?, ?, ?)', (seller_name, seller_rating, driver_rating, driver_reviews_num, new_car_id))

        cursor = conn.execute('INSERT INTO Price (price_drop, price, car_id) VALUES (?, ?, ?)', (price_drop, price, new_car_id))

        conn.commit()
        conn.close()

        return redirect('car_list')

    return render(request, 'add_car.html')

def car_update(request, car_id):
    conn = sqlite3.connect('Full_Car_Database.db')
    conn.row_factory = sqlite3.Row

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
        "car": car_data,
        "carattributes": car_attributes_data,
        "carhistory": car_history_data,
        "dealer": dealer_data,
        "price": price_data,
    }

    if request.method == 'POST':
        # Get the updated data from the form and update the database
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
        accidents_or_damage = request.POST.get('accidents_or_damage') == "on"
        one_owner = request.POST.get('one_owner') == "on"
        personal_use_only = request.POST.get('personal_use_only') == "on"
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
        conn.close()

        return redirect('car_list')

    return render(request, 'car_form.html', context)

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

    colnames = cursor.description  # column names
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])
    df_yr = pd.DataFrame(cursor.fetchall(), columns=colnames_list)

    # Plot the results
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

def generate_graph4():
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('''
        SELECT Car.year, COUNT(Car.year)
        FROM Car
        INNER JOIN CarAttributes
        ON Car.car_id = CarAttributes.car_id
        WHERE Car.year > 2000 AND CarAttributes.mpg > 30
        GROUP BY Car.year;
        ''')

    colnames = cursor.description #column names
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])

    df_man = pd.DataFrame(cursor.fetchall(), columns=colnames_list)

    df_man['Year_Group'] = df_man['year'].apply(lambda x: str((x // 5) * 5 + 1) + '-' + str((x // 5) * 5 + 5))  # Grouping every five years, e.g., 2001-2005

    # Plotting the boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df_man, x='Year_Group', y='COUNT(Car.year)')
    plt.xlabel('Year Group')
    plt.ylabel('Count of Cars')
    plt.tight_layout()
    

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

def generate_graph5():
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('''
        Select Car.manufacturer, COUNT(Car.manufacturer)
        FROM Car
        GROUP BY Car.manufacturer;
        ''')

    colnames = cursor.description #column names
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])

    df_man = pd.DataFrame(cursor.fetchall(), columns=colnames_list)

    df_man['Percentage'] = df_man['COUNT(Car.manufacturer)'] / df_man['COUNT(Car.manufacturer)'].sum() * 100

    # Group manufacturers with less than 4% into "Others"
    df_man.loc[df_man['Percentage'] < 4, 'manufacturer'] = 'Others'
    df_man = df_man.groupby('manufacturer').sum()

    # Creating a pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(df_man['COUNT(Car.manufacturer)'], labels=df_man.index, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')

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

def generate_graph6():
    conn = sqlite3.connect('Full_Car_Database.db')
    cursor = conn.execute('''
    Select Car.manufacturer, CarAttributes.fuel_type, COUNT(CarAttributes.fuel_type)
    FROM Car
    INNER JOIN CarAttributes
    ON Car.car_id = CarAttributes.car_id
    GROUP BY Car.manufacturer, CarAttributes.fuel_type;
        ''')

    colnames = cursor.description #column names
    colnames_list = []
    for row in colnames:
        colnames_list.append(row[0])

    df_man = pd.DataFrame(cursor.fetchall(), columns=colnames_list)

    # Pivot the data to create a matrix with fuel types as columns, manufacturers as rows, and counts as values
    heatmap_data = df_man.pivot(index='manufacturer', columns='fuel_type', values='COUNT(CarAttributes.fuel_type)').fillna(0)

    # Create the heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap='YlGnBu')

    # Add labels and a title
    plt.xlabel('Fuel Type')
    plt.ylabel('Manufacturer')

    # Rotate the y-axis labels for better visibility
    plt.yticks(rotation=0)

    # Show the plot
    plt.tight_layout()
    
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
    graph4 = generate_graph4()
    graph5 = generate_graph5()
    graph6 = generate_graph6()

    context = {"graph1": graph1, "graph2": graph2, "graph3": graph3, "graph4": graph4, "graph5": graph5, "graph6": graph6}
    return render(request, "image_page.html", context)
