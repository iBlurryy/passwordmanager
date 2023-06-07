import tkinter as tk
import ttkbootstrap as ttk 
import sqlite3
from tkinter import messagebox

'''
notes --
encryption for database
fix logout menubar for edit entry frame 

extra --
make it downloadable to the public
improve gui
change what you see in listbox so it doesn't show password and email (blur it out maybe)
Ensure people enter valid email 
with the new x.pack_forget() we can change how our program fundamentally works instead of deleted a frame we can just hide it
make a different type of database // goes with make it downloadbale to the public because we need to make sure users can log in on different computers
'''
# Functions

#Brings the user back to the login screen from data entry screen
def logout_function(dataEntry_frame):
    global isLoggedIn
    dataEntry_frame.destroy()
    isLoggedIn = False
    login_screen()

# brings user back to the login screen from sign up screen
def back_function(signUp_Frame):
    global backOption
    signUp_Frame.destroy()
    backOption = False
    login_screen()
    

def finishSignUp(signUp_Frame, signUp_emailEntry, signUp_passwordEntry): # From sign up page when hitting the submit button it goes back to login screen
    global conn
    email = signUp_emailEntry.get()
    password = signUp_passwordEntry.get()


    cursor.execute("SELECT * FROM user WHERE account_email = ?", (email,))
    checkExist = cursor.fetchone()

    if checkExist:
        messagebox.showerror("Sign Up Failed", "This email already exists. Please try again with a different email")
        return

    signUp_data = [(email, password)] # put information from signup fields here 
    
    # uses cursor to insert the signUp_data list into the database
    cursor.executemany('''
                    INSERT INTO user (account_email, account_password) VALUES (?, ?)
                ''' , signUp_data) # puts it into our database
    conn.commit()
    
    signUp_Frame.destroy()
    login_screen()

def finishLogin(loginWindow, accountEmail_entry, accountPassword_entry):
    global conn
    global email
    email = accountEmail_entry.get()
    password = accountPassword_entry.get()


    cursor.execute("SELECT * FROM user WHERE account_email = ? AND account_password = ?", (email,password))
    conn.commit()
    checkExist3 = cursor.fetchmany()

    if checkExist3:
        data_entry(loginWindow, email) # not sure if this will work later due to the fact we need to store the id of whoever logged in to make sure we know which entry is which when displaying the list
    else:
        messagebox.showerror("Login Failed ", "Please try again.")
    

def load_entries(accountEmail, dataList):
    global conn2
    global cursor2

    cursor2.execute("SELECT * FROM entry WHERE account_email = ?", (accountEmail,))
    entries = cursor2.fetchall()

    for entry in entries:
        dataList.insert(ttk.END, f"Website: {entry[3]}, Email: {entry[1]}, Password: {entry[2]}")

def submitData(accountEmail, inputMail, inputPassword, inputWebsite, dataList): # Submit Entry Button for Data Entry Screen
    global conn2
    email = inputMail.get()
    password = inputPassword.get()
    website = inputWebsite.get()

    cursor2.execute("SELECT * FROM entry WHERE account_email = ? AND website_title = ?", (accountEmail, website,))
    conn2.commit()
    checkExist = cursor2.fetchone()

    if checkExist:
        messagebox.showerror("Data Entry Failed", "An entry for this website already exists. Please try again with a different website.")
        return

    entry_data = [(accountEmail, email, password, website)]

    cursor2.executemany('''INSERT INTO entry (account_email, website_email, website_password, website_title) VALUES (?, ?, ?, ?)''', entry_data)

    conn2.commit()

    cursor2.execute("SELECT * FROM entry WHERE account_email = ? AND website_title = ?", (accountEmail, website,))
    checkExist2 = cursor2.fetchone()

    if checkExist2:
        dataList.insert(ttk.END, f"Website: {website}, Email: {email}, Password:{password}")
    else:
        messagebox.showerror("Data Entry Failed", "Unable to add the entry to the database.")
    
    
    

