import mysql.connector as mysql
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt

# ------------------ CONFIG ------------------ #
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "port": 3306,
    "password": "Asg@584769",
    "database": "game"
}

# ------------------ AUTO DATABASE & TABLE CREATION + MIGRATION ------------------ #
def setup_database():
    con = None
    cursor = None
    try:
        # create database if missing
        con = mysql.connect(host=DB_CONFIG["host"], user=DB_CONFIG["user"],
                            port=DB_CONFIG["port"], password=DB_CONFIG["password"])
        cursor = con.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS `{}`".format(DB_CONFIG["database"]))
        con.commit()
        cursor.close()
        con.close()

        # connect to DB and ensure base tables exist
        con = mysql.connect(**DB_CONFIG)
        cursor = con.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gamestore (
                product_id VARCHAR(10) PRIMARY KEY,
                product_name VARCHAR(50),
                company VARCHAR(30),
                type VARCHAR(30),
                category VARCHAR(30),
                price INT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS console (
                product_id VARCHAR(10) PRIMARY KEY,
                product_name VARCHAR(50),
                features VARCHAR(100),
                colours VARCHAR(50),
                company VARCHAR(30),
                price INT
            )
        """)
        con.commit()

        # ensure new columns exist (migration)
        ensure_column_exists("gamestore", "monthly_users", "INT", default="0")
        ensure_column_exists("gamestore", "total_revenue", "INT", default="0")
        ensure_column_exists("console", "monthly_users", "INT", default="0")
        ensure_column_exists("console", "total_revenue", "INT", default="0")

        print("✅ Database and tables ready (migrations applied).")
    except mysql.Error as err:
        print("Database Error:", err)
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if con and con.is_connected():
            try:
                con.close()
            except:
                pass

def ensure_column_exists(table_name, column_name, column_type="INT", default=None):
    """
    Add column to table if it doesn't exist.
    column_type should be a valid MySQL column type string (e.g. "INT", "VARCHAR(100)").
    default is a string representing default value (no quoting); pass None for no default.
    """
    con = None
    cursor = None
    try:
        con = mysql.connect(**DB_CONFIG)
        cursor = con.cursor()
        # Check existence in information_schema
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """, (DB_CONFIG["database"], table_name, column_name))
        exists = cursor.fetchone()[0] > 0
        if not exists:
            # Build ALTER TABLE statement
            if default is not None:
                alter_sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {column_type} DEFAULT {default}"
            else:
                alter_sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {column_type}"
            cursor.execute(alter_sql)
            con.commit()
            print(f"Added column `{column_name}` to `{table_name}`")
    except mysql.Error as err:
        print(f"Error ensuring column {column_name} on {table_name}:", err)
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if con and con.is_connected():
            try:
                con.close()
            except:
                pass

# ------------------ DATABASE FUNCTIONS ------------------ #
def execute_query(query, params=None, fetch=False):
    con = None
    cursor = None
    try:
        con = mysql.connect(**DB_CONFIG)
        cursor = con.cursor()
        cursor.execute(query, params or ())
        if fetch:
            data = cursor.fetchall()
            return data
        con.commit()
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if con and con.is_connected():
            try:
                con.close()
            except:
                pass

# ------------------ INSERT WINDOW ------------------ #
def open_insert_window(table):
    if not table:
        messagebox.showwarning("Select Table", "Please select Games or Consoles first.")
        return

    form = Toplevel(root)
    form.title(f"Insert into {table}")
    form.geometry("420x500")
    form.configure(bg="#222")
    form.resizable(False, False)

    if table == "gamestore":
        fields = [
            "product_id", "product_name", "company",
            "type", "category", "price",
            "monthly_users", "total_revenue"
        ]
    else:
        fields = [
            "product_id", "product_name", "features",
            "colours", "company", "price",
            "monthly_users", "total_revenue"
        ]

    Label(form, text=f"Add New Record to {table.upper()}",
          font=("Arial", 14, "bold"), bg="#222", fg="cyan").pack(pady=8)

    form_frame = Frame(form, bg="#222")
    form_frame.pack(pady=6, padx=8)

    entries = {}
    for idx, field in enumerate(fields):
        Label(form_frame, text=f"{field} :", font=("Arial", 10),
              bg="#222", fg="white").grid(row=idx, column=0, sticky="e", pady=6, padx=(2, 8))
        ent = Entry(form_frame, width=28)
        ent.grid(row=idx, column=1, pady=6, padx=(0, 6))
        entries[field] = ent

    def save_data():
        values = []
        for f in fields:
            v = entries[f].get().strip()
            if v == "":
                messagebox.showwarning("Missing value", "All fields are required.")
                return
            values.append(v)

        try:
            # Convert numeric fields safely using their names
            values[fields.index("price")] = int(values[fields.index("price")])
            values[fields.index("monthly_users")] = int(values[fields.index("monthly_users")])
            values[fields.index("total_revenue")] = int(values[fields.index("total_revenue")])
        except ValueError:
            messagebox.showwarning("Invalid", "Price, Monthly Users, and Total Revenue must be numbers.")
            return

        try:
            if table == "gamestore":
                query = """INSERT INTO gamestore 
                           (product_id, product_name, company, type, category, price, monthly_users, total_revenue)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            else:
                query = """INSERT INTO console 
                           (product_id, product_name, features, colours, company, price, monthly_users, total_revenue)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

            execute_query(query, tuple(values))
            messagebox.showinfo("Success", "Record inserted successfully!")
            form.destroy()
            display_records(table)
        except mysql.Error as err:
            messagebox.showerror("DB Error", f"{err}")

    btn_frame = Frame(form, bg="#222")
    btn_frame.pack(pady=12)
    Button(btn_frame, text="💾 Save Record", bg="#4CAF50", fg="white",
           width=16, command=save_data).grid(row=0, column=0, padx=8)
    Button(btn_frame, text="❌ Cancel", bg="#f44336", fg="white",
           width=16, command=form.destroy).grid(row=0, column=1, padx=8)

