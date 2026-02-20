# 🍳 Smart Indian Pantry - Your Ingredients, Our Recipes

Smart Indian Pantry is a full-stack web application designed to help you discover Indian recipes based on the ingredients you already have at home. Using an intelligent matching algorithm and a focus on Indian household staples, it reduces food waste and makes meal planning effortless.



## ✨ Features

- **🔐 Secure Authentication**: JWT-based login and registration system with password hashing (bcrypt).
- **🥘 Quick Kitchen**: One-tap selection for 500+ common Indian staples (Ginger, Garlic, Masalas, etc.).
- **🔍 Smart Search**: Access a database of 3,000+ ingredients with real-time filtering.
- **💡 Intelligent Recommendations**: Get recipes ranked by how many ingredients you already own.
- **📖 Detailed Recipes**: Full cooking instructions, prep time, and cuisine details.
- **📱 Modern & Responsive UI**: A premium, dark-themed interface built with Bootstrap 5 and Glassmorphism aesthetics.

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-JWT-Extended
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Bootstrap 5
- **Data Processing**: Pandas, Regex

## 🚀 Setup & Installation

### 1. Prerequisites
- Python 3.8+
- PostgreSQL
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/smart-indian-pantry.git
cd smart-indian-pantry
```

### 3. Setup Environment Variables
Create a `.env` file in the root directory:
```env
DB_NAME=smart_pantry
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
JWT_SECRET_KEY=your_super_secret_key
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Initialize Database & Load Data
Ensure your PostgreSQL server is running, then execute:
```bash
python init_db.py
python load_dataset.py
```

### 6. Run the Application
```bash
python app.py
```
The app will be available at `http://127.0.0.1:5001`.

## 📂 Project Structure
- `/templates`: HTML pages (Pantry, Recipes, Auth).
- `/static`: CSS, Shared JS, and Images.
- `app.py`: Main Flask application with API endpoints.
- `load_dataset.py`: Data cleaning and database ingestion script.
- `schema.sql`: PostgreSQL database structure.

## 🤝 Contributing
Feel free to fork this project and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

