# app.py
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    name = request.form['name']
    gender = request.form['gender']
    weight_lbs = float(request.form['weight_lbs'])
    height_ft = int(request.form['height_ft'])
    height_in = int(request.form['height_in'])
    target_weight = float(request.form['target_weight'])
    weekly_loss = float(request.form['weekly_loss'])
    
    # Reset result variables
    result_line_1 = None
    result_line_2 = None
    result_line_3 = None
    result_line_4 = None
    result_line_5 = None
    result_line_6 = None

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

    # Prepare result lines
    result_line_1 = f"1. Estimated BMR (Basal Metabollic Rate): {bmr} calories/day"
    result_line_2 = f"2. Estimated TDEE (Total Daily Energy Expenditure): {tdee} calories/day"
    result_line_3 = f"3. Target Weight: {target_weight} lbs"
    result_line_4 = f"4. Weekly Weight Loss Goal: {weekly_loss} lbs"
    result_line_5 = f"5. Recommended Daily Calorie Intake: {target_calories} calories"
    result_line_6 = f"6. Estimated Time to Reach Target Weight: {weeks_to_reach_target_weight} weeks"

    # Render the template with result lines
    return render_template('index.html', 
                            name=name,
                            result_line_1=result_line_1,
                            result_line_2=result_line_2,
                            result_line_3=result_line_3,
                            result_line_4=result_line_4,
                            result_line_5=result_line_5,
                            result_line_6=result_line_6)

if __name__ == '__main__':
    app.run(debug=True)


