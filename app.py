import streamlit as st
import pandas as pd
import plotly.express as px
import yaml
import bcrypt

# datasets
dataset = pd.read_csv("modified_januaryy.csv")
dataset_feb = pd.read_csv("modified_febuary.csv")



jan_late = pd.read_csv("january_raw.csv")
feb_late = pd.read_csv("febuary_raw.csv")


#---------------------read hashed password--------------------------------------------------------#
with open("passwords.yaml", "r") as file:
    hashed_password = yaml.safe_load(file)["hashed_password"]

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
#------------------------------------------------------------------------------------------------------#
#-----------------------------------main application----------------------------------------------
def main():
    st.set_page_config(page_title="AttendDash", page_icon="📊")
    header_html = """
    <h1 style='text-align: center; color: white; border-bottom: 2px solid grey; padding-bottom: 10px;'>AttendDash</h1>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    st.write("\n\n\n\n\n")  
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.form(key="login_form"):
            password = st.text_input("Enter Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if verify_password(password, hashed_password):
                    st.session_state.logged_in = True
                    st.success("Logged in successfully!")
                    st.experimental_rerun()
                else: 
                    st.error("Incorrect Password! Try Agaain.")

  
    if st.session_state.logged_in:
        st.session_state.logged_in = True
        #---------------------------------January data-----------------------------------------------------------#
        def january(dataset, jan_late):
            def count_occurrences(row):
                late_count = (row == "L").sum()
                absent_count = (row == "A").sum()
                on_time_count = (row == "O").sum()
                return late_count, absent_count, on_time_count

            counts = dataset.set_index('name').apply(count_occurrences, axis=1)

            dataset["Late"], dataset["Absent"], dataset["On Time"] = zip(*counts)

            most_late_employee = dataset.loc[dataset["Late"].idxmax(), "name"]
            most_late_count = dataset["Late"].max()

            most_absent_employee = dataset.loc[dataset["Absent"].idxmax(), "name"]
            most_absent_count = dataset["Absent"].max()

            most_on_time_employee = dataset.loc[dataset["On Time"].idxmax(), "name"]
            most_on_time_count = dataset["On Time"].max()
            col1, col2, col3 = st.columns(3)

            most_late_count_str = str(most_late_count)
            most_absent_count_str = str(most_absent_count)
            most_on_time_count_str = str(most_on_time_count)

            col2.metric("Employee With Most Late", most_late_employee, most_late_count_str, delta_color='off')
            col3.metric("Employee with Most Absences", most_absent_employee, most_absent_count_str, delta_color="inverse")
            col1.metric("Employee with Most On-time", most_on_time_employee, most_on_time_count_str)
            
            #----------------------------------------------------------------------------------------------------------------------#
            
         
            def visualize(row):
                late_count = (row == "L").sum()
                absent_count = (row == "A").sum()
                on_time_count = (row == "O").sum()
                dayoff_count = (row == "D").sum()
                return late_count, absent_count, on_time_count, dayoff_count

            late_counts = []
            absent_counts = []
            on_time_counts = []
            dayoff_counts = []

            for day in range(1, 32):
                row = dataset[f'jan{day}']
                # Count occurrences for the current day
                late_count, absent_count, on_time_count, dayoff_count = visualize(row)
                # Append counts to the lists
                late_counts.append(late_count)
                absent_counts.append(absent_count)
                on_time_counts.append(on_time_count)
                dayoff_counts.append(dayoff_count)

            df = pd.DataFrame({'Day': range(1, 32),
                            'Late': late_counts,
                            'Absent': absent_counts,
                            'On Time': on_time_counts,
                            'Dayoff': dayoff_counts})

            df_melted = pd.melt(df, id_vars=['Day'], var_name='Status', value_name='Count')
            fig = px.bar(df_melted, x='Day', y='Count', color='Status', barmode='stack',
                        labels={'Count': 'Number of Employees', 'Day': 'Day of January'},
                        title='Attendance Status Throughout January',
                        color_discrete_map={'Late': 'gray', 'Absent': 'red', 'On Time': 'green', 'Dayoff': 'blue'})

            fig.update_layout(height=600, width=760)
            st.plotly_chart(fig)
            #-----------------------------------------------------------------------------------------------------------------#
            attendance_summary = {'January': [], 'Absents': [], 'Lates': [], 'Ontime': []}
            
            
            for day in range(1, 32):
                absents = []
                lates = []
                ontime = []
                dayoff = []

                for index in range(len(dataset['name'])):
                    if dataset[f'jan{day}'][index] == 'A':
                        absents.append(dataset['name'][index])
                    elif dataset[f'jan{day}'][index] == 'L':
                        lates.append(dataset['name'][index])
                    elif dataset[f'jan{day}'][index] == 'O':
                        ontime.append(dataset['name'][index])


            
                attendance_summary['January'].append(day)
                attendance_summary['Absents'].append(', '.join(absents))
                attendance_summary['Lates'].append(', '.join(lates))
                attendance_summary['Ontime'].append(', '.join(ontime))
            

            
            result_df = pd.DataFrame(attendance_summary)

            
            with st.expander("Show Attendance Summary From January 1-31"):
                st.dataframe(result_df, height=1100, width=1500)
                
            
            attendance_summary = {'January': [], 'Dayoff': []}

            
            for day in range(1, 32):
                
                dayoff = []

                for index in range(len(dataset['name'])):
                    if dataset[f'jan{day}'][index] == 'D':
                        dayoff.append(dataset['name'][index])

                attendance_summary['January'].append(day)
                attendance_summary['Dayoff'].append(', '.join(dayoff))

            
            result_df_dayoff = pd.DataFrame(attendance_summary)

            with st.expander("Show Day-offs Summary from Jan 1-31"):
                st.dataframe(result_df_dayoff, height=1150, width=700)
            #-----------------------------------------------------------------------------------#
            # Define the late threshold in minutes (08:01 AM)
            late_threshold_minutes = 8 * 60 

            # Function to convert time string to minutes since midnight
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

            # Convert lateness from minutes to hours and minutes
            late_df['Hours'] = late_df['Lateness'] // 60
            late_df['Minutes'] = late_df['Lateness'] % 60
            late_df.drop(columns=['Lateness'], inplace=True)

            # sort dataframe
            late_df['January'] = late_df['January'].str.extract(r'(\d+)').astype(int)
            late_df = late_df.sort_values(by='January')

            with st.expander("Show Lateness Records"):
                st.dataframe(late_df, height=600, width=1000)
            #---------------------------------------------------------------------------------------------------------#    
                
                
                
        def febuary(dataset_feb, feb_late):
            
            def count_occurrences(row):
                late_count = (row == "L").sum()
                absent_count = (row == "A").sum()
                on_time_count = (row == "O").sum()
                return late_count, absent_count, on_time_count

            counts = dataset_feb.set_index('name').apply(count_occurrences, axis=1)

            dataset_feb["Late"], dataset_feb["Absent"], dataset_feb["On Time"] = zip(*counts)

            most_late_employee = dataset_feb.loc[dataset_feb["Late"].idxmax(), "name"]
            most_late_count = dataset_feb["Late"].max()

            most_absent_employee = dataset_feb.loc[dataset_feb["Absent"].idxmax(), "name"]
            most_absent_count = dataset_feb["Absent"].max()

            most_on_time_employee = dataset_feb.loc[dataset_feb["On Time"].idxmax(), "name"]
            most_on_time_count = dataset_feb["On Time"].max()
            col1, col2, col3 = st.columns(3)

            most_late_count_str = str(most_late_count)
            most_absent_count_str = str(most_absent_count)
            most_on_time_count_str = str(most_on_time_count)

            col2.metric("Employee With Most Late", most_late_employee, most_late_count_str, delta_color='off')
            col3.metric("Employee with Most Absences", most_absent_employee, most_absent_count_str, delta_color="inverse")
            col1.metric("Employee with Most On-time", most_on_time_employee, most_on_time_count_str)
            
            #--------------------------------------------------------------------------------------------------------------------------#
            def visualize(row):
                late_count = (row == "L").sum()
                absent_count = (row == "A").sum()
                on_time_count = (row == "O").sum()
                dayoff_count = (row == "D").sum()
                return late_count, absent_count, on_time_count, dayoff_count

            # storecountts
            late_counts = []
            absent_counts = []
            on_time_counts = []
            dayoff_counts = []

            for day in range(1, 30):
                row = dataset_feb[f'feb{day}']
                late_count, absent_count, on_time_count, dayoff_count = visualize(row)
                # Append counts to the lists
                late_counts.append(late_count)
                absent_counts.append(absent_count)
                on_time_counts.append(on_time_count)
                dayoff_counts.append(dayoff_count)

            df = pd.DataFrame({'Day': range(1, 30),
                            'Late': late_counts,
                            'Absent': absent_counts,
                            'On Time': on_time_counts,
                            'Dayoff': dayoff_counts})

            df_melted = pd.melt(df, id_vars=['Day'], var_name='Status', value_name='Count')

            fig = px.bar(df_melted, x='Day', y='Count', color='Status', barmode='stack',
                        labels={'Count': 'Number of Employees', 'Day': 'Day of Febuary'},
                        title='Attendance Status Throughout febuary',
                        color_discrete_map={'Late': 'gray', 'Absent': 'red', 'On Time': 'green', 'Dayoff': 'blue'})

            fig.update_layout(height=600, width=760)

            st.plotly_chart(fig)
            
        #------------------------------------------------------------------------------------------------------#
            attendance_summary = {'Febuary': [], 'Absents': [], 'Lates': [], 'Ontime': []}

            for day in range(1, 30):
                absents = []
                lates = []
                ontime = []
                dayoff = []

                for index in range(len(dataset['name'])):
                    if dataset_feb[f'feb{day}'][index] == 'A':
                        absents.append(dataset_feb['name'][index])
                    elif dataset_feb[f'feb{day}'][index] == 'L':
                        lates.append(dataset_feb['name'][index])
                    elif dataset_feb[f'feb{day}'][index] == 'O':
                        ontime.append(dataset_feb['name'][index])


                attendance_summary['Febuary'].append(day)
                attendance_summary['Absents'].append(', '.join(absents))
                attendance_summary['Lates'].append(', '.join(lates))
                attendance_summary['Ontime'].append(', '.join(ontime))
            

            result_df = pd.DataFrame(attendance_summary)
            with st.expander("Show Attendance Summary From Feb 1-29"):
                st.dataframe(result_df, height=1100, width=1500)
                
            attendance_summary = {'Febuary': [], 'Dayoff': []}


            for day in range(1, 30):
                dayoff = []

                for index in range(len(dataset_feb['name'])):
                    if dataset_feb[f'feb{day}'][index] == 'D':
                        dayoff.append(dataset_feb['name'][index])

                
                attendance_summary['Febuary'].append(day)
                attendance_summary['Dayoff'].append(', '.join(dayoff))

            result_df_dayoff = pd.DataFrame(attendance_summary)
            
            with st.expander("Show Day-offs Summary from Feb 1-29"):
                st.dataframe(result_df_dayoff, height=1150, width=700)
            # define the late threshold in minutes 08:01 AM
            #--------------------------------------------------------------------------#
            # define the late threshold in minutes 08:01 AM
            late_threshold_minutes = 8 * 60

            #convert time string to minutes since midnight
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

            for index, row in feb_late.iterrows():
                name = row['name']
                for day, time in row.items():
                    if day != 'name':
                        minutes = time_to_minutes(time)
                        lateness = calculate_lateness(minutes)
                        if lateness is not None:
                            late_records.append((day, name, lateness))

            late_df = pd.DataFrame(late_records, columns=['Febuary', 'Name', 'Lateness'])

            late_df['Hours'] = late_df['Lateness'] // 60
            late_df['Minutes'] = late_df['Lateness'] % 60
            late_df.drop(columns=['Lateness'], inplace=True)

            late_df['Febuary'] = late_df['Febuary'].str.extract(r'(\d+)').astype(int)
            late_df = late_df.sort_values(by='Febuary')

            with st.expander("Show Lateness Records"):
                st.dataframe(late_df, height=600, width=1000)
            
        #------------------------------------------------------------------------------------------------------------#
        
        def march(dataset_feb):
            st.write("No stored Data")



        option = st.selectbox(
            'Select MOnth:',
            ('January', 'Febuary', 'March')
        )

        if option == 'January':
            january(dataset, jan_late)
        elif option == "Febuary":
            febuary(dataset_feb, feb_late)
        elif option == "March":
            march(dataset)
    

        
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()            
main()