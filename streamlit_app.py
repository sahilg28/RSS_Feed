import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import glob
import os

# Set page config
st.set_page_config(
    page_title="Global News Dashboard",
    page_icon="📰",
    layout="wide"
)

def load_data():
    """
    Load and combine all news data from CSV files.
    """
    # Get all CSV files in the data directory
    csv_files = glob.glob('data/*.csv')
    
    if not csv_files:
        st.error("No data files found in the data directory!")
        return None
    
    # Read and combine all CSV files
    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
        except Exception as e:
            st.warning(f"Error reading {file}: {str(e)}")
    
    if not dfs:
        st.error("No valid data found!")
        return None
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Convert published_date to datetime
    try:
        # First, ensure the column exists
        if 'published_date' not in combined_df.columns:
            st.error("No published_date column found in the data!")
            return None
            
        # Convert to datetime, handling various formats
        combined_df['published_date'] = pd.to_datetime(
            combined_df['published_date'],
            errors='coerce'
        )
        
        # Remove rows with invalid dates
        combined_df = combined_df.dropna(subset=['published_date'])
        
        if len(combined_df) == 0:
            st.error("No valid dates found in the data!")
            return None
            
    except Exception as e:
        st.error(f"Error parsing dates: {str(e)}")
        return None
    
    # Remove duplicates
    combined_df = combined_df.drop_duplicates(subset=['title', 'url'])
    
    return combined_df

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("📰 Global News Dashboard")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Country filter
    countries = sorted(df['country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        countries,
        default=countries[:5]
    )
    
    # Source filter
    sources = sorted(df['source'].unique())
    selected_sources = st.sidebar.multiselect(
        "Select Sources",
        sources,
        default=sources[:5]
    )
    
    # Date range filter
    min_date = df['published_date'].min().date()
    max_date = df['published_date'].max().date()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(max_date - timedelta(days=7), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Language filter
    languages = sorted(df['language'].unique())
    selected_languages = st.sidebar.multiselect(
        "Select Languages",
        languages,
        default=languages
    )
    
    # Apply filters
    mask = (
        df['country'].isin(selected_countries) &
        df['source'].isin(selected_sources) &
        df['language'].isin(selected_languages) &
        (df['published_date'].dt.date >= date_range[0]) &
        (df['published_date'].dt.date <= date_range[1])
    )
    filtered_df = df[mask]
    
    # Display statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Articles by Country")
        country_counts = filtered_df['country'].value_counts()
        st.bar_chart(country_counts)
    
    with col2:
        st.subheader("Articles by Source")
        source_counts = filtered_df['source'].value_counts()
        st.bar_chart(source_counts)
    
    # Search functionality
    search_query = st.text_input("🔍 Search articles", "")
    if search_query:
        search_mask = (
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['description'].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # Display articles table
    st.subheader(f"Articles ({len(filtered_df)})")
    
    # Format the dataframe for display
    display_df = filtered_df[['title', 'published_date', 'source', 'country', 'language']].copy()
    display_df['published_date'] = display_df['published_date'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Add clickable links
    display_df['link'] = filtered_df['url'].apply(
        lambda x: f'<a href="{x}" target="_blank">Read Article</a>'
    )
    
    # Display the table with clickable links
    st.write(
        display_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 