import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="India Census Data Explorer",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
    <style>
    /* Main title styling */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0 1rem 0;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    /* Info box styling */
    .info-box {
        background-color: #e7f3ff;
        border-left: 5px solid #2196F3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* Success box styling */
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* Stats container */
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# ==================== DATA LOADING WITH CACHING ====================
@st.cache_data
def load_data():
    """Load and cache the census data"""
    try:
        df = pd.read_csv('india.csv')
        return df
    except FileNotFoundError:
        st.error("❌ Error: 'india.csv' file not found. Please ensure the file is in the correct directory.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()


df = load_data()

# ==================== HEADER SECTION ====================
st.markdown('<h1 class="main-title">INDIA CENSUS DATA EXPLORER</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Interactive Geospatial Visualization of Indian Demographics</p>',
            unsafe_allow_html=True)

# ==================== SIDEBAR CONFIGURATION ====================
with st.sidebar:
    st.title("🎛️ Settings")
    st.markdown("---")

    # State Selection
    st.subheader("📍 Location Filter")
    list_of_states = ['Overall India'] + sorted(df['State'].unique().tolist())
    selected_state = st.selectbox(
        'Select Region',
        list_of_states,
        help="Choose a specific state or view all of India"
    )

    st.markdown("---")

    # Parameter Selection
    st.subheader("📊 Data Parameters")
    numeric_columns = sorted(df.select_dtypes(include=[np.number]).columns.tolist())

    # Remove coordinate columns from parameter options
    numeric_columns = [col for col in numeric_columns if col not in ['Latitude', 'Longitude']]

    primary = st.selectbox(
        '🔵 Primary Parameter (Size)',
        numeric_columns,
        help="This parameter will control the size of markers on the map"
    )

    secondary = st.selectbox(
        '🟠 Secondary Parameter (Color)',
        numeric_columns,
        index=1 if len(numeric_columns) > 1 else 0,
        help="This parameter will control the color gradient of markers"
    )

    st.markdown("---")

    # Visualization Settings
    st.subheader("⚙️ Visualization Settings")

    map_style = st.selectbox(
        'Map Style',
        ['carto-positron', 'open-street-map', 'carto-darkmatter', 'stamen-terrain'],
        help="Choose the base map style"
    )

    marker_size = st.slider(
        'Marker Size',
        min_value=10,
        max_value=50,
        value=35,
        help="Adjust the maximum size of markers"
    )

    show_stats = st.checkbox('Show Statistics', value=True)
    show_comparison = st.checkbox('Show Comparison Charts', value=True)

    st.markdown("---")

    plot = st.button('🗺️ Generate Visualization', type="primary", use_container_width=True)

# ==================== MAIN CONTENT ====================
if plot:
    # Filter data based on selection
    if selected_state == 'Overall India':
        filtered_df = df.copy()
        zoom_level = 4
        center_lat = 20.5937
        center_lon = 78.9629
    else:
        filtered_df = df[df['State'] == selected_state].copy()
        zoom_level = 6
        center_lat = filtered_df['Latitude'].mean()
        center_lon = filtered_df['Longitude'].mean()

    # ==================== KEY STATISTICS ====================
    if show_stats:
        st.markdown("### 📈 Key Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Total Districts",
                value=f"{len(filtered_df):,}",
                delta=None
            )

        with col2:
            st.metric(
                label=f"Avg {primary}",
                value=f"{filtered_df[primary].mean():,.2f}",
                delta=f"{((filtered_df[primary].mean() / df[primary].mean() - 1) * 100):.1f}%" if selected_state != 'Overall India' else None
            )

        with col3:
            st.metric(
                label=f"Avg {secondary}",
                value=f"{filtered_df[secondary].mean():,.2f}",
                delta=f"{((filtered_df[secondary].mean() / df[secondary].mean() - 1) * 100):.1f}%" if selected_state != 'Overall India' else None
            )

        with col4:
            st.metric(
                label="States Covered",
                value=filtered_df['State'].nunique()
            )

        st.markdown("---")

    # ==================== MAIN MAP VISUALIZATION ====================
    st.markdown(f"### 🗺️ Geographic Distribution - {selected_state}")
    st.markdown(f"*Bubble size represents **{primary}** | Color intensity represents **{secondary}***")

    # Create the map
    fig_map = px.scatter_mapbox(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        size=primary,
        color=secondary,
        hover_name='District',
        hover_data={
            'State': True,
            primary: ':,.2f',
            secondary: ':,.2f',
            'Latitude': False,
            'Longitude': False
        },
        color_continuous_scale='Viridis',
        size_max=marker_size,
        zoom=zoom_level,
        center={"lat": center_lat, "lon": center_lon},
        mapbox_style=map_style,
        height=600,
        title=f"District-wise Analysis: {primary} vs {secondary}"
    )

    fig_map.update_layout(
        font=dict(size=12),
        title_font=dict(size=20, family="Arial Black"),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    st.plotly_chart(fig_map, use_container_width=True, key='main_map')

    # ==================== COMPARISON CHARTS ====================
    if show_comparison:
        st.markdown("---")
        st.markdown(f"### 📊 Comparative Analysis - {selected_state}")

        # Create two columns for charts
        col1, col2 = st.columns(2)

        with col1:
            # Top 10 districts by primary parameter
            top_districts = filtered_df.nlargest(10, primary)[['District', primary, 'State']].reset_index(drop=True)

            fig_bar = px.bar(
                top_districts,
                x=primary,
                y='District',
                orientation='h',
                color=primary,
                color_continuous_scale='Blues',
                title=f'Top 10 Districts by {primary}',
                labels={primary: primary, 'District': 'District'},
                height=400
            )

            fig_bar.update_layout(
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig_bar, use_container_width=True, key='bar_chart')

        with col2:
            # Scatter plot: Primary vs Secondary
            fig_scatter = px.scatter(
                filtered_df,
                x=primary,
                y=secondary,
                color='State' if selected_state == 'Overall India' else primary,
                size=primary,
                hover_name='District',
                title=f'{primary} vs {secondary}',
                trendline="ols",
                height=400
            )

            fig_scatter.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))

            st.plotly_chart(fig_scatter, use_container_width=True, key='scatter_chart')

        # Distribution plots
        st.markdown("#### 📉 Distribution Analysis")
        col3, col4 = st.columns(2)

        with col3:
            fig_hist_primary = px.histogram(
                filtered_df,
                x=primary,
                nbins=30,
                title=f'Distribution of {primary}',
                color_discrete_sequence=['#636EFA'],
                height=350
            )
            fig_hist_primary.update_layout(showlegend=False)
            st.plotly_chart(fig_hist_primary, use_container_width=True, key='hist_primary')

        with col4:
            fig_hist_secondary = px.histogram(
                filtered_df,
                x=secondary,
                nbins=30,
                title=f'Distribution of {secondary}',
                color_discrete_sequence=['#EF553B'],
                height=350
            )
            fig_hist_secondary.update_layout(showlegend=False)
            st.plotly_chart(fig_hist_secondary, use_container_width=True, key='hist_secondary')

    # ==================== DATA TABLE ====================
    st.markdown("---")
    st.markdown("### 📋 Detailed Data Table")

    # Display options
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"*Showing {len(filtered_df)} districts*")
    with col2:
        if st.button('📥 Download CSV'):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f'india_census_{selected_state.replace(" ", "_")}.csv',
                mime='text/csv',
            )

    # Display dataframe with custom styling
    st.dataframe(
        filtered_df[['State', 'District', primary, secondary]].sort_values(by=primary, ascending=False),
        use_container_width=True,
        height=400
    )

    # ==================== SUMMARY STATISTICS ====================
    with st.expander("📊 View Summary Statistics"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{primary} Statistics**")
            stats_primary = filtered_df[primary].describe()
            st.dataframe(stats_primary, use_container_width=True)

        with col2:
            st.markdown(f"**{secondary} Statistics**")
            stats_secondary = filtered_df[secondary].describe()
            st.dataframe(stats_secondary, use_container_width=True)

else:
    # ==================== WELCOME SCREEN ====================
    st.markdown("""
    <div class="info-box">
        <h3>👋 Welcome to India Census Data Explorer!</h3>
        <p>This interactive dashboard helps you visualize and analyze Indian Census data across different states and districts.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎯 Features")
        st.markdown("""
        - Interactive geospatial maps
        - Multi-parameter comparison
        - Statistical analysis
        - Export capabilities
        - Real-time filtering
        """)

    with col2:
        st.markdown("### 📊 Available Data")
        st.markdown(f"""
        - **Total Districts:** {len(df):,}
        - **States/UTs:** {df['State'].nunique()}
        - **Parameters:** {len(numeric_columns)}
        - **Data Points:** {len(df) * len(numeric_columns):,}
        """)

    with col3:
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        1. Select a state from sidebar
        2. Choose primary parameter
        3. Choose secondary parameter
        4. Click 'Generate Visualization'
        5. Explore the interactive map!
        """)

    st.markdown("---")

    # Preview data
    st.markdown("### 👀 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.markdown("""
    <div class="success-box">
        <p>💡 <strong>Tip:</strong> Use the sidebar controls to customize your visualization. You can compare different parameters and explore state-specific data.</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN CONTENT ====================
if plot:
    # Filter data based on selection
    if selected_state == 'Overall India':
        filtered_df = df.copy()
        zoom_level = 4
        center_lat = 20.5937
        center_lon = 78.9629
    else:
        filtered_df = df[df['State'] == selected_state].copy()
        zoom_level = 6
        center_lat = filtered_df['Latitude'].mean()
        center_lon = filtered_df['Longitude'].mean()

    # ==================== KEY STATISTICS ====================
    if show_stats:
        st.markdown("### 📈 Key Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Total Districts",
                value=f"{len(filtered_df):,}",
                delta=None
            )

        with col2:
            st.metric(
                label=f"Avg {primary}",
                value=f"{filtered_df[primary].mean():,.2f}",
                delta=f"{((filtered_df[primary].mean() / df[primary].mean() - 1) * 100):.1f}%" if selected_state != 'Overall India' else None
            )

        with col3:
            st.metric(
                label=f"Avg {secondary}",
                value=f"{filtered_df[secondary].mean():,.2f}",
                delta=f"{((filtered_df[secondary].mean() / df[secondary].mean() - 1) * 100):.1f}%" if selected_state != 'Overall India' else None
            )

        with col4:
            st.metric(
                label="States Covered",
                value=filtered_df['State'].nunique()
            )

        st.markdown("---")

    # ==================== MAIN MAP VISUALIZATION ====================
    st.markdown(f"### 🗺️ Geographic Distribution - {selected_state}")
    st.markdown(f"*Bubble size represents **{primary}** | Color intensity represents **{secondary}***")

    # Create the map
    fig_map = px.scatter_mapbox(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        size=primary,
        color=secondary,
        hover_name='District',
        hover_data={
            'State': True,
            primary: ':,.2f',
            secondary: ':,.2f',
            'Latitude': False,
            'Longitude': False
        },
        color_continuous_scale='Viridis',
        size_max=marker_size,
        zoom=zoom_level,
        center={"lat": center_lat, "lon": center_lon},
        mapbox_style=map_style,
        height=600,
        title=f"District-wise Analysis: {primary} vs {secondary}"
    )

    fig_map.update_layout(
        font=dict(size=12),
        title_font=dict(size=20, family="Arial Black"),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # ==================== COMPARISON CHARTS ====================
    if show_comparison:
        st.markdown("---")
        st.markdown(f"### 📊 Comparative Analysis - {selected_state}")

        # Create two columns for charts
        col1, col2 = st.columns(2)

        with col1:
            # Top 10 districts by primary parameter
            top_districts = filtered_df.nlargest(10, primary)[['District', primary, 'State']].reset_index(drop=True)

            fig_bar = px.bar(
                top_districts,
                x=primary,
                y='District',
                orientation='h',
                color=primary,
                color_continuous_scale='Blues',
                title=f'Top 10 Districts by {primary}',
                labels={primary: primary, 'District': 'District'},
                height=400
            )

            fig_bar.update_layout(
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # Scatter plot: Primary vs Secondary
            fig_scatter = px.scatter(
                filtered_df,
                x=primary,
                y=secondary,
                color='State' if selected_state == 'Overall India' else primary,
                size=primary,
                hover_name='District',
                title=f'{primary} vs {secondary}',
                trendline="ols",
                height=400
            )

            fig_scatter.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))

            st.plotly_chart(fig_scatter, use_container_width=True)

        # Distribution plots
        st.markdown("#### 📉 Distribution Analysis")
        col3, col4 = st.columns(2)

        with col3:
            fig_hist_primary = px.histogram(
                filtered_df,
                x=primary,
                nbins=30,
                title=f'Distribution of {primary}',
                color_discrete_sequence=['#636EFA'],
                height=350
            )
            fig_hist_primary.update_layout(showlegend=False)
            st.plotly_chart(fig_hist_primary, use_container_width=True)

        with col4:
            fig_hist_secondary = px.histogram(
                filtered_df,
                x=secondary,
                nbins=30,
                title=f'Distribution of {secondary}',
                color_discrete_sequence=['#EF553B'],
                height=350
            )
            fig_hist_secondary.update_layout(showlegend=False)
            st.plotly_chart(fig_hist_secondary, use_container_width=True)

    # ==================== DATA TABLE ====================
    st.markdown("---")
    st.markdown("### 📋 Detailed Data Table")

    # Display options
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"*Showing {len(filtered_df)} districts*")
    with col2:
        if st.button('📥 Download CSV'):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f'india_census_{selected_state.replace(" ", "_")}.csv',
                mime='text/csv',
            )

    # Display dataframe with custom styling
    st.dataframe(
        filtered_df[['State', 'District', primary, secondary]].sort_values(by=primary, ascending=False),
        use_container_width=True,
        height=400
    )

    # ==================== SUMMARY STATISTICS ====================
    with st.expander("📊 View Summary Statistics"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{primary} Statistics**")
            stats_primary = filtered_df[primary].describe()
            st.dataframe(stats_primary, use_container_width=True)

        with col2:
            st.markdown(f"**{secondary} Statistics**")
            stats_secondary = filtered_df[secondary].describe()
            st.dataframe(stats_secondary, use_container_width=True)

else:
    # ==================== WELCOME SCREEN ====================
    st.markdown("""
    <div class="info-box">
        <h3>👋 Welcome to India Census Data Explorer!</h3>
        <p>This interactive dashboard helps you visualize and analyze Indian Census data across different states and districts.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎯 Features")
        st.markdown("""
        - Interactive geospatial maps
        - Multi-parameter comparison
        - Statistical analysis
        - Export capabilities
        - Real-time filtering
        """)

    with col2:
        st.markdown("### 📊 Available Data")
        st.markdown(f"""
        - **Total Districts:** {len(df):,}
        - **States/UTs:** {df['State'].nunique()}
        - **Parameters:** {len(numeric_columns)}
        - **Data Points:** {len(df) * len(numeric_columns):,}
        """)

    with col3:
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        1. Select a state from sidebar
        2. Choose primary parameter
        3. Choose secondary parameter
        4. Click 'Generate Visualization'
        5. Explore the interactive map!
        """)

    st.markdown("---")

    # Preview data
    st.markdown("### 👀 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.markdown("""
    <div class="success-box">
        <p>💡 <strong>Tip:</strong> Use the sidebar controls to customize your visualization. You can compare different parameters and explore state-specific data.</p>
    </div>
    """, unsafe_allow_html=True)
