# How to Run Smart Pantry in VS Code

Follow these steps to set up and run the application on your local machine.

## Prerequisites

1.  **Python**: Ensure Python 3.x is installed.
2.  **PostgreSQL**: Ensure PostgreSQL is installed and running.
3.  **VS Code**: Ensure you have the "Python" extension installed.

## Step 1: Open Project in VS Code

1.  Open VS Code.
2.  Click on **File > Open Folder...** and select the `Smart Pantry-Your Ingredients Our Recipes` folder.

## Step 2: Set Up Environment Variables

1.  Check the `.env` file in the root directory.
2.  Ensure the database credentials match your local PostgreSQL setup:
    ```env
    DB_NAME=smart_pantry
    DB_USER=postgres
    DB_PASSWORD=your_password_here
    DB_HOST=localhost
    DB_PORT=5432
    JWT_SECRET_KEY=my-super-secret-key
    ```

## Step 3: Install Dependencies

1.  Open the integrated terminal in VS Code (**Terminal > New Terminal**).
2.  Run the following command to install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Step 4: Initialize the Database

1.  In the terminal, run the database initialization script. This will create the necessary tables using `schema.sql`.
    ```bash
    python init_db.py
    ```
2.  You should see: `Database initialized successfully!`

## Step 5: Load the Dataset

1.  Run the dataset loader script to populate the database with recipes and ingredients:
    ```bash
    python load_dataset.py
    ```
2.  Wait for the message: `Dataset loaded successfully!` (This might take a minute).

## Step 6: Start the Application

1.  Run the Flask app:
    ```bash
    python app.py
    ```
2.  The terminal will show: `Running on http://127.0.0.1:5001`.

## Step 7: Use the App

Open your browser and navigate to:
`http://127.0.0.1:5001/`

### Tip: Running with VS Code Debugger

1.  Click on the **Run and Debug** icon in the Sidebar.
2.  Select **Python File** to run the current script (e.g., `app.py`) with debugging enabled.
