import streamlit as st
from datetime import datetime
from firebase_config import db, create_user_with_email_password, sign_in_with_email_password
import matplotlib.pyplot as plt
import random
import smtplib  # Assuming you use email for OTP
from email.mime.text import MIMEText

# Load custom CSS for better UI
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

import streamlit as st

# Initialize session state variables if not already done
if "user_uid" not in st.session_state:
    st.session_state.user_uid = None
if "otp" not in st.session_state:
    st.session_state.otp = None
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "registration_step" not in st.session_state:
    st.session_state.registration_step = 0  # Initialize at step 0 (before OTP is sent)

# Function to simulate sending an OTP (replace with actual logic)
def send_otp_simulation(user_uid):
    st.session_state.otp = "123456"  # Simulate OTP generation
    st.session_state.otp_sent = True
    st.session_state.registration_step = 1  # Move to the verification step
    st.success(f"OTP sent to user: {user_uid}")

# Real OTP sending functionality with email
def send_real_otp(email):
    otp = random.randint(100000, 999999)
    st.session_state.otp = otp  # Store OTP in session state
    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = 'your_email@gmail.com'  # Replace with your email
    msg['To'] = email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('your_email@gmail.com', 'your_password')  # Replace with your email credentials
            server.send_message(msg)
        return True
    except Exception as e:
        st.error("Error sending OTP. Please try again.")
        return False

# Function to verify the OTP
def verify_otp(input_otp):
    if input_otp == str(st.session_state.otp):
        st.success("OTP Verified Successfully!")
        st.session_state.registration_step = 2  # Complete registration step
    else:
        st.error("Invalid OTP. Please try again.")

# Function to handle user registration
def register_user():
    if st.session_state.registration_step == 0:
        # Step 0: Input user details and send OTP
        st.header("Register User")
        user_email = st.text_input("Enter Email")

        if st.button("Send OTP"):
            if user_email:
                st.session_state.user_email = user_email
                if send_real_otp(user_email):
                    st.success("OTP sent! Please check your email.")
                    st.session_state.registration_step = 1  # Move to OTP verification step
            else:
                st.error("Please enter a valid email.")

    elif st.session_state.registration_step == 1:
        # Step 1: OTP Verification step
        st.header("Verify OTP")
        input_otp = st.text_input("Enter the OTP")

        if st.button("Verify OTP"):
            verify_otp(input_otp)

    elif st.session_state.registration_step == 2:
        # Step 2: Registration Completed
        st.success("Registration completed successfully!")
        if st.button("Register New User"):
            st.session_state.registration_step = 0  # Reset for a new registration

# Call the register_user function to manage registration flow
register_user()


# Login existing users
def login_user(email, password):
    user_uid = sign_in_with_email_password(email, password)
    if user_uid:
        st.session_state.user_uid = user_uid  # Save user ID to session state
        st.success("Login successful!")
        return user_uid
    else:
        st.error("Invalid credentials. Please try again.")
        return None

# Function to store expense data in Firestore
def store_expense(user_uid, name, amount, category, date, description):
    expense_data = {
        "user_uid": user_uid,
        "name": name,
        "amount": amount,
        "category": category,
        "date": date.strftime("%Y-%m-%d"),
        "description": description,
        "month": date.month,
        "year": date.year
    }
    db.collection("expenses").add(expense_data)
    st.success("Expense added successfully! 🎉")

# Function to retrieve monthly expenses
def get_monthly_expenses(user_uid, month, year):
    expenses_ref = db.collection("expenses").where("user_uid", "==", user_uid).where("month", "==", month).where("year", "==", year).stream()
    total_expense = 0
    category_totals = {}
    for expense in expenses_ref:
        expense_data = expense.to_dict()
        amount = expense_data['amount']
        category = expense_data['category']

        total_expense += amount
        category_totals[category] = category_totals.get(category, 0) + amount

    return total_expense, category_totals

# Function to plot a pie chart for category-wise expenses
def plot_category_expenses(category_totals):
    if category_totals:
        labels = category_totals.keys()
        sizes = category_totals.values()

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig1)
    else:
        st.write("No expenses to display.")

# Function to store savings goals in Firestore
def store_saving_goal(user_uid, goal_name, target_amount, current_amount, due_date):
    saving_goal_data = {
        "user_uid": user_uid,
        "goal_name": goal_name,
        "target_amount": target_amount,
        "current_amount": current_amount,
        "due_date": due_date.strftime("%Y-%m-%d"),
    }
    db.collection("saving_goals").add(saving_goal_data)
    st.success("Saving goal added successfully! 💰")

# Function to retrieve savings goals from Firestore
def get_saving_goals(user_uid):
    goals_ref = db.collection("saving_goals").where("user_uid", "==", user_uid).stream()
    goals = []
    for goal in goals_ref:
        goal_data = goal.to_dict()
        goals.append(goal_data)
    return goals

