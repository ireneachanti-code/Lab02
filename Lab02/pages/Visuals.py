# This creates the page for displaying data visualizations.
# It reads data from both 'data.csv' and 'data.json' to create graphs.

import streamlit as st
import pandas as pd
import json # The 'json' module is needed to work with JSON files.
import os # The 'os' module helps with file system operations.
import matplotlib.pyplot as plt

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Visualizations",
    page_icon="📈",
)

# PAGE TITLE AND INFORMATION                
st.title("Data Visualizations 📊")
st.write("This page displays graphs based on the collected data.")


# DATA LOADING
# A crucial step is to load the data from the files.
# It's important to add error handling to prevent the app from crashing if a file is empty or missing.

st.divider()
st.header("Raw Data")

# TO DO:
# 1. Load the data from 'data.csv' into a pandas DataFrame.
#    - Use a 'try-except' block or 'os.path.exists' to handle cases where the file doesn't exist.
# 2. Load the data from 'data.json' into a Python dictionary.
#    - Use a 'try-except' block here as well.

if "selected_class" not in st.session_state:
    st.session_state.selected_class = None
if "ma_window" not in st.session_state:
    st.session_state.ma_window = 3
if "json_n" not in st.session_state:
    st.session_state.json_n = 5

def load_first_existing(path_options):
    """Return the first existing non-empty file path from a list."""
    for p in path_options:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    return None

csv_path = "data.csv"
json_path = load_first_existing(["class_data.json", "data.json"])

# Load CSV 
if csv_path and os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
    try:
        df = pd.read_csv(csv_path)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        df = pd.DataFrame()
else:
    st.warning("No CSV data found.")
    df = pd.DataFrame()

# Load JSON
if json_path:
    try:
        with open(json_path, "r") as f:
            json_data = json.load(f)
        # JSON loaded silently — no message shown
    except Exception as e:
        json_data = {}
else:
    json_data = {}

def is_class_data_format(df_: pd.DataFrame) -> bool:
    """Detects if CSV columns follow 'Class' / 'Professor' pattern."""
    return any(col.endswith("Class") for col in df_.columns) or any(col.endswith("Professor") for col in df_.columns)


# GRAPH CREATION
# The lab requires you to create 3 graphs: one static and two dynamic.
# You must use both the CSV and JSON data sources at least once.

st.divider()
st.header("Graphs")

# GRAPH 1 (STATIC): Professor Liking vs Class Liking
st.subheader("Graph 1 (Static): Comparison of Class and Professor Ratings by Course")
# TO DO:
# - Create a static graph (e.g., bar chart, line chart) using st.bar_chart() or st.line_chart().
# - Use data from either the CSV or JSON file.
# - Write a description explaining what the graph shows.
st.write(
    "This static bar chart compares how much students liked each class "
    "versus how much they liked its professor, based on survey data."
)

if not df.empty:
    class_cols = [c for c in df.columns if c.endswith("Class")]
    prof_cols = [c for c in df.columns if c.endswith("Professor")]

    if class_cols and prof_cols:
        paired_data = []

        for class_col in class_cols:
            base_name = class_col.replace(" Class", "")
            prof_col = f"{base_name} Professor"

            if prof_col in df.columns:
                df[class_col] = pd.to_numeric(df[class_col], errors="coerce")
                df[prof_col] = pd.to_numeric(df[prof_col], errors="coerce")

                class_avg = df[class_col].mean(skipna=True)
                prof_avg = df[prof_col].mean(skipna=True)

                if not pd.isna(class_avg) and not pd.isna(prof_avg):
                    paired_data.append((base_name, class_avg, prof_avg))

        if paired_data:
            result_df = pd.DataFrame(paired_data, columns=["Course", "Class Liking", "Professor Liking"])

            fig, ax = plt.subplots()
            x = range(len(result_df))
            ax.bar([i - 0.2 for i in x], result_df["Class Liking"], width=0.4, label="Class Liking", color="skyblue")
            ax.bar([i + 0.2 for i in x], result_df["Professor Liking"], width=0.4, label="Professor Liking", color="lightgreen")

            ax.set_xticks(x)
            ax.set_xticklabels(result_df["Course"], rotation=45, ha="right")
            ax.set_ylabel("Average Rating (0–10)")
            ax.set_title("Professor vs Class Liking by Course")
            ax.set_ylim(0, 10)
            ax.legend()

            st.pyplot(fig)
        else:
            st.warning("No matching Class/Professor pairs found with numeric data.")
    else:
        st.warning("Your CSV must contain columns ending with 'Class' and 'Professor'.")
else:
    st.warning("No CSV data available for this graph.")




# GRAPH 2 (DYNAMIC): Class vs Professor Comparison (Pie Chart)
st.subheader("Graph 2 (Dynamic): Class vs Professor Comparison")
# TODO:
# - Create a dynamic graph that changes based on user input.
# - Use at least one interactive widget (e.g., st.slider, st.selectbox, st.multiselect).
# - Use Streamlit's Session State (st.session_state) to manage the interaction.
# - Add a '#NEW' comment next to at least 3 new Streamlit functions you use in this lab.
# - Write a description explaining the graph and how to interact with it.

st.write(
    "This pie chart shows how the average Class rating compares "
    "to the average Professor rating as a pie chart. You can adjust how many of the most "
    "recent submissions are included."
)