# ------------------ UPDATE / DELETE / DISPLAY ------------------ #
def open_update_window(table):
    if not table:
        messagebox.showwarning("Select Table", "Please select Games or Consoles first.")
        return

    pid = simpledialog.askstring("Update", "Enter Product ID to update:")
    if not pid:
        return

    try:
        data = execute_query(f"SELECT * FROM {table} WHERE product_id = %s", (pid,), fetch=True)
        if not data:
            messagebox.showinfo("Not Found", "No record found with that Product ID.")
            return
        current = data[0]
    except mysql.Error as err:
        messagebox.showerror("DB Error", f"{err}")
        return

    form = Toplevel(root)
    form.title(f"Update {table} - {pid}")
    form.geometry("420x500")
    form.configure(bg="#222")
    form.resizable(False, False)

    if table == "gamestore":
        fields = [
            "product_id", "product_name", "company",
            "type", "category", "price",
            "monthly_users", "total_revenue"
        ]
    else:
        fields = [
            "product_id", "product_name", "features",
            "colours", "company", "price",
            "monthly_users", "total_revenue"
        ]

    Label(form, text=f"Update Record {pid}", font=("Arial", 14, "bold"), bg="#222", fg="cyan").pack(pady=8)
    form_frame = Frame(form, bg="#222")
    form_frame.pack(pady=6, padx=8)

    entries = {}
    for idx, field in enumerate(fields):
        Label(form_frame, text=f"{field} :", font=("Arial", 10), bg="#222", fg="white").grid(
            row=idx, column=0, sticky="e", pady=6, padx=(2, 8)
        )
        ent = Entry(form_frame, width=28)
        ent.grid(row=idx, column=1, pady=6, padx=(0, 6))
        # protect against schema changes: if current row shorter than expected, use empty
        try:
            ent.insert(0, str(current[idx]))
        except IndexError:
            ent.insert(0, "")
        if field == "product_id":
            ent.config(state="readonly")
        entries[field] = ent

    def save_update():
        values = []
        for f in fields:
            v = entries[f].get().strip()
            if v == "":
                messagebox.showwarning("Missing value", "All fields are required.")
                return
            values.append(v)
        try:
            # convert numeric fields
            values[fields.index("price")] = int(values[fields.index("price")])
            values[fields.index("monthly_users")] = int(values[fields.index("monthly_users")])
            values[fields.index("total_revenue")] = int(values[fields.index("total_revenue")])
        except ValueError:
            messagebox.showwarning("Invalid", "Numeric fields must be numbers.")
            return

        try:
            if table == "gamestore":
                q = """UPDATE gamestore SET product_name=%s, company=%s, type=%s, category=%s,
                       price=%s, monthly_users=%s, total_revenue=%s WHERE product_id=%s"""
                params = (values[1], values[2], values[3], values[4],
                          values[5], values[6], values[7], values[0])
            else:
                q = """UPDATE console SET product_name=%s, features=%s, colours=%s, company=%s,
                       price=%s, monthly_users=%s, total_revenue=%s WHERE product_id=%s"""
                params = (values[1], values[2], values[3], values[4],
                          values[5], values[6], values[7], values[0])
            execute_query(q, params)
            messagebox.showinfo("Success", "Record updated successfully!")
            form.destroy()
            display_records(table)
        except mysql.Error as err:
            messagebox.showerror("DB Error", f"{err}")

    Button(form, text="💾 Save Changes", bg="#2196F3", fg="white",
           width=16, command=save_update).pack(pady=12)

def delete_record(table):
    if not table:
        messagebox.showwarning("Select Table", "Please select Games or Consoles first.")
        return
    pid = simpledialog.askstring("Delete", "Enter Product ID to delete:")
    if not pid:
        return
    if not messagebox.askyesno("Confirm", f"Delete record with Product ID '{pid}'?"):
        return
    try:
        execute_query(f"DELETE FROM {table} WHERE product_id = %s", (pid,))
        messagebox.showinfo("Deleted", "Record deleted successfully.")
        display_records(table)
    except mysql.Error as err:
        messagebox.showerror("DB Error", f"{err}")