def deleteEntry(accountEmail, dataList):
    global conn2
    global cursor2

    selected_indices = dataList.curselection()

    if not selected_indices:
        messagebox.showerror("No Selection", "Please select an entry to delete.")
        return

    for i in reversed(dataList.curselection()):
        selected_entry = dataList.get(i)
        website_name = selected_entry.split(",")[0].split(": ")[1].strip()
        

        cursor2.execute("DELETE FROM entry WHERE account_email = ? AND website_title = ?", (accountEmail, website_name))
        conn2.commit()
        dataList.delete(i)


def editEntry(dataEntry_frame, accountEmail, dataList):
    global conn2
    global cursor2
    
    # frame
    editEntry_frame = ttk.Frame(window)

    # selects entry
    selected_indices = dataList.curselection()


    # prints out if nothing is selected
    if not selected_indices:
        messagebox.showerror("No Selection", "Please select an entry to delete.")
        return
    
    for i in reversed(dataList.curselection()):
        selected_entry = dataList.get(i)
        website_name = selected_entry.split(",")[0].split(": ")[1].strip()
        email = selected_entry.split(",")[1].split(": ")[1].strip()
        password = selected_entry.split(",")[2].split(": ")[1].strip()

        cursor2.execute("SELECT * FROM entry WHERE account_email = ? AND website_title = ?", (accountEmail, website_name))
        old_entry = cursor2.fetchone()

        if not old_entry:
            messagebox.showerror("No Entry", "No entry found in the database for this selection.")
            return
        
        conn2.commit()
        
        #hides previous frame
        dataEntry_frame.pack_forget()

        # Labels, Entries, Button
        website_label = ttk.Label(master=editEntry_frame, text="Website: ", font=("Arial", 15))
        
        website_entry = ttk.Entry(master=editEntry_frame, font=("Arial", 15))
        website_entry.insert(0, website_name)
        

        email_label = ttk.Label(master=editEntry_frame, text="Email: ", font=("Arial", 15))
        
        email_entry = ttk.Entry(master=editEntry_frame, font=("Arial", 15))
        email_entry.insert(0, email)
        

        password_label = ttk.Label(master=editEntry_frame, text="Password: ", font=("Arial", 15))
       
        password_entry = ttk.Entry(master=editEntry_frame, font=("Arial", 15))
        password_entry.insert(0, password)
        

        save_button = ttk.Button(master=editEntry_frame, text="Save Entry", 
                            command= lambda: finishEdit(old_entry, accountEmail, website_entry, email_entry, password_entry, dataList, editEntry_frame, dataEntry_frame))
        
        editEntry_frame.pack()
        website_label.pack()
        website_entry.pack()
        email_label.pack()
        email_entry.pack()
        password_label.pack()
        password_entry.pack()
        save_button.pack(pady=4)


        

def finishEdit(old_entry, accountEmail, website_entry, email_entry, password_entry, dataList, editEntry_frame, dataEntry_frame):
    #Return to the data_entry page and add edited info to the database 
    global conn2
    global cursor2
    
    new_website = website_entry.get()
    new_email = email_entry.get()
    new_password = password_entry.get()

    # CHECK IF THE NEW WEBSITE NAME ALREADY EXISTS FOR THE USER
    cursor2.execute("SELECT * FROM entry WHERE account_email = ? AND website_title = ?", (accountEmail, new_website))
    checkExist4 = cursor2.fetchone()

    if checkExist4 and checkExist4[3] != old_entry[3]:
        messagebox.showerror("Data Entry Failed", "An entry for this website already exists. Please try again with a different website.")
        return

    #Removes old entry from database
    cursor2.execute("DELETE FROM entry WHERE account_email = ? AND website_title = ?", (accountEmail, old_entry[3]))
    conn2.commit()

    # insert updated entry into DB

    cursor2.execute('''INSERT INTO entry(account_email, website_email, website_password, website_title) VALUES (?, ?, ?, ?)''', 
                    (accountEmail, new_email, new_password, new_website))
    conn2.commit()

    # update the listbox
    for i in reversed(dataList.curselection()):
        dataList.delete(i)

    dataList.insert(ttk.END, f"Website: {new_website}, Email: {new_email}, Password: {new_password},")

    # close the frame and return to data entry screen
    editEntry_frame.destroy()
    # reshows dataEntry
    dataEntry_frame.pack()

