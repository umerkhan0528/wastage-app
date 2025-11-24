import streamlit as st
import pandas as pd
import numpy as np

st.title("Wastage Analysis Tool")

uploaded = st.file_uploader("Upload your Foodpanda CSV file", type=["csv"])

wastage_reasons = [
"Change of mind – customer cancelled",
"Courier accident",
"Courier unreachable",
"Customer cancelled; Order took longer than expected ",
"Customer never received the order ",
"Customer received inedible food",
"Duplicate order",
"Food quality:Spillage",
"Incorrect address",
"No rider available",
"Order modification is not possible",
"Outside delivery area",
"Unsafe delivery area",
"Technical problem",
"Too late delivery",
"Unable to find customer",
"Unable to pay"
]


def process(df):
    df['Is Wastage'] = df['Cancellation reason'].isin(wastage_reasons)
    df['Cancel Stage'] = np.where(df['Is Wastage'],
                                  np.where(df['In delivery at'].isna(),"Before pickup","After pickup"),
                                  "")

    for col in ['Accepted at','In delivery at','Cancelled at']:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    def calc_delay(row):
        if row['Cancel Stage']=="Before pickup":
            if pd.notnull(row['Accepted at']) and pd.notnull(row['Cancelled at']):
                return (row['Cancelled at'] - row['Accepted at']).total_seconds()/60
        if row['Cancel Stage']=="After pickup":
            if pd.notnull(row['Accepted at']) and pd.notnull(row['In delivery at']):
                return (row['In delivery at'] - row['Accepted at']).total_seconds()/60
        return np.nan

    df['Delay (mins)'] = df.apply(calc_delay, axis=1)
    return df

if uploaded:
    df = pd.read_csv(uploaded)
    result = process(df)
    st.success("Processing completed!")
    st.dataframe(result)
    csv = result.to_csv(index=False).encode('utf-8')
    st.download_button("Download Processed File", csv, "processed.csv", "text/csv")
