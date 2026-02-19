-- Database Schema for Smart Indian Pantry
DROP TABLE IF EXISTS user_pantry CASCADE;
DROP TABLE IF EXISTS recipe_ingredients CASCADE;
DROP TABLE IF EXISTS ingredients CASCADE;
DROP TABLE IF EXISTS recipes CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recipes Table
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    instructions TEXT NOT NULL,
    image_url TEXT,
    category VARCHAR(100),
    is_vegetarian BOOLEAN DEFAULT TRUE,
    prep_time VARCHAR(50),
    cuisine VARCHAR(100)
);

-- Ingredients Table
CREATE TABLE IF NOT EXISTS ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100)
);

-- RecipeIngredients (Relationship Table)
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
    PRIMARY KEY (recipe_id, ingredient_id)
);

-- UserPantry Table
CREATE TABLE IF NOT EXISTS user_pantry (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, ingredient_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_recipe_title ON recipes(title);
CREATE INDEX IF NOT EXISTS idx_ingredient_name ON ingredients(name);
