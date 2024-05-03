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
    
def search_recipes(query, calories_from=None, calories_to=None, limit=None):
    headers = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
    }
    params = {
        "q": query,
    }
    
    # Add optional parameters if provided
    if calories_from is not None:
        params["calories_from"] = calories_from
    if calories_to is not None:
        params["calories_to"] = calories_to
    if limit is not None:
        params["limit"] = limit

    response = requests.get(API_URL, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error:", response.status_code)
        return None



def generate_meal_plans(target_calories, meal_type):
    # Determine caloric distribution (e.g., 30% for breakfast, 40% for lunch, 30% for dinner)
    if meal_type == 'breakfast':
        calories_percentage = 0.3
    elif meal_type == 'lunch':
        calories_percentage = 0.4
    elif meal_type == 'dinner':
        calories_percentage = 0.3
    else:
        raise ValueError("Invalid meal type. Must be 'breakfast', 'lunch', or 'dinner'.")

    meal_calories = int(target_calories * calories_percentage)

    # Query the database for recipes within the caloric range for the specified meal
    meal_recipes = search_recipes(query="", calories_from=meal_calories - 50,
                                   calories_to=meal_calories + 50,
                                   limit=1)  # Limit to a reasonable number of options
    
    if meal_recipes is None:
        print("No recipes found for", meal_type)
        return None

    if len(meal_recipes) == 0:
        print("No recipes found for", meal_type)
        return None

    # Select a suitable recipe for the specified meal
    selected_meal = meal_recipes[0]  # Assuming the first recipe is selected
    
    # Prepare the meal data
    meal_data = {
        'name': selected_meal.get('name', ''),
        'image_url': selected_meal.get('image_url', ''),
        'calories': selected_meal.get('calories', ''),
        'ingredients': selected_meal.get('ingredients', [])
    }
    
    print("Meal Data for", meal_type, ":", meal_data)

    return meal_data




def select_recipe(recipes, target_calories):
    # Choose the recipe with the closest caloric value to the target
    selected_recipe = None
    min_difference = float('inf')

    for recipe in recipes:
        calories = recipe['calories']
        difference = abs(calories - target_calories)
        if difference < min_difference:
            min_difference = difference
            selected_recipe = recipe

    return selected_recipe

@app.route('/mealplans')
@login_required
def mealPlan():
    # Retrieve target calories from session
    target_calories = session.get('target_calories')
    
    # Generate meal plans for each meal type
    breakfast = generate_meal_plans(target_calories, 'breakfast')
    lunch = generate_meal_plans(target_calories, 'lunch')
    dinner = generate_meal_plans(target_calories, 'dinner')
    
    # Create a dictionary containing meal data for each meal type
    data = {
        'breakfast': breakfast,
        'lunch': lunch,
        'dinner': dinner
    }
    
    # Render the mealplans.html template with meal data
    return render_template('mealplans.html', data=data)



if __name__ == '__main__':
    app.run(debug=True)