def on_closing():
    cursor.close()
    conn.close()
    window.quit()
    window.destroy()




# window
window = ttk.Window(themename='darkly')
window.title("Password Manager")
window.geometry("1280x720")

window.protocol("WM_DELETE_WINDOW", on_closing)

isLoggedIn = False
backOption = False

# menubar options/commands
optionsMenu = ttk.Menu(master=window)
optionsMenu.add_command(label="Exit", command=on_closing)   

# menubar cascades
menubar = ttk.Menu(master=window)
menubar.add_cascade(label="Options", menu=optionsMenu)
window.config(menu=menubar)


# SQL database

conn = sqlite3.connect("login_information.db")

conn2 = sqlite3.connect("entry_information.db")

cursor = conn.cursor() # connection to a cursor

cursor2 = conn2.cursor() 

cursor.execute('''CREATE TABLE IF NOT EXISTS user(account_email, account_password)''')

cursor2.execute('''CREATE TABLE IF NOT EXISTS entry(account_email, website_email, website_password, website_title)''')



# commits connection
conn.commit()
conn2.commit()

#Creates the login Screen and allows the user to access the data entry page with the submit button or 
#access the sign-up page with the sign-up button
def login_screen():    
    global isLoggedIn
    global backOption

    if isLoggedIn == False and 'Logout' in optionsMenu.entrycget(1, 'label'):
        optionsMenu.delete(1)

    if backOption == False and 'Back' in optionsMenu.entrycget(1, 'label'):
        optionsMenu.delete(1)

    loginWindow = ttk.Frame(window)
    
    titleLabel = ttk.Label(master = loginWindow, 
                           text = "Login", 
                           font = ("Coolvetica", 24), 
                           foreground="white", 
                           background="#222222", 
                           padding=10)
    
    accountEmail_label = ttk.Label(master = loginWindow, 
                             text ="Enter Account Email: ", 
                             font = ("Coolvetica", 15), 
                             foreground = "white", 
                             background="#222222")
    
    accountPassword_label = ttk.Label(master = loginWindow, 
                                text ="Enter Account Password: ",
                                font = ("Coolvetica", 15),
                                foreground = "white",
                                background="#222222")
    
    accountEmail_entry = ttk.Entry(master = loginWindow, 
                                   font = ("Coolvetica", 13), 
                                   foreground = "white", 
                                   background="#222222")
    
    accountPassword_entry = ttk.Entry(master = loginWindow, 
                                      font = ("Coolvetica", 13), 
                                      foreground = "white", 
                                      background="#222222")
    
    signIn_button = ttk.Button(master = loginWindow, 
                               text = "Log in", 
                               command = lambda: finishLogin(loginWindow, accountEmail_entry, accountPassword_entry,))
    
    signUp_button = ttk.Button(master = loginWindow,
                               text='Sign Up',
                               command= lambda: sign_up(loginWindow))
    

    titleLabel.pack()
    accountEmail_label.pack()
    accountEmail_entry.pack()
    accountPassword_label.pack()
    accountPassword_entry.pack()
    signIn_button.pack(pady=7)
    signUp_button.pack()

    loginWindow.place(relx=0.5, rely=0.5, anchor='center')

