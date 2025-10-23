# This creates the page for users to input data.
# The collected data should be appended to the 'data.csv' file.

import streamlit as st
import pandas as pd
import os # The 'os' module is used for file system operations (e.g. checking if a file exists).
import json

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Survey",
    page_icon="📝",
)
# PAGE TITLE AND USER DIRECTIONS
st.title("Class & Professor Survey 📝")
st.write("For each applicable subject, please rate each class and professor 0–10. Subjects with either rating 0 will be ignored.")

classes = ["Math", "Computer Science", "Science", "History", "English", "Elective 1", "Elective 2", "Other"]

all_columns = []
for cls in classes:
    all_columns.append(f"{cls} Class")
    all_columns.append(f"{cls} Professor")

# DATA INPUT FORM
# 'st.form' creates a container that groups input widgets.
# The form is submitted only when the user clicks the 'st.form_submit_button'.
# This is useful for preventing the app from re-running every time a widget is changed.
with st.form("survey_form"):
    # Create text input widgets for the user to enter data.
    # The first argument is the label that appears above the input box.
    submission = {}
    for cls in classes:
        st.subheader(cls)
        class_rating = st.slider(f"How much do you like the {cls} class?", 0, 10, key=f"class_{cls}")
        prof_rating = st.slider(f"How much do you like the {cls} professor?", 0, 10, key=f"prof_{cls}")
        # Only save if BOTH > 0
        submission[f"{cls} Class"] = class_rating if class_rating > 0 and prof_rating > 0 else ""
        submission[f"{cls} Professor"] = prof_rating if class_rating > 0 and prof_rating > 0 else ""

    # The submit button for the form.
    submitted = st.form_submit_button("Submit Data")
    
    # This block of code runs ONLY when the submit button is clicked.
    if submitted:
        if all(value == "" for value in submission.values()):
            st.warning("You didn't provide any valid ratings (both class and professor must be > 0).")
        else:
            file_exists = os.path.isfile("data.csv")
            submission_df = pd.DataFrame([submission], columns=all_columns)
            submission_df.to_csv("data.csv", mode='a', header=not file_exists, index=False)


            # Update JSON summary
            if os.path.exists("data.json"):
                with open("data.json", "r") as f:
                    data = json.load(f)
            else:
                data = {"Total Surveys": 0}

            data["Total Surveys"] = data.get("Total Surveys", 0) + 1
            data["Last Submission"] = submission

            with open("data.json", "w") as f:
                json.dump(data, f, indent=4)

            st.success("Your data has been submuitted!")

# DATA DISPLAY
# This section shows the current contents of the CSV file, which helps in debugging.
st.divider() # Adds a horizontal line for visual separation.
st.header("Current Data in CSV")

# Check if the CSV file exists and is not empty before trying to read it.
if os.path.exists('data.csv') and os.path.getsize('data.csv') > 0:
    # Read the CSV file into a pandas DataFrame.
    current_data_df = pd.read_csv('data.csv')
    # Display the DataFrame as a table.
    st.dataframe(current_data_df)
else:
    st.warning("The 'data.csv' file is empty or does not exist yet.")
