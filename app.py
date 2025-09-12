import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration for a wider layout and custom title
st.set_page_config(page_title="Enhanced Data Dashboard", layout="wide")

# Title of the dashboard
st.title("Data Dashboard")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Cache file loading for performance
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Default filtered_df (so it's always available in all tabs)
    filtered_df = df.copy()

    # Sidebar settings
    st.sidebar.header("Dashboard Settings")
    show_rows = st.sidebar.slider("Number of rows to display", min_value=5, max_value=50, value=10, step=5)
    sort_column = st.sidebar.selectbox("Sort data by", ["None"] + df.columns.to_list())
    sort_order = st.sidebar.radio("Sort order", ["Ascending", "Descending"])

    # Apply sorting
    if sort_column != "None":
        ascending = True if sort_order == "Ascending" else False
        try:
            df = df.sort_values(by=sort_column, ascending=ascending)
        except Exception as e:
            st.warning(f"Could not sort by {sort_column}: {e}")

    # Tabs for organization
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Preview", "📊 Summary", "🔎 Filter", "📈 Visualizations"])

    # ---------------- Tab 1: Data Preview ----------------
    with tab1:
        st.subheader("Data Preview")
        st.write(df.head(show_rows))

    # ---------------- Tab 2: Data Summary ----------------
    with tab2:
        st.subheader("Data Summary")
        show_detailed_stats = st.checkbox("Show detailed statistics", value=False)
        if show_detailed_stats:
            st.write(df.describe(include="all").transpose())
        else:
            st.write(df.describe().transpose())

    # ---------------- Tab 3: Filtering ----------------
    with tab3:
        st.subheader("Filter Data")
        col1, col2 = st.columns(2)

        with col1:
            selected_column = st.selectbox("Select column to filter", df.columns.to_list())
            unique_values = df[selected_column].dropna().unique()
            default_values = [unique_values[0]] if len(unique_values) > 0 else []
            selected_values = st.multiselect(
                "Select values (multiple)",
                unique_values,
                default=default_values
            )

        with col2:
            filter_type = st.radio("Filter type", ["Include selected values", "Exclude selected values"])

        # Apply filtering
        if len(selected_values) > 0:
            if filter_type == "Include selected values":
                filtered_df = df[df[selected_column].isin(selected_values)]
            else:
                filtered_df = df[~df[selected_column].isin(selected_values)]
        else:
            filtered_df = df.copy()

        st.write(f"Filtered Data ({len(filtered_df)} rows)")
        st.dataframe(filtered_df, use_container_width=True)

        # Download filtered data
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name="filtered_data.csv",
            mime="text/csv"
        )

    # ---------------- Tab 4: Visualizations ----------------
    with tab4:
        st.subheader("Data Visualization")

        # Plot settings
        col3, col4 = st.columns(2)

        with col3:
            plot_type = st.selectbox("Select plot type", ["Line Chart", "Scatter Plot", "Bar Chart", "Histogram"])

        with col4:
            plot_height = st.slider("Plot height", 300, 800, 400, 50)

        # Handle histogram separately
        if plot_type == "Histogram":
            y_column = st.selectbox("Select column for histogram", df.columns.to_list())
            x_column = y_column  # use same column for labeling
        else:
            x_column = st.selectbox("Select x-axis column", df.columns.to_list())
            y_column = st.selectbox("Select y-axis column", df.columns.to_list())

        # Generate Plot
        if st.button("Generate Plot"):
            fig, ax = plt.subplots(figsize=(10, plot_height / 100))

            try:
                if plot_type == "Line Chart":
                    ax.plot(filtered_df[x_column], filtered_df[y_column], marker="o")
                elif plot_type == "Scatter Plot":
                    ax.scatter(filtered_df[x_column], filtered_df[y_column])
                elif plot_type == "Bar Chart":
                    ax.bar(filtered_df[x_column], filtered_df[y_column])
                elif plot_type == "Histogram":
                    ax.hist(filtered_df[y_column].dropna(), bins=20)

                ax.set_xlabel(x_column if x_column else "")
                ax.set_ylabel(y_column)
                ax.set_title(f"{plot_type}: {y_column} vs {x_column}" if x_column else f"{plot_type}: {y_column}")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)

            except Exception as e:
                st.error(f"Error generating plot: {e}")

        # Correlation Heatmap
        st.subheader("Correlation Heatmap")
        if st.checkbox("Show correlation heatmap"):
            numeric_df = filtered_df.select_dtypes(include="number")
            if not numeric_df.empty:
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
                ax.set_title("Correlation Heatmap")
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("No numeric columns available for correlation heatmap.")

else:
    st.write("Waiting on file upload...")
