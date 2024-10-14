import json
import os
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score

#Load all JSON files from a specified folder and assign a label to the data
def load_data_from_folder(folder_path, label):
    data = []
    labels = []

    # Go through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as json_file:
                questions = json.load(json_file)

                # Extract the problem text
                if 'problem' in questions:
                    data.append(questions['problem'])
                    labels.append(label)

    return data, labels

algebra_path = 'C:/Users/27640/PycharmProjects/math_project/.venv/train/algebra'
geometry_path = 'C:/Users/27640/PycharmProjects/math_project/.venv/train/geometry'
counting_path = 'C:/Users/27640/PycharmProjects/math_project/.venv/train/counting_and_probability'

# Load data from each folder
algebra_data, algebra_labels = load_data_from_folder(algebra_path, 'Algebra')
print(f"Loaded {len(algebra_data)} questions from Algebra")

geometry_data, geometry_labels = load_data_from_folder(geometry_path, 'Geometry')
print(f"Loaded {len(geometry_data)} questions from Geometry")

counting_data, counting_labels = load_data_from_folder(counting_path, 'Counting and Probability')
print(f"Loaded {len(counting_data)} questions from Counting and Probability")

# Combine data and labels from all topics
data = algebra_data + geometry_data + counting_data
labels = algebra_labels + geometry_labels + counting_labels

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

