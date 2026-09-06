import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_data():
    """Load all required datasets from dataset directory."""
    students = pd.read_csv('dataset/students.csv')
    courses = pd.read_csv('dataset/courses.csv')
    interactions = pd.read_csv('dataset/interactions.csv')
    return students, courses, interactions

def popularity_recommendations(courses_df, top_n=5):
    """Model 1: Top rated courses system-wide."""
    popular = courses_df.sort_values(by='avg_rating', ascending=False)
    return popular[['course_id', 'course_name', 'domain', 'avg_rating']].head(top_n)

def content_based_recommendations(student_id, students_df, courses_df, top_n=5):
    """Model 2: TF-IDF & Cosine Similarity based on Student Interest."""
    student = students_df[students_df['student_id'] == student_id]
    if student.empty:
        return courses_df[['course_id', 'course_name', 'domain', 'difficulty']].head(top_n)
    
    interest = student.iloc[0]['interests']
    
    # TF-IDF Vectorization on course skills and domain
    tfidf = TfidfVectorizer(stop_words='english')
    courses_df['features'] = courses_df['domain'].fillna('') + ' ' + courses_df['skills'].fillna('')
    tfidf_matrix = tfidf.fit_transform(courses_df['features'])
    
    # User Profile Vector
    user_vector = tfidf.transform([interest])
    
    # Compute Cosine Similarity Scores
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()
    
    recs = courses_df.copy()
    recs['confidence_score'] = similarity_scores.round(2)
    recs = recs.sort_values(by='confidence_score', ascending=False)
    
    return recs[['course_id', 'course_name', 'domain', 'difficulty', 'confidence_score']].head(top_n)

def hybrid_recommendations(student_id, students_df, courses_df, interactions_df, top_n=5):
    """Model 3: Hybrid Model combining Content Match & Peer Ratings."""
    content_recs = content_based_recommendations(student_id, students_df, courses_df, top_n=len(courses_df))
    
    # Calculate average rating per course from interaction matrix
    peer_ratings = interactions_df.groupby('course_id')['rating'].mean().reset_index()
    peer_ratings.rename(columns={'rating': 'peer_score'}, inplace=True)
    
    hybrid_df = content_recs.merge(peer_ratings, on='course_id', how='left').fillna({'peer_score': 3.0})
    
    # Calculate Hybrid Score: 60% Content Match + 40% Peer Rating (normalized to 0-1)
    hybrid_df['hybrid_score'] = (0.6 * hybrid_df['confidence_score']) + (0.4 * (hybrid_df['peer_score'] / 5.0))
    hybrid_df['hybrid_score'] = hybrid_df['hybrid_score'].round(2)
    
    hybrid_df = hybrid_df.sort_values(by='hybrid_score', ascending=False)
    return hybrid_df[['course_id', 'course_name', 'domain', 'difficulty', 'hybrid_score']].head(top_n)