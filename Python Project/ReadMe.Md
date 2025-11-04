🎮 Game Store Management System (Tkinter + MySQL)

A Python desktop application built using Tkinter GUI and MySQL database for managing game and console store data.
This application allows users to insert, update, delete, view, and visualize product information with easy-to-use forms and charts.

🧩 Features

✅ Automatic Database Setup

Creates the game database and required tables (gamestore, console) automatically on startup.

Automatically adds missing columns (monthly_users, total_revenue) if they don’t exist.

✅ GUI Management System

Intuitive Tkinter interface for managing records.

Buttons for insert, update, delete, and refresh operations.

✅ Data Visualization

Pie Chart to show the percentage of monthly users per product.

Bar Chart to display total revenue for each game or console.

✅ Dual Tables Supported

Manage both gamestore and console data in the same interface.

🛠️ Technologies Used
Component	Technology
Frontend (GUI)	Tkinter
Database	MySQL
Data Visualization	Matplotlib
Backend Language	Python 3
📦 Installation Guide
1. Clone or Download

Download the project folder or clone it using:

git clone https://github.com/your-username/game-store-management.git
cd game-store-management

2. Install Dependencies

Make sure Python 3 and MySQL are installed.
Then install required Python modules:

pip install mysql-connector-python matplotlib

3. Set Up MySQL

Open MySQL and ensure your root credentials match the configuration in the script:

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "port": 3306,
    "password": "Asg@584769",
    "database": "game"
}


⚠️ Update the password and user as per your system setup.

4. Run the Application

Execute:

python main.py


The GUI window will launch automatically.

🧮 Database Structure
Table 1: gamestore
Column	Type	Description
product_id	VARCHAR(10)	Primary key
product_name	VARCHAR(50)	Game name
company	VARCHAR(30)	Publisher name
type	VARCHAR(30)	Game type
category	VARCHAR(30)	Category or genre
price	INT	Price of game
monthly_users	INT	Monthly active users
total_revenue	INT	Total revenue generated
Table 2: console
Column	Type	Description
product_id	VARCHAR(10)	Primary key
product_name	VARCHAR(50)	Console name
features	VARCHAR(100)	Key console features
colours	VARCHAR(50)	Available colors
company	VARCHAR(30)	Manufacturer
price	INT	Price
monthly_users	INT	Monthly users
total_revenue	INT	Total revenue
🎨 GUI Controls
Button	Function
🎮 Games	Switch to the Game Store table view
🕹️ Consoles	Switch to the Console table view
➕ Insert	Add a new product entry
✏️ Update	Modify an existing record
🗑️ Delete	Remove a record by Product ID
🔄 Refresh	Reload and display all records
📊 Pie (Users)	Show a pie chart of monthly users
📈 Bar (Revenue)	Show a bar chart of total revenue
📊 Example Visualization

Pie Chart: Distribution of monthly users among games/consoles.

Bar Chart: Comparison of total revenue per product.

💡 Error Handling & Validation

Alerts shown if fields are missing or invalid.

Database errors are caught and displayed.

Ensures numeric fields like price, monthly_users, and total_revenue are valid integers.

🚀 Future Enhancements

Add search functionality by product name or company.

Include data export to CSV or PDF.

Integrate login system for admin access.

Add dark/light theme toggle.

📷 Screenshots (optional)

You can include screenshots like:

Main dashboard

Insert form

Bar and Pie chart views

🧑‍💻 Author

Developed by: Aryan Ghanghas
Language: Python
Database: MySQL
