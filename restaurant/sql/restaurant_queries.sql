-- Restaurant Analytics SQL Queries
-- Comprehensive business intelligence queries for restaurant review analysis

-- =============================================
-- 1. BASIC BUSINESS METRICS
-- =============================================

-- Total restaurants, users, and reviews
SELECT 
    COUNT(DISTINCT restaurant_id) as total_restaurants,
    COUNT(DISTINCT user_id) as total_users,
    COUNT(*) as total_reviews,
    AVG(rating) as average_rating,
    MAX(review_date) as latest_review_date,
    MIN(review_date) as earliest_review_date
FROM reviews;

-- Monthly review growth
SELECT 
    DATE_TRUNC('month', review_date) as review_month,
    COUNT(*) as review_count,
    AVG(rating) as avg_rating,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT restaurant_id) as unique_restaurants
FROM reviews
GROUP BY DATE_TRUNC('month', review_date)
ORDER BY review_month;

-- =============================================
-- 2. RESTAURANT PERFORMANCE ANALYSIS
-- =============================================

-- Top 10 restaurants by average rating (min 10 reviews)
SELECT 
    r.name,
    r.cuisine_type,
    r.price_range,
    r.location,
    COUNT(rev.review_id) as review_count,
    ROUND(AVG(rev.rating), 2) as avg_rating,
    ROUND(AVG(rev.food_rating), 2) as avg_food_rating,
    ROUND(AVG(rev.service_rating), 2) as avg_service_rating,
    ROUND(AVG(rev.ambiance_rating), 2) as avg_ambiance_rating
FROM restaurants r
JOIN reviews rev ON r.restaurant_id = rev.restaurant_id
GROUP BY r.restaurant_id, r.name, r.cuisine_type, r.price_range, r.location
HAVING COUNT(rev.review_id) >= 10
ORDER BY avg_rating DESC
LIMIT 10;

-- Bottom 10 restaurants by average rating (min 5 reviews)
SELECT 
    r.name,
    r.cuisine_type,
    r.price_range,
    r.location,
    COUNT(rev.review_id) as review_count,
    ROUND(AVG(rev.rating), 2) as avg_rating,
    ROUND(AVG(rev.food_rating), 2) as avg_food_rating,
    ROUND(AVG(rev.service_rating), 2) as avg_service_rating
FROM restaurants r
JOIN reviews rev ON r.restaurant_id = rev.restaurant_id
GROUP BY r.restaurant_id, r.name, r.cuisine_type, r.price_range, r.location
HAVING COUNT(rev.review_id) >= 5
ORDER BY avg_rating ASC
LIMIT 10;

-- Most popular restaurants (most reviews)
SELECT 
    r.name,
    r.cuisine_type,
    r.price_range,
    r.location,
    COUNT(rev.review_id) as review_count,
    ROUND(AVG(rev.rating), 2) as avg_rating,
    COUNT(DISTINCT rev.user_id) as unique_reviewers
FROM restaurants r
JOIN reviews rev ON r.restaurant_id = rev.restaurant_id
GROUP BY r.restaurant_id, r.name, r.cuisine_type, r.price_range, r.location
ORDER BY review_count DESC
LIMIT 15;

-- =============================================
-- 3. CUISINE ANALYSIS
-- =============================================

-- Cuisine performance comparison
SELECT 
    cuisine_type,
    COUNT(DISTINCT restaurant_id) as restaurant_count,
    COUNT(*) as total_reviews,
    ROUND(AVG(rating), 2) as avg_rating,
    ROUND(AVG(food_rating), 2) as avg_food_rating,
    ROUND(AVG(service_rating), 2) as avg_service_rating,
    ROUND(AVG(ambiance_rating), 2) as avg_ambiance_rating
FROM restaurants r
JOIN reviews rev ON r.restaurant_id = rev.restaurant_id
GROUP BY cuisine_type
HAVING COUNT(*) >= 50  -- Only cuisines with significant reviews
ORDER BY avg_rating DESC;

-- Price range distribution by cuisine
SELECT 
    cuisine_type,
    price_range,
    COUNT(*) as restaurant_count,
    ROUND(AVG(avg_rating), 2) as avg_rating
FROM restaurants
GROUP BY cuisine_type, price_range
ORDER BY cuisine_type, 
    CASE price_range 
        WHEN '$' THEN 1 
        WHEN '$$' THEN 2 
        WHEN '$$$' THEN 3 
        WHEN '$$$$' THEN 4 
    END;

