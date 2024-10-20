import streamlit as st
from openai import OpenAI
import config
import requests
import datetime
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime, timedelta

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

# Email-sending function
def send_email(recipient_email, subject, message_body):
    try:
        sender_email = config.SENDER_EMAIL  # Your email from config
        app_password = config.EMAIL_PASSWORD  # App password from config

        # Setting up MIME
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the body with the msg instance
        msg.attach(MIMEText(message_body, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        server.login(sender_email, app_password)  # Login to your email

        # Convert the message to a string and send
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()

        return "Email sent successfully!"

    except Exception as e:
        return f"Failed to send email. Error: {str(e)}"

def schedule_meeting(user_email, meeting_datetime):
    # Define the URL for the scheduling API
    url = 'https://api.calendly.com/scheduled_events'

    # Calculate the end time for the meeting (30 minutes duration)
    start_time = meeting_datetime
    end_time = start_time + timedelta(minutes=30)

    # Define the payload for the meeting request
    payload = {
        "event": {
            "name": "Meeting with Ashish",
            "start_time": start_time.isoformat() + "Z",  # Use ISO format
            "end_time": end_time.isoformat() + "Z",
            "duration": 30,  # Duration in minutes
            "invitee": {
                "email": user_email
            }
        }
    }

    # Set the headers for authentication
    headers = {
        "Authorization": f"Bearer {config.CALENDLY_API_TOKEN}",
        "Content-Type": "application/json"
    }

    # Make the request to schedule the meeting
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        return True, response.json()  # Return success and response JSON
    else:
        return False, response.text  # Return failure message

# Function to escalate issues to human agents
def escalate_to_human(user_input, user_email, user_contact, issue_intensity):
    subject = "Escalation Request from Chatbot"
    
    # Create message body with user details
    message_body = (
        f"User Inquiry: {user_input}\n"
        f"User Email: {user_email}\n"
        f"User Contact No: {user_contact}\n"
        f"Issue Intensity: {issue_intensity}\n"
        "Please assist with the above inquiry."
    )
    
    # Send the email using the send_email function
    send_email("ashishlathkar7@gmail.com", subject, message_body)
    
    return "Your request has been escalated to a human agent. You will be contacted shortly."

# Calendarific API URL
CALENDARIFIC_URL = "https://calendarific.com/api/v2/holidays"

# Function to fetch holidays using Calendarific API
def fetch_holidays(api_key, country, year, month, day):
    params = {
        'api_key': api_key,
        'country': country,
        'year': year,
        'month': month,
        'day': day,
    }
    try:
        response = requests.get(CALENDARIFIC_URL, params=params)
        data = response.json()
        if response.status_code == 200:
            holidays = data.get('response', {}).get('holidays', [])
            return holidays
        else:
            return f"Error fetching holidays: {data.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return f"Error occurred: {str(e)}"

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

# Email-sending section
st.subheader("Send an Email")

recipient_email = st.text_input("Recipient Email")
subject = st.text_input("Email Subject")
message_body = st.text_area("Message Body")

if st.button("Send Email"):
    if recipient_email and subject and message_body:
        response = send_email(recipient_email, subject, message_body)
        st.success(response)
    else:
        st.error("Please fill out all fields.")

# Streamlit UI
st.title("Schedule a Meeting with Ashish")

# User input for email and meeting time
user_email = st.text_input("Your Email:")
meeting_date = st.date_input("Select Date:")
meeting_time = st.time_input("Select Time:")

# Combine date and time into a single datetime object
if meeting_date and meeting_time:
    meeting_datetime = datetime.combine(meeting_date, meeting_time)

# Button to schedule the meeting
if st.button("Schedule Meeting"):
    if user_email and meeting_date and meeting_time:
        success, result = schedule_meeting(user_email, meeting_datetime)
        if success:
            st.success("Meeting scheduled successfully!")
            st.json(result)  # Display response JSON for confirmation
        else:
            st.error(f"Failed to schedule meeting: {result}")
    else:
        st.warning("Please fill in all fields.")

# Escalation Section
st.subheader("Escalate to Human Assistance")
escalation_input = st.text_area("Describe your issue or request for human assistance:")
user_email = st.text_input("Your email address for follow-up:")
user_contact = st.text_input("Your contact number:")
issue_intensity = st.selectbox("Issue Intensity", ["Low", "Medium", "High"])

if st.button("Escalate Issue"):
    if escalation_input and user_email and user_contact:
        escalation_response = escalate_to_human(escalation_input, user_email, user_contact, issue_intensity)
        st.success(escalation_response)
        
        # Display contact option
        st.markdown("You can also contact us directly at +1 940 493 0104.")
    else:
        st.warning("Please provide your issue, email address, and contact number.")

st.title("Event and Holiday Reminder System")

# User inputs
event_title = st.text_input("Event Title", placeholder="Enter your event title")
event_description = st.text_area("Event Description", placeholder="Enter event details")
event_date = st.date_input("Event Date")
event_time = st.time_input("Event Time")
country_code = st.text_input("Country Code (e.g., US for United States)", max_chars=2).upper()
recipient_email = st.text_input("Your Email", placeholder="Enter your email for event confirmation")

# Submit button
if st.button("Check Holiday and Schedule Event"):
    if not recipient_email:
        st.error("Please enter a valid email address.")

    # Parse the date input
    event_year = event_date.year
    event_month = event_date.month
    event_day = event_date.day

    # Fetch holidays for the provided country and date
    holidays = fetch_holidays(config.CALENDARIFIC_API_KEY, country_code, event_year, event_month, event_day)

    # Display holidays or schedule event
    if isinstance(holidays, str):
        st.error(holidays)  # If there's an error with the API call
    elif holidays:
        # If holidays are found
        st.warning(f"Public Holidays on {event_date}:")
        for holiday in holidays:
            st.write(f"- {holiday['name']}: {holiday['description']}")
        st.write("Consider rescheduling your event if it conflicts with a holiday.")
    else:
        # No holidays found, allow the user to proceed with scheduling the event
        st.success("No public holidays on this date. You can proceed with your event.")
        st.write(f"Event '{event_title}' scheduled on {event_date} at {event_time}.")

        # Prepare the email content
        subject = f"Event Reminder: {event_title}"
        message_body = (
            f"Hello,\n\nYour event '{event_title}' is scheduled on {event_date} at {event_time}.\n\n"
            f"Event Details:\nDescription: {event_description}\nDate: {event_date}\nTime: {event_time}\n\n"
            f"Thank you!"
        )

        # Send confirmation email
        email_status = send_email(recipient_email, subject, message_body)
        if "successfully" in email_status:
            st.success("Confirmation email sent successfully!")
        else:
            st.error(f"Failed to send email: {email_status}")
