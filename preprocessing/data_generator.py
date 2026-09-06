import pandas as pd
import numpy as np
import random
import os

os.makedirs('dataset', exist_ok=True)

# 1. Generate Courses Data
courses = [
    {"course_id": "C001", "course_name": "Python Programming", "domain": "CS", "difficulty": "Beginner", "skills": "python basics", "duration": "6 weeks", "instructor": "Dr. Pallavi Mishra", "avg_rating": 4.5},
    {"course_id": "C002", "course_name": "Data Structures", "domain": "CS", "difficulty": "Intermediate", "skills": "arrays trees graphs", "duration": "8 weeks", "instructor": "Prof. R. Sharma", "avg_rating": 4.6},
    {"course_id": "C003", "course_name": "Machine Learning", "domain": "AI", "difficulty": "Intermediate", "skills": "python ml scikit-learn", "duration": "10 weeks", "instructor": "Dr. Krishna Madhuri", "avg_rating": 4.8},
    {"course_id": "C004", "course_name": "Deep Learning", "domain": "AI", "difficulty": "Advanced", "skills": "neural networks pytorch", "duration": "12 weeks", "instructor": "Dr. Krishna Madhuri", "avg_rating": 4.7},
    {"course_id": "C005", "course_name": "Computer Vision", "domain": "AI", "difficulty": "Advanced", "skills": "opencv cnn image processing", "duration": "8 weeks", "instructor": "Dr. A. Verma", "avg_rating": 4.6},
]
pd.DataFrame(courses).to_csv('dataset/courses.csv', index=False)

# 2. Generate Students Data
students = []
depts = ['CSE', 'ECE', 'AI', 'Data Science']
interests_list = ['AI', 'Data Science', 'Web Development', 'Cloud']

for i in range(1, 11):
    s_id = f"S{i:03d}"
    completed = random.sample(["C001", "C002", "C003"], k=random.randint(1, 2))
    students.append({
        "student_id": s_id,
        "department": random.choice(depts),
        "cgpa": round(random.uniform(6.5, 9.8), 2),
        "interests": random.choice(interests_list),
        "previously_completed_courses": ";".join(completed)
    })
pd.DataFrame(students).to_csv('dataset/students.csv', index=False)

# 3. Generate Interaction & Activity Data
interactions = []
for i in range(1, 11):
    s_id = f"S{i:03d}"
    for c in courses:
        if random.random() > 0.3:
            viewed = 1
            completed = random.choice([0, 1])
            interactions.append({
                "student_id": s_id,
                "course_id": c["course_id"],
                "courses_viewed": viewed,
                "courses_completed": completed,
                "learning_progress": 100 if completed else random.randint(10, 90),
                "quiz_scores": random.randint(60, 100),
                "time_spent": round(random.uniform(1.0, 25.0), 1),
                "likes": random.choice([0, 1]),
                "rating": random.randint(3, 5)
            })
pd.DataFrame(interactions).to_csv('dataset/interactions.csv', index=False)

print("✅ Updated datasets successfully created in dataset/ directory!")