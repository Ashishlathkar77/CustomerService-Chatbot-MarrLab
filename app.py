import streamlit as st
from openai import OpenAI
import config
import requests
import datetime

# Set up OpenAI API Key
client = OpenAI(api_key=config.OPENAI_API_KEY)

# Function to categorize user inquiries
def categorize_query(user_input):
    prompt = (
        f"Categorize the following inquiry into one of the categories: "
        f"scheduling, reminders, information retrieval, task management, general assistance, or general knowledge.\n"
        f"Inquiry: \"{user_input}\"\nCategory:"
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    category = response.choices[0].message.content.strip()
    return category

# Function to set a reminder
def set_reminder(reminder_text):
    return f"Reminder set: {reminder_text}"

# Function to schedule an event
def schedule_event(event_details):
    return f"Event scheduled: {event_details}"

# Function to get weather information
def get_weather(city):
    city = city.strip()
    if not city:
        return "City name cannot be empty."
    
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&APPID={config.WEATHER_API_KEY}"
    
    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        data = response.json()

        if 'weather' in data and 'main' in data and 'wind' in data:
            weather = data['weather'][0]['description'].capitalize()
            temp = round(data['main']['temp'])
            humidity = data['main']['humidity']
            wind_speed = round(data['wind']['speed'])
            
            return (
                f"The weather in {city} is: {weather}. "
                f"Temperature: {temp}ºF, Humidity: {humidity}%, Wind Speed: {wind_speed} mph."
            )
        else:
            return f"No weather data found for {city}. Response: {data}"

    except requests.exceptions.HTTPError as errh:
        return f"Http Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return f"Error Connecting: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"An error occurred: {err}"

# Function to get news information
def get_news():
    news_url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={config.NEWS_API_KEY}"

    try:
        response = requests.get(news_url)
        response.raise_for_status()
        data = response.json()

        if 'articles' in data:
            summaries = []
            for article in data['articles']:
                title = article['title']
                description = article['description'] if article['description'] else "No description available."
                url = article['url']
                published_at = article['publishedAt']

                summaries.append(f"**{title}**: {description} \n*Published on: {published_at}*  \n[Read more]({url})")
            return "\n\n".join(summaries)
        else:
            return "No articles found."

    except requests.exceptions.HTTPError as errh:
        return f"Http Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return f"Error Connecting: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"An error occurred: {err}"

# Function to manage a to-do list
to_do_list = []

def manage_todo_list(action, task=None):
    if action == "add":
        if task:
            to_do_list.append(task)
            return f"Task added: {task}"
        else:
            return "No task provided."
    elif action == "view":
        return "\n".join(to_do_list) if to_do_list else "To-do list is empty."
    elif action == "remove":
        if task in to_do_list:
            to_do_list.remove(task)
            return f"Task removed: {task}"
        else:
            return "Task not found."
# Function to handle general knowledge queries
def get_general_knowledge_response(user_input):
    prompt = (
        f"Provide a detailed response to the following question:\n"
        f"Question: \"{user_input}\"\n"
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

# Function to get Yelp recommendations for restaurants
def get_restaurant_recommendations(city):
    headers = {
        "Authorization": f"Bearer {config.YELP_API_KEY}"
    }
    url = f"https://api.yelp.com/v3/businesses/search?term=restaurants&location={city}&limit=5"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        recommendations = []
        for business in data['businesses']:
            name = business['name']
            rating = business['rating']
            address = ", ".join(business['location']['display_address'])
            recommendations.append(f"**{name}** - Rating: {rating}/5\nLocation: {address}")
        
        return "\n\n".join(recommendations)
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Function to get movie recommendations from TMDB
def get_movie_recommendations(genre=None, year_filter=None):
    # TMDB base URL for movies
    base_url = "https://api.themoviedb.org/3/discover/movie"
    
    # Genre IDs for TMDB (you can expand this as needed)
    genre_ids = {
        "Action": 28,
        "Comedy": 35,
        "Drama": 18,
        "Horror": 27,
        "Science Fiction": 878,
        "Romance": 10749,
        "Thriller": 53
    }
    
    # Prepare the parameters for the API request
    params = {
        "api_key": config.TMDB_API_KEY,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": 1
    }
    
    # Add genre filter if selected
    if genre and genre in genre_ids:
        params["with_genres"] = genre_ids[genre]
    
    # Add year filter based on user input
    if year_filter == "After 2000":
        params["primary_release_date.gte"] = "2000-01-01"
    elif year_filter == "Before 2000":
        params["primary_release_date.lte"] = "1999-12-31"
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        recommendations = []
        for movie in data['results'][:5]:  # Limit to 5 movies
            title = movie['title']
            overview = movie['overview']
            release_date = movie.get('release_date', 'Unknown')
            recommendations.append(f"**{title}** (Released: {release_date}): {overview}")
        
        return "\n\n".join(recommendations)
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Streamlit app UI
st.title("Customer Service Chatbot")
st.write("Ask me anything related to scheduling, reminders, weather, news, tasks, recommendations, or general knowledge!")

user_input = st.text_input("Your question:")

if user_input:
    # Categorize user query
    category = categorize_query(user_input)
    st.text_area("Categorized Query:", value=category, height=50)

    # Handle different categories of inquiries
    if category == "reminders":
        reminder_text = user_input.replace("remind me to", "").strip()
        response = set_reminder(reminder_text)
        st.text_area("Response:", value=response, height=50)

    elif category == "scheduling":
        event_details = user_input.replace("schedule", "").strip()
        response = schedule_event(event_details)
        st.text_area("Response:", value=response, height=50)

    elif category == "information retrieval":
        if "weather" in user_input.lower():
            city = user_input.lower().replace("what's the weather like in", "").replace("weather in", "").replace("what is", "").replace("?", "").strip()
            response = get_weather(city)
            st.text_area("Response:", value=response, height=50)
        elif "news" in user_input.lower():
            response = get_news()
            st.text_area("Response:", value=response, height=50)
        else:
            response = "Sorry, I can't help with that."
            st.text_area("Response:", value=response, height=50)

    elif category == "task management":
        if "add" in user_input:
            task = user_input.replace("add", "").strip()
            response = manage_todo_list("add", task)
            st.text_area("Response:", value=response, height=50)
        elif "view" in user_input:
            response = manage_todo_list("view")
            st.text_area("Response:", value=response, height=50)
        elif "remove" in user_input:
            task = user_input.replace("remove", "").strip()
            response = manage_todo_list("remove", task)
            st.text_area("Response:", value=response, height=50)

    elif category == "general assistance":
        if "recommend" in user_input:
            category = user_input.replace("recommend", "").strip()
            response = get_recommendations(category)
            st.text_area("Response:", value=response, height=50)
        else:
            response = "How can I assist you further?"
            st.text_area("Response:", value=response, height=50)

    elif category == "general knowledge":
        response = get_general_knowledge_response(user_input)
        st.text_area("Response:", value=response, height=50)

# New section for recommendations (restaurants, movies, etc.)
st.subheader("Get Recommendations")
recommendation_type = st.selectbox("Choose a recommendation type:", ["Restaurants", "Movies"])

if recommendation_type == "Restaurants":
    city = st.text_input("Enter the city for restaurant recommendations:")
    if st.button("Get Restaurant Recommendations"):
        if city:
            recommendations = get_restaurant_recommendations(city)
            st.text_area("Recommendations:", value=recommendations, height=200)
        else:
            st.warning("Please enter a city.")

elif recommendation_type == "Movies":
    # Movie genre selection
    movie_genre = st.selectbox("Select a genre:", ["Any", "Action", "Comedy", "Drama", "Horror", "Science Fiction", "Romance", "Thriller"])
    # Year filter for movie recommendations
    year_filter = st.selectbox("Select a time period:", ["Any", "After 2000", "Before 2000"])
    if st.button("Get Movie Recommendations"):
        genre = movie_genre if movie_genre != "Any" else None
        year = year_filter if year_filter != "Any" else None
    
        recommendations = get_movie_recommendations(genre, year)
        st.text_area("Movie Recommendations:", value=recommendations, height=200)