def display_records(table):
    for i in tree.get_children():
        tree.delete(i)
    try:
        data = execute_query(f"SELECT * FROM {table}", fetch=True)
    except mysql.Error as err:
        messagebox.showerror("DB Error", f"{err}")
        return

    if table == "gamestore":
        cols = ("product_id", "product_name", "company", "type", "category", "price", "monthly_users", "total_revenue")
    else:
        cols = ("product_id", "product_name", "features", "colours", "company", "price", "monthly_users", "total_revenue")

    tree["columns"] = cols
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=110, anchor="w")

    for row in data:
        # if row has fewer columns due to old schema, pad with empty values
        if len(row) < len(cols):
            row = tuple(list(row) + [0]*(len(cols)-len(row)))
        tree.insert("", "end", values=row)

# ------------------ CHART FUNCTIONS ------------------ #
def show_pie_chart(table):
    try:
        data = execute_query(f"SELECT product_name, monthly_users FROM {table}", fetch=True)
    except mysql.Error as err:
        messagebox.showerror("DB Error", f"{err}")
        return
    if not data:
        messagebox.showinfo("No Data", "No records found to plot.")
        return
    names, users = zip(*data)
    plt.figure(figsize=(6, 6))
    plt.pie(users, labels=names, autopct="%1.1f%%", startangle=140)
    plt.title(f"Monthly Users - {table.upper()}")
    plt.show()

def show_bar_chart(table):
    try:
        data = execute_query(f"SELECT product_name, total_revenue FROM {table}", fetch=True)
    except mysql.Error as err:
        messagebox.showerror("DB Error", f"{err}")
        return
    if not data:
        messagebox.showinfo("No Data", "No records found to plot.")
        return
    names, revenue = zip(*data)
    plt.figure(figsize=(7, 5))
    plt.bar(names, revenue)
    plt.title(f"Total Revenue - {table.upper()}")
    plt.xlabel("Product Name")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# ------------------ UI CONTROL ------------------ #
def show_game_ui():
    current_table.set("gamestore")
    lbl_table.config(text="🎮 Game Store Records")
    display_records("gamestore")

def show_console_ui():
    current_table.set("console")
    lbl_table.config(text="🕹️ Console Records")
    display_records("console")

# ------------------ MAIN ------------------ #
setup_database()

root = Tk()
root.title("🎮 Game Store Management System")
root.geometry("1000x680")
root.configure(bg="#222")

title = Label(root, text="GAME STORE MANAGEMENT SYSTEM",
              font=("Arial Black", 20), bg="#222", fg="cyan")
title.pack(pady=12)

frame = Frame(root, bg="#222")
frame.pack(pady=6)

Button(frame, text="🎮 Games", width=16, bg="#444", fg="white",
       font=("Arial", 12), command=show_game_ui).grid(row=0, column=0, padx=12)
Button(frame, text="🕹️ Consoles", width=16, bg="#444", fg="white",
       font=("Arial", 12), command=show_console_ui).grid(row=0, column=1, padx=12)

lbl_table = Label(root, text="Select a category", font=("Arial", 14), bg="#222", fg="yellow")
lbl_table.pack(pady=8)

tree_frame = Frame(root)
tree_frame.pack(fill=BOTH, expand=True, padx=12, pady=6)
tree = ttk.Treeview(tree_frame, show="headings", height=15)
tree.pack(side=LEFT, fill=BOTH, expand=True)

scroll = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
tree.configure(yscroll=scroll.set)
scroll.pack(side=RIGHT, fill=Y)

action_frame = Frame(root, bg="#222")
action_frame.pack(pady=8)

current_table = StringVar(value="")

Button(action_frame, text="➕ Insert", width=14, bg="#4CAF50", fg="white",
       command=lambda: open_insert_window(current_table.get())).grid(row=0, column=0, padx=8)
Button(action_frame, text="✏️ Update", width=14, bg="#2196F3", fg="white",
       command=lambda: open_update_window(current_table.get())).grid(row=0, column=1, padx=8)
Button(action_frame, text="🗑️ Delete", width=14, bg="#f44336", fg="white",
       command=lambda: delete_record(current_table.get())).grid(row=0, column=2, padx=8)
Button(action_frame, text="🔄 Refresh", width=14, bg="#9C27B0", fg="white",
       command=lambda: display_records(current_table.get())).grid(row=0, column=3, padx=8)
Button(action_frame, text="📊 Pie (Users)", width=14, bg="#FF9800", fg="white",
       command=lambda: show_pie_chart(current_table.get())).grid(row=0, column=4, padx=8)
Button(action_frame, text="📈 Bar (Revenue)", width=14, bg="#00BCD4", fg="white",
       command=lambda: show_bar_chart(current_table.get())).grid(row=0, column=5, padx=8)

show_game_ui()
root.mainloop()