-- =============================================
-- 4. USER BEHAVIOR ANALYSIS
-- =============================================

-- Most active users
SELECT 
    u.user_id,
    COUNT(rev.review_id) as review_count,
    ROUND(AVG(rev.rating), 2) as avg_rating_given,
    MIN(rev.review_date) as first_review_date,
    MAX(rev.review_date) as latest_review_date,
    AVG(rev.review_length) as avg_review_length
FROM users u
JOIN reviews rev ON u.user_id = rev.user_id
GROUP BY u.user_id
HAVING COUNT(rev.review_id) >= 10
ORDER BY review_count DESC
LIMIT 20;

-- User rating behavior analysis
SELECT 
    CASE 
        WHEN review_count = 1 THEN 'One-time Reviewer'
        WHEN review_count BETWEEN 2 AND 5 THEN 'Occasional Reviewer'
        WHEN review_count BETWEEN 6 AND 20 THEN 'Regular Reviewer'
        ELSE 'Super Reviewer'
    END as user_type,
    COUNT(*) as user_count,
    ROUND(AVG(avg_rating), 2) as avg_rating_given,
    ROUND(AVG(review_count), 1) as avg_reviews_per_user
FROM (
    SELECT 
        user_id,
        COUNT(*) as review_count,
        AVG(rating) as avg_rating
    FROM reviews
    GROUP BY user_id
) user_stats
GROUP BY user_type
ORDER BY 
    CASE user_type
        WHEN 'One-time Reviewer' THEN 1
        WHEN 'Occasional Reviewer' THEN 2
        WHEN 'Regular Reviewer' THEN 3
        WHEN 'Super Reviewer' THEN 4
    END;

-- =============================================
-- 5. TEMPORAL ANALYSIS
-- =============================================

-- Daily review patterns
SELECT 
    EXTRACT(DOW FROM review_date) as day_of_week,
    CASE EXTRACT(DOW FROM review_date)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    COUNT(*) as review_count,
    ROUND(AVG(rating), 2) as avg_rating
FROM reviews
GROUP BY EXTRACT(DOW FROM review_date), day_name
ORDER BY day_of_week;

-- Hourly review patterns
SELECT 
    EXTRACT(HOUR FROM review_date) as review_hour,
    COUNT(*) as review_count,
    ROUND(AVG(rating), 2) as avg_rating
FROM reviews
GROUP BY EXTRACT(HOUR FROM review_date)
ORDER BY review_hour;

-- Monthly performance trends
SELECT 
    DATE_TRUNC('month', review_date) as review_month,
    COUNT(*) as review_count,
    ROUND(AVG(rating), 2) as avg_rating,
    ROUND(AVG(food_rating), 2) as avg_food_rating,
    ROUND(AVG(service_rating), 2) as avg_service_rating
FROM reviews
GROUP BY DATE_TRUNC('month', review_date)
ORDER BY review_month;

-- =============================================
-- 6. RATING ANALYSIS
-- =============================================

-- Rating distribution
SELECT 
    rating,
    COUNT(*) as review_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews), 2) as percentage
FROM reviews
GROUP BY rating
ORDER BY rating;

-- Component rating correlations
SELECT 
    ROUND(CORR(rating, food_rating), 3) as rating_food_correlation,
    ROUND(CORR(rating, service_rating), 3) as rating_service_correlation,
    ROUND(CORR(rating, ambiance_rating), 3) as rating_ambiance_correlation,
    ROUND(CORR(food_rating, service_rating), 3) as food_service_correlation
FROM reviews;

-- Rating vs review length analysis
SELECT 
    rating,
    COUNT(*) as review_count,
    ROUND(AVG(review_length), 0) as avg_review_length,
    ROUND(AVG(useful_count), 2) as avg_useful_votes
FROM reviews
GROUP BY rating
ORDER BY rating;

-- =============================================
-- 7. PRICE RANGE ANALYSIS
-- =============================================

-- Performance by price range
SELECT 
    r.price_range,
    COUNT(DISTINCT r.restaurant_id) as restaurant_count,
    COUNT(rev.review_id) as review_count,
    ROUND(AVG(rev.rating), 2) as avg_rating,
    ROUND(AVG(rev.food_rating), 2) as avg_food_rating,
    ROUND(AVG(rev.service_rating), 2) as avg_service_rating,
    ROUND(AVG(rev.ambiance_rating), 2) as avg_ambiance_rating,
    ROUND(AVG(rev.review_length), 0) as avg_review_length
