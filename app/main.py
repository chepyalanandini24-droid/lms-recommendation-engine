import streamlit as st
import pandas as pd
from recommendation import (
    load_data,
    popularity_recommendations,
    content_based_recommendations,
    hybrid_recommendations
)
from datetime import datetime
import os

# Set Page Config
st.set_page_config(page_title="AI LMS Recommendation Engine", layout="wide")

# Load Data
students_df, courses_df, interactions_df = load_data()

# --- SIDEBAR: STUDENT LOGIN SIMULATION ---
st.sidebar.title("Student Login Simulation")
student_ids = students_df['student_id'].unique()
selected_student_id = st.sidebar.selectbox("Select Student ID", student_ids)

# Fetch Current Student Profile
student_info = students_df[students_df['student_id'] == selected_student_id].iloc[0]

st.sidebar.markdown("---")
st.sidebar.write(f"**Department:** {student_info['department']}")
st.sidebar.write(f"**CGPA:** {student_info['cgpa']}")
st.sidebar.write(f"**Primary Interest:** {student_info['interests']}")

# Display Previously Completed Courses
completed_courses = student_info.get('previously_completed_courses', 'None')
st.sidebar.write(f"**Completed Courses:** {completed_courses}")

# --- MAIN DASHBOARD ---
st.title("🎓 AI-Based LMS Course Recommendation Engine")

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Hybrid & Personalized", 
    "🔥 Popularity", 
    "📊 Student Activity & Progress",
    "🔍 Search & Catalog", 
    "💬 Student Feedback"
])

# TAB 1: HYBRID & PERSONALIZED
with tab1:
    st.subheader(f"Recommendations for Student {selected_student_id}")
    col1, col2 = st.columns(2)
    
    hybrid_recs = hybrid_recommendations(selected_student_id, students_df, courses_df, interactions_df)
    content_recs = content_based_recommendations(selected_student_id, students_df, courses_df)
    
    with col1:
        st.markdown("### Hybrid Model (Content + Collaborative)")
        st.dataframe(hybrid_recs, width="stretch")
        
    with col2:
        st.markdown("### Content-Based (Interest Match)")
        st.dataframe(content_recs, width="stretch")

# TAB 2: POPULARITY
with tab2:
    st.subheader("🔥 Top Rated System-Wide")
    pop_recs = popularity_recommendations(courses_df)
    st.dataframe(pop_recs, width="stretch")

# TAB 3: STUDENT ACTIVITY & LEARNING PROGRESS
with tab3:
    st.subheader(f"📈 Activity & Learning Progress for {selected_student_id}")
    
    student_activity = interactions_df[interactions_df['student_id'] == selected_student_id]
    
    if not student_activity.empty:
        merged_activity = student_activity.merge(courses_df[['course_id', 'course_name']], on='course_id', how='left')
        
        activity_display = merged_activity[[
            'course_id', 'course_name', 'learning_progress', 
            'quiz_scores', 'time_spent', 'courses_viewed', 'courses_completed', 'likes'
        ]]
        
        st.dataframe(activity_display, width="stretch")
        
        st.markdown("---")
        st.markdown("### 🎯 Active Course Completion Tracker")
        for idx, row in activity_display.iterrows():
            st.write(f"**{row['course_name']}** - Progress: {row['learning_progress']}% | Quiz Score: {row['quiz_scores']}% | Time Spent: {row['time_spent']} hrs")
            st.progress(int(row['learning_progress']))
    else:
        st.info("No interaction history available for this student.")

# TAB 4: SEARCH & CATALOG
with tab4:
    st.subheader("Search Courses")
    search_query = st.text_input("Enter skill or domain (e.g., Python, AI, Web)")
    
    if search_query:
        filtered_courses = courses_df[
            courses_df['skills'].str.contains(search_query, case=False, na=False) |
            courses_df['domain'].str.contains(search_query, case=False, na=False)
        ]
        st.dataframe(filtered_courses, width="stretch")
    else:
        st.dataframe(courses_df, width="stretch")

# TAB 5: STUDENT FEEDBACK
with tab5:
    st.subheader("💬 Course Discussion & Student Reviews")
    
    # Select course for viewing/adding comments
    selected_course_for_comments = st.selectbox(
        "Select a course to join the discussion:", 
        courses_df['course_name'].unique(),
        key="comment_course_select"
    )
    
    # Load Comments Dataset Safely
    comments_path = "dataset/comments.csv"
    if os.path.exists(comments_path):
        comments_df = pd.read_csv(comments_path)
    else:
        comments_df = pd.DataFrame(columns=["comment_id", "student_id", "course_name", "comment_text", "timestamp"])

    # Filter comments for the selected course
    course_comments = comments_df[comments_df['course_name'] == selected_course_for_comments]

    st.markdown("### 🗣️ Existing Peer Discussions")
    if not course_comments.empty:
        for index, row in course_comments.iterrows():
            st.markdown(f"> **{row['student_id']}** _({row['timestamp']})_:\n> {row['comment_text']}")
            st.markdown("---")
    else:
        st.info("No comments yet for this course. Be the first to share your thoughts!")

    # --- Comment Submission Form ---
    with st.form(key="comment_form", clear_on_submit=True):
        st.markdown("### ✍️ Post a Review or Question")
        user_comment = st.text_area("Write your comment or review here:")
        submit_button = st.form_submit_button(label="Post Comment")
        
        if submit_button:
            if user_comment.strip() != "":
                new_comment_id = f"C{len(comments_df) + 101}"
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                new_row = pd.DataFrame([{
                    "comment_id": new_comment_id,
                    "student_id": selected_student_id,  # Automatically uses the student selected in sidebar
                    "course_name": selected_course_for_comments,
                    "comment_text": user_comment,
                    "timestamp": current_time
                }])
                
                comments_df = pd.concat([comments_df, new_row], ignore_index=True)
                comments_df.to_csv(comments_path, index=False)
                
                st.success("Comment posted successfully!")
                st.rerun()
            else:
                st.warning("Comment cannot be empty.")

