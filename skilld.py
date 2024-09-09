import pandas as pd
import streamlit as st
from fpdf import FPDF
from io import BytesIO

# Function to read Excel files and return DataFrame with normalized column names
@st.cache
def read_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

# Load and display subject data
def load_subject_data():
    file_path = st.file_uploader("Upload Subject Excel File", type=["xlsx", "xls"])
    if file_path:
        subjects_df = read_excel_file(file_path)
        if subjects_df is not None:
            return subjects_df
    return None

# Load and display room data
def load_room_data():
    file_path = st.file_uploader("Upload Room Excel File", type=["xlsx", "xls"])
    if file_path:
        rooms_df = read_excel_file(file_path)
        if rooms_df is not None:
            return rooms_df
    return None

# Load and display faculty data with checkboxes
def load_faculty_data():
    file_path = st.file_uploader("Upload Faculty Excel File", type=["xlsx", "xls"])
    if file_path:
        faculty_df = read_excel_file(file_path)
        if faculty_df is not None:
            return faculty_df
    return None

# Function to generate and display the timetable
def generate_timetable(subjects_df, rooms_df, faculty_df):
    if subjects_df is None or rooms_df is None or faculty_df is None:
        st.warning("Please upload subject, room, and faculty files first.")
        return
    
    st.subheader("Generated Timetable")
    
    # Collect selected faculty only
    selected_faculty = st.multiselect(
        "Select Faculty Members",
        options=faculty_df['faculty name'].tolist(),
        default=[]
    )

    if not selected_faculty:
        st.warning("No faculty members selected!")
        return

    faculty_filtered_df = faculty_df[faculty_df['faculty name'].isin(selected_faculty)]

    timetable_data = []
    for year in subjects_df.columns:
        subjects_list = subjects_df[year].dropna().tolist()
        for i, subject in enumerate(subjects_list):
            room_index = i % len(rooms_df)
            room = rooms_df.iloc[room_index]

            # Determine how many faculty members are required
            faculty_count = 2 if room.get('capacity', 0) > 50 else 1
            faculty_list = []
            for j in range(faculty_count):
                faculty_index = (i + j) % len(faculty_filtered_df)
                faculty = faculty_filtered_df.iloc[faculty_index]
                faculty_name = faculty.get('faculty name', 'N/A')
                faculty_list.append(faculty_name)
    
            building = room.get('building', 'N/A').title()
            room_number = room.get('room number', 'N/A')
            faculty_assigned = ", ".join(faculty_list)
    
            date_time = st.text_input(f"Enter Date & Time for '{subject}' ({year.title()}):", "Not Assigned")
    
            timetable_data.append([year.title(), subject, room_number, building, date_time, faculty_assigned])
    
    if timetable_data:
        df_timetable = pd.DataFrame(timetable_data, columns=["Year", "Subject", "Room Number", "Building", "Date & Time", "Faculty"])
        st.write(df_timetable)

        # Button to download timetable as PDF
        if st.button("Download Timetable as PDF"):
            save_timetable_as_pdf(df_timetable)

def save_timetable_as_pdf(timetable_df):
    buffer = BytesIO()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Generated Timetable", ln=True, align="C")

    # Add timetable data to PDF
    for index, row in timetable_df.iterrows():
        row_text = " | ".join(row.astype(str))
        pdf.cell(200, 10, txt=row_text, ln=True, align="L")

    pdf.output(buffer)
    buffer.seek(0)
    
    st.download_button(
        label="Download PDF",
        data=buffer,
        file_name="timetable.pdf",
        mime="application/pdf"
    )

def main():
    st.title("Subject, Room, and Faculty Details Viewer")

    subjects_df = load_subject_data()
    rooms_df = load_room_data()
    faculty_df = load_faculty_data()

    if subjects_df is not None and rooms_df is not None and faculty_df is not None:
        generate_timetable(subjects_df, rooms_df, faculty_df)

if __name__ == "__main__":
    main()
