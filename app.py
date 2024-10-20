import streamlit as st
from openai import OpenAI
import config
import requests
import datetime
from google_calendar import authenticate_google_calendar, create_event

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
    
    # Correctly constructing the weather URL
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&APPID={config.WEATHER_API_KEY}"
    
    try:
        response = requests.get(weather_url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Check if the API response has the necessary keys
        if 'weather' in data and 'main' in data and 'wind' in data:
            weather = data['weather'][0]['description'].capitalize()  # More detailed description
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
                published_at = article['publishedAt']  # Get the published date

                # Format the output string
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

# Function to provide recommendations
def get_recommendations(category):
    recommendations = {
        "restaurants": "Here are some recommended restaurants: Restaurant A, Restaurant B, Restaurant C.",
    }
    return recommendations.get(category, "No recommendations available for this category.")

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

# New section for scheduling events
st.subheader("Schedule an Event")
with st.form(key='schedule_event_form'):
    summary = st.text_input("Event Title:")
    description = st.text_area("Event Description:")
    start_date = st.date_input("Start Date:", value=datetime.date.today())
    start_time = st.time_input("Start Time:")
    end_date = st.date_input("End Date:", value=start_date)
    end_time = st.time_input("End Time:")
    
    # Submit button inside the form
    submit_button = st.form_submit_button("Schedule Event")
    
    if submit_button:
        # Combine date and time into a single datetime object
        start_datetime = datetime.datetime.combine(start_date, start_time)
        end_datetime = datetime.datetime.combine(end_date, end_time)

        # Authenticate and create event
        service = authenticate_google_calendar()
        event = create_event(service, summary, description, start_datetime.isoformat(), end_datetime.isoformat())
        st.success(f"Event created: {event.get('htmlLink')}")
