import random
import requests
import mysql.connector
from datetime import datetime
from faker import Faker

# Replace these values with your database credentials
db_config = {
    'user': 'admin',
    'password': 'admin',
    'host': 'localhost',
    'database': 'ktering'
}

# Function to fetch image URLs from Foodish API
def fetch_foodish_urls(num_urls):
    urls = []
    for _ in range(num_urls):
        response = requests.get("https://foodish-api.com/api")
        if response.status_code == 200:
            data = response.json()
            urls.append(data['image'])
        else:
            urls.append('https://example.com/default.jpg')  # Fallback URL
    return urls

# Connect to the database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Function to delete all data from all tables in the correct order
def delete_all_data():
    # Define the order of tables to delete data from, respecting foreign key constraints
    table_order = [
        'food_review_images',
        'food_review',
        'food_images',
        'favorites',
        'quantity_food',
        'address',
        'food',
        'order_items',
        'kterer_review',
        'order',
        'notifications',
        'oauth_access_tokens',
        'oauth_auth_codes',
        'oauth_clients',
        'oauth_personal_access_clients',
        'oauth_refresh_tokens',
        'personal_access_tokens',
        'support',
        'kterer',
        'users'
    ]

    for table_name in table_order:
        cursor.execute(f"DELETE FROM `{table_name}`")
        print(f"Deleted all data from table {table_name}")
    conn.commit()

