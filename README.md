# SmartFinance

SmartFinance is a Python web application for loan assessment,
financial risk analysis, insurance estimates and EMI planning.

The project is designed with a simple and understandable stack:

- Python
- Flask
- SQLite
- Pandas
- Scikit-learn
- Joblib
- HTML
- CSS
- JavaScript

No MongoDB, React or Node.js is required.


## Main Features

- Home page
- User registration
- User login/logout
- User dashboard
- Loan application
- Machine-learning loan prediction
- Financial risk score
- Application history
- EMI calculator
- Vehicle insurance estimate
- Medical insurance estimate
- Contact Us
- Basic administrator dashboard


## Project Structure

```text
SmartFinance/
│
├── app.py
├── requirements.txt
├── README.md
├── PROJECT_STRUCTURE.txt
├── run_windows.bat
│
├── data/
│   └── loan_data.csv
│
├── models/
│   └── loan_model.pkl
│
├── ml/
│   └── train_model.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── loan.html
│   ├── loan_result.html
│   ├── emi.html
│   ├── vehicle.html
│   ├── medical.html
│   ├── contact.html
│   └── admin.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── main.js
```


## Run the Project

### Step 1: Open the folder

Open the extracted SmartFinance folder in VS Code.


### Step 2: Create a virtual environment

Windows:

```text
python -m venv venv
```

Activate it:

```text
venv\Scripts\activate
```


### Step 3: Install packages

```text
pip install -r requirements.txt
```


### Step 4: Run the application

```text
python app.py
```


### Step 5: Open the website

Open:

```text
http://127.0.0.1:5000
```


## Retrain the ML Model

If you want to train the model again:

```text
python ml/train_model.py
```

The trained model is saved to:

```text
models/loan_model.pkl
```


## Important Note

The loan result is a machine-learning prediction for this
application and is not an official bank lending decision.

The financial risk score shown by the application is a
project-specific indicator. It is not an official CIBIL score.

The vehicle and medical insurance pages are academic
rule-based estimates. They are not real insurance quotes.


## Contact

mohitki7780264@gmail.com
