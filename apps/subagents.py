import streamlit as st
import sqlite3
import pandas as pd
from statistics import mean
import altair as alt

#Connect to Main Database   
mainDB = sqlite3.connect('mainDB')
#Create cursor to interact with Database
mainDBcursor = mainDB.cursor()

#Get all Sub Agents Listed within Sub Agents Table
mainDBcursor.execute("select * from subagents")    
result = mainDBcursor.fetchall();


def app():
    st.title('Sub Agents')
    #Connect to Main Database  
    mainDB = sqlite3.connect('mainDB')
    #Create cursor to interact with Database
    mainDBcursor = mainDB.cursor()
    
    
    #Page Headers
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.subheader("Agency Name")
    with col2:
        st.subheader("Agency Tier")
    with col3:
        st.subheader("Agency Rocket Code")
    with col4:
        st.subheader("Agency Carrier Codes")
    st.markdown("---")
    st.markdown("##")
    st.markdown("##")

    
    #For loop to create each agency
    for agency in result:
        agencyName, agencyTier, agencyCode, carrierCodes = st.columns(4, gap="medium")
        
        with agencyName:
            #Write Agency Name
            st.write(agency[1])
        with agencyTier:
            #Write Agency Tier
            st.write(agency[2])
        with agencyCode:
            #Write Agency Rocket Code
            st.write(agency[3])
        with carrierCodes:
            #Show all Agency Carrier Codes
            with st.expander("See Agency Carrier Codes"):
                st.write(f'Aon Edge Code: {agency[4]}')
                st.write(f'Palomar Code: {agency[5]}')
                st.write(f'Wright National Code: {agency[6]}')
        
        #Agency Revenue Details
        with st.expander("Agency Revenue Details"):
            #Agency SAAS Cost based on tier
            agencySAAS = 0
            if agency[2] == "Base":
                agencySAAS = 50
            elif agency[2]  == "Premium":
                agencySAAS = 75
            elif agency[2] == "Enterprise":
                agencySAAS = 100 

            
            #Get all override amounts from OverrideRevenue Table
            mainDBcursor.execute("select id, month, rocket_code, override_amount from overriderevenue where rocket_code=?", (agency[3],))
            agencyOverrideAmounts = mainDBcursor.fetchall();
            
            #Array of all overrides for agency to sum and get total
            agencyTotalORArray = []
            for item in agencyOverrideAmounts:
                agencyTotalORArray.append(item[3])
            
            
            #Get all the list of unique months in the Override Revenue Table
            mainDBcursor.execute("select distinct month from overriderevenue")
            monthsList = mainDBcursor.fetchall();
            
            #Array to hold unique months 
            uniqueMonths = []
            #For loop to append months without extra characters to above array
            for month in monthsList:
                Cmonth = str(month).replace("'", "").replace(",", "").replace("(", "").replace(")", "")
                uniqueMonths.append(Cmonth)    

            #Array to hold the total Override for each month
            monthsOR = []
            
            #For loop that finds that total Agency Overrides for each month 
            for month in uniqueMonths:
                #Pull data from overriderevenue when the month is equal to the current month in the loop and the agency code matches
                mainDBcursor.execute("select id, month, rocket_code, override_amount from overriderevenue where month=? and rocket_code=?", (month, agency[3]))
                monthOR = mainDBcursor.fetchall();  
                
                #Array that holds all the overrides for the current month
                monthTotalArray = []
                #Append each override for the month to the above array
                for override in monthOR:
                    monthTotalArray.append(override[3])
                #Appen the total of the months override to monthsOR
                monthsOR.append(round(sum(monthTotalArray), 2))  
                
            
            saasCol, avgORCol, totalORCol = st.columns(3, gap="large")
            
            with saasCol:
                #Agency months SAAS Cost based on tier
                st.subheader("SAAS Revenue")
                st.write(f'${str(agencySAAS)}/mo')
            with avgORCol:
                #Average Overide for Agency per month
                st.subheader("Avg. Monthly Override Revenue")
                st.write(f'${str(round(mean(monthsOR), 2))}/mo')
            with totalORCol:
                #Total Agency Override
                st.subheader("Total Override Revenue")
                st.write(f'${round(sum(agencyTotalORArray), 2)}')

            st.markdown("---")
            
            #Dataframe for chart using uniqueMonths and monthsOR
            agencyChartDf = pd.DataFrame({'Month': uniqueMonths, 'Revenue': monthsOR}, columns=['Month', 'Revenue'])
            
            dataCol1, dataCol2 = st.columns([3, 1])
            
            with dataCol1:
                #Line Chart to display dataframe
                agency_line_chart = alt.Chart(agencyChartDf).mark_line().encode(y= alt.Y( 'Revenue', title='Total Revenue'), x= alt.X( 'Month', title='Month')).properties(title="Total Override Revenue").configure_title(fontSize=23).configure_axis(titleFontSize=16, labelFontSize=14, titlePadding=15, labelPadding=10).configure_axisBottom(labelAngle=360)
                st.altair_chart(agency_line_chart, use_container_width=True)
            with dataCol2:
                st.write(agencyChartDf.sort_values(by=['Month'], ascending=False).style.format({'Revenue': '{:.2f}'}))

            st.markdown("##")
            
            pieChartCarriers = []
            pieChartCarrierTotals = []
            
            #Get all the list of unique months in the Override Revenue Table
            mainDBcursor.execute("select distinct carrier_name from overriderevenue where rocket_code=?", (agency[3],))
            agencyCarrierList = mainDBcursor.fetchall();
            
            #Array to hold unique Carriers 
            agencyuniqueCarriers = []
            #For loop to append carriers without extra characters to above array
            for item in agencyCarrierList:
                carrierC = str(item).replace("'", "").replace(",", "").replace("(", "").replace(")", "")
                agencyuniqueCarriers.append(carrierC)   
                
            for carrier in agencyuniqueCarriers:
                #Get all override amounts from OverrideRevenue Table for agency with specific carrier 
                mainDBcursor.execute("select carrier_name, rocket_code, override_amount from overriderevenue where rocket_code=? and carrier_name=?", (agency[3], carrier))
                agencyCarrierOR = mainDBcursor.fetchall();
                
                #Array that holds all the overrides for the current carrier
                carrierTotalArray = []
                #Append each override for the carrier to the above array
                for override in agencyCarrierOR:
                    carrierTotalArray.append(override[2])
                    
                #Append the Carrier to pieChartCarriers
                pieChartCarriers.append(carrier)
                #Append the total of the carrier override to pieChartCarrierTotals
                pieChartCarrierTotals.append(round(sum(carrierTotalArray), 2))  
            
            
            carrierPieChartDf = pd.DataFrame({"Carrier": pieChartCarriers, "Total": pieChartCarrierTotals})
            
            
            pieDataCol1, pieDataCol2 = st.columns([3, 1])
            
            with pieDataCol1:
                #Pie Chart to display override per carrier
                carrierPieChart = alt.Chart(carrierPieChartDf).mark_arc().encode(theta=alt.Theta(field="Total", type="quantitative"), color=alt.Color(field="Carrier", type="nominal"))
                st.altair_chart(carrierPieChart, use_container_width=True)
            with pieDataCol2:
                st.write(carrierPieChartDf.sort_values(by=['Total'], ascending=False).style.format({'Total': '{:.2f}'}))
        
        st.markdown("##")    
        st.markdown("---")