# Function to generate and insert data
def populate_data():
    fake = Faker()

    # Sample data for users table
    users = [
        (fake.uuid4(), fake.first_name(), fake.last_name(), 'customer', fake.email(), fake.phone_number(), fake.country(), datetime.now(), datetime.now(), None, 1, fake.sha256())
        for _ in range(50)
    ]

    # Insert data into users
    user_query = """
        INSERT INTO users (client_id, first_name, last_name, user_type, email, phone, country, created_at, updated_at, deleted_at, email_notification, affiliate_link)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(user_query, users)

    # Retrieve the auto-incremented IDs of inserted users
    cursor.execute("SELECT id, client_id FROM users")
    user_ids = cursor.fetchall()
    user_id_map = {client_id: user_id for user_id, client_id in user_ids}

    # Fetch URLs from Foodish API
    foodish_urls = fetch_foodish_urls(len(users))

    # Sample data for kterer table
    kterer = [
        (None, user_id_map[user[0]], 1, 0, None, foodish_urls[i], fake.text(), fake.word(), None, None, fake.address(), fake.city(), fake.building_number(), fake.state(), fake.country(), fake.postcode(), datetime.now(), datetime.now(), None, fake.uuid4(), fake.uuid4())
        for i, user in enumerate(users)
    ]

    # Insert data into kterer
    kterer_query = """
        INSERT INTO kterer (id, user_id, is_verified, admin_verified, stripe_account_id, profile_image_url, bio, ethnicity, experienceUnit, experienceValue, street_address, city, apartment, province, country, postal_code, created_at, updated_at, deleted_at, door_dash_business_id, door_dash_store_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(kterer_query, kterer)

    # Retrieve the auto-incremented IDs of inserted kterer
    cursor.execute("SELECT id, user_id FROM kterer")
    kterer_ids = cursor.fetchall()
    kterer_id_map = {user_id: kterer_id for kterer_id, user_id in kterer_ids}

    # Sample data for address table
    address = [
        (fake.uuid4(), user_id_map[user[0]], fake.address(), 'Home', datetime.now(), datetime.now(), None)
        for user in users
    ]

    # Insert data into address
    address_query = """
        INSERT INTO address (id, user_id, address, type, created_at, updated_at, deleted_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(address_query, address)

    # Sample data for food table
    food = [
        (fake.uuid4(),
          kterer_id_map[user_id_map[user[0]]],
            fake.word(), 
            fake.text(), 
            fake.text(),
          random.choice(['doesnt-have-meat', 'hand-slaughtered']), 
          random.choice([0, 1]), 
          random.choice(['None', 'Vegetarian']), 
          random.choice(['None', 'Desserts']), 
          random.choice([0, 1]),  
          random.choice(['Other', 'Chicken', 'Beef', 'Pork', 'None']),
          random.choice([
    "Trending",
    "Indian",
    "Asian",
    "Mexican",
    "Middle Eastern",
    "Vegan",
    "Chicken",
    "Desserts",
    "Drinks"
]), 
          datetime.now(), 
          datetime.now(), 
          None, 
          25)
        for user in users for _ in range(1)  # assuming each user has one kterer and each kterer has one food item for simplicity
    ]

    # Insert data into food
    food_query = """
        INSERT INTO food (id, kterer_id, name, description, ingredients, halal, kosher, vegetarian, desserts, contains_nuts, meat_type, ethnic_type, created_at, updated_at, deleted_at, auto_delivery_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(food_query, food)

    # Sample data for food_images table
    food_images = [
        (fake.uuid4(), food_item[0], foodish_urls[i % len(foodish_urls)], datetime.now(), datetime.now(), None)
        for i, food_item in enumerate(food)
    ]

    # Insert data into food_images
    food_images_query = """
        INSERT INTO food_images (id, food_id, image_url, created_at, updated_at, deleted_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(food_images_query, food_images)

    # Sample data for food_review table
    food_review = [
        (fake.uuid4(), user_id_map[user[0]], food_item[0], fake.random_int(min=1, max=5), fake.text(), datetime.now(), datetime.now(), None)
        for user in users for food_item in food
    ]

    # Insert data into food_review
    food_review_query = """
        INSERT INTO food_review (id, user_id, food_id, rating, review, created_at, updated_at, deleted_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(food_review_query, food_review)

    # Sample data for food_review_images table
    food_review_images = [
        (fake.uuid4(), review[0], foodish_urls[i % len(foodish_urls)], datetime.now(), datetime.now(), None)
        for i, review in enumerate(food_review)
    ]

    # Insert data into food_review_images
    food_review_images_query = """
        INSERT INTO food_review_images (id, food_review_id, image_url, created_at, updated_at, deleted_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(food_review_images_query, food_review_images)

    # Sample data for favorites table
    favorites = [
        (fake.uuid4(), user_id_map[user[0]], kterer_id_map[user_id_map[user[0]]], datetime.now(), datetime.now(), None)
        for user in users
    ]

    # Insert data into favorites
    favorites_query = """
        INSERT INTO favorites (id, user_id, kterer_id, created_at, updated_at, deleted_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(favorites_query, favorites)

    # Sample data for kterer_review table
    kterer_review = [
        (fake.uuid4(), user_id_map[user[0]], kterer_id_map[user_id_map[user[0]]], fake.random_int(min=1, max=5), fake.text(), datetime.now(), datetime.now(), None)
        for user in users
    ]

    # Insert data into kterer_review
    kterer_review_query = """
        INSERT INTO kterer_review (id, user_id, kterer_id, rating, review, created_at, updated_at, deleted_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(kterer_review_query, kterer_review)

    # Sample data for order table
    orders = [
        (None, fake.uuid4(), user_id_map[user[0]], kterer_id_map[user_id_map[user[0]]], datetime.now(), datetime.now(), fake.uuid4(), fake.address(), fake.city(), fake.state(), fake.postcode(), fake.country(), None)
        for user in users
    ]

    # Insert data into order
    order_query = """
        INSERT INTO `order` (id, uuid, user_id, kterer_id, created_at, updated_at, payment_id, address, city, state, postal_code, country, deleted_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(order_query, orders)

    # Retrieve the auto-incremented IDs of inserted orders
    cursor.execute("SELECT id, uuid FROM `order`")
    order_ids = cursor.fetchall()
    order_id_map = {uuid: order_id for order_id, uuid in order_ids}

    # Sample data for order_items table
    order_items = [
        (None, fake.uuid4(), order_id_map[order[1]], fake.word(), fake.random_int(min=1, max=10), fake.pydecimal(left_digits=4, right_digits=2, positive=True), datetime.now(), datetime.now(), None, food_item[0])
        for order in orders for food_item in food
    ]

    # Insert data into order_items
    order_items_query = """
        INSERT INTO order_items (id, uuid, order_id, food_name, quantity, price, created_at, updated_at, deleted_at, food_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(order_items_query, order_items)

    # Sample data for quantity_food table
    # quantity_food = [
    #     (fake.uuid4(), food_item[0], fake.word(), fake.word(), fake.word(), datetime.now(), datetime.now(), None)
    #     for food_item in food
    # ]

    quantity_food = [
        (
            fake.uuid4(), 
            food_item[0], 
            random.choice(["small", "medium", "large"]), 
            fake.pydecimal(left_digits=4, right_digits=2, positive=True), 
            fake.random_int(min=1, max=10), 
            datetime.now(), 
            datetime.now(), 
            None,
            )
        for food_item in food
    ]

    # Insert data into quantity_food
    quantity_food_query = """
        INSERT INTO quantity_food (id, food_id, size, price, quantity, created_at, updated_at, deleted_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(quantity_food_query, quantity_food)

    # Sample data for support table
    support = [
        (None, fake.email(), fake.word(), fake.text(), datetime.now(), datetime.now())
        for _ in range(3)
    ]

    # Insert data into support
    support_query = """
        INSERT INTO support (id, email, subject, message, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(support_query, support)

    # Sample data for notifications table
    notifications = [
        (fake.uuid4(), fake.word(), fake.word(), user_id_map[user[0]], fake.text(), None, datetime.now(), datetime.now(), None)
        for user in users
    ]

    # Insert data into notifications
    notifications_query = """
        INSERT INTO notifications (id, type, notifiable_type, notifiable_id, data, read_at, created_at, updated_at, deleted_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(notifications_query, notifications)

    conn.commit()

# Execute the functions
delete_all_data()
populate_data()

# Close the cursor and connection
cursor.close()
conn.close()
