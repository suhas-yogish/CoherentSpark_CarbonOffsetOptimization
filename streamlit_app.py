# Standart python imports
from enum import Enum
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import requests
import json


st.set_page_config(layout="wide")

markdown_about_model = """

### Use Case Demonstration - using Spark for Carbon Tax Calculations and Offsetting Optimization

- The carbon model builds upon the base GHG emissions tool provided universally online. GHG emissions report is part of the TCFD regulations that companies are required to submit.
- In this model, one of the key Spark functionality illustrated involves xCall. We assume that the Controller model is the main file which consolidates the GHG Emission report across companies in different countries with varying inputs and outputs to the GHG emission model. 
- Illustrations were provided in this model to depict scenarios such as the consolidation of Scope 1, Scope 2, Scope 3 emissions over the years across countries, as well as simple projections and carbon tax calculations.
- Carbon Tax Credit optimization is also illustrated in this model. Key Spark functionality illustrated here would be using the xSolve function to derive optimized carbon credits amount to be purchased in each respective country through a goal seek method. 
- OECD Data can also be called into the model to derive the optimal carbon credit amount/carbon tax required using xCall or OECD API """

markdown_about_spark = """## **[Coherent Spark](https://coherent.global/spark/)**

### Building business software is now as easy as creating an Excel worksheet.

- Convert spreadsheets into ready-to-integrate APIs
- Centralize, secure & audit business logic
- Automate complex modeling, testing & business impact simulation """

tab1, tab2 = st.tabs(['Carbon Tax Calculations', 'About Coherent Spark'])
with tab1:
    st.markdown(markdown_about_model)
    
with tab2:
    st.markdown(markdown_about_spark)
    # Embed Coherent Spark video
    components.html(
        """
        <iframe src="https://player.vimeo.com/video/673532746?h=7ce2921baa" width="640" height="360" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen </iframe>
        """,
        height=360,
    )

x_synthetic_key = 'eecee262-6c42-4219-beb7-19362ef9697b'

def CallSparkEngine(xInput_a_Country, xInput_b_CO2_Emitted, xInput_1_FET, xInput_2_CT, 
                    xInput_3_ETS_PP, xInput_4_FF_subsidy, xInput_5_Carbon_Credits, xInput_5i_Offset_Cap):

    url = "https://excel.uat.us.coherent.global/coherent/api/v3/folders/ESG/services/Controller v1/Execute"
    
    payload = json.dumps({
       "request_data": {
          "inputs": {
              "1_FET": xInput_1_FET,
              "2_CT": xInput_2_CT,
              "3_ETS_PP": xInput_3_ETS_PP,
              "4_FF_subsidy": xInput_4_FF_subsidy,
              "5_Carbon_Credits":xInput_5_Carbon_Credits,
              "5i_Offset_Cap": xInput_5i_Offset_Cap,
              "a_Country": xInput_a_Country,
              "b_CO2_Emitted": xInput_b_CO2_Emitted
            }
       }
    })
    headers = {
       'Content-Type': 'application/json', 
       'x-tenant-name': 'coherent',
       'x-synthetic-key': 'eecee262-6c42-4219-beb7-19362ef9697b'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    outputs = json.loads(response.text)['response_data']['outputs']
    
    return outputs

def illustrations(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Scope 1 Combustions (Stationary, Mobile and Refrigerants)'],
        name='Scope 1 Combustions (Stationary, Mobile and Refrigerants)',
        marker_color='crimson',
        text=df['Scope 1 Combustions (Stationary, Mobile and Refrigerants)']
    ))
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Scope 2 Combustions (Purchased Electricity)'],
        name='Scope 2 Combustions (Purchased Electricity)',
        marker_color='lightslategrey',
        text=df['Scope 2 Combustions (Purchased Electricity)']
    ))

    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Scope 3 (Transportations)'],
        name='Scope 3 (Transportations)',
        marker_color='cornflowerblue',
        text=df['Scope 3 (Transportations)']
    ))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_traces(texttemplate='%{text:$.3s}', textposition='outside')
    fig.update_layout(barmode='group', width=1200, height=600, bargroupgap=0.1)
    return fig

