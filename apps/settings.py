import streamlit as st
import sqlite3


def app():
    st.title("Settings")       
    
    #Connect to Main Database 
    mainDB = sqlite3.connect('mainDB')
    #Create cursor to interact with Database
    mainDBcursor = mainDB.cursor()
    
    #Get all Sub Agents Listed within Sub Agents Table
    mainDBcursor.execute("select * from subagents")
    result = mainDBcursor.fetchall();
    
    
    #Form to add New Sub Agents to Database
    with st.form("addSubAgent", clear_on_submit=True):
        st.subheader('Add Sub Agent')
        newAgencyName = st.text_input("Add Agency Name", "", placeholder="Agency Name")
        newAgencyTier = st.text_input("Add Agency Tier", "", placeholder="Base")
        newRocketCode = st.text_input("Add Rocket Code", "", placeholder="RocketCode000")
        newAonCode = st.text_input("Add Aon Code", "", placeholder="0000")
        newPalomarCode = st.text_input("Add Palomar Code", "", placeholder="PSIC-0000-0")
        newWrightCode = st.text_input("Add Wright Code", "", placeholder='000000')
        
        submitted = st.form_submit_button("Submit")
        
        #When submitted add New Agent to Database
        if submitted:
            mainDBcursor.execute("insert into subagents(agency_name, tier, rocket_code, aon_code, palomar_code, wright_code) values(?, ?, ?, ?, ?, ?)", (newAgencyName, newAgencyTier, newRocketCode, int(newAonCode), newPalomarCode, int(newWrightCode)))
              
        
    #agencyNameCol, tierCol, rocketAgencyCodeCol, aonCodeCol, palomarCodeCol, wrightCodeCol = st.columns(6)
    
    #with agencyNameCol:
        #st.subheader("Agency Name")
        #for item in result:
            #st.write(item[1])
    #with tierCol:
        #st.subheader("Tier")
        #for item in result:
            #st.write(item[2])
    #with rocketAgencyCodeCol:
        #st.subheader("Rocket Code")
        #for item in result:
            #st.write(item[3])
    #with aonCodeCol:
        #st.subheader("Aon Code")
        #for item in result:
            #st.write(str(item[4]))
    #with palomarCodeCol:
        #st.subheader("Palomar Code")
        #for item in result:
            #st.write(item[5])
    #with wrightCodeCol:
        #st.subheader("Wright Code")
        #for item in result:
            #st.write(str(item[6]))
    
    
    #Save Changes made to Database        
    mainDB.commit()
