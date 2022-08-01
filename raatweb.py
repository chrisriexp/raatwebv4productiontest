import pandas as pd
import streamlit as st
from multiapp import MultiApp
from apps import downloads, home, settings, revenue, subagents
import sqlite3

app = MultiApp()

mainDB = sqlite3.connect('mainDB')
mainDBcursor = mainDB.cursor()

#mainDBcursor.execute("CREATE TABLE subagents(id INTEGER PRIMARY KEY AUTOINCREMENT, agency_name varchar(100) UNIQUE not null, tier varchar(15) not null, rocket_code char(13) UNIQUE not null, aon_code int UNIQUE not null, palomar_code char(11) UNIQUE not null, wright_code int UNIQUE not null)")
#mainDBcursor.execute("CREATE TABLE overriderevenue(id INTEGER PRIMARY KEY AUTOINCREMENT,uniqueparam varchar(100) UNIQUE not null, month char(7) not null, agency_name varchar(100) not null, rocket_code char(13) not null, carrier_name varchar(30) not null, override_amount int not null)")


st.set_page_config(page_title="R.A.A.T Web V4",
                   page_icon="./img/favicon.png",
                   layout="wide"
                   )

st.markdown("<h1 style='text-align: center; color: white;'>R.A.A.T Web V4</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>RocketMGA Accounting Automation Tool</h3>", unsafe_allow_html=True)

app.add_app("Home", home.app)
app.add_app("Downloads", downloads.app)
app.add_app("Revenue", revenue.app)
app.add_app("Sub Agents", subagents.app)
app.add_app("Settings", settings.app)


app.run()

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


    

