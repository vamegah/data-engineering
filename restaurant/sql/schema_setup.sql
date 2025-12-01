-- Restaurant Analytics Database Schema
-- Create tables for restaurant review analysis

-- Restaurants table
CREATE TABLE IF NOT EXISTS restaurants (
    restaurant_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    cuisine_type VARCHAR(100),
    price_range VARCHAR(10),
    location VARCHAR(100),
    avg_rating DECIMAL(3,2),
    review_count INTEGER,
    opening_year INTEGER
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    join_date DATE,
    location VARCHAR(100),
    review_count INTEGER
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    review_id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) REFERENCES restaurants(restaurant_id),
    user_id VARCHAR(50) REFERENCES users(user_id),
    rating DECIMAL(2,1) CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATE,
    useful_count INTEGER,
    service_rating INTEGER CHECK (service_rating >= 1 AND service_rating <= 5),
    food_rating INTEGER CHECK (food_rating >= 1 AND food_rating <= 5),
    ambiance_rating INTEGER CHECK (ambiance_rating >= 1 AND ambiance_rating <= 5)
);

-- Create indexes for better query performance
CREATE INDEX idx_reviews_restaurant_id ON reviews(restaurant_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_date ON reviews(review_date);
CREATE INDEX idx_restaurants_cuisine ON restaurants(cuisine_type);
CREATE INDEX idx_restaurants_location ON restaurants(location);

-- Create a materialized view for restaurant statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS restaurant_stats AS
SELECT 
    r.restaurant_id,
    r.name,
    r.cuisine_type,
    r.price_range,
    r.location,
    COUNT(DISTINCT rev.review_id) as total_reviews,
    AVG(rev.rating) as avg_rating,
    AVG(rev.service_rating) as avg_service_rating,
    AVG(rev.food_rating) as avg_food_rating,
    AVG(rev.ambiance_rating) as avg_ambiance_rating,
    COUNT(DISTINCT rev.user_id) as unique_reviewers
FROM restaurants r
LEFT JOIN reviews rev ON r.restaurant_id = rev.restaurant_id
GROUP BY r.restaurant_id, r.name, r.cuisine_type, r.price_range, r.location;

CREATE INDEX idx_restaurant_stats_cuisine ON restaurant_stats(cuisine_type);
CREATE INDEX idx_restaurant_stats_rating ON restaurant_stats(avg_rating);

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW restaurant_stats;

-- Display table counts
SELECT 
    (SELECT COUNT(*) FROM restaurants) as restaurant_count,
    (SELECT COUNT(*) FROM users) as user_count,
    (SELECT COUNT(*) FROM reviews) as review_count;