from flask import render_template,redirect,request,Flask,flash
import mysql.connector
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor

app=Flask(__name__)
app.secret_key='hi'




mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3307",
    database='fitness'
)

mycursor = mydb.cursor()

def executionquery(query,values):
    mycursor.execute(query,values)
    mydb.commit()
    return

def retrivequery1(query,values):
    mycursor.execute(query,values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        c_password = request.form['confirm_password']
        if password == c_password:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = []
            for i in email_data:
                email_data_list.append(i[0])
            if email.upper() not in email_data_list:
                query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                values = (name, email, password)
                executionquery(query, values)
                flash("Registration successful!", "success")
                return render_template('login.html', message="Successfully Registered!")
            return render_template('register.html', message="This email ID is already exists!")
        return render_template('register.html', message="Conform password is not match!")
    return render_template('register.html')



@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])
        
        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)
            if password.upper() == password__data[0][0]:
                global user_email
                user_email = email

                return redirect("/home")
            return render_template('login.html', message= "Invalid Password!!")
        return render_template('login.html', message= "This email ID does not exist!")
    return render_template('login.html')


@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template('home.html')

models = joblib.load(open('models/random.joblib', 'rb'))
scaler = joblib.load(open('models/scal.joblib', 'rb'))

@app.route('/prediction', methods=['POST', 'GET'])
def prediction():
    if request.method == 'POST':
        try:
            density = float(request.form['density'])
            age = int(request.form['age'])
            weight = float(request.form['weight'])
            neck = float(request.form['neck'])
            chest = float(request.form['chest'])
            abdomen = float(request.form['abdomen'])
            hip = float(request.form['hip'])
            thigh = float(request.form['thigh'])
            knee = float(request.form['knee'])
            biceps = float(request.form['biceps'])

            input_features = np.array([[density, age, weight, neck, chest, abdomen, hip, thigh, knee, biceps]])

            # Scale the input
            input_scaled = scaler.transform(input_features)

            # Make prediction
            prediction = models.predict(input_scaled)
            rounded_prediction = round(prediction[0], 2)
            print(rounded_prediction)

            # Categorize the body fat percentage and provide suggestions
            if rounded_prediction <= 2:
                condition="Bellow Essential Fat"
                definition = " This is a dangerously low body fat percentage, lower than the essential fat required for normal bodily functions. This condition can lead to serious health risks, including hormone imbalances, immune system suppression, and organ dysfunction. Immediate intervention to restore proper nutrition and energy reserves is required."
                food_suggestions = """Increase calorie intake with a balanced diet that includes high-quality proteins (chicken, fish, eggs), healthy fats (olive oil, avocados), and carbohydrates (sweet potatoes, brown rice, quinoa). Consider adding nutrient-dense snacks like nuts, seeds, and whole grains."""
                exercise_suggestions = """Focus on restoring energy balance through light physical activities like walking or gentle yoga. Avoid intense exercise until energy reserves are restored."""
            elif rounded_prediction <=6:
                condition="Essential"
                definition = " This is the minimum fat required for the body to function properly. It includes fat essential for hormone production, organ protection, and cell function. This range is generally seen in athletes and those with very low body fat, but it can be a risk if not managed properly."
                food_suggestions = """Increase healthy fat intake with nutrient-dense foods such as avocados, nuts, seeds, and fatty fish (salmon, mackerel). Incorporate calorie-rich meals, including complex carbs like whole grains, legumes, and starchy vegetables."""
                exercise_suggestions = """Gentle exercises like walking, swimming, or stretching to support recovery. Focus on light, low-impact activities that don't deplete energy stores."""
            elif  rounded_prediction <= 13:
                condition="Athletes"
                definition = "This body fat percentage is typically seen in athletes who have a lean physique for performance purposes. This range supports optimal athletic performance, particularly in sports requiring endurance or speed. It indicates a healthy balance of muscle mass and fat."
                food_suggestions = """Prioritize lean proteins (chicken, turkey, fish), complex carbohydrates (sweet potatoes, quinoa, oats), and healthy fats (avocados, nuts, olive oil). Hydrate well and consume balanced meals throughout the day to support muscle recovery and performance."""
                exercise_suggestions = """Continue a mix of strength training and cardio exercises to maintain muscle tone and improve cardiovascular fitness. Include flexibility and mobility work to avoid injury."""
            elif rounded_prediction <= 20:
                condition="Fitness"
                definition = "This is a healthy body fat percentage range for individuals who engage in regular physical activity. People within this category generally have good muscle tone, cardiovascular health, and maintain a healthy weight. It is an ideal range for those who focus on fitness and wellness."
                food_suggestions = """Follow a balanced diet with proteins (lean meats, fish, tofu), healthy fats (avocados, almonds), and vegetables. Minimize processed foods and refined sugars. Incorporate nutrient-dense snacks like Greek yogurt, mixed nuts, and protein shakes."""
                exercise_suggestions = """Maintain a routine that includes both strength training (weights, bodyweight exercises) and aerobic exercises (running, cycling, swimming) to maintain a healthy weight and cardiovascular health."""
            elif rounded_prediction <= 30:
                condition=" Avarage"
                definition = "This is a common body fat percentage range for most adults. People in this range are typically at moderate risk for lifestyle-related health issues such as high cholesterol, diabetes, and heart disease if they do not follow healthy eating and exercise habits."
                food_suggestions = """Focus on a variety of whole foods, including lean proteins (chicken, fish), healthy fats (olive oil, nuts), and whole grains (brown rice, quinoa). Limit processed foods, sugars, and refined carbs. Ensure you are eating balanced meals and snacks throughout the day."""
                exercise_suggestions = """Incorporate both strength training (resistance bands, dumbbells) and aerobic exercises (walking, jogging, cycling) to maintain fitness and promote a healthy metabolism."""
            else:

                condition= "Obese "   
                definition=" Obesity is associated with a higher risk of health issues such as heart disease, diabetes, hypertension, and joint problems. People in this range often have excess body fat that can affect overall health, and weight loss strategies are crucial to reduce these risks."
                food_suggestions = """Work towards a calorie-controlled diet with whole foods like vegetables, lean proteins (chicken, turkey, tofu), and whole grains (brown rice, quinoa). Cut down on sugars, refined carbs, and processed foods. Aim for balanced meals with plenty of fiber from vegetables and whole grains."""
                exercise_suggestions = """Start with light, low-impact exercises such as walking, swimming, or cycling, and gradually increase intensity as your fitness improves. Include strength training to build muscle mass and boost metabolism."""

                

            return render_template('prediction.html', prediction=rounded_prediction, condition=condition, 
                       definition=definition, food_suggestions=food_suggestions, exercise_suggestions=exercise_suggestions)

        except Exception as e:
            return render_template('prediction.html', prediction=f"Error: {str(e)}")
    
    return render_template('prediction.html', prediction=None, category=None, food_suggestions=None, exercise_suggestions=None)



@app.route('/model', methods=['GET', 'POST'])
def model():
    accuracy = None  # Initialize accuracy to prevent undefined variable error
    if request.method == 'POST':
        algorithm = request.form.get('algo')  # Fetch selected algorithm

        # Corrected algorithm names for consistency
        if algorithm == "Random Forest":
            accuracy = 97.52
        elif algorithm == "XGBoost":
            accuracy = 96.86
        elif algorithm == "LSTM":
            accuracy = 91.55

    return render_template('model.html', accuracy=accuracy)


if __name__=='__main__':
    app.run(debug=True)