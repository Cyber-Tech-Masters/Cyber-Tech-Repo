import json
import os
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score

#Load JSON file from a specified folder and assign a label to the data
def load_data_from_file(file_path, label):
    data = []
    labels = []

    with open(file_path, 'r') as json_file:
        questions = json.load(json_file)
        
    # Go through the list of questions and extract the 'problem' text
     for question in questions:
        if 'problem' in questions:
         data.append(questions['problem'])
         labels.append(label)

    return data, labels

# Path to JSON files
algebra_path = ''
geometry_path = ''
counting_path = ''

# Load data from each file
algebra_data, algebra_labels = load_data_from_file(algebra_file, 'Algebra')
print(f"Loaded {len(algebra_data)} questions from Algebra")

geometry_data, geometry_labels = load_data_from_file(geometry_file, 'Geometry')
print(f"Loaded {len(geometry_data)} questions from Geometry")

counting_data, counting_labels = load_data_from_file(counting_file, 'Counting and Probability')
print(f"Loaded {len(counting_data)} questions from Counting and Probability")

# Combine data and labels from all topics
data = algebra_data + geometry_data + counting_data
labels = algebra_labels + geometry_labels + counting_labels

# Check if data is loaded correctly
if not data:
    print("No data loaded. Make sure the JSON files contain questions with the 'problem' key.")
    exit()

# Convert text data using CountVectorizer to feature vectors
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(data)

# Split data into training and test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)

# Initialize the Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model on training data
model.fit(X_train, y_train)

# Make predictions on the test data
y_pred = model.predict(X_test)

# Evaluate the model accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

