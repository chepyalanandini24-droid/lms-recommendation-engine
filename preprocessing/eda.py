import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs('notebooks', exist_ok=True)

# Phase 2: Preprocessing
courses = pd.read_csv('dataset/courses.csv')
students = pd.read_csv('dataset/students.csv')
interactions = pd.read_csv('dataset/interactions.csv')

# Handle Missing & Duplicates
courses.drop_duplicates(inplace=True)
students.drop_duplicates(inplace=True)
interactions.drop_duplicates(inplace=True)

# Categorical Encoding & Normalization
students['dept_code'] = students['department'].astype('category').cat.codes
students['cgpa_norm'] = (students['cgpa'] - students['cgpa'].min()) / (students['cgpa'].max() - students['cgpa'].min())

# Phase 3: Exploratory Data Analysis (EDA Visualizations)
plt.figure(figsize=(12, 8))

# 1. Popular Courses
plt.subplot(2, 2, 1)
sns.barplot(data=courses, x='avg_rating', y='course_name', palette='viridis')
plt.title('Most Popular Courses by Avg Rating')

# 2. Student Interests
plt.subplot(2, 2, 2)
students['interests'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
plt.title('Student Interest Distribution')

# 3. Rating Distribution
plt.subplot(2, 2, 3)
sns.histplot(interactions['rating'], kde=True, bins=5, color='purple')
plt.title('Interaction Rating Distribution')

# 4. Department Preferences
plt.subplot(2, 2, 4)
sns.countplot(data=students, x='department', palette='Blues')
plt.title('Student Count by Department')

plt.tight_layout()
plt.savefig('notebooks/eda_visualizations.png')
print("✅ Phase 2 Preprocessing & Phase 3 EDA completed. Saved graphs to notebooks/eda_visualizations.png")