if not df.empty and is_class_data_format(df):
    classes_available = sorted({c.replace(" Class", "") for c in df.columns if c.endswith("Class")})

    if classes_available:
        if st.session_state.selected_class is None:
            st.session_state.selected_class = classes_available[0]

        selected = st.selectbox(
            "Choose a class:",
            classes_available,
            index=classes_available.index(st.session_state.selected_class),
            key="selected_class"
        )

        cls_col = f"{selected} Class"
        prof_col = f"{selected} Professor"

        if cls_col in df.columns and prof_col in df.columns:
            cls_series = pd.to_numeric(df[cls_col], errors="coerce").fillna(0)
            prof_series = pd.to_numeric(df[prof_col], errors="coerce").fillna(0)

            if len(df) > 1:
                num_entries = st.slider(
                    "Select how many data submissions you would like to include "
                    "(e.g., if 4, chart includes last 4 submissions).",
                    min_value=1,
                    max_value=len(df),
                    value=min(4, len(df))
                )
            else:
                num_entries = 1  # Default to 1 when only one row
                st.info("Only one submission found — showing all available data.")

            cls_series_recent = cls_series.tail(num_entries)
            prof_series_recent = prof_series.tail(num_entries)

            cls_avg = cls_series_recent.mean()
            prof_avg = prof_series_recent.mean()

            if pd.isna(cls_avg):
                cls_avg = 0
            if pd.isna(prof_avg):
                prof_avg = 0

            total = cls_avg + prof_avg

            if total == 0:
                st.warning("⚠️ No valid data found for this class. Please submit survey data first.")
                fig, ax = plt.subplots()
                ax.pie(
                    [1, 1],
                    labels=["No Data", "No Data"],
                    colors=["lightgray", "darkgray"],
                    autopct="%1.1f%%",
                    startangle=90
                )
                ax.set_title(f"{selected}: No Data Yet")
                st.pyplot(fig)

            else:
                labels = ["Class Liking", "Professor Liking"]
                values = [cls_avg, prof_avg]
                colors = ["skyblue", "lightgreen"]

                fig, ax = plt.subplots()
                ax.pie(
                    values,
                    labels=labels,
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=colors,
                    textprops={"color": "black"}
                )
                ax.set_title(f"{selected}: Class vs Professor Averages (Last {num_entries} Submissions)")
                ax.axis("equal")
                st.pyplot(fig)

                st.write(f"**Class Average:** {cls_avg:.2f}")
                st.write(f"**Professor Average:** {prof_avg:.2f}")

        else:
            st.info("Selected class columns not found.")
    else:
        st.info("No class columns found to build a comparison.")
else:
    st.warning("No CSV data available for this graph.")


# GRAPH 3 (DYNAMIC): Class vs Professor Liking Over Submissions
st.subheader("Graph 3 (Dynamic): Class vs Professor Liking Over Submissions")
# TO DO:
# - Create another dynamic graph.
# - If you used CSV data for Graph 1 & 2, you MUST use JSON data here (or vice-versa).
# - This graph must also be interactive and use Session State.
# - Remember to add a description and use '#NEW' comments.

st.write(
    "This graph shows how overall student opinions of their classes and professors have changed over time"
    "with each new survey submission."
)

if os.path.exists("data.csv"):
    try:
        df = pd.read_csv("data.csv")

        class_cols = [c for c in df.columns if c.endswith("Class")]
        prof_cols = [c for c in df.columns if c.endswith("Professor")]

        if not class_cols or not prof_cols:
            st.warning("No valid 'Class' or 'Professor' columns found in data.csv.")
        else:
            df[class_cols + prof_cols] = df[class_cols + prof_cols].apply(pd.to_numeric, errors="coerce")

            df["Avg_Class_Liking"] = df[class_cols].mean(axis=1, skipna=True)
            df["Avg_Professor_Liking"] = df[prof_cols].mean(axis=1, skipna=True)

            df["Submission_Number"] = range(1, len(df) + 1)

            max_points = len(df)
            if max_points <= 1:
                num_points = 1
            else:
                num_points = st.slider(
                    "Select how many recent submissions to display:",
                    min_value=1,
                    max_value=max_points,
                    value=max_points,
                    key="class_prof_line_points"
                )
            df_recent = df.tail(num_points)

            fig, ax = plt.subplots()
            ax.plot(df_recent["Submission_Number"], df_recent["Avg_Class_Liking"], marker="o", label="Class Liking", color="skyblue")
            ax.plot(df_recent["Submission_Number"], df_recent["Avg_Professor_Liking"], marker="s", label="Professor Liking", color="lightgreen")

            ax.set_title("Average Class vs Professor Liking (Per Submission)")
            ax.set_xlabel("Survey Submission #")
            ax.set_ylabel("Average Rating (0–10)")
            ax.set_ylim(0, 10)
            ax.grid(alpha=0.3)
            ax.legend()

            st.pyplot(fig)

            st.write(f"**Latest Average Class Rating:** {df['Avg_Class_Liking'].iloc[-1]:.2f}")
            st.write(f"**Latest Average Professor Rating:** {df['Avg_Professor_Liking'].iloc[-1]:.2f}")

    except Exception as e:
        st.error(f"Error reading data.csv: {e}")
else:
    st.warning("No data.csv file found.")



