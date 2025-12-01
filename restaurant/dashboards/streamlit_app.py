#!/usr/bin/env python3
"""
Restaurant Analytics Dashboard
Interactive Streamlit application for restaurant review analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os

warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="Restaurant Analytics Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .section-header {
        font-size: 1.5rem;
        color: #1f77b4;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    """Load and cache all necessary data"""
    try:
        # Load processed data
        restaurants = pd.read_csv("../data/processed/cleaned/restaurants_clean.csv")
        users = pd.read_csv("../data/processed/cleaned/users_clean.csv")
        reviews = pd.read_csv("../data/processed/cleaned/reviews_clean.csv")
        restaurant_agg = pd.read_csv(
            "../data/processed/aggregated/restaurant_aggregated.csv"
        )
        cuisine_agg = pd.read_csv("../data/processed/aggregated/cuisine_aggregated.csv")
        monthly_trends = pd.read_csv("../data/processed/aggregated/monthly_trends.csv")

        # Convert dates
        reviews["review_date"] = pd.to_datetime(reviews["review_date"])
        users["join_date"] = pd.to_datetime(users["join_date"])
        monthly_trends["review_month"] = pd.to_datetime(monthly_trends["review_month"])

        # Try to locate sentiment analysis results in several candidate paths and merge
        candidate_sentiment_paths = [
            "../data/processed/cleaned/sentiment_analysis_result.csv",
            "../data/processed/cleaned/sentiment_analysis_results.csv",
            "../data/processed/sentiment_analysis_result.csv",
            "../data/processed/sentiment_analysis_results.csv",
        ]

        sentiment_df = None
        for p in candidate_sentiment_paths:
            if os.path.exists(p):
                try:
                    sentiment_df = pd.read_csv(p)
                    break
                except Exception:
                    sentiment_df = None

        if sentiment_df is not None and "review_id" in sentiment_df.columns:
            # Keep review_id and any sentiment columns, but avoid overwriting core review fields
            exclude_cols = {"restaurant_id", "rating", "review_text"}
            cols_to_merge = [c for c in sentiment_df.columns if c not in exclude_cols]
            if "review_id" not in cols_to_merge:
                cols_to_merge = ["review_id"] + [
                    c for c in cols_to_merge if c != "review_id"
                ]

            # Ensure keys are strings for a safe join
            reviews["review_id"] = reviews["review_id"].astype(str)
            sentiment_df["review_id"] = sentiment_df["review_id"].astype(str)

            try:
                reviews = reviews.merge(
                    sentiment_df[cols_to_merge].drop_duplicates(subset=["review_id"]),
                    on="review_id",
                    how="left",
                )
                # Small note in Streamlit if available
                try:
                    st.info(
                        "Merged sentiment analysis results into reviews (if available)"
                    )
                except Exception:
                    pass
            except Exception:
                # If merge fails, continue without sentiment
                pass

        # If merged sentiment is present but non-informative (all zeros or only 'Neutral'),
        # compute a VADER fallback from review_text to provide meaningful variation.
        try:
            need_vader = False
            if "compound" in reviews.columns:
                # check if compound is all NaN or all near-zero
                comp = pd.to_numeric(reviews["compound"], errors="coerce")
                if comp.notna().sum() == 0:
                    need_vader = True
                else:
                    # check variance / unique values (tolerate tiny float noise)
                    unique_nonzero = (comp.abs() > 1e-6).sum()
                    if unique_nonzero == 0:
                        need_vader = True
            else:
                need_vader = True

            if not need_vader and "vader_sentiment" in reviews.columns:
                vals = reviews["vader_sentiment"].dropna().unique()
                if len(vals) == 0 or (len(vals) == 1 and vals[0] == "Neutral"):
                    need_vader = True

            if need_vader:
                # compute VADER scores as fallback
                try:
                    import nltk

                    try:
                        from nltk.sentiment import SentimentIntensityAnalyzer
                    except Exception:
                        nltk.download("vader_lexicon")
                        from nltk.sentiment import SentimentIntensityAnalyzer

                    nltk.download("vader_lexicon")
                    sia = SentimentIntensityAnalyzer()

                    def _compound(text):
                        try:
                            return float(sia.polarity_scores(str(text))["compound"])
                        except Exception:
                            return np.nan

                    reviews["compound"] = reviews.get("compound")
                    # compute for rows where compound is missing or zero
                    mask_compute = reviews["compound"].isna() | (
                        pd.to_numeric(reviews["compound"], errors="coerce").abs()
                        <= 1e-6
                    )
                    if mask_compute.any():
                        reviews.loc[mask_compute, "compound"] = reviews.loc[
                            mask_compute, "review_text"
                        ].apply(_compound)

                    # map to categorical vader_sentiment
                    def _label(c):
                        try:
                            c = float(c)
                        except Exception:
                            return "Neutral"
                        if c >= 0.05:
                            return "Positive"
                        elif c <= -0.05:
                            return "Negative"
                        else:
                            return "Neutral"

                    reviews["vader_sentiment"] = reviews["compound"].apply(_label)
                    try:
                        st.info(
                            "Computed VADER sentiment fallback for reviews (replaced missing/neutral values)"
                        )
                    except Exception:
                        pass
                except Exception:
                    # if nltk or vader not available, skip silently
                    pass
        except Exception:
            pass

        return restaurants, users, reviews, restaurant_agg, cuisine_agg, monthly_trends
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None


def main():
    """Main dashboard application"""

    # Title and description
    st.markdown(
        '<h1 class="main-header">🍽️ Restaurant Analytics Dashboard</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    Comprehensive analysis of restaurant reviews, customer sentiment, and business performance metrics.
    Explore trends, identify opportunities, and make data-driven decisions.
    """
    )

    # Load data
    with st.spinner("Loading data..."):
        restaurants, users, reviews, restaurant_agg, cuisine_agg, monthly_trends = (
            load_data()
        )

    if restaurants is None:
        st.error("Failed to load data. Please check if the data files exist.")
        return

    # Sidebar filters
    st.sidebar.header("🔍 Filters & Controls")

    # Cuisine filter
    all_cuisines = ["All"] + sorted(restaurants["cuisine_type"].unique().tolist())
    selected_cuisine = st.sidebar.selectbox("Select Cuisine Type", all_cuisines)

    # Price range filter
    all_prices = ["All"] + sorted(restaurants["price_range"].unique().tolist())
    selected_price = st.sidebar.selectbox("Select Price Range", all_prices)

    # Rating filter
    min_rating, max_rating = st.sidebar.slider(
        "Select Rating Range", min_value=1.0, max_value=5.0, value=(3.0, 5.0), step=0.1
    )

    # Date range filter
    if not reviews.empty:
        min_date = reviews["review_date"].min().date()
        max_date = reviews["review_date"].max().date()
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    # Apply filters
    filtered_restaurants = restaurants.copy()
    filtered_reviews = reviews.copy()

    if selected_cuisine != "All":
        filtered_restaurants = filtered_restaurants[
            filtered_restaurants["cuisine_type"] == selected_cuisine
        ]
        restaurant_ids = filtered_restaurants["restaurant_id"].tolist()
        filtered_reviews = filtered_reviews[
            filtered_reviews["restaurant_id"].isin(restaurant_ids)
        ]

    if selected_price != "All":
        filtered_restaurants = filtered_restaurants[
            filtered_restaurants["price_range"] == selected_price
        ]
        restaurant_ids = filtered_restaurants["restaurant_id"].tolist()
        filtered_reviews = filtered_reviews[
            filtered_reviews["restaurant_id"].isin(restaurant_ids)
        ]

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_reviews = filtered_reviews[
            (filtered_reviews["review_date"].dt.date >= start_date)
            & (filtered_reviews["review_date"].dt.date <= end_date)
        ]

    filtered_reviews = filtered_reviews[
        (filtered_reviews["rating"] >= min_rating)
        & (filtered_reviews["rating"] <= max_rating)
    ]

    # Executive Summary Section
    st.markdown(
        '<div class="section-header">📊 Executive Summary</div>', unsafe_allow_html=True
    )

    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_restaurants = len(filtered_restaurants)
        st.metric("Total Restaurants", f"{total_restaurants:,}")

    with col2:
        total_reviews = len(filtered_reviews)
        st.metric("Total Reviews", f"{total_reviews:,}")

    with col3:
        avg_rating = (
            filtered_reviews["rating"].mean() if not filtered_reviews.empty else 0
        )
        st.metric("Average Rating", f"{avg_rating:.2f}")

    with col4:
        unique_users = (
            filtered_reviews["user_id"].nunique() if not filtered_reviews.empty else 0
        )
        st.metric("Unique Users", f"{unique_users:,}")

    with col5:
        if not filtered_restaurants.empty and not filtered_reviews.empty:
            reviews_per_restaurant = len(filtered_reviews) / len(filtered_restaurants)
            st.metric("Reviews/Restaurant", f"{reviews_per_restaurant:.1f}")
        else:
            st.metric("Reviews/Restaurant", "0")

    # Business Overview Section
    st.markdown(
        '<div class="section-header">📈 Business Overview</div>', unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        # Rating distribution
        if not filtered_reviews.empty:
            fig = px.histogram(
                filtered_reviews,
                x="rating",
                nbins=20,
                title="Rating Distribution",
                color_discrete_sequence=["#1f77b4"],
            )
            fig.update_layout(
                xaxis_title="Rating", yaxis_title="Number of Reviews", showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters")

    with col2:
        # Cuisine distribution
        if not filtered_restaurants.empty:
            cuisine_counts = (
                filtered_restaurants["cuisine_type"].value_counts().head(10)
            )
            fig = px.pie(
                values=cuisine_counts.values,
                names=cuisine_counts.index,
                title="Top 10 Cuisine Types",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters")

    # Performance Analysis Section
    st.markdown(
        '<div class="section-header">🏆 Performance Analysis</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(
        ["🏪 Restaurant Performance", "🍕 Cuisine Performance", "💰 Price Analysis"]
    )

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Top restaurants by rating
            if not filtered_reviews.empty:
                top_restaurants = (
                    filtered_reviews.groupby("restaurant_id")
                    .agg({"rating": ["count", "mean"], "restaurant_id": "first"})
                    .round(3)
                )
                top_restaurants.columns = [
                    "review_count",
                    "avg_rating",
                    "restaurant_id",
                ]
                top_restaurants = top_restaurants[
                    top_restaurants["review_count"] >= 5
                ].nlargest(10, "avg_rating")

                # Merge with restaurant names
                # Ensure no index conflicts
                if "restaurant_id" in top_restaurants.index.names:
                    top_restaurants = top_restaurants.reset_index(drop=True)

                top_restaurants = top_restaurants.merge(
                    restaurants[["restaurant_id", "name", "cuisine_type"]],
                    on="restaurant_id",
                )

                st.subheader("🏅 Top Rated Restaurants")
                for idx, row in top_restaurants.iterrows():
                    st.write(f"**{row['name']}** ({row['cuisine_type']})")
                    st.write(
                        f"⭐ {row['avg_rating']:.2f}/5 | 📝 {row['review_count']} reviews"
                    )
                    st.markdown("---")

        with col2:
            # Restaurant performance scatter
            if not filtered_reviews.empty:
                restaurant_performance = (
                    filtered_reviews.groupby("restaurant_id")
                    .agg({"rating": ["count", "mean"], "restaurant_id": "first"})
                    .round(3)
                )
                restaurant_performance.columns = [
                    "review_count",
                    "avg_rating",
                    "restaurant_id",
                ]

                fig = px.scatter(
                    restaurant_performance,
                    x="review_count",
                    y="avg_rating",
                    size="review_count",
                    hover_name="restaurant_id",
                    title="Restaurant Performance: Popularity vs Rating",
                    labels={
                        "review_count": "Number of Reviews",
                        "avg_rating": "Average Rating",
                    },
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            # Cuisine performance
            if not filtered_reviews.empty and not filtered_restaurants.empty:
                cuisine_perf = filtered_reviews.merge(
                    filtered_restaurants[["restaurant_id", "cuisine_type"]],
                    on="restaurant_id",
                )
                cuisine_stats = (
                    cuisine_perf.groupby("cuisine_type")
                    .agg({"rating": ["count", "mean"], "restaurant_id": "nunique"})
                    .round(3)
                )
                cuisine_stats.columns = [
                    "review_count",
                    "avg_rating",
                    "restaurant_count",
                ]
                cuisine_stats = cuisine_stats[
                    cuisine_stats["review_count"] >= 10
                ].sort_values("avg_rating", ascending=False)

                fig = px.bar(
                    cuisine_stats.reset_index(),
                    x="cuisine_type",
                    y="avg_rating",
                    title="Average Rating by Cuisine Type",
                    color="avg_rating",
                    color_continuous_scale="Viridis",
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Cuisine popularity vs rating
            if not filtered_reviews.empty and not filtered_restaurants.empty:
                cuisine_pop = filtered_reviews.merge(
                    filtered_restaurants[["restaurant_id", "cuisine_type"]],
                    on="restaurant_id",
                )
                cuisine_pop_stats = (
                    cuisine_pop.groupby("cuisine_type")
                    .agg({"rating": ["count", "mean"], "restaurant_id": "nunique"})
                    .round(3)
                )
                cuisine_pop_stats.columns = [
                    "review_count",
                    "avg_rating",
                    "restaurant_count",
                ]

                fig = px.scatter(
                    cuisine_pop_stats.reset_index(),
                    x="review_count",
                    y="avg_rating",
                    size="restaurant_count",
                    color="cuisine_type",
                    hover_name="cuisine_type",
                    title="Cuisine Popularity vs Rating",
                    labels={
                        "review_count": "Total Reviews",
                        "avg_rating": "Average Rating",
                    },
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            # Price range performance
            if not filtered_reviews.empty and not filtered_restaurants.empty:
                price_perf = filtered_reviews.merge(
                    filtered_restaurants[["restaurant_id", "price_range"]],
                    on="restaurant_id",
                )
                price_stats = (
                    price_perf.groupby("price_range")
                    .agg(
                        {
                            "rating": ["count", "mean"],
                            "food_rating": "mean",
                            "service_rating": "mean",
                            "ambiance_rating": "mean",
                        }
                    )
                    .round(3)
                )
                price_stats.columns = [
                    "review_count",
                    "avg_rating",
                    "avg_food",
                    "avg_service",
                    "avg_ambiance",
                ]

                # Reorder price ranges
                price_order = ["$", "$$", "$$$", "$$$$"]
                price_stats = price_stats.reindex(price_order)

                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        name="Overall", x=price_stats.index, y=price_stats["avg_rating"]
                    )
                )
                fig.add_trace(
                    go.Bar(name="Food", x=price_stats.index, y=price_stats["avg_food"])
                )
                fig.add_trace(
                    go.Bar(
                        name="Service",
                        x=price_stats.index,
                        y=price_stats["avg_service"],
                    )
                )
                fig.add_trace(
                    go.Bar(
                        name="Ambiance",
                        x=price_stats.index,
                        y=price_stats["avg_ambiance"],
                    )
                )

                fig.update_layout(
                    title="Rating Components by Price Range",
                    xaxis_title="Price Range",
                    yaxis_title="Average Rating",
                    barmode="group",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Value analysis
            if not filtered_restaurants.empty:
                value_analysis = (
                    filtered_restaurants.groupby("price_range")
                    .agg(
                        {
                            "avg_rating": "mean",
                            "review_count": "sum",
                            "restaurant_id": "count",
                        }
                    )
                    .round(3)
                )
                value_analysis = value_analysis.reindex(price_order)

                st.subheader("💰 Value Analysis")
                for price in price_order:
                    if price in value_analysis.index:
                        data = value_analysis.loc[price]
                        st.write(f"**{price}**")
                        st.write(f"Average Rating: {data['avg_rating']:.2f}/5")
                        st.write(f"Total Reviews: {data['review_count']:,}")
                        st.write(f"Restaurants: {data['restaurant_id']}")
                        st.markdown("---")

    # Temporal Analysis Section
    st.markdown(
        '<div class="section-header">📅 Temporal Analysis</div>', unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        # Monthly trends
        if not monthly_trends.empty:
            fig = px.line(
                monthly_trends,
                x="review_month",
                y="review_count",
                title="Monthly Review Volume Trend",
                markers=True,
            )
            fig.update_layout(xaxis_title="Month", yaxis_title="Number of Reviews")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Daily patterns
        if not filtered_reviews.empty:
            filtered_reviews["day_of_week"] = filtered_reviews[
                "review_date"
            ].dt.day_name()
            daily_patterns = filtered_reviews["day_of_week"].value_counts()
            day_order = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            daily_patterns = daily_patterns.reindex(day_order)

            fig = px.bar(
                x=daily_patterns.index,
                y=daily_patterns.values,
                title="Review Volume by Day of Week",
                labels={"x": "Day of Week", "y": "Number of Reviews"},
            )
            st.plotly_chart(fig, use_container_width=True)

    # User Behavior Section
    st.markdown(
        '<div class="section-header">👥 User Behavior</div>', unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        # User activity levels
        if not users.empty:
            activity_counts = users["user_activity"].value_counts()
            fig = px.pie(
                values=activity_counts.values,
                names=activity_counts.index,
                title="User Activity Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Reviews per user distribution
        if not users.empty:
            active_users = users[users["review_count"] > 0]
            fig = px.histogram(
                active_users,
                x="review_count",
                nbins=30,
                title="Distribution of Reviews per User",
                log_y=True,
            )
            fig.update_layout(
                xaxis_title="Number of Reviews",
                yaxis_title="Number of Users (Log Scale)",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Advanced Analytics Section
    st.markdown(
        '<div class="section-header">🔍 Advanced Analytics</div>',
        unsafe_allow_html=True,
    )

    # Check if sentiment data exists
    sentiment_columns = ["compound", "vader_sentiment"]
    has_sentiment_data = all(
        col in filtered_reviews.columns for col in sentiment_columns
    )

    if has_sentiment_data and not filtered_reviews.empty:
        tab1, tab2, tab3 = st.tabs(
            ["😊 Sentiment Analysis", "📊 Correlation Analysis", "🎯 Business Insights"]
        )

        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                # Sentiment distribution
                sentiment_counts = filtered_reviews["vader_sentiment"].value_counts()
                fig = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    title="Review Sentiment Distribution",
                    color=sentiment_counts.index,
                    color_discrete_map={
                        "Positive": "green",
                        "Neutral": "gray",
                        "Negative": "red",
                    },
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Sentiment vs rating
                sentiment_rating = filtered_reviews.groupby("vader_sentiment")[
                    "rating"
                ].mean()
                fig = px.bar(
                    x=sentiment_rating.index,
                    y=sentiment_rating.values,
                    title="Average Rating by Sentiment",
                    color=sentiment_rating.index,
                    color_discrete_map={
                        "Positive": "green",
                        "Neutral": "gray",
                        "Negative": "red",
                    },
                    labels={"x": "Sentiment", "y": "Average Rating"},
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            # Correlation heatmap
            numeric_cols = [
                "rating",
                "food_rating",
                "service_rating",
                "ambiance_rating",
                "review_length",
            ]
            available_cols = [
                col for col in numeric_cols if col in filtered_reviews.columns
            ]

            if len(available_cols) >= 2:
                corr_matrix = filtered_reviews[available_cols].corr()

                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale="RdBu_r",
                    title="Correlation Matrix",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient data for correlation analysis")

        with tab3:
            # Business recommendations
            st.subheader("🎯 Data-Driven Recommendations")

            # Generate insights
            if not filtered_reviews.empty and not filtered_restaurants.empty:
                # Top performing cuisine
                cuisine_perf = filtered_reviews.merge(
                    filtered_restaurants[["restaurant_id", "cuisine_type"]],
                    on="restaurant_id",
                )
                best_cuisine = (
                    cuisine_perf.groupby("cuisine_type")["rating"].mean().idxmax()
                )
                best_cuisine_rating = (
                    cuisine_perf.groupby("cuisine_type")["rating"].mean().max()
                )

                # Most discussed aspects
                if "detected_aspects" in filtered_reviews.columns:
                    all_aspects = []
                    for aspects in filtered_reviews["detected_aspects"].dropna():
                        all_aspects.extend(
                            eval(aspects) if isinstance(aspects, str) else aspects
                        )
                    aspect_counts = pd.Series(all_aspects).value_counts()
                    top_aspect = (
                        aspect_counts.index[0] if len(aspect_counts) > 0 else "N/A"
                    )

                col1, col2 = st.columns(2)

                with col1:
                    st.info(
                        f"**🍽️ Focus Area**: {best_cuisine} cuisine shows highest satisfaction ({best_cuisine_rating:.2f}/5)"
                    )
                    st.info(
                        f"**💰 Price Strategy**: Analyze {selected_price if selected_price != 'All' else 'all'} price points for optimization"
                    )
                    st.info(
                        f"**⭐ Quality Focus**: {top_aspect if 'top_aspect' in locals() else 'Service'} is the most discussed aspect"
                    )

                with col2:
                    st.info(
                        f"**📈 Growth Opportunity**: {filtered_reviews['review_date'].dt.month.mode()[0]} is the peak review month"
                    )
                    st.info(
                        f"**👥 Engagement**: {len(users[users['review_count'] == 0])} inactive users represent growth potential"
                    )
                    st.info(
                        f"**🔧 Improvement**: Restaurants below {min_rating} rating need immediate attention"
                    )

    else:
        st.info(
            "Sentiment analysis data not available. Run the sentiment analysis notebook first."
        )

    # Data Export Section
    st.markdown(
        '<div class="section-header">💾 Data Export</div>', unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Export Filtered Reviews"):
            csv = filtered_reviews.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="filtered_reviews.csv",
                mime="text/csv",
            )

    with col2:
        if st.button("📊 Export Restaurant Stats"):
            restaurant_stats = (
                filtered_reviews.groupby("restaurant_id")
                .agg(
                    {
                        "rating": ["count", "mean", "std"],
                        "food_rating": "mean",
                        "service_rating": "mean",
                    }
                )
                .round(3)
            )
            restaurant_stats.columns = [
                "review_count",
                "avg_rating",
                "rating_std",
                "avg_food",
                "avg_service",
            ]
            csv = restaurant_stats.to_csv()
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="restaurant_stats.csv",
                mime="text/csv",
            )

    with col3:
        if st.button("📋 Export Summary Report"):
            summary_data = {
                "Metric": [
                    "Total Restaurants",
                    "Total Reviews",
                    "Average Rating",
                    "Unique Users",
                ],
                "Value": [
                    total_restaurants,
                    total_reviews,
                    f"{avg_rating:.2f}",
                    unique_users,
                ],
            }
            summary_df = pd.DataFrame(summary_data)
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="summary_report.csv",
                mime="text/csv",
            )

    # Footer
    st.markdown("---")
    st.markdown(
        "**Built with Streamlit** | "
        "**Data Engineering Portfolio** | "
        "Restaurant Review Analytics Dashboard"
    )


if __name__ == "__main__":
    main()