FROM restaurants r
JOIN reviews rev ON r.restaurant_id = rev.restaurant_id
GROUP BY r.price_range
ORDER BY 
    CASE r.price_range 
        WHEN '$' THEN 1 
        WHEN '$$' THEN 2 
        WHEN '$$$' THEN 3 
        WHEN '$$$$' THEN 4 
    END;

-- Value for money analysis (rating vs price)
SELECT 
    price_range,
    cuisine_type,
    COUNT(*) as restaurant_count,
    ROUND(AVG(avg_rating), 2) as avg_rating,
    ROUND(AVG(review_count), 1) as avg_reviews
FROM restaurants
GROUP BY price_range, cuisine_type
HAVING COUNT(*) >= 3
ORDER BY avg_rating DESC;

-- =============================================
-- 8. SENTIMENT ANALYSIS QUERIES
-- =============================================

-- Sentiment distribution by rating
SELECT 
    rating,
    vader_sentiment,
    COUNT(*) as review_count,
    ROUND(AVG(compound), 3) as avg_sentiment_score
FROM reviews
WHERE vader_sentiment IS NOT NULL
GROUP BY rating, vader_sentiment
ORDER BY rating, vader_sentiment;

-- Top positive and negative aspects
SELECT 
    'Positive' as sentiment_type,
    aspect,
    COUNT(*) as mention_count,
    ROUND(AVG(rating), 2) as avg_rating
FROM (
    SELECT 
        UNNEST(detected_aspects) as aspect,
        rating
    FROM reviews 
    WHERE vader_sentiment = 'Positive'
) positive_aspects
GROUP BY aspect
ORDER BY mention_count DESC
LIMIT 10;

SELECT 
    'Negative' as sentiment_type,
    aspect,
    COUNT(*) as mention_count,
    ROUND(AVG(rating), 2) as avg_rating
FROM (
    SELECT 
        UNNEST(detected_aspects) as aspect,
        rating
    FROM reviews 
    WHERE vader_sentiment = 'Negative'
) negative_aspects
GROUP BY aspect
ORDER BY mention_count DESC
LIMIT 10;

-- Sentiment by cuisine type
SELECT 
    r.cuisine_type,
    rev.vader_sentiment,
    COUNT(*) as review_count,
    ROUND(AVG(rev.compound), 3) as avg_sentiment_score,
    ROUND(AVG(rev.rating), 2) as avg_rating
FROM restaurants r
JOIN reviews rev ON r.restaurant_id = rev.restaurant_id
WHERE rev.vader_sentiment IS NOT NULL
GROUP BY r.cuisine_type, rev.vader_sentiment
HAVING COUNT(*) >= 10
ORDER BY r.cuisine_type, 
    CASE rev.vader_sentiment 
        WHEN 'Positive' THEN 1 
        WHEN 'Neutral' THEN 2 
        WHEN 'Negative' THEN 3 
    END;

-- =============================================
-- 9. BUSINESS INTELLIGENCE DASHBOARD QUERIES
-- =============================================

-- Executive summary metrics
SELECT 
    (SELECT COUNT(*) FROM restaurants) as total_restaurants,
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM reviews) as total_reviews,
    (SELECT ROUND(AVG(rating), 2) FROM reviews) as platform_avg_rating,
    (SELECT COUNT(DISTINCT cuisine_type) FROM restaurants) as unique_cuisines,
    (SELECT ROUND(AVG(review_count), 1) FROM restaurants) as avg_reviews_per_restaurant;

-- Growth metrics (last 6 months vs previous 6 months)
WITH recent_period AS (
    SELECT 
        COUNT(*) as recent_reviews,
        ROUND(AVG(rating), 2) as recent_avg_rating
    FROM reviews
    WHERE review_date >= CURRENT_DATE - INTERVAL '6 months'
),
previous_period AS (
    SELECT 
        COUNT(*) as previous_reviews,
        ROUND(AVG(rating), 2) as previous_avg_rating
    FROM reviews
    WHERE review_date BETWEEN CURRENT_DATE - INTERVAL '12 months' AND CURRENT_DATE - INTERVAL '6 months'
)
SELECT 
    recent_reviews,
    previous_reviews,
    ROUND((recent_reviews - previous_reviews) * 100.0 / previous_reviews, 1) as growth_percentage,
    recent_avg_rating,
    previous_avg_rating,
    ROUND(recent_avg_rating - previous_avg_rating, 2) as rating_change
