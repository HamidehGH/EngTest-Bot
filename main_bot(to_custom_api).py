import os
import requests
import psycopg2
import schedule
import time
from dotenv import load_dotenv

load_dotenv()


# Establish a connection to your PostgreSQL database
conn = psycopg2.connect(
    dbname="TestDB",
    user="postgres",
    password="123456",
    host="localhost"
)

cur = conn.cursor()

# Your bot's token
bot_token = os.getenv('API_KEY')
chat_id = "454795115"

# The base URL for the custom Telegram API
api_url = 'https://myworker.hgh5310.workers.dev' 

#api_url = 'https://api.telegram.org'
'''
# Function to send a request to your custom Telegram API
def send_telegram_request(method, payload):
    url = f"{api_url}/bot{bot_token}/{method}"
    response = requests.post(url, json=payload)

    return response.json()

'''
# Function to send a request to your custom Telegram API
def send_telegram_request(method, payload):
    url = f"{api_url}/bot{bot_token}/{method}"
    response = requests.post(url, json=payload)

    response_data = response.json()  # Convert response to JSON format
    print("Sending...")
    if 'ok' in response_data and response_data['ok']:
        print("Message sent successfully!")
    else:
        error_description = response_data.get('description', 'Unknown error')
        print(f"Error sending message: {error_description}")
        print('trying again...')
        send_random_question()
        
    return response_data


# Function to get a random question from the database
def get_random_question_from_db():
    cur.execute("SELECT * FROM EnglishQuestions1 ORDER BY RANDOM() LIMIT 1")
    

    result = cur.fetchone()
    return result if result else "No questions found in the database."

# Function to send a message with inline keyboard
def send_message_with_keyboard(chat_id, text, options):
    print("Sending the question...")
    keyboard = [[{"text": option, "callback_data": f"answer_{idx}_{text}"}] for idx, option in enumerate(options)]
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {"inline_keyboard": keyboard}
    }
    return send_telegram_request("sendMessage", payload)

# Function to edit an existing message with a new keyboard
def edit_message_with_keyboard(chat_id, message_id, text, options):
    keyboard = [[{"text": option, "callback_data": f"answer_{idx}_{text}"}] for idx, option in enumerate(options)]
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "reply_markup": {"inline_keyboard": keyboard}
    }
    return send_telegram_request("editMessageText", payload)

# Function to answer a callback query
def answer_callback_query(callback_query_id, text, show_alert=False):
    payload = {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": show_alert
    }
    return send_telegram_request("answerCallbackQuery", payload)

# Function to send a random question to the user
def send_random_question():
    print("Preparing a random question...")
    question = get_random_question_from_db()
    question_text = question[0]
    options = question[1]
    send_message_with_keyboard(chat_id, question_text, options)

# Function to handle button clicks (callback queries)
def handle_button_click(update):
    try:
        if 'callback_query' not in update:
            return 
        print("خر")
        query = update['callback_query']
        data = query['data']
        idx = int(data.split('_')[1])
        question_text = '_'.join(data.split('_')[2:])

        cur.execute("SELECT * FROM EnglishQuestions1 WHERE question = %s", (question_text,))
        row = cur.fetchone()

        if row:
            options = row[1]
            answer = row[2]
            explanation = row[3]

            if options[idx] == answer:
                # Correct answer
                new_options = [f"{option} ✅" if i == idx else option for i, option in enumerate(options)]
                answer_text = f"Correct666666! 🎉 \n{explanation}"
            else:
                # Incorrect answer
                new_options = [f"{option} ❌" if i == idx else option for i, option in enumerate(options)]
                answer_text = f"Incorrect666666! 😕 \n{explanation}"

            edit_message_with_keyboard(
                chat_id=query['message']['chat']['id'],
                message_id=query['message']['message_id'],
                text=question_text,
                options=new_options
            )
            answer_callback_query(query['id'], answer_text, show_alert=True)

    except Exception as e:
        print(f"Error processing callback query: {e}")

# Function to get updates from Telegram
def get_updates(offset=None):
    payload = {"offset": offset} if offset else {}
    response = send_telegram_request("getUpdates", payload)
    return response.get('result', [])




# Main function to run the bot
def main():
    print("Starting the Telegram bot...")
    update_offset = None

    schedule.every(30).seconds.do(send_random_question)

    while True:
        try:
            # Get updates from Telegram
            updates = get_updates(offset=update_offset)

            # Process updates
            for update in updates:
                handle_button_click(update)

                # Update the offset to avoid processing the same update multiple times
                update_offset = update['update_id'] + 1


            # Run pending scheduled jobs
            schedule.run_pending()

            # Sleep for a short time to avoid excessive API requests
            time.sleep(1)

        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)  # Wait before retrying
            
'''
# Main function to run the bot
def main():
    print("Starting the Telegram bot...")
    update_offset = None

    while True:
        try:
            # Get updates from Telegram
            updates = get_updates(offset=update_offset)

            # Process updates
            for update in updates:
                handle_button_click(update)

                # Update the offset to avoid processing the same update multiple times
                update_offset = update['update_id'] + 1

            # Schedule sending a question every 300 seconds
            #schedule.every(60).seconds.do(send_random_question)

            # Run pending scheduled jobs
            schedule.run_pending()

            # Sleep for a short time to avoid excessive API requests
            time.sleep(1)

        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)  # Wait before retrying

'''
            
if __name__ == '__main__':
    print("Initializing the bot script...")
    main()