# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import requests

app = Flask(__name__)

APP_ID = "e64946d4"
APP_KEY = "1181d64ea87ac046c421e171ec31f6c2"
API_URL = "https://api.edamam.com/search"

app.secret_key = 'csc132'  # Change this to a random secret key
login_manager = LoginManager()
login_manager.init_app(app)

# Mock user database
users = {'user1': {'username': 'user1', 'password': 'password1'}}

# User class for Flask-Login
class User(UserMixin):
    pass

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(username):
    if username in users:
        user = User()
        user.id = username
        return user

# Routes for login, signup, dashboard
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = {'username': username, 'password': password}
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Retrieve calculated values from session
    bmr = session.get('bmr')
    tdee = session.get('tdee')
    target_weight = session.get('target_weight')
    weekly_loss = session.get('weekly_loss')
    target_calories = session.get('target_calories')
    weeks_to_reach_target_weight = session.get('weeks_to_reach_target_weight')
    height = session.get('height')
    weight = session.get('weight')
    
    return render_template('dashboard.html',
                            bmr=bmr,
                            tdee=tdee,
                            target_weight=target_weight,
                            weekly_loss=weekly_loss,
                            target_calories=target_calories,
                            weeks_to_reach_target_weight=weeks_to_reach_target_weight,
                            height=height,
                            weight=weight)

@app.route('/mealplans')
@login_required
def mealPlans():
    target_calories = session.get('target_calories')
    breakfast_calories = int(0.3 * target_calories)
    lunch_calories = int(0.4 * target_calories)
    dinner_calories = int(0.3 * target_calories)

    # Define the parameters for the Edamam API request for breakfast
    breakfast_params = {
        'q': 'recipe',
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'calories': f"{breakfast_calories}",
        'mealType': 'breakfast',
        'from': 0,
        'to': 1
    }

    # Make a GET request to the Edamam API for breakfast
    breakfast_response = requests.get(API_URL, params=breakfast_params)

    # Define the parameters for the Edamam API request for lunch
    lunch_params = {
        'q': 'recipe',
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'calories': f"{lunch_calories}",
        'mealType': 'lunch',
        'from': 0,
        'to': 1
    }

    # Make a GET request to the Edamam API for lunch
    lunch_response = requests.get(API_URL, params=lunch_params)

    # Define the parameters for the Edamam API request for dinner
    dinner_params = {
        'q': 'recipe',
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'calories': f"{dinner_calories}",
        'mealType': 'dinner',
        'from': 0,
        'to': 1
    }

    # Make a GET request to the Edamam API for dinner
    dinner_response = requests.get(API_URL, params=dinner_params)

    # Process breakfast response
    if breakfast_response.status_code == 200:
        breakfast_data = breakfast_response.json()
        breakfast_recipes = extract_recipes(breakfast_data)
    else:
        breakfast_recipes = []

    # Process lunch response
    if lunch_response.status_code == 200:
        lunch_data = lunch_response.json()
        lunch_recipes = extract_recipes(lunch_data)
    else:
        lunch_recipes = []

    # Process dinner response
    if dinner_response.status_code == 200:
        dinner_data = dinner_response.json()
        dinner_recipes = extract_recipes(dinner_data)
    else:
        dinner_recipes = []

    return render_template('mealplans.html',
                           target_calories=target_calories,
                           breakfast_recipes=breakfast_recipes,
                           lunch_recipes=lunch_recipes,
                           dinner_recipes=dinner_recipes)


def extract_recipes(data):
    recipes = []
    for hit in data.get('hits', []):
        recipe_data = hit.get('recipe')
        recipe_info = {
            'label': recipe_data.get('label'),
            'image': recipe_data.get('image'),
            'ingredients': recipe_data.get('ingredientLines'),
            'total_calories': recipe_data.get('calories')
        }
        recipes.append(recipe_info)
    return recipes


# In your dashboard.html template, you can iterate over the recipes and display them
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Calculator routes
@app.route('/')
def home():
    logged_in = current_user.is_authenticated  # Check if user is logged in
    return render_template('home.html', logged_in=logged_in)

@app.route('/calculator', methods=['GET', 'POST'])
def calculate():
    #Initialize result lines for display later
    result_line_1 = None
    result_line_2 = None
    result_line_3 = None
    result_line_4 = None
    result_line_5 = None
    result_line_6 = None
    
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        weight_lbs = float(request.form['weight_lbs'])
        height_ft = int(request.form['height_ft'])
        height_in = int(request.form['height_in'])
        target_weight = float(request.form['target_weight'])
        weekly_loss = float(request.form['weekly_loss'])
        

        # Convert height from feet and inches to inches
        height_inches = (height_ft * 12) + height_in
        
        # Calculate BMR (Basal Metabolic Rate) using Harris-Benedict equation
        if gender == 'M':
            bmr = round((10 * weight_lbs) + (6.25 * height_inches) - (5 * 25) + 5)
        else:  # Female
            bmr = round((10 * weight_lbs) + (6.25 * height_inches) - (5 * 25) - 161)

        # Calculate TDEE (Total Daily Energy Expenditure)
        # Assuming a sedentary lifestyle for simplicity
        tdee = round(bmr * 1.2)

        # Calculate the recommended calorie intake per day to achieve the target weight
        # Adjust the caloric deficit based on the desired weekly weight loss (1-3 lbs)
        caloric_deficit_per_day = weekly_loss * 500  # Aim for a 500-calorie deficit per day for each pound of weight loss per week
        target_calories = round(tdee - caloric_deficit_per_day)

        # Estimate the number of weeks it should take to reach the target weight
        weeks_to_reach_target_weight = round((weight_lbs - target_weight) / weekly_loss)
        
        # Store calculated values in session
        session['bmr'] = bmr
        session['tdee'] = tdee
        session['target_weight'] = target_weight
        session['weekly_loss'] = weekly_loss
        session['target_calories'] = target_calories
        session['weeks_to_reach_target_weight'] = weeks_to_reach_target_weight
        session['height'] = str(height_ft) + "'" + str(height_in) + "''"
        session['weight'] = str(weight_lbs)

        # Prepare result lines
        result_line_1 = f"1. Estimated BMR (Basal Metabolic Rate): {bmr} calories/day"
        result_line_2 = f"2. Estimated TDEE (Total Daily Energy Expenditure): {tdee} calories/day"
        result_line_3 = f"3. Target Weight: {target_weight} lbs"
        result_line_4 = f"4. Weekly Weight Loss Goal: {weekly_loss} lbs"
        result_line_5 = f"5. Recommended Daily Calorie Intake: {target_calories} calories"
        result_line_6 = f"6. Estimated Time to Reach Target Weight: {weeks_to_reach_target_weight} weeks"

        # Render the template with result lines
        return render_template('calculator.html', 
                                name=name,
                                result_line_1=result_line_1,
                                result_line_2=result_line_2,
                                result_line_3=result_line_3,
                                result_line_4=result_line_4,
                                result_line_5=result_line_5,
                                result_line_6=result_line_6)
    else:
        return render_template('calculator.html')
    




if __name__ == '__main__':
    app.run(debug=True)
