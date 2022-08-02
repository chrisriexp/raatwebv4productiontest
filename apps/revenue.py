import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

#Connect to Main Database   
mainDB = sqlite3.connect('mainDB')
#Create cursor to interact with Database
mainDBcursor = mainDB.cursor()

#Get all Sub Agents Listed within Sub Agents Table
mainDBcursor.execute("select * from subagents")    
result = mainDBcursor.fetchall();

def app():
    st.title("Revenue")
    
    #Connect to Main Database  
    mainDB = sqlite3.connect('mainDB')
    #Create cursor to interact with Database
    mainDBcursor = mainDB.cursor()
    
    #Array to hold int values for the subscription tiers
    saasIntArr = []
    
    #For loop to look through sub agent table and get all of the tiers listed and asign them to int values and apend to array
    for agency in result:
        saasFee = 0 
        if agency[2] == "Base":
            saasFee = 50
        elif agency[2]  == "Premium":
            saasFee = 75
        elif agency[2] == "Enterprise":
            saasFee = 100      
        saasIntArr.append(saasFee)
    
    #Get all override amounts from OverrideRevenue Table
    mainDBcursor.execute("select id, override_amount from overriderevenue")
    overrideAmounts = mainDBcursor.fetchall();
    
    #For every override amount that was pulled add the amount to array so that it can be totaled 
    orArray = []
    for item in overrideAmounts:
        orArray.append(item[1])
        
        
    
    #Get all the list of unique months in the Override Revenue Table
    mainDBcursor.execute("select distinct month from overriderevenue")
    monthsList = mainDBcursor.fetchall();
    
    #Array to hold all the unique months in the Override Revenue Table
    months = []
    #Array to hold the total commission for the unique months in the Override Revenue Table
    monthTotalOR = []
    
    
    #For loop to go through all the unique months in the Override Revenue Table and append the month and month total to the above arrays 
    for month in monthsList:
        Cmonth = str(month).replace("'", "").replace(",", "").replace("(", "").replace(")", "")
        
        months.append(Cmonth)
        
        mainDBcursor.execute("select id, month, override_amount from overriderevenue where month=?", (month))
        monthOR = mainDBcursor.fetchall();       
        
        monthORArray = []
        for override in monthOR:
            monthORArray.append(override[2])

        monthTotalOR.append(round(sum(monthORArray), 2))
     
        
        
    leftCol, middleCol, rightCol = st.columns(3)
    
    with leftCol:
        #Gross Software as a Service Revenue from Subscription Tiers
        st.markdown("##")
        st.markdown("<h3 style='text-align: center; color: white;'>SAAS Gross Revenue</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: white;'>${sum(saasIntArr)}/mo</h2>", unsafe_allow_html=True)
    with middleCol:
        #Gross Override Revenue
        st.markdown("##")
        st.markdown("<h3 style='text-align: center; color: white;'>Override Gross Revenue</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: white;'>${round(sum(orArray), 2)}</h2>", unsafe_allow_html=True)
    with rightCol:
        #Total Revenue from SAAS and Overrides combined
        st.markdown("##")
        st.markdown("<h3 style='text-align: center; color: white;'>Total Gross Revenue</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: white;'>${round(sum(orArray)+sum(saasIntArr), 2)}</h2>", unsafe_allow_html=True)

    st.markdown("##")
    st.markdown("---")  
    st.markdown("##") 
    
    
    dataCol1, dataCol2 = st.columns([3, 1])
    
    #Dataframe for chart using the months Array and monthTotalOR Array
    chartDf = pd.DataFrame({'Month': months, 'Revenue': monthTotalOR}, columns=['Month', 'Revenue'])
    
    with dataCol1:
        #Line Chart to display dataframe
        line_chart = alt.Chart(chartDf).mark_line().encode(y= alt.Y( 'Revenue', title='Total Revenue'), x= alt.X( 'Month', title='Month')).properties(title="Override Revenue").configure_title(fontSize=23).configure_axis(titleFontSize=16, labelFontSize=14, titlePadding=15, labelPadding=10).configure_axisBottom(labelAngle=360)
        st.altair_chart(line_chart, use_container_width=True)
    with dataCol2:
        st.write(chartDf.style.format({'Revenue': '{:.2f}'}))
        
    st.markdown("##")
    st.markdown("##")
    
    #Sorted Bar Chart to show all subagents in decreasing order of more revenue from overrides
    
    sortedBarAgencies = []
    sortedBarTotals = []

    for agency in result:
        mainDBcursor.execute("select agency_name, rocket_code, override_amount from overriderevenue where rocket_code=?", (agency[3],))
        agencyOverrideAmounts = mainDBcursor.fetchall();
        
        #Array that holds all the overrides for the current agency
        agencyTotalArray = []
        #Append each override for the agency to the above array
        for override in agencyOverrideAmounts:
            agencyTotalArray.append(override[2])
        
        #Append the Agency to sortedBarAgencies
        sortedBarAgencies.append(agency[1])
        #Append the total of the agency override to sortedBarTotals
        sortedBarTotals.append(round(sum(agencyTotalArray), 2)) 
        
    
    agencySortedBarDf = pd.DataFrame({"Agency": sortedBarAgencies, "Total": sortedBarTotals})
    
    sortedBarDataCol1, sortedBarDataCol2 = st.columns([3, 1])
    
    with sortedBarDataCol1:
        agencySortedBar = alt.Chart(agencySortedBarDf).mark_bar().encode(x=alt.X('Total:Q', title='Total Override Revenue'), y=alt.Y('Agency:N', sort='-x')).properties(title="Sub Agent Total Override Revenue").configure_title(fontSize=23).configure_axis(titleFontSize=16, labelFontSize=14, titlePadding=15, labelPadding=10)
        st.altair_chart(agencySortedBar, use_container_width=True)
    with sortedBarDataCol2:
        st.write(agencySortedBarDf.sort_values(by=['Total'], ascending=False).style.format({'Total': '{:.2f}'}))