# Function to store debt information in Firestore
def store_debt(user_uid, debt_name, amount_due, due_date, payment_status):
    debt_data = {
        "user_uid": user_uid,
        "debt_name": debt_name,
        "amount_due": amount_due,
        "due_date": due_date.strftime("%Y-%m-%d"),
        "payment_status": payment_status,
    }
    db.collection("debts").add(debt_data)
    st.success("Debt added successfully! 💳")

# Function to retrieve debts from Firestore
def get_debts(user_uid):
    debts_ref = db.collection("debts").where("user_uid", "==", user_uid).stream()
    debts = []
    for debt in debts_ref:
        debt_data = debt.to_dict()
        debts.append(debt_data)
    return debts

#####yaha

# Authentication UI
st.sidebar.title("User Authentication")

auth_menu = ["Login", "Register"]
auth_choice = st.sidebar.selectbox("Auth Menu", auth_menu)

if auth_choice == "Register":
    st.sidebar.header("Register New User")
    reg_email = st.sidebar.text_input("Email")
    reg_password = st.sidebar.text_input("Password", type="password")
    if reg_email and reg_password:
        register_user(reg_email, reg_password)

elif auth_choice == "Login":
    st.sidebar.header("Login")
    login_email = st.sidebar.text_input("Email")
    login_password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if login_email and login_password:
            login_user(login_email, login_password)

# Streamlit UI for the Expense Tracker
st.title("💰 Personal Expense Tracker")

# Display the tracker only if the user is logged in
if st.session_state.user_uid:
    st.sidebar.title("Expense Tracker Menu")
    menu = ["Add Expense", "View Monthly Summary", "Savings Goals", "Debt Tracking"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Expense":
        st.header("Add a New Expense")

        # Input fields for expense details
        name = st.text_input("Name of the Expense")
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        categories = ["Food", "Transport", "Entertainment", "Bills", "Other"]
        category = st.selectbox("Category", categories)
        date = st.date_input("Date", max_value=datetime.today())
        description = st.text_area("Description")

        # Add expense button
        if st.button("Add Expense"):
            if name and amount > 0 and category and date:
                store_expense(st.session_state.user_uid, name, amount, category, date, description)
            else:
                st.error("Please provide all the required fields!")

    elif choice == "View Monthly Summary":
        st.header("Monthly Expense Summary")

        # Select month and year
        today = datetime.today()
        month = st.selectbox("Month", range(1, 13), index=today.month-1)
        year = st.selectbox("Year", range(2000, today.year+1), index=today.year-2000)

        # Show summary and category-wise pie chart
        if st.button("Show Summary"):
            total_expense, category_totals = get_monthly_expenses(st.session_state.user_uid, month, year)
            st.write(f"Total Expenses for {month}/{year}: ₹{total_expense:.2f}")
            plot_category_expenses(category_totals)

    elif choice == "Savings Goals":
        st.header("Add Savings Goal")

        # Input fields for savings goal details
        goal_name = st.text_input("Goal Name")
        target_amount = st.number_input("Target Amount", min_value=0.0, step=0.01)
        current_amount = st.number_input("Current Amount", min_value=0.0, step=0.01)
        due_date = st.date_input("Due Date", min_value=datetime.today())

        # Add savings goal button
        if st.button("Add Saving Goal"):
            if goal_name and target_amount > 0 and current_amount >= 0 and due_date:
                store_saving_goal(st.session_state.user_uid, goal_name, target_amount, current_amount, due_date)
            else:
                st.error("Please provide all the required fields!")

        # Display existing savings goals
        st.header("Your Savings Goals")
        saving_goals = get_saving_goals(st.session_state.user_uid)
        if saving_goals:
            for goal in saving_goals:
                st.write(f"**Goal:** {goal['goal_name']}")
                st.write(f"**Target Amount:** ₹{goal['target_amount']}")
                st.write(f"**Current Amount:** ₹{goal['current_amount']}")
                st.write(f"**Due Date:** {goal['due_date']}")
                st.write("---")
        else:
            st.write("No savings goals found.")

    elif choice == "Debt Tracking":
        st.header("Add Debt Information")

        # Input fields for debt details
        debt_name = st.text_input("Debt Name")
        amount_due = st.number_input("Amount Due", min_value=0.0, step=0.01)
        due_date = st.date_input("Due Date", min_value=datetime.today())
        payment_status = st.selectbox("Payment Status", ["Pending", "Paid"])

        # Add debt button
        if st.button("Add Debt"):
            if debt_name and amount_due > 0 and due_date:
                store_debt(st.session_state.user_uid, debt_name, amount_due, due_date, payment_status)
            else:
                st.error("Please provide all the required fields!")

        # Display existing debts
        st.header("Your Debts")
        debts = get_debts(st.session_state.user_uid)
        if debts:
            for debt in debts:
                st.write(f"**Debt Name:** {debt['debt_name']}")
                st.write(f"**Amount Due:** ₹{debt['amount_due']}")
                st.write(f"**Due Date:** {debt['due_date']}")
                st.write(f"**Payment Status:** {debt['payment_status']}")
                st.write("---")
        else:
            st.write("No debts found.")

