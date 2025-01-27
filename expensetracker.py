import tkinter as tk
from tkinter import messagebox
import sqlite3

def init_db():
    connection = sqlite3.connect('expenses.db')
    cursor = connection.cursor()
    sql_command = '''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, date TEXT, category TEXT, description TEXT, amount REAL)'''  
    cursor.execute(sql_command)
    connection.commit()
    connection.close()

def add_expense():
    date = entry_date.get()
    category = entry_category.get()
    description = entry_description.get()
    amount = entry_amount.get()

    if not amount.replace('.', '', 1).isdigit():  
        messagebox.showerror("Error", "Amount must be a valid number")
        return

    amount = float(amount)  

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
                   (date, category, description, amount))
    conn.commit()
    conn.close()
    clear_fields()
    load_expenses()

# Create a dictionary to map listbox items to their expense IDs
expense_mapping = {}

def load_expenses():
    listbox_expenses.delete(0, tk.END)  # Clear existing records
    expense_mapping.clear()  # Clear the mapping dictionary

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    rows = cursor.fetchall()
    
    for row in rows:
        expense_id = row[0]  # Get the ID of the expense
        amount = float(row[4])  # Convert amount to float

        # Format the amount
        if amount.is_integer():
            formatted_amount = f"Rs. {int(amount)}"
        else:
            formatted_amount = f"Rs. {amount:.2f}"

        # Format the row
        formatted_row = f"{row[1]:<15}   {row[2]:<15}   {row[3]:<20}   {formatted_amount}"
        
        # Insert into the listbox and map the index to the expense ID
        listbox_index = listbox_expenses.size()  # Get the current size to calculate the index
        listbox_expenses.insert(tk.END, formatted_row)
        expense_mapping[listbox_index] = expense_id  # Map the index to the expense ID

    conn.close()

def delete_expense():
    try:
        # Get the selected item's index
        selected_index = listbox_expenses.curselection()[0]
        
        # Get the expense ID using the mapping
        expense_id = expense_mapping[selected_index]
        
        # Connect to the database and delete the expense
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        conn.close()
        
        # Reload the expenses list
        load_expenses()
    except IndexError:
        messagebox.showerror("Error", "Please select an expense to delete")

def show_summary():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    summary = cursor.fetchall()
    conn.close()

    if not summary:
        messagebox.showinfo("Summary", "No expenses found.")
        return

    summary_text = "Summary:\n"
    for category, total in summary:
        summary_text += f"{category}: Rs. {total:.2f}\n"  

    messagebox.showinfo("Summary", summary_text)

def clear_fields():
    entry_date.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_description.delete(0, tk.END)
    entry_amount.delete(0, tk.END)

def edit_expense():
    try:
        selected_item = listbox_expenses.curselection()[0]
        expense_data = listbox_expenses.get(selected_item).split()

        expense_id = expense_data[0]
        date = expense_data[1]
        category = expense_data[2]
        description = expense_data[3]
        amount = expense_data[4].replace('Rs.', '').strip() 

        entry_date.delete(0, tk.END)
        entry_date.insert(0, date)
        entry_category.delete(0, tk.END)
        entry_category.insert(0, category)
        entry_description.delete(0, tk.END)
        entry_description.insert(0, description)
        entry_amount.delete(0, tk.END)
        entry_amount.insert(0, amount)

        global editing_id
        editing_id = expense_id

    except IndexError:
        messagebox.showerror("Error", "Please select an expense to edit")

def save_edit():
    try:
        date = entry_date.get()
        category = entry_category.get()
        description = entry_description.get()
        amount = entry_amount.get()

        if not amount.replace('.', '', 1).isdigit():  
            messagebox.showerror("Error", "Amount must be a valid number")
            return

        amount = float(amount)  

        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("""UPDATE expenses
                          SET date = ?, category = ?, description = ?, amount = ? WHERE id = ?""",
                       (date, category, description, amount, editing_id))
        
        conn.commit()
        conn.close()

        clear_fields()
        load_expenses()

    except ValueError:
        messagebox.showerror("Error", "Amount must be a valid number")

editing_id = None

root = tk.Tk()
root.title("Expense Tracker")
root.geometry("500x400")
init_db()

frame_input = tk.Frame(root)
frame_input.pack(pady=10)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

frame_listbox = tk.Frame(root)
frame_listbox.pack(pady=10)

# Input labels and entry fields
label_date = tk.Label(frame_input, text="Date:")
label_date.grid(row=0, column=0, padx=5, pady=5)
entry_date = tk.Entry(frame_input)
entry_date.grid(row=0, column=1, padx=5, pady=5)

label_category = tk.Label(frame_input, text="Category:")
label_category.grid(row=1, column=0, padx=5, pady=5)
entry_category = tk.Entry(frame_input)
entry_category.grid(row=1, column=1, padx=5, pady=5)

label_description = tk.Label(frame_input, text="Description:")
label_description.grid(row=2, column=0, padx=5, pady=5)
entry_description = tk.Entry(frame_input)
entry_description.grid(row=2, column=1, padx=5, pady=5)

label_amount = tk.Label(frame_input, text="Amount:")
label_amount.grid(row=3, column=0, padx=5, pady=5)
entry_amount = tk.Entry(frame_input)
entry_amount.grid(row=3, column=1, padx=5, pady=5)

btn_add = tk.Button(frame_buttons, text="Add Expense", command=add_expense)
btn_add.grid(row=0, column=0, padx=3, pady=5)

btn_edit = tk.Button(frame_buttons, text="Edit Expense", command=edit_expense)
btn_edit.grid(row=0, column=1, padx=3, pady=5)

btn_save = tk.Button(frame_buttons, text="Save Edit", command=save_edit)
btn_save.grid(row=0, column=2, padx=3, pady=5)

btn_delete = tk.Button(frame_buttons, text="Delete Expense", command=delete_expense)
btn_delete.grid(row=0, column=3, padx=3, pady=5)

btn_summary = tk.Button(frame_buttons, text="Show Monthly Summary", command=show_summary)
btn_summary.grid(row=0, column=4, padx=3, pady=5)

listbox_expenses = tk.Listbox(frame_listbox, width=80, height=10)
listbox_expenses.pack()

root.mainloop()


