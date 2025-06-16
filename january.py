import streamlit as st
import pandas as pd

jan_late = pd.read_csv("january_raw.csv")

late_threshold_minutes = 8 * 60 

def time_to_minutes(time_str):
    if time_str in ['dayoff', '0:00']:
        return None
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    except (ValueError, AttributeError):
        return None

def calculate_lateness(minutes):
    if minutes is None:
        return None
    if minutes >= late_threshold_minutes:
        return minutes - late_threshold_minutes
    return None

late_records = []

for index, row in jan_late.iterrows():
    name = row['name']
    for day, time in row.items():
        if day != 'name':
            minutes = time_to_minutes(time)
            lateness = calculate_lateness(minutes)
            if lateness is not None:
                late_records.append((day, name, lateness))

late_df = pd.DataFrame(late_records, columns=['January', 'Name', 'Lateness'])

late_df['Hours'] = late_df['Lateness'] // 60
late_df['Minutes'] = late_df['Lateness'] % 60
late_df.drop(columns=['Lateness'], inplace=True)

late_df['January'] = late_df['January'].str.extract(r'(\d+)').astype(int)
late_df = late_df.sort_values(by='January')

st.title('Employee Lateness Report')
st.write("This application displays the lateness records of employees for January.")

with st.expander("Show Lateness Records"):
    st.dataframe(late_df, height=600, width=1000)
