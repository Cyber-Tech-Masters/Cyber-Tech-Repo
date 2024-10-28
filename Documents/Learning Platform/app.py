from bottle import Bottle, run, template, request, static_file, redirect, response
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Bottle()

model = None


{Liya}


{Milie}


@app.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')


@app.route('/')
def redirect_to_register():
    return redirect('/register')


@app.route('/register')
def register():
    return template('views/register')


@app.route('/register', method='POST')
def handle_register():
    username = request.forms.get('username')
    password = request.forms.get('password')

    data = load_data()

    if username in data:
        return "Username already exists! Try another username."

    data[username] = {'password': password, 'quiz_scores': [], 'mcqs': [], 'wrong_answers': []}
    save_data(data)

    response.set_cookie("username", username)

    return redirect(f"/quiz/{username}")


@app.route('/login')
def login():
    return template('views/login')


@app.route('/login', method='POST')
def handle_login():
    username = request.forms.get('username')
    password = request.forms.get('password')

    data = load_data()

    if username in data and data[username]['password'] == password:
        response.set_cookie("username", username)
        return redirect(f"/quiz/{username}")
    return "Login failed! Invalid username or password."

{Gift}


@app.route('/quiz/<username>')
def quiz(username):
    logged_in_user = request.get_cookie("username")
    if logged_in_user != username:
        return "Unauthorized access. Please log in."

    # Fetch and add questions from local dataset
    dataset_rows = fetch_local_dataset()
    questions_data = process_dataset(dataset_rows)

    if not questions_data:
        return "No questions available from the dataset."

    add_dataset_questions_to_student(username, questions_data)

    # Load the student's data
    data = load_data()

    # Fetch the first 15 questions for the quiz
    student_mcqs = data[username]['mcqs'][:15]

    print(f"Loaded questions for {username}: {student_mcqs}")

    # Pass an empty feedback variable when displaying the quiz for the first time
    return template('views/quiz', username=username, mcqs=student_mcqs, feedback="")


# Mapping of topics to study resources
resources_map = {
    "Algebra": "https://www.khanacademy.org/math/algebra",
    "Geometry": "https://www.khanacademy.org/math/geometry",
    "Probability": "https://www.khanacademy.org/math/probability",
    "Uncategorized": "https://www.khanacademy.org"
}


# Track the number of correct answers by category
def track_performance_by_category(mcqs, wrong_answers):
    # Initialize performance tracking for all categories, including Uncategorized
    performance = {"Algebra": 0, "Geometry": 0, "Probability": 0, "Uncategorized": 0}
    total_per_category = {"Algebra": 0, "Geometry": 0, "Probability": 0, "Uncategorized": 0}

    for mcq in mcqs:
        category = mcq.get("category", "Uncategorized").capitalize()

        # Safeguard: If category is missing or not in performance, default to Uncategorized
        if category not in performance:
            category = "Uncategorized"

        total_per_category[category] += 1
        if mcq["question"] not in wrong_answers:
            performance[category] += 1

    return performance, total_per_category


def generate_feedback_by_category(performance, total_per_category):
    feedback = []
    feedback.append("Category Performance:<br>")
    feedback.append("<ul>")

    for category, correct_count in performance.items():
        total_questions = total_per_category[category]
        if total_questions > 0:
            percentage = (correct_count / total_questions) * 100
            feedback.append(f"<li>{category}: {correct_count}/{total_questions} ({percentage:.2f}%)</li>")
            if percentage < 50:
                feedback.append(
                    f"<a href='{resources_map.get(category)}' target='_blank'>Learn more about {category}</a>")

    feedback.append("</ul>")
    return "<br>".join(feedback)


@app.route('/quiz', method='POST')
@app.route('/quiz', method='POST')
@app.route('/quiz', method='POST')
def handle_quiz():
    username = request.get_cookie('username')
    data = load_data()

    if username not in data:
        return "Student not found."

    if 'wrong_answers' not in data[username]:
        data[username]['wrong_answers'] = []

    mcqs = data[username]['mcqs'][:15]
    total_questions = len(mcqs)
    score = 0
    wrong_answers = []

    if total_questions == 0:
        return f"No questions were available for the quiz, {username}."

    # Compare student answers with correct answers
    for index, mcq in enumerate(mcqs):
        # Get the user's answer and correct answer, and normalize them (strip and lowercase)
        user_answer = request.forms.get(f'q{index + 1}').strip().lower()  # Normalize user input
        correct_answer = mcq['correct'].strip().lower()  # Normalize correct answer

        # Debugging print
        print(f"User Answer: {user_answer}, Correct Answer: {correct_answer}")

        # Compare the user's answer to the correct answer
        if user_answer == correct_answer:
            score += 1
        else:
            wrong_answers.append(mcq['question'])  # Track wrong answers

    # Save the student's quiz score and wrong answers
    data[username]['quiz_scores'].append(score)
    data[username]['wrong_answers'] += wrong_answers
    save_data(data)

    # Calculate percentage score
    percentage_score = (score / total_questions) * 100

    # Track performance by category
    performance, total_per_category = track_performance_by_category(mcqs, wrong_answers)

    # Generate category feedback
    category_feedback = generate_feedback_by_category(performance, total_per_category)

    # Predict the future score (rounded)
    predicted_score = predict_future_score(username)
    if predicted_score is not None:
        category_feedback += f"<br>Based on your past performance, your predicted score for the next quiz is: {predicted_score}"

    # Generate and include the regression plot in the feedback
    regression_image = create_regression_plot(username)
    if regression_image:
        category_feedback += f"<br><img src='{regression_image}' alt='Regression Line Graph'>"

    return f"Thank you for participating, {username}! You scored {score}/{total_questions} ({percentage_score:.2f}%).<br>{category_feedback} <a href='/login'>Go back to login</a>"


# Generate and save regression plot
def create_regression_plot(username):
    data = load_data()

    if username not in data:
        return None

    # Gather features (total attempts and wrong answers) and scores
    X = np.array([[i + 1, len(data[username]['wrong_answers'])] for i in range(len(data[username]['quiz_scores']))])
    y = np.array(data[username]['quiz_scores'])

    # Fit the linear regression model
    model = LinearRegression()
    model.fit(X[:, 0].reshape(-1, 1), y)  # Fit on total attempts vs. score

    # Predict using the linear model
    predictions = model.predict(X[:, 0].reshape(-1, 1))

    # Create the plot
    plt.figure(figsize=(6, 4))
    plt.scatter(X[:, 0], y, color='blue', label='Actual Scores')
    plt.plot(X[:, 0], predictions, color='red', label='Regression Line')
    plt.title(f"Regression Line for {username}")
    plt.xlabel('Total Attempts')
    plt.ylabel('Quiz Scores')
    plt.legend()

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the image to base64 and return as a string
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return f"data:image/png;base64,{image_base64}"


if __name__ == "__main__":
    train_model()  # Train the model at startup
    run(app, host='localhost', port=8080, debug=True)
