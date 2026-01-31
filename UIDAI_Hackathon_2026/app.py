
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ------------------------------------------------------------------------------
# 1. Page Configuration & Styling
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="UIDAI Stress Command Center",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# Custom Styling for "Modern" look (Preserving the dark/contrast theme users liked)
st.markdown("""
<style>
    .main-header {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #0E1117;
        text-align: center;
        padding: 1rem;
        border-bottom: 2px solid #FF4B4B;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stDataFrame {
        border-radius: 10px;
    }
    .warning-banner {
        background-color: #FF4B4B;
        color: white;
        padding: 0.75rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 2. Data Loading & Cleaning
# ------------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('final_uidai_data.csv')
    except FileNotFoundError:
        st.error("Critical Error: 'final_uidai_data.csv' not found in directory.")
        return None

    # 1. Dynamic Stress Calculation
    if 'total_stress_index' not in df.columns:
        df['total_stress_index'] = df.get('demo_update_ratio', 0) + df.get('bio_update_ratio', 0)

    # 2. Identify High Stress (Top 5%)
    if 'is_high_stress' not in df.columns:
        if not df['total_stress_index'].empty:
            threshold = df['total_stress_index'].quantile(0.95)
            df['is_high_stress'] = df['total_stress_index'] > threshold
        else:
            df['is_high_stress'] = False
            
    # Ensure month is datetime for trending
    if 'month' in df.columns:
        df['month_dt'] = pd.to_datetime(df['month'])
        
    return df

df = load_data()

if df is None:
    st.stop()

# ------------------------------------------------------------------------------
# 3. Sidebar Filters (NEW: Interactive Analytics)
# ------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/c/cf/Aadhaar_Logo.svg", width=150)
    st.header("🎛️ Analysis Controls")
    
    # State Filter
    all_states = sorted(df['state'].astype(str).unique().tolist())
    selected_state = st.selectbox("🌍 Filter by Region", ["All India"] + all_states)
    
    # Date Filter
    if 'month_dt' in df.columns:
        min_date = df['month_dt'].min()
        max_date = df['month_dt'].max()
        
        st.markdown("### 📅 Date Range")
        col1, col2 = st.columns(2)
        start_date = col1.date_input("Start", min_date, format="DD/MM/YYYY")
        end_date = col2.date_input("End", max_date, format="DD/MM/YYYY")
    
    st.markdown("---")
    st.info("💡 Adjust filters to drill down into specific regional stress patterns.")

# Applying Filters
df_filtered = df.copy()

# Date Filter Application
if 'month_dt' in df_filtered.columns:
    mask = (df_filtered['month_dt'].dt.date >= start_date) & (df_filtered['month_dt'].dt.date <= end_date)
    df_filtered = df_filtered.loc[mask]

# State Filter Application
if selected_state != "All India":
    df_filtered = df_filtered[df_filtered['state'] == selected_state]

# ------------------------------------------------------------------------------
# 4. Map Logic (Coordinates Dictionary)
# ------------------------------------------------------------------------------
STATE_COORDS = {
    "Andhra Pradesh": [15.9129, 79.7400],
    "Arunachal Pradesh": [28.2180, 94.7278],
    "Assam": [26.2006, 92.9376],
    "Bihar": [25.0961, 85.3131],
    "Chhattisgarh": [21.2787, 81.8661],
    "Goa": [15.2993, 74.1240],
    "Gujarat": [22.2587, 71.1924],
    "Haryana": [29.0588, 76.0856],
    "Himachal Pradesh": [31.1048, 77.1734],
    "Jharkhand": [23.6102, 85.2799],
    "Karnataka": [15.3173, 75.7139],
    "Kerala": [10.8505, 76.2711],
    "Madhya Pradesh": [22.9734, 78.6569],
    "Maharashtra": [19.7515, 75.7139],
    "Manipur": [24.6637, 93.9063],
    "Meghalaya": [25.4670, 91.3662],
    "Mizoram": [23.1645, 92.9376],
    "Nagaland": [26.1584, 94.5624],
    "Odisha": [20.9517, 85.0985],
    "Punjab": [31.1471, 75.3412],
    "Rajasthan": [27.0238, 74.2179],
    "Sikkim": [27.5330, 88.5122],
    "Tamil Nadu": [11.1271, 78.6569],
    "Telangana": [18.1124, 79.0193],
    "Tripura": [23.9408, 91.9882],
    "Uttar Pradesh": [26.8467, 80.9462],
    "Uttarakhand": [30.0668, 79.0193],
    "West Bengal": [22.9868, 87.8550],
    "Delhi": [28.7041, 77.1025],
    "Jammu and Kashmir": [33.7782, 76.5762],
    "Ladakh": [34.1526, 77.5770],
    "Chandigarh": [30.7333, 76.7794],
    "Puducherry": [11.9416, 79.8083],
    "Dadra and Nagar Haveli": [20.1809, 73.0169],
    "Daman and Diu": [20.4283, 72.8397],
    "Lakshadweep": [10.5667, 72.6417],
    "Andaman and Nicobar Islands": [11.7401, 92.6586],
    "The Dadra And Nagar Haveli And Daman And Diu": [20.4283, 72.8397]
}

def create_map_data(dframe):
    # Only map what is in the filtered view
    state_agg = dframe.groupby('state')['total_stress_index'].mean().reset_index()
    lat = []
    lon = []
    found_states = []
    stress_vals = []
    
    for _, row in state_agg.iterrows():
        s_name = row['state']
        coords = STATE_COORDS.get(s_name)
        if coords:
            found_states.append(s_name)
            lat.append(coords[0])
            lon.append(coords[1])
            stress_vals.append(row['total_stress_index'])
    
    return pd.DataFrame({
        'State': found_states,
        'lat': lat,
        'lon': lon,
        'Average Stress': stress_vals
    })

map_df = create_map_data(df) # We visualize the Full National Map for context, or you can switch to df_filtered to zoom

# ------------------------------------------------------------------------------
# 5. Header & Warning
# ------------------------------------------------------------------------------
title_prefix = f"{selected_state}" if selected_state != "All India" else "National"
st.markdown(f"<h1 class='main-header'>🇮🇳 UIDAI Identity Stress Monitoring System ({title_prefix})</h1>", unsafe_allow_html=True)

high_risk_districts = df_filtered[df_filtered['is_high_stress']]
if not high_risk_districts.empty:
    count = len(high_risk_districts)
    st.markdown(f"<div class='warning-banner'>⚠️ ALERT: {count} Districts Identified as High Risk in current view</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 6. Zone A: Key Metrics (Reactive)
# ------------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

# Calculate reactive metrics
avg_demo = df_filtered['demo_update_ratio'].mean()
avg_bio = df_filtered['bio_update_ratio'].mean()
high_risk_count = high_risk_districts.shape[0]
total_enrol = df_filtered['total_enrolments'].sum() if 'total_enrolments' in df.columns else 0

with c1:
    st.metric(label="Avg Demographic Stress", value=f"{avg_demo:.2f}")
with c2:
    st.metric(label="Avg Biometric Stress", value=f"{avg_bio:.2f}")
with c3:
    st.metric(label="High Risk Districts", value=high_risk_count, delta="Alerts", delta_color="inverse")
with c4:
    st.metric(label="Total Enrolments (Filtered)", value=f"{total_enrol:,}")

st.divider()

# ------------------------------------------------------------------------------
# 7. Zone B (Map) & Zone C (Charts)
# ------------------------------------------------------------------------------
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📍 Geospatial Stress Heatmap")
    
    if not map_df.empty:
        fig_map = px.scatter_geo(
            map_df,
            lat='lat',
            lon='lon',
            hover_name="State",
            size="Average Stress",
            color="Average Stress",
            color_continuous_scale="Reds",
            scope="asia", 
            projection="natural earth"
        )
        
        # Smart Zoom
        if selected_state != "All India" and selected_state in STATE_COORDS:
            # Zoom into the selected state
            center_lat = STATE_COORDS[selected_state][0]
            center_lon = STATE_COORDS[selected_state][1]
            zoom_lat_range = [center_lat - 5, center_lat + 5]
            zoom_lon_range = [center_lon - 5, center_lon + 5]
        else:
            # Default India view
            center_lat = 22.0
            center_lon = 82.0
            zoom_lat_range = [6, 38]
            zoom_lon_range = [68, 98]

        fig_map.update_geos(
            visible=False, 
            resolution=50,
            showcountries=True, countrycolor="Black",
            center={"lat": center_lat, "lon": center_lon},
            lataxis_range=zoom_lat_range, 
            lonaxis_range=zoom_lon_range
        )
        fig_map.update_layout(
            geo=dict(
                scope='asia',
                projection_type='mercator',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                countrycolor='rgb(204, 204, 204)',
            ),
            margin={"r":0,"t":10,"l":0,"b":0},
            height=600
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No geospatial data available.")

with col_right:
    # 1. Trend Chart (Reactive)
    st.subheader("📈 Stress Trend")
    if 'month_dt' in df_filtered.columns and not df_filtered.empty:
        trend = df_filtered.groupby('month_dt')['total_stress_index'].mean().reset_index()
        fig_trend = px.line(
            trend, x='month_dt', y='total_stress_index',
            markers=True,
            title=f"Stress Over Time ({selected_state})"
        )
        fig_trend.update_layout(xaxis_title="Month", yaxis_title="Stress Index", height=300)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No trend data available for current selection.")

    # 2. Top Districts (Reactive)
    st.subheader(f"🚨 Top High-Stress Districts ({selected_state})")
    if not df_filtered.empty:
        # Sort by total stress
        top_5 = df_filtered.sort_values(by='total_stress_index', ascending=False).head(10)
        
        st.dataframe(
            top_5[['district', 'state', 'total_stress_index']],
            hide_index=True,
            use_container_width=True,
            column_config={
                "total_stress_index": st.column_config.NumberColumn(
                    "Stress Score",
                    format="%.2f"
                )
            }
        )
        
        # Download Button for Hackathon Value
        csv_data = top_5.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Priority List",
            data=csv_data,
            file_name=f"high_stress_districts_{selected_state}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available.")

    with st.expander("ℹ️ About Indicators"):
        st.markdown("""
        **Total Stress Index** = Demo Update Ratio + Bio Update Ratio.
        \n**High Risk**: Top 5% of districts by stress score.
        """)
