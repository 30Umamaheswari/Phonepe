# # to check tables are stored in sqlite3 db
# import sqlite3
#
# db_path = "C:\\Users\\visha\\Desktop\\SQLite3\\phonepe.db"
# conn = sqlite3.connect(db_path)
#
# query = "SELECT name FROM sqlite_master WHERE type='table';"
#
# # Execute the query
# cursor = conn.execute(query)
#
# # Fetch all the table names
# table_names = cursor.fetchall()
#
# # Close the cursor
# cursor.close()
#
# print("Tables in the database:")
# for table in table_names:
#     print(table[0])
# conn.close()
import sqlite3

import pandas as pd
import streamlit as st
from matplotlib import cm
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns


st.set_page_config(
    page_title="Phonepe Plus",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define the background image URL
background_image_url = "https://images.unsplash.com/photo-1638272181967-7d3772a91265?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80"

# Use CSS to set the background image
page_bg_img = f"""
<style>
[data-testid="stSidebar"] {{
    background-color: rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
}}
[data-testid="stAppViewContainer"] {{
    background-image: url("{background_image_url}");
    background-size: cover;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

st.title('Phonepe Plus Data Visualization')

with st.sidebar:
    select = option_menu('Menu', ["Home", "Aggregation data", "Map data", "Top data"],
                         default_index=0,
                         orientation="vertical",
                         styles={"nav-link": {"font-size": "15px", "text-align": "left",
                                              "margin": "0px", "--hover-color": "#BCADD0"}})

db_path = "C:\\Users\\visha\\Desktop\\SQLite3\\phonepe.db"
conn = sqlite3.connect(db_path)

if select == "Home":
    url = 'phonepe.jpeg'
    st.image(url)


if select == "Aggregation data":
    tab1, tab2 = st.tabs(["$\small TRANSACTION $", "$\small USERS $"])
    query = "SELECT * FROM aggregated_transaction;"
    df_agg_trans = pd.read_sql_query(query, conn)
    with tab1:
        st.write('Aggregation transaction data details are shown here for your visualization')
        col1, col2 = st.columns(2)


        selected_year = col1.selectbox("Select Year", df_agg_trans['Year'].unique())
        selected_state = col2.selectbox("Select State", df_agg_trans['State'].unique())
        selected_quarter = col1.selectbox("Select Quarter", df_agg_trans['Quarter'].unique())

        # Filter the data based on user selection
        filtered_df = df_agg_trans[(df_agg_trans['Year'] == selected_year) & (df_agg_trans["Quarter"] == selected_quarter) & (df_agg_trans['State'] == selected_state)]
        x = filtered_df['Transaction_type']

        tick_positions = range(len(filtered_df))

        # Plot the filtered data
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.patch.set_alpha(0.3)
        sns.set(rc={'axes.facecolor': '.9', 'figure.facecolor': (169/255, 169/255, 169/255, 0)})


        plt.grid(False, linestyle='-', alpha=0.3)

        colr = ['#FFFF66', '#FFCC00', '#FFD700', '#FFA500', '#FF9900']

        plt.bar(x, filtered_df['Transaction_count'],log=True, color=colr)
        plt.xlabel('Transaction Type', size=15, color='indianred')
        plt.ylabel('Transaction Count', size=15, color='indianred')
        plt.title(f'Transaction Count for each transaction type in {selected_year}', size=20, color='darkred')
        plt.xticks(rotation=45, ha='right',size=10, color='dimgrey')
        plt.yticks(size=10, color='dimgrey')
        plt.ylim(filtered_df['Transaction_count'].min(), filtered_df['Transaction_count'].max())
        col1.pyplot(plt)

        y = filtered_df['Transaction_amount']
        colo1 = ['#7EB26D', '#E6AC27', '#717CA6', '#A6ACAF', '#1F8A70']

        plt.bar(x, y, color=colo1)
        plt.xlabel('Transaction Type', size=15, color='crimson')
        plt.ylabel('Transaction Amount', size=15, color='crimson')
        plt.title(f'Transaction Amount for each transaction type in {selected_year}', size=20, color='darksalmon')
        plt.ylim(y.min(), y.max())
        plt.xticks(rotation=45, ha='right', size=10, color='dimgrey')
        plt.yticks(size=10, color='dimgrey')
        col2.pyplot(plt)

        filtered_df = df_agg_trans[
            (df_agg_trans['Year'] == selected_year) & (df_agg_trans["Quarter"] == selected_quarter)]

        # Get top 10 transaction amounts and counts based on state
        top_10_amounts = filtered_df.groupby("State")["Transaction_amount"].sum().nlargest(10)
        top_10_counts = filtered_df.groupby("State")["Transaction_count"].sum().nlargest(10)

        # Create expanders for top 10 transaction amounts and counts
        with col1.expander(f"Top 10 Transaction Amounts by State in {selected_year} - Q{selected_quarter}"):
            st.bar_chart(top_10_amounts)
            st.write("Top 10 Transaction Amounts Table:")
            st.dataframe(filtered_df.loc[filtered_df['State'].isin(top_10_amounts.index)][
                             ['State', 'Transaction_amount']].sort_values(by='Transaction_amount', ascending=True))

        selected_transaction_type = col2.selectbox("Select Transaction Type", df_agg_trans['Transaction_type'].unique())

        # Filter the data based on user selection
        filtered_df = df_agg_trans[df_agg_trans['Transaction_type'] == selected_transaction_type]

        # Get the top 5 states based on transaction count
        top_5_states = filtered_df.groupby("State")["Transaction_amount"].sum().nlargest(5)

        # Create an expander to show the bar graph
        with col2.expander(f"Top 5 States for Transaction Type '{selected_transaction_type}'"):
            colo = ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f']

            plt.figure(figsize=(8, 6))
            plt.bar(top_5_states.index, top_5_states.values, color=colo)
            plt.xlabel('State', color='palegoldenrod',size=10)
            plt.ylabel('Total Transaction Amount', color='palegoldenrod',size=10)
            plt.title(f'Top 5 States for Transaction Type "{selected_transaction_type}"', color='darkgoldenrod',size=20)
            plt.xticks(rotation=30, ha='right', size=10, color='dimgrey')
            plt.yticks(size=10, color='dimgrey')
            st.pyplot(plt)

    with tab2:
        query = "SELECT * FROM aggregated_user;"
        df_ag_user = pd.read_sql_query(query, conn)
        df_agg_user = pd.read_csv("C:\\Users\\visha\\Desktop\\Projects\\Phonepe-Pluse\\Data\\aggregated_user.csv")
        # df_agg_user = df_ag_user.drop_duplicates()
        # st.table(df_agg_user)

        st.markdown(":white[Plots for Aggregation Users]")

        selected_state = st.selectbox("Select State", df_agg_user['State'].unique(), key='state')
        quart = st.radio("Select Quarter", [1, 2, 3, 4])
        col1, col2 = st.columns(2)
        year = [2018, 2019, 2020, 2021, 2022, 2023]

        filtered_df = df_agg_user[(df_agg_user['Quarter'] == selected_quarter) & (df_agg_user['State'] == selected_state)]

        # Plot scatter plot based on user input
        sns.set(rc={'axes.facecolor': '.9', 'figure.facecolor': (169/255, 169/255, 169/255, 0)})

        plt.figure(figsize=(10, 6))
        plt.scatter(filtered_df['Year'], filtered_df['registeredUser'], color='crimson', marker='o',s=100)
        plt.title(f'Registered Users Scatter Plot (Quarter {quart}, State {selected_state})', color='tomato',size=20)
        plt.xlabel('Year', color='chocolate',size=10)
        plt.ylabel('Registered Users', color='chocolate',size=10)
        plt.xticks(size=10, color='dimgrey')
        plt.yticks(size=10, color='dimgrey')
        plt.tight_layout()

        # Display the plot using Streamlit
        col1.pyplot(plt)

        plt.figure(figsize=(10, 6))
        plt.scatter(filtered_df['Year'], filtered_df['appOpens'], color='goldenrod', marker='o',s=100)
        plt.title(f'App Opens Scatter Plot (Quarter {quart}, State {selected_state})', color='saddlebrown',size=20)
        plt.xlabel('Year', color='sienna',size=10)
        plt.ylabel('Registered Users', color='sienna',size=10)
        plt.xticks(size=10, color='dimgrey')
        plt.yticks(size=10, color='dimgrey')
        plt.tight_layout()
        col2.pyplot(plt)

        query = "SELECT * FROM users_mobilebrand;"
        df_user_mobile = pd.read_sql_query(query, conn)

        st.title("Bar Chart for Brand and Count")
        selected_year = st.selectbox("Select Year", df_user_mobile['Year'].unique())
        selected_state = st.selectbox("Select State", df_user_mobile['State'].unique(), key='k')

        # Filter dataframe based on user selections
        filtered_df = df_user_mobile[(df_user_mobile['Year'] == selected_year) & (df_user_mobile['State'] == selected_state) & (df_user_mobile['Quarter'] == 4)]


        # Create a bar chart for brand distribution
        col = ['#ff7f0e', '#2ca02c', '#d62728', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#1E90FF',
                  '#FF1493', '#FFD700']

        plt.figure(figsize=(8, 6))
        plt.bar(filtered_df['Brand'], filtered_df['Count'], color=col)
        plt.title(f'Brand Distribution for {selected_state} in {selected_year} (Q4)', color='seagreen',size=20)
        plt.xlabel('Brand', color='lightseagreen',size=10)
        plt.ylabel('Count', color='lightseagreen',size=10)
        plt.xticks(rotation=30, ha='right')
        plt.xticks(size=10, color='dimgrey')
        plt.yticks(size=10, color='dimgrey')
        plt.tight_layout()

        # Display the bar chart using Streamlit
        st.pyplot(plt)

if select == 'Top data':
    query = "SELECT * FROM top_transaction;"
    df_top_trans = pd.read_sql_query(query, conn)
    # st.table(df_top_trans)

    query = "SELECT * FROM top_user;"
    df_top_user = pd.read_sql_query(query, conn)

    st.write("")
    v = st.radio('Choose type', ['Transaction', 'User'])
    if v == 'Transaction':
        filtered_df = df_top_trans[df_top_trans['Entity_Type'] == 'District']

        st.title("Pie Chart based on Districts for Amount and Count")
        selected_state = st.selectbox("Select State", filtered_df['State'].unique())
        selected_year = st.selectbox("Select Year", filtered_df['Year'].unique())
        selected_quarter = st.selectbox("Select Quarter", filtered_df['Quarter'].unique())

        col3, col4 = st.columns(2)
        # Filter dataframe based on user selections
        filtered_df1 = filtered_df[
            (filtered_df['State'] == selected_state) &
            (filtered_df['Year'] == selected_year) &
            (filtered_df['Quarter'] == selected_quarter) &
            (filtered_df['Entity_Type'] == 'District')
            ]

        # Create a pie chart for district count
        colors = ['darkgoldenrod', 'gold', 'orange', 'goldenrod', 'lightgoldenrodyellow', 'wheat',
                  'tan', 'navajowhite', 'darkkhaki', 'oldlace', 'peru']  # Define colors

        plt.figure(figsize=(8, 8))
        plt.pie(filtered_df1['Count'], autopct='%1.1f%%', colors=colors)
        plt.title(f'District Count Distribution in {selected_state} ({selected_year}, Quarter {selected_quarter})', color='firebrick',size=19)
        plt.legend(title="Districts", labels=filtered_df1['Entity_Name'], loc="center left", bbox_to_anchor=(1, 0.5))

        # Display the pie chart using Streamlit
        col3.pyplot(plt)

        colors = ['darkslategrey', 'paleturquoise', 'mediumturquoise', 'aquamarine', 'cadetblue', 'cyan',
                  'mediumaquamarine', 'navajowhite', 'darkkhaki', 'oldlace', 'peru']  # Define colors

        plt.figure(figsize=(8, 8))
        plt.pie(filtered_df1['Amount'], autopct='%1.1f%%', colors=colors)
        plt.title(f'District Amount Distribution in {selected_state} ({selected_year}, Quarter {selected_quarter})', color='maroon',size=19)
        plt.legend(title="Districts", labels=filtered_df1['Entity_Name'], loc="center left", bbox_to_anchor=(1, 0.5))

        # Display the pie chart using Streamlit
        col4.pyplot(plt)

        # grouped_df = filtered_df.groupby(['Year', 'Entity_Name'], as_index=False)['Count'].sum()
        #
        # st.title("Top Districts by Count")
        # selected_year = st.selectbox("Select Year", grouped_df['Year'].unique())
        #
        # # Filter grouped dataframe based on user-selected year
        # filtered_df2 = grouped_df[grouped_df['Year'] == selected_year]
        #
        # # Sort filtered dataframe by 'Count' in descending order and display in table form
        # sorted_df = filtered_df2.sort_values(by='Count', ascending=False).head(5)
        # st.write("Top Districts:")
        # st.table(sorted_df[['Entity_Name', 'Count']])

        grouped_df = filtered_df.groupby(['Year', 'Entity_Name'], as_index=False)['Amount'].sum()

        # Streamlit UI components
        st.title("Top Districts by Amount")
        selected_year = st.selectbox("Select Year", grouped_df['Year'].unique(), key='m')

        # Filter grouped dataframe based on user-selected year
        filtered_df2 = grouped_df[grouped_df['Year'] == selected_year]

        # Sort filtered dataframe by 'Count' in descending order and display in table form
        sorted_df = filtered_df2.sort_values(by='Amount', ascending=False).head(5)
        st.write("Top Districts:")
        st.table(sorted_df[['Entity_Name', 'Amount']])

        # Pincode
        filtered_df = df_top_trans[df_top_trans['Entity_Type'] == 'Pincode']

        st.title("Pie Chart based on Pincode for Amount and Count")

        col3, col4 = st.columns(2)
        # Filter dataframe based on user selections
        filtere_df1 = filtered_df[
            (filtered_df['State'] == selected_state) &
            (filtered_df['Year'] == selected_year) &
            (filtered_df['Quarter'] == selected_quarter) &
            (filtered_df['Entity_Type'] == 'Pincode')
            ]

        # Create a pie chart for pincode count
        colors = ['lightpink', 'crimson', 'rosybrown', 'pink', 'hotpink', 'orchid',
                  'tan', 'navajowhite', 'darkkhaki', 'darksalmon', 'bisque']  # Define colors

        plt.figure(figsize=(8, 8))
        plt.pie(filtere_df1['Count'], autopct='%1.1f%%', colors=colors)
        plt.title(f'Pincode Count Distribution in {selected_state} ({selected_year}, Quarter {selected_quarter})', color='firebrick',size=19)
        plt.legend(title="Pincodes", labels=filtere_df1['Entity_Name'], loc="center left", bbox_to_anchor=(1, 0.5))

        # Display the pie chart using Streamlit
        col3.pyplot(plt)

        grouped_df = filtered_df.groupby(['Year', 'Entity_Name'], as_index=False)['Amount'].sum()

        st.title("Top Districts by Amount")
        selected_year = st.selectbox("Select Year", grouped_df['Year'].unique(), key='b')

        # Filter grouped dataframe based on user-selected year
        filtered_df2 = grouped_df[grouped_df['Year'] == selected_year]

        # top 5 districts
        sorted_df = filtered_df2.sort_values(by='Amount', ascending=False).head(5)
        st.write("Top Districts:")
        st.table(sorted_df[['Entity_Name', 'Amount']])

    if v == 'User':
        vl = df_top_user[df_top_user['Entity_Type'] == 'District']

        st.title("Pie Chart based on Districts")
        selected_state = st.selectbox("Select State", vl['State'].unique())
        selected_year = st.selectbox("Select Year", vl['Year'].unique())
        selected_quarter = st.selectbox("Select Quarter", vl['Quarter'].unique())

        col5, col6 = st.columns(2)
        # Filter dataframe based on user selections
        l = vl[
            (vl['State'] == selected_state) &
            (vl['Year'] == selected_year) &
            (vl['Quarter'] == selected_quarter) &
            (vl['Entity_Type'] == 'District')
            ]

        # Create a pie chart for district count
        sns.set_palette("pastel")

        plt.figure(figsize=(8, 8))
        plt.pie(l['registeredUser'], autopct='%1.1f%%')
        plt.title(f'District RegisteredUser Distribution in {selected_state} ({selected_year}, Quarter {selected_quarter})', color='olive',size=19)
        plt.legend(title="Districts", labels=l['Entity_Name'], loc="center left", bbox_to_anchor=(1, 0.5))

        # Display the pie chart using Streamlit
        col5.pyplot(plt)

        grouped_df = vl.groupby(['Year', 'Entity_Name'], as_index=False)['registeredUser'].sum()

        col6.title("Top Districts by Registered User")
        selected_year = col6.selectbox("Select Year", grouped_df['Year'].unique(), key='b')

        # Filter grouped dataframe based on user-selected year
        filtered_df2 = grouped_df[grouped_df['Year'] == selected_year]

        # top 5 registered user by districts
        sorted_df = filtered_df2.sort_values(by='registeredUser', ascending=False).head(5)
        col6.table(sorted_df[['Entity_Name', 'registeredUser']])

        vv = df_top_user[df_top_user['Entity_Type'] == 'Pincode']

        st.title("Pie Chart based on Pincodes")

        col7, col8 = st.columns(2)
        # Filter dataframe based on user selections
        u = vv[
            (vv['State'] == selected_state) &
            (vv['Year'] == selected_year) &
            (vv['Quarter'] == selected_quarter) &
            (vv['Entity_Type'] == 'Pincode')
            ]

        # Create a pie chart for district count
        sns.set_palette("deep")
        sns.set(rc={'axes.facecolor': '.9', 'figure.facecolor': (0, 0, 0, 0)})

        plt.figure(figsize=(8, 8))
        plt.pie(u['registeredUser'], autopct='%1.1f%%')
        plt.title(f'Pincode RegisteredUser Distribution in {selected_state} ({selected_year}, Quarter {selected_quarter})', color='darkolivegreen', size=19)
        plt.legend(title="Pincodes", labels=u['Entity_Name'], loc="center left", bbox_to_anchor=(1, 0.5))

        # Display the pie chart using Streamlit
        col7.pyplot(plt)

        # group by pincode
        grouped_df = vv.groupby(['Year', 'Entity_Name'], as_index=False)['registeredUser'].sum()

        col8.title("Top area of Pincode by Registered User")
        selected_year = col8.selectbox("Select Year", grouped_df['Year'].unique(), key='c')

        # Filter grouped dataframe based on user-selected year
        filtered_df2 = grouped_df[grouped_df['Year'] == selected_year]

        # top 5 registered user
        sorted_df = filtered_df2.sort_values(by='registeredUser', ascending=False).head(5)
        col8.table(sorted_df[['Entity_Name', 'registeredUser']])

# map_data
if select == 'Map data':

    query = "SELECT * FROM map_transaction;"
    df_map_trans = pd.read_sql_query(query, conn)

    lat = [10.0001051, 15.9240905, 28.0937702, 26.4073841, 25.6440845, 30.72984395, 21.6637359,
           20.7181749499999, 28.6517178, 15.3004543, 22.3850051, 29, 31.81676015, 32.7185614, 23.4559809,
           14.5203896, 10.3528744, 33.9456407, 10.8132489, 23.8143419, 18.9068356, 24.7208818, 25.5379432,
           23.2146169, 26.1630556, 20.5431241, 10.91564885, 30.9293211, 26.8105777, 27.601029, 10.9094334,
           17.8495919, 23.7750823, 27.1303344, 30.0417376, 22.9964948]

    log = [93.0000194, 80.1863809, 94.5921326, 93.2551303, 85.906508, 76.7841456701605, 81.8406351,
           70.9323834101063, 77.2219388, 74.0855134, 71.745261, 76, 77.3493205196885, 74.8580917, 85.2557301,
           75.7223521, 76.5120396, 77.6568576, 73.6804620941119, 77.5340719, 75.6741579, 93.9229386, 91.2999102,
           92.8687612, 94.5884911, 84.6897321, 79.8069487984423, 75.5004841, 73.7684549, 88.4541363868014,
           78.3665347, 79.1151663, 91.7025091, 80.859666, 79.089691, 87.6855882]

    uv = st.radio("Select type", ["Transaction", "User"])

    # map view for map_transaction
    if uv == "Transaction":
        c1, c2 = st.columns([0.7,0.3], gap='large')
        y = c1.select_slider('Slide Year', options=[2018, 2019, 2020, 2021, 2022, 2023])
        qua = c2.select_slider('Select Quarter', options=[1, 2, 3, 4])

        c1.markdown("## :white[Overall State Data - Transactions Amount]")

        # find total for count and amount
        filt_df = df_map_trans.groupby('State').agg({
            'Count': 'sum',
            'amount': 'sum'
        }).reset_index()

        # Rename columns
        filt_df.rename(columns={'Count': 'Total_transaction', 'amount': 'Total_amount'}, inplace=True)

        # Create a DataFrame with lat, lon, and state
        lat_lon_df = pd.DataFrame({'Latitude': lat, 'Longitude': log, 'State': filt_df['State']})

        # Merge with filt_df based on 'State'
        merged_df = filt_df.merge(lat_lon_df, on='State')

        # Create Geo Plot using Plotly Express
        sns.set(rc={'axes.facecolor': '#0000FF', 'figure.facecolor': (0, 0, 0, 0)})

        fig = px.scatter_geo(
            merged_df,
            lat='Latitude',
            lon='Longitude',
            hover_name='State',
            size='Total_transaction',  # Size of marker based on total transactions
            color='Total_amount',  # Color of marker based on total amount
            scope='asia',
            title=f'Total Transactions and Amount by State ({y}, Quarter {qua})'
        )

        # Show the Geo Plot using Streamlit
        c1.plotly_chart(fig)

        # top 5 states for total transaction amount
        top_states_5 = filt_df.nlargest(5, 'Total_transaction')
        c2.write('Top 5 States - Transaction Amount')
        c2.table(top_states_5[['State', 'Total_transaction', 'Total_amount']])

    # map view for map user
    if uv == 'User':
        query = "SELECT * FROM map_user;"
        df_map_user = pd.read_sql_query(query, conn)

        c1, c2 = st.columns(2, gap='large')
        y = c1.select_slider('Slide Year', options=[2018, 2019, 2020, 2021, 2022, 2023])
        qua = c2.select_slider('Select Quarter', options=[1, 2, 3, 4])

        c1.markdown("## :white[Overall State Data - Registered User]")

        # find total for registered user and app opens
        fil_df = df_map_user.groupby('State').agg({
            'registerUser': 'sum',
            'appOnes': 'sum'
        }).reset_index()

        # Rename columns
        fil_df.rename(columns={'registerUser': 'Total_registeredUsers', 'appOnes': 'Total_appOpens'}, inplace=True)

        # Create a DataFrame with lat, lon, and state
        lat_lon_df = pd.DataFrame({'Latitude': lat, 'Longitude': log, 'State': fil_df['State']})

        # Merge with fil_df based on 'State'
        merged_df = fil_df.merge(lat_lon_df, on='State')

        # Create Geo Plot using Plotly Express

        fig = px.scatter_geo(
            merged_df,
            lat='Latitude',
            lon='Longitude',
            hover_name='State',
            size='Total_registeredUsers',
            color='Total_appOpens',
            scope='asia',
            title=f'Total Registered Users by State ({y}, Quarter {qua})'
        )

        # Show the Geo Plot
        c1.plotly_chart(fig)

        # top 5 states based on registered user
        top_state_5 = fil_df.nlargest(5, 'Total_registeredUsers')
        c2.write('Top 5 States - Registered Users')
        c2.table(top_state_5[['State', 'Total_registeredUsers', 'Total_appOpens']])


