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
    
    
    #Array to hold all unique sug agents      
    agencys = []
    #Array to hold all unique sug agent codes     
    agencycodes = []
    #Append all unique sub agents to above array
    for agency in result:
        agencys.append(agency[1])
        agencycodes.append(agency[3])
    
    df2subagents = []
    df2month = []
    df2totalOR = []
    
    #Graph and Dataframe to show revenue from each subagent over the months
    for month in months:
        for agency in agencys:
            #Query to look for all transactions for the specific month 
            mainDBcursor.execute("select month, agency_name, override_amount from overriderevenue where month=? and agency_name=?", (month, agency))
            agencyMonthOR = mainDBcursor.fetchall();    
            
            agencyMonthORArray = []
            for override in agencyMonthOR:
                agencyMonthORArray.append(override[2])
            
            df2subagents.append(agency)
            df2month.append(month)
            df2totalOR.append(round(sum(agencyMonthORArray), 2))
    
    
      
    subAgentsMonthlyORDf = pd.DataFrame({'Agency': df2subagents, 'Month': df2month, 'OverrideAmt': df2totalOR}, columns=['Agency', 'Month', 'OverrideAmt'])  
    
    #Line Chart to display dataframe
    carrierLineChart = alt.Chart(subAgentsMonthlyORDf).mark_line().encode(y= alt.Y( 'OverrideAmt', title='Total Revenue'), x= alt.X( 'Month', title='Month'), color='Agency').properties(title="Sub Agent Override Revenue").configure_title(fontSize=23).configure_axis(titleFontSize=16, labelFontSize=14, titlePadding=15, labelPadding=10).configure_axisBottom(labelAngle=360)
    st.altair_chart(carrierLineChart, use_container_width=True)
    
    #st.write(subAgentsMonthlyORDf.style.format({'OverrideAmt': '{:.2f}'}))
    
    st.markdown("##")
    st.markdown("##")
    
    dfAgencyName = []
    dfTier = []
    dfRocketCode = []
    dfAgencyTotalOR = []
    
    for agency in result:
        dfAgencyName.append(agency[1])
        dfTier.append(agency[2])
        dfRocketCode.append(agency[3])
        
        #Get all override amounts from OverrideRevenue Table
        mainDBcursor.execute("select id, rocket_code, override_amount from overriderevenue where rocket_code=?", (agency[3],))
        agencyOverrideAmounts = mainDBcursor.fetchall();
        
        dfAgencyORArray = []
        #Array of all overrides for agency to sum and get total
        for item in agencyOverrideAmounts:
            dfAgencyORArray.append(item[2])
        
        dfAgencyTotalOR.append(round(sum(dfAgencyORArray), 2))
        
    #Dataframe based on the above arrays to use in the Chart
    carrierDf = pd.DataFrame({'Agency Name': dfAgencyName, 'Tier': dfTier, 'Rocket Code': dfRocketCode, 'Total Override': dfAgencyTotalOR}, columns=['Agency Name', 'Tier', 'Rocket Code', 'Total Override'])
            
    #st.dataframe(carrierDf.style.format({'Total Override': '{:.2f}'}))