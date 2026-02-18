import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- GOOGLE SHEETS SETUP ----------------

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_ID = "1kh0gXSw2iH_2ImSAJfj95YMIhpQMUfPoBnss-pk-IkI"
sheet = client.open_by_key(SHEET_ID).sheet1


def insert_data(type_, amount, date, remark):
    sheet.append_row([type_, amount, date, remark])


def load_data():
    records = sheet.get_all_records()
    return pd.DataFrame(records)


def delete_row(row_number):
    sheet.delete_rows(row_number)


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Stock App",
    layout="centered"
)

st.markdown("<h2 style='text-align:center;'>📊 Stock Maintenance App</h2>", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Add Investment", "Add Sell", "Investment History", "Sell History"]
)

# ---------------- DASHBOARD ----------------

if menu == "Dashboard":

    df = load_data()

    if not df.empty:
        invest_total = df[df["Type"] == "invest"]["Amount"].astype(float).sum()
        sell_total = df[df["Type"] == "sell"]["Amount"].astype(float).sum()
        profit = sell_total - invest_total
    else:
        invest_total = sell_total = profit = 0

    col1, col2 = st.columns(2)

    col1.metric("Total Invested", f"₹ {invest_total}")
    col2.metric("Total Sold", f"₹ {sell_total}")

    st.metric("Profit / Loss", f"₹ {profit}")

# ---------------- ADD INVESTMENT ----------------

elif menu == "Add Investment":

    st.subheader("➕ Add Investment")

    amount = st.number_input("Enter Amount", min_value=0.0, format="%.2f")
    date = st.date_input("Select Date", value=datetime.today())
    remark = st.text_input("Remark")

    if st.button("Save Investment"):
        if amount > 0:
            insert_data("invest", amount, date.strftime("%d-%m-%Y"), remark)
            st.success("Investment Saved Successfully!")
        else:
            st.error("Please enter valid amount")

# ---------------- ADD SELL ----------------

elif menu == "Add Sell":

    st.subheader("➖ Add Sell")

    amount = st.number_input("Enter Amount", min_value=0.0, format="%.2f")
    date = st.date_input("Select Date", value=datetime.today())
    remark = st.text_input("Remark")

    if st.button("Save Sell"):
        if amount > 0:
            insert_data("sell", amount, date.strftime("%d-%m-%Y"), remark)
            st.success("Sell Saved Successfully!")
        else:
            st.error("Please enter valid amount")

# ---------------- INVEST HISTORY ----------------

elif menu == "Investment History":

    st.subheader("📈 Investment History")

    df = load_data()

    if not df.empty:
        invest_df = df[df["Type"] == "invest"].copy()

        if not invest_df.empty:
            invest_df.reset_index(inplace=True)

            for i, row in invest_df.iterrows():
                col1, col2 = st.columns([4,1])
                col1.write(f"₹ {row['Amount']} | {row['Date']} | {row['Remark']}")

                if col2.button("❌", key=f"inv_{i}"):
                    delete_row(row["index"] + 2)  # +2 because sheet index starts from 1 and header
                    st.success("Transaction Deleted")
                    st.rerun()
        else:
            st.info("No Investment transactions found.")
    else:
        st.info("No Data Available.")

# ---------------- SELL HISTORY ----------------

elif menu == "Sell History":

    st.subheader("📉 Sell History")

    df = load_data()

    if not df.empty:
        sell_df = df[df["Type"] == "sell"].copy()

        if not sell_df.empty:
            sell_df.reset_index(inplace=True)

            for i, row in sell_df.iterrows():
                col1, col2 = st.columns([4,1])
                col1.write(f"₹ {row['Amount']} | {row['Date']} | {row['Remark']}")

                if col2.button("❌", key=f"sell_{i}"):
                    delete_row(row["index"] + 2)
                    st.success("Transaction Deleted")
                    st.rerun()
        else:
            st.info("No Sell transactions found.")
    else:
        st.info("No Data Available.")