# st.header('ESG Carbon Offset Optimization')

with st.sidebar:
    st.image('https://drive.google.com/uc?export=view&id=1UZ-YcQm-K5JNaRd1uAZNNBqInqSYIBH5')
    xInput_a_Country = st.selectbox('Country', ('France', 'Germany', 'Italy', 'Switzerland'))
    xInput_b_CO2_Emitted = st.number_input('Average Amount of CO2 emitted (tonne)', 905.98)

    st.subheader('Tax (Average in Currency Unit per tCO2e)')
    xInput_1_FET = st.slider('Fuel Excise Tax', 0.0, 100.0, 20.0)
    xInput_2_CT = st.slider('Carbon Tax', 0.0, 10.0, 2.0)
    xInput_3_ETS_PP = st.number_input('ETS Permit Price', 0.0)
    xInput_4_FF_subsidy = st.number_input('Fossil Fuel Subsidy', 0.10)

    st.subheader('Carbon Credits Offsetting')
    xInput_5_Carbon_Credits = st.slider('Carbon Credits Price (Average in Currency Unit per tCO2e)', 0.0, 50.0, 4.57)
    xInput_5i_Offset_Cap = st.slider('Offset Cap/Limit (%)', 0.0, 100.0, 7.0)
    
    button = st.button('Solve for Carbon Credits', type='primary')
    

