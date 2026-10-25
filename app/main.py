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

# Navigation Tabs (Expanded to 6 Tabs)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Hybrid & Personalized", 
    "🔥 Popularity", 
    "📊 Student Activity & Progress",
    "🔍 Search & Catalog", 
    "💬 Student Feedback",
    "🌍 External Opportunities"
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
    st.subheader("💬 Course Ratings, Reviews & Discussions")
    
    # Select course for viewing/adding comments
    selected_course_for_comments = st.selectbox(
        "Select a course to view or review:", 
        courses_df['course_name'].unique(),
        key="comment_course_select"
    )
    
    # Load Comments Dataset Safely
    comments_path = "dataset/comments.csv"
    if os.path.exists(comments_path):
        comments_df = pd.read_csv(comments_path)
        if 'rating' not in comments_df.columns:
            comments_df['rating'] = 5  # Fallback if rating column is missing
    else:
        comments_df = pd.DataFrame(columns=["comment_id", "student_id", "course_name", "rating", "comment_text", "timestamp"])

    # Filter comments for the selected course
    course_comments = comments_df[comments_df['course_name'] == selected_course_for_comments]

    st.markdown("### 🗣️ Existing Student Reviews & Ratings")
    if not course_comments.empty:
        for index, row in course_comments.iterrows():
            stars = "⭐" * int(row.get('rating', 5))
            st.markdown(f"> **{row['student_id']}** - {stars} _({row['timestamp']})_:\n> {row['comment_text']}")
            st.markdown("---")
    else:
        st.info("No reviews yet for this course. Be the first to rate and review!")

    # --- Comment & Rating Submission Form (Using Dynamic Unique Keys) ---
    with st.form(key=f"comment_form_{selected_course_for_comments}", clear_on_submit=True):
        st.markdown("### ✍️ Leave Your Rating & Review")
        user_rating = st.slider("Course Rating (1 to 5 Stars)", 1, 5, 5, key=f"rating_slider_{selected_course_for_comments}")
        user_comment = st.text_area("Write your review or question here:", key=f"comment_text_{selected_course_for_comments}")
        submit_button = st.form_submit_button(label="Submit Review")
        
        if submit_button:
            if user_comment.strip() != "":
                new_comment_id = f"C{len(comments_df) + 101}"
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                new_row = pd.DataFrame([{
                    "comment_id": new_comment_id,
                    "student_id": selected_student_id,  # Uses student selected in sidebar
                    "course_name": selected_course_for_comments,
                    "rating": user_rating,
                    "comment_text": user_comment,
                    "timestamp": current_time
                }])
                
                comments_df = pd.concat([comments_df, new_row], ignore_index=True)
                comments_df.to_csv(comments_path, index=False)
                
                st.success("Review and rating submitted successfully!")
                st.rerun()
            else:
                st.warning("Review text cannot be empty.")
    # TAB 6: EXTERNAL OPPORTUNITIES & HACKATHONS
with tab6:
    st.subheader("🌍 External Academic Programs & Hackathons")
    st.markdown("Boost your resume with curated external hackathons, research opportunities, and professional certifications tailored to your skills.")
    
    # Load External Programs Dataset
    ext_path = "dataset/external_programs.csv"
    if os.path.exists(ext_path):
        ext_df = pd.read_csv(ext_path)
        
        # Smart Filtering: Match programs where required skills overlap with student interests
        student_interest = student_info['interests'].lower()
        
        # Filter matching programs or show all if no exact keyword match
        matched_ext = ext_df[
            ext_df['skills_required'].str.lower().apply(lambda x: any(word in x for word in student_interest.split()))
        ]
        
        if matched_ext.empty:
            matched_ext = ext_df  # Fallback to show all if no direct overlap
            
        st.markdown(f"### Recommended Opportunities for {selected_student_id} (Interest: _{student_info['interests']}_)")
        st.dataframe(matched_ext, width="stretch")
        
        st.markdown("---")
        st.markdown("### 📝 Register / Apply for Programs")
        selected_program = st.selectbox("Select a program to view details:", ext_df['program_name'].unique())
        
        prog_details = ext_df[ext_df['program_name'] == selected_program].iloc[0]
        st.info(f"**Category:** {prog_details['category']} | **Mode:** {prog_details['mode']} | **Status/Link:** {prog_details['deadline_or_link']}")
        
        if st.button("Express Interest / Apply"):
            st.success(f"Successfully registered student {selected_student_id} for {selected_program}! Confirmation email simulated.")
    else:
        st.warning("External programs dataset not found.")
    
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

