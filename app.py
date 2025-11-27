import streamlit as st
import pandas as pd
import plotly.express as px

#######
# Page Config
#######
st.set_page_config(
    page_title="Customer Purchase Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

#######
# Title and Description
#######
st.title("Customer Purchase Analytics Dashboard")

def load_sample_data():
    return pd.read_csv('shopping_behavior.csv')

# Load data
df = load_sample_data()

# Create a state abbreviation mapping for the map
state_abbreviations = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
    'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# Add state codes to the dataframe
df['State_Code'] = df['Location'].map(state_abbreviations)

# Sidebar filters
st.sidebar.header("Filters")

# Custom multiselect function with "All" option
def multiselect_with_all(label, options, default_selection=["All"]):
    # Add "All" option to the beginning
    all_options = ["All"] + list(options)
    
    selected = st.sidebar.multiselect(
        label,
        options=all_options,
        default=default_selection
    )
    
    # If "All" is selected, return all options (excluding "All")
    if "All" in selected:
        return list(options)
    else:
        return selected

# Gender filter - Only "All" as default
gender_filter = multiselect_with_all(
    "Select Gender:",
    options=df['Gender'].unique(),
    default_selection=["All"]
)

# Season filter - Only "All" as default
season_filter = multiselect_with_all(
    "Select Season:",
    options=df['Season'].unique(),
    default_selection=["All"]
)

# Location filter - Only "All" as default
location_filter = multiselect_with_all(
    "Select Location:",
    options=df['Location'].unique(),
    default_selection=["All"]
)

# Apply filters
filtered_df = df[
    (df['Gender'].isin(gender_filter)) &
    (df['Season'].isin(season_filter)) &
    (df['Location'].isin(location_filter))
]

# Display active filters
st.sidebar.markdown("---")
st.sidebar.write(f"**Records:** {len(filtered_df)} of {len(df)}")

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['Purchase Amount (USD)'].sum()
    st.metric("Total Sales", f"${total_sales:,.0f}")

with col2:
    avg_purchase = filtered_df['Purchase Amount (USD)'].mean()
    st.metric("Average Purchase", f"${avg_purchase:.2f}")

with col3:
    total_customers = filtered_df['Customer ID'].nunique()
    st.metric("Total Customers", total_customers)

with col4:
    avg_rating = filtered_df['Review Rating'].mean()
    st.metric("Average Rating", f"{avg_rating:.1f}/5")

# Row 1: Seasonal Analysis and Payment Methods
col1, col2 = st.columns(2)

with col1:
    # Sales by Season
    season_sales = filtered_df.groupby('Season')['Purchase Amount (USD)'].sum().reset_index()
    fig1 = px.pie(
        season_sales,
        values='Purchase Amount (USD)',
        names='Season',
        title='Sales Distribution by Season',
        hole=0.4
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("""
    **Insight:** The donut chart reveals seasonal purchasing patterns. 
    Identify which seasons drive the highest revenue for strategic planning.
    """)

with col2:
    # Payment Method Analysis
    payment_distribution = filtered_df['Payment Method'].value_counts().reset_index()
    payment_distribution.columns = ['Payment Method', 'Count']
    
    fig2 = px.bar(
        payment_distribution,
        x='Payment Method',
        y='Count',
        title='Payment Method Distribution',
        color='Payment Method',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
    **Insight:** Bar chart showing customer preferences for payment methods. 
    Useful for optimizing payment processing and customer experience.
    """)

# Row 2: USA Map (Full Width)
st.subheader("Geographic Distribution")
# USA Map - Sales by State
state_sales = filtered_df.groupby(['Location', 'State_Code'])['Purchase Amount (USD)'].agg(['sum', 'count']).reset_index()
state_sales.columns = ['Location', 'State_Code', 'Total_Sales', 'Customer_Count']

fig_map = px.choropleth(
    state_sales,
    locations='State_Code',
    locationmode='USA-states',
    color='Total_Sales',
    scope='usa',
    title='USA Sales Distribution by State',
    color_continuous_scale='Blues',
    hover_data=['Location', 'Total_Sales', 'Customer_Count'],
    labels={'Total_Sales': 'Total Sales ($)', 'Customer_Count': 'Number of Customers'}
)

fig_map.update_layout(
    geo=dict(
        lakecolor='rgb(255, 255, 255)',
        landcolor='rgb(217, 217, 217)',
    ),
    height=500
)

st.plotly_chart(fig_map, use_container_width=True)

st.markdown("""
**Insight:** The choropleth map shows sales distribution across US states. 
Darker shades indicate higher sales volumes. Hover over states to see exact numbers and customer counts.
""")

# Row 3: Top Locations and Customer Distribution
col3, col4 = st.columns(2)

with col3:
    # Top Locations by Sales
    location_sales = filtered_df.groupby('Location')['Purchase Amount (USD)'].sum().nlargest(6).reset_index()
    fig3 = px.bar(
        location_sales,
        x='Purchase Amount (USD)',
        y='Location',
        orientation='h',
        title='Top 6 Locations by Sales',
        color='Purchase Amount (USD)',
        color_continuous_scale='Viridis'
    )
    fig3.update_layout(
        xaxis_title="Total Sales (USD)",
        yaxis_title="Location"
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("""
    **Insight:** Horizontal bar chart highlighting top-performing locations. 
    Useful for identifying regional performance and targeting marketing efforts.
    """)

with col4:
    # Customer count by state
    state_customers = filtered_df.groupby(['Location', 'State_Code']).size().reset_index(name='Customer_Count')
    fig4 = px.bar(
        state_customers.nlargest(8, 'Customer_Count'),
        x='Customer_Count',
        y='Location',
        orientation='h',
        title='Top 8 States by Customer Count',
        color='Customer_Count',
        color_continuous_scale='Plasma'
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("""
    **Insight:** Shows states with the highest number of unique customers. 
    Compare with sales data to identify high-value customer regions.
    """)

# Row 4: Additional Analysis
col5, col6 = st.columns(2)

with col5:
    # Average purchase by payment method
    avg_by_payment = filtered_df.groupby('Payment Method')['Purchase Amount (USD)'].mean().reset_index()
    fig5 = px.bar(
        avg_by_payment,
        x='Payment Method',
        y='Purchase Amount (USD)',
        title='Average Purchase Amount by Payment Method',
        color='Payment Method',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig5.update_layout(
        yaxis_title="Average Purchase Amount (USD)"
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("""
    **Insight:** Compare average transaction values across different payment methods. 
    Higher averages may indicate customer preferences or payment limitations.
    """)

with col6:
    # Review Rating Distribution
    rating_distribution = filtered_df['Review Rating'].value_counts().sort_index().reset_index()
    rating_distribution.columns = ['Review Rating', 'Count']
    
    fig6 = px.bar(
        rating_distribution,
        x='Review Rating',
        y='Count',
        title='Customer Review Rating Distribution',
        color='Review Rating',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig6, use_container_width=True)
    
    st.markdown("""
    **Insight:** Distribution of customer review ratings. 
    Monitor customer satisfaction levels and identify areas for improvement.
    """)

# Additional Insights Section
st.header("Key Insights & Recommendations")

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.subheader("Patterns Discovered")
    st.markdown("""
    - **Seasonal Revenue Patterns**: Clear quarterly sales fluctuations and peak performance periods
    - **Geographic Concentration**: Regional sales hotspots and market penetration by state
    - **Payment Preferences**: Dominant payment methods and customer behavior trends
    - **Customer Distribution**: Geographic spread of customer base vs purchasing power
    - **Regional Performance**: Top-performing locations and underperforming markets
    - **Customer Satisfaction**: Review rating distribution and service quality indicators
    """)

with insight_col2:
    st.subheader("Business Recommendations")
    st.markdown("""
    - **Seasonal Optimization**: Align inventory and marketing with high-revenue quarters
    - **Regional Strategy**: Focus expansion efforts on high-potential geographic markets
    - **Payment System Enhancement**: Optimize support for customer-preferred payment methods
    - **Customer Acquisition**: Target regions with high customer density for loyalty programs
    - **Performance Benchmarking**: Apply successful strategies from top regions to underperformers
    - **Quality Improvement**: Address areas with lower review ratings to enhance customer experience
    - **Resource Allocation**: Direct marketing budgets to top-performing seasons and locations
    """)

# Data summary by location
with st.expander("Location Performance Summary"):
    location_summary = filtered_df.groupby('Location').agg({
        'Purchase Amount (USD)': ['sum', 'mean', 'count'],
        'Review Rating': 'mean',
        'Customer ID': 'nunique'
    }).round(2)
    location_summary.columns = ['Total Sales', 'Average Purchase', 'Transaction Count', 'Avg Rating', 'Unique Customers']
    location_summary = location_summary.sort_values('Total Sales', ascending=False)
    st.dataframe(location_summary, use_container_width=True)

with st.expander("View Filtered Data Table"):
    st.dataframe(filtered_df, use_container_width=True)