if button:
    outputs = CallSparkEngine(xInput_a_Country, xInput_b_CO2_Emitted, xInput_1_FET, xInput_2_CT, 
                              xInput_3_ETS_PP, xInput_4_FF_subsidy, xInput_5_Carbon_Credits, xInput_5i_Offset_Cap/100)
    
    effectiveCarbonRate = outputs['1_ECR']
    netEffectiveCarbonRate = outputs['2_NECR']
    totalCarbonTax = outputs['3_Total_Carbon_Tax']
    maxCreditOffset = outputs['4_Max_Offset_Amt']
    numberOfCarbonCredits = outputs['Carbon_Credit_Units'] 
    netTaxAfterCarbonCredits = outputs['5_Carbon_Nett_Tax']
    
    franceCTP = pd.DataFrame(outputs['FranceCTP'])
    franceCTP = franceCTP.set_index('Carbon Tax France')
    franceCTP = franceCTP.T
    
    franceCTA = pd.DataFrame(outputs['FranceCTA'])
    franceCTA = franceCTA.set_index('Carbon Tax France')
    franceCTA = franceCTA.T
    
    italyCTP = pd.DataFrame(outputs['ItalyCTP'])
    italyCTP = italyCTP.set_index('Carbon Tax Italy')
    italyCTP = italyCTP.T
    
    italyCTA = pd.DataFrame(outputs['ItalyCTA'])
    italyCTA = italyCTA.set_index('Carbon Tax Italy')
    italyCTA = italyCTA.T
    
    germanyCTP = pd.DataFrame(outputs['GermanyCTP'])
    germanyCTP = germanyCTP.set_index('Carbon Tax Germany')
    germanyCTP = germanyCTP.T
    
    germanyCTA = pd.DataFrame(outputs['GermanyCTA'])
    germanyCTA = germanyCTA.set_index('Carbon Tax Germany')
    germanyCTA = germanyCTA.T
    
    swizCTP = pd.DataFrame(outputs['SwizCTP'])
    swizCTP = swizCTP.set_index('Carbon Tax Swizterland')
    swizCTP = swizCTP.T
    
    swizCTA = pd.DataFrame(outputs['SwizCTA'])
    swizCTA = swizCTA.set_index('Carbon Tax Swizterland')
    swizCTA = swizCTA.T
    
    if xInput_a_Country == "France":
        st.subheader('France Carbon Tax Calculations')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        col1.metric(label="Effective Carbon Rate", value="$"+str(round(effectiveCarbonRate, 2)))
        col2.metric(label="Net Effective Carbon Rate", value="$"+str(round(netEffectiveCarbonRate, 2)))
        col3.metric(label="Total Carbon Tax", value="$"+str(round(totalCarbonTax, 2)))
        col4.metric(label="Max Credit Offset", value="$"+str(round(maxCreditOffset, 2)))
        col5.metric(label="No. of Units of Carbon Credit", value=str(round(numberOfCarbonCredits)))
        col6.metric(label="Net Tax after Carbon Credits", value="$"+str(round(netTaxAfterCarbonCredits, 2)))
        
        tab1, tab2 = st.tabs(['Carbon Tax Amount', 'Carbon Tax Projections'])
        with tab1:
            fig = illustrations(franceCTA)
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            fig = illustrations(franceCTP)
            st.plotly_chart(fig, use_container_width=True)
            
    if xInput_a_Country == "Germany":
        st.subheader('Germany Carbon Tax Calculations')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        col1.metric(label="Effective Carbon Rate", value="$"+str(round(effectiveCarbonRate, 2)))
        col2.metric(label="Net Effective Carbon Rate", value="$"+str(round(netEffectiveCarbonRate, 2)))
        col3.metric(label="Total Carbon Tax", value="$"+str(round(totalCarbonTax, 2)))
        col4.metric(label="Max Credit Offset", value="$"+str(round(maxCreditOffset, 2)))
        col5.metric(label="No. of Units of Carbon Credit", value=str(round(numberOfCarbonCredits)))
        col6.metric(label="Net Tax after Carbon Credits", value="$"+str(round(netTaxAfterCarbonCredits, 2)))
        
        tab1, tab2 = st.tabs(['Carbon Tax Amount', 'Carbon Tax Projections'])
        with tab1:
            fig = illustrations(germanyCTA)
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            fig = illustrations(germanyCTP)
            st.plotly_chart(fig, use_container_width=True)
            
    if xInput_a_Country == "Italy":
        st.subheader('Italy Carbon Tax Calculations')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        col1.metric(label="Effective Carbon Rate", value="$"+str(round(effectiveCarbonRate, 2)))
        col2.metric(label="Net Effective Carbon Rate", value="$"+str(round(netEffectiveCarbonRate, 2)))
        col3.metric(label="Total Carbon Tax", value="$"+str(round(totalCarbonTax, 2)))
        col4.metric(label="Max Credit Offset", value="$"+str(round(maxCreditOffset, 2)))
        col5.metric(label="No. of Units of Carbon Credit", value=str(round(numberOfCarbonCredits)))
        col6.metric(label="Net Tax after Carbon Credits", value="$"+str(round(netTaxAfterCarbonCredits, 2)))
        
        tab1, tab2 = st.tabs(['Carbon Tax Amount', 'Carbon Tax Projections'])
        with tab1:
            fig = illustrations(italyCTA)
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            fig = illustrations(italyCTP)
            st.plotly_chart(fig, use_container_width=True)
            
    if xInput_a_Country == "Switzerland":
        st.subheader('Switzerland Carbon Tax Calculations')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        col1.metric(label="Effective Carbon Rate", value="$"+str(round(effectiveCarbonRate, 2)))
        col2.metric(label="Net Effective Carbon Rate", value="$"+str(round(netEffectiveCarbonRate, 2)))
        col3.metric(label="Total Carbon Tax", value="$"+str(round(totalCarbonTax, 2)))
        col4.metric(label="Max Credit Offset", value="$"+str(round(maxCreditOffset, 2)))
        col5.metric(label="No. of Units of Carbon Credit", value=str(round(numberOfCarbonCredits)))
        col6.metric(label="Net Tax after Carbon Credits", value="$"+str(round(netTaxAfterCarbonCredits, 2)))
        
        tab1, tab2 = st.tabs(['Carbon Tax Amount', 'Carbon Tax Projections'])
        with tab1:
            fig = illustrations(swizCTA)
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            fig = illustrations(swizCTP)
            st.plotly_chart(fig, use_container_width=True)
