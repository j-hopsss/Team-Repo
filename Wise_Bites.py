from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user

app = Flask(__name__)

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
            return redirect(url_for('redirect_user'))
        else:
            error = "Invalid username or password. Please try again."
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = {'username': username, 'password': password}
            return redirect(url_for('login'))
        else:
            error = "Username already exists. Please choose a different username."
            return render_template('signup.html', error=error)
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Redirect user based on their login status and actions
# Redirect user to the homepage
@app.route('/')
def redirect_user():
    return redirect(url_for('home'))

# Homepage route
@app.route('/home')
def home():
    return render_template('home.html', logged_in=current_user.is_authenticated)

# Calculator route
@app.route('/calculator', methods=['GET', 'POST'])
@login_required
def calculate():
    if request.method == 'POST':
        name = request.form['name']
        weight_lbs = float(request.form['weight_lbs'])
        height_ft = int(request.form['height_ft'])
        height_in = int(request.form['height_in'])
        target_weight = float(request.form['target_weight'])
        weekly_change = float(request.form['weekly_change'])
        gender = request.form['gender']
        
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
        # Adjust the caloric deficit or surplus based on the desired weekly weight change
        if target_weight > weight_lbs:
            # Target weight is higher, user wants to gain weight
            weekly_change_abs = abs(weekly_change)  # Ensure weekly change is positive
            caloric_change_per_day = weekly_change_abs * 500  # Aim for a 500-calorie change per day for each pound of weight change per week
            target_calories = round(tdee + caloric_change_per_day)
        else:
            # Target weight is lower, user wants to lose weight
            weekly_change_abs = abs(weekly_change)  # Ensure weekly change is positive
            caloric_change_per_day = weekly_change_abs * 500  # Aim for a 500-calorie change per day for each pound of weight change per week
            target_calories = round(tdee - caloric_change_per_day)

        # Estimate the number of weeks it should take to reach the target weight
        weeks_to_reach_target_weight = round((target_weight - weight_lbs) / weekly_change)

        # Prepare result lines
        result_line_1 = f"1. Estimated BMR (Basal Metabolic Rate): {bmr} calories/day"
        result_line_2 = f"2. Estimated TDEE (Total Daily Energy Expenditure): {tdee} calories/day"
        result_line_3 = f"3. Target Weight: {target_weight} lbs"
        result_line_4 = f"4. Desired Weekly Weight Change: {weekly_change} lbs"
        result_line_5 = f"5. Recommended Daily Calorie Intake: {target_calories} calories"
        result_line_6 = f"6. Estimated Time to Reach Target Weight: {abs(weeks_to_reach_target_weight)} weeks"

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
        # If it's a GET request, just render the calculator template without processing form data
        return render_template('calculator.html')

if __name__ == '__main__':
    app.run(debug=True)