FROM recent_period, previous_period;

-- Quality hotspots (restaurants needing attention)
SELECT 
    r.name,
    r.cuisine_type,
    r.price_range,
    r.location,
    COUNT(rev.review_id) as review_count,
    ROUND(AVG(rev.rating), 2) as avg_rating,
    ROUND(AVG(rev.service_rating), 2) as avg_service_rating,
    ROUND(AVG(rev.food_rating), 2) as avg_food_rating
FROM restaurants r
JOIN reviews rev ON r.restaurant_id = rev.restaurant_id
GROUP BY r.restaurant_id, r.name, r.cuisine_type, r.price_range, r.location
HAVING COUNT(rev.review_id) >= 5 
    AND AVG(rev.rating) < 3.0
ORDER BY avg_rating ASC
LIMIT 15;

-- Success stories (high rating with significant reviews)
SELECT 
    r.name,
    r.cuisine_type,
    r.price_range,
    r.location,
    COUNT(rev.review_id) as review_count,
    ROUND(AVG(rev.rating), 2) as avg_rating,
    ROUND(AVG(rev.service_rating), 2) as avg_service_rating,
    ROUND(AVG(rev.food_rating), 2) as avg_food_rating
FROM restaurants r
JOIN reviews rev ON r.restaurant_id = rev.restaurant_id
GROUP BY r.restaurant_id, r.name, r.cuisine_type, r.price_range, r.location
HAVING COUNT(rev.review_id) >= 10 
    AND AVG(rev.rating) >= 4.5
ORDER BY avg_rating DESC
LIMIT 15;

-- =============================================
-- 10. ADVANCED ANALYTICS QUERIES
-- =============================================

-- Restaurant clustering by performance
SELECT 
    CASE 
        WHEN avg_rating >= 4.5 AND review_count >= 20 THEN 'Elite'
        WHEN avg_rating >= 4.0 AND review_count >= 10 THEN 'High Performer'
        WHEN avg_rating >= 3.5 THEN 'Solid Performer'
        WHEN avg_rating >= 3.0 THEN 'Needs Improvement'
        ELSE 'Critical Attention Needed'
    END as performance_tier,
    COUNT(*) as restaurant_count,
    ROUND(AVG(avg_rating), 2) as avg_rating_in_tier,
    ROUND(AVG(review_count), 1) as avg_reviews_in_tier
FROM (
    SELECT 
        r.restaurant_id,
        r.name,
        COUNT(rev.review_id) as review_count,
        ROUND(AVG(rev.rating), 2) as avg_rating
    FROM restaurants r
    LEFT JOIN reviews rev ON r.restaurant_id = rev.restaurant_id
    GROUP BY r.restaurant_id, r.name
) restaurant_stats
GROUP BY performance_tier
ORDER BY 
    CASE performance_tier
        WHEN 'Elite' THEN 1
        WHEN 'High Performer' THEN 2
        WHEN 'Solid Performer' THEN 3
        WHEN 'Needs Improvement' THEN 4
        WHEN 'Critical Attention Needed' THEN 5
    END;

-- User engagement segmentation
SELECT 
    CASE 
        WHEN user_tenure_days < 30 THEN 'New User (<30 days)'
        WHEN user_tenure_days BETWEEN 30 AND 180 THEN 'Active User (1-6 months)'
        WHEN user_tenure_days BETWEEN 181 AND 365 THEN 'Established User (6-12 months)'
        ELSE 'Veteran User (>1 year)'
    END as user_segment,
    COUNT(*) as user_count,
    ROUND(AVG(review_count), 1) as avg_reviews_per_user,
    ROUND(AVG(user_tenure_days), 0) as avg_tenure_days
FROM users
WHERE review_count > 0
GROUP BY user_segment
ORDER BY 
    CASE user_segment
        WHEN 'New User (<30 days)' THEN 1
        WHEN 'Active User (1-6 months)' THEN 2
        WHEN 'Established User (6-12 months)' THEN 3
        WHEN 'Veteran User (>1 year)' THEN 4
    END;

-- Seasonal trends analysis
SELECT 
    EXTRACT(MONTH FROM review_date) as month,
    TO_CHAR(review_date, 'Month') as month_name,
    COUNT(*) as review_count,
    ROUND(AVG(rating), 2) as avg_rating,
    ROUND(AVG(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) * 100, 1) as positive_review_pct
FROM reviews
GROUP BY EXTRACT(MONTH FROM review_date), month_name
ORDER BY month;