#Destroys the login screen and takes the user to the data entry page. NEED TO RETRIEVE DATA ENTRY FOR PASSWORD MANAGER DATABASE 
def data_entry(loginWindow, accountEmail):
    global isLoggedIn
    loginWindow.destroy()
    isLoggedIn = True

    if 'Logout' not in optionsMenu.entrycget(1, 'label'):
        optionsMenu.add_command(label = "Logout",command=lambda: logout_function(dataEntry_frame))

    dataEntry_frame = ttk.Frame(master = window)

    # Website Label
    enterWebsite = ttk.Label(master =  dataEntry_frame, 
                        font=("Arial", 15),
                        foreground="white",
                        background="#222222",
                        text="Enter Website Title: ",
                        border= 6)
    enterWebsite.pack()

    # input for website
    inputWebsite = ttk.Entry(master =  dataEntry_frame,
                    font=("Arial", 15))
    inputWebsite.pack()

    # Email Label
    emailLabel = ttk.Label(master = dataEntry_frame, 
                        font=("Arial", 15),
                        foreground="white",
                        background="#222222",
                        text="Enter E-Mail: ", 
                        border= 6)

    emailLabel.pack()

    # input for email
    inputMail = ttk.Entry(master =  dataEntry_frame,
                    font=("Arial", 15))
    inputMail.pack()

    # Password Label
    enterPassword = ttk.Label(master =  dataEntry_frame, 
                        font=("Arial", 15),
                        foreground="white",
                        background="#222222",
                        text="Enter Password: ",
                        border= 6)
    enterPassword.pack()

    # input for password
    inputPassword = ttk.Entry(master =  dataEntry_frame,
                    font=("Arial", 15))
    inputPassword.pack()

    # submit button
    submitButton = ttk.Button(master = dataEntry_frame,
                              text = "Submit", width=25,
                              command = lambda:submitData(accountEmail, inputMail, inputPassword, inputWebsite, dataList))
    submitButton.pack(pady= 5)

    # listbox
    dataList = tk.Listbox(master=dataEntry_frame, font=("Arial", 10), width=40, border=20)
    dataList.pack()



    # delete item button 
    deleteItem = ttk.Button(master=dataEntry_frame, text="Delete", 
                            command=lambda:deleteEntry(accountEmail, dataList))
    deleteItem.pack(side="right", padx=3, pady=3)
    
    # edit list button
    editList = ttk.Button(master=dataEntry_frame, text="Edit", 
                          command=lambda:editEntry(dataEntry_frame, accountEmail, dataList))
    editList.pack(side="right", pady=3)

    load_entries(accountEmail, dataList)

    dataEntry_frame.pack()

#Destroys the login screen and takes the user to the sign-up screen 
def sign_up(loginWindow):
    global backOption
    loginWindow.destroy()
    backOption = True

    if 'Back' not in optionsMenu.entrycget(1, 'label'):
        optionsMenu.add_command(label = "Back",command=lambda: back_function(signUp_Frame))

    signUp_Frame = ttk.Frame(window)
    
    signUp_title = ttk.Label(master=signUp_Frame, font = ("Arial", 20), foreground="white", background="#222222", text="SIGN-UP:", border= 8)
    signUp_emailLabel = ttk.Label(master=signUp_Frame, font=("Arial", 15), foreground="white", background="#222222", text="Enter email:", border=6)
    signUp_emailEntry = ttk.Entry(master=signUp_Frame, font=("Arial", 15))
    signUp_passwordLabel = ttk.Label(master=signUp_Frame, font=("Arial", 15), foreground="white", background="#222222", text="Enter password:", border=6)
    signUp_passwordEntry = ttk.Entry(master=signUp_Frame, font=("Arial", 15))
    signUp_button = ttk.Button(master=signUp_Frame, text="Sign Up", command= lambda: finishSignUp(signUp_Frame, signUp_emailEntry, signUp_passwordEntry))
    
    signUp_title.pack()
    signUp_emailLabel.pack()
    signUp_emailEntry.pack()
    signUp_passwordLabel.pack()
    signUp_passwordEntry.pack()
    signUp_button.pack(pady=3)
    
    signUp_Frame.place(relx=0.5, rely=0.5, anchor='center')

login_screen()

# run
window.mainloop()