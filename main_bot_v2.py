import os
import requests
import psycopg2
import schedule
import time
from dotenv import load_dotenv

load_dotenv()


class TelegramBot():

    def __init__(self):
        print('Initializing the Telegram Bot...')
        self.api_url = 'https://api.telegram.org'
        self.bot_token = os.getenv('API_KEY')
        self.chat_id = os.getenv('CHAT_ID')
        self.update_offset = None
        self.db_conn = None


    #Establishes and returns a new database connection
    def get_db_connection(self):
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"))


    #Checks if the database connection is active, and reconnects if not
    def ensure_db_connection(self):
        if self.db_conn is None or self.db_conn.closed != 0:
            print('Database connection is closed or was not established. Reconnecting...')
            try:
                self.db_conn = self.get_db_connection()
                print('Database connection is successful')
            except psycopg2.OperationalError as e:
                print(f'Database connection Failed:{e}')
                self.db_conn = None
    


    def send_telegram_request(self, method, payload):
        url = f"{self.api_url}/bot{self.bot_token}/{method}"
        print("Sending request:", method)
        try: 
            response = requests.post(url, json=payload)
            response_data = response.json()
            if 'ok' in response_data and response_data['ok']:
                print("Request sent successfully!")
                return response_data

            else:
                error_description = response_data.get('description', 'Unknown error')
                print(f"Error sending message: {error_description}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error sending telegram request: {e}")
            return None



    def get_random_question_from_db(self):
        self.ensure_db_connection()
        if not self.db_conn:
            return None
        
        try:
            with self.db_conn.cursor() as cur:
                # Checks if there are any unsent questions
                cur.execute("SELECT EXISTS (SELECT 1 FROM questions WHERE is_sent = 0)")
                exists_unsent = cur.fetchone()[0]
                if not exists_unsent:
                    print('All the questions are sent. Refreshing the database..')
                    cur.execute("UPDATE questions SET is_sent = 0")
                    conn.commit()
                    print("Database refreshed. Fetching the first question now...")
                
                cur.execute("SELECT * FROM questions WHERE is_sent = 0 ORDER BY id ASC LIMIT 1")
                result = cur.fetchone()
                return result
                
        except Exception as e:
            print(f"Error in get_random_question_from_db: {e}")
            return None



    def handle_button_click(self, update):
        if 'callback_query' not in update:
            return 

        self.ensure_db_connection()
        if not self.db_conn:
            return None

        try:
            with self.db_conn.cursor() as cur:
                print("Answer received")
                query = update['callback_query']
                chat_id = query['message']['chat']['id']
                message_id = query['message']['message_id']
                data = query['data']
                question_id = int(data.split('_')[2])
                idx = int(data.split('_')[1])
                cur.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
                row = cur.fetchone()
                if row:
                    question_text = row[1]
                    options = row[2]
                    answer = row[3]
                    explanation = row[4]
                    if options[idx] == answer:
                        # Correct answer
                        new_options = [f"{option} ✅" if i == idx else option for i, option in enumerate(options)]
                        answer_text = f"Correct! 🎉 \n{explanation}"
                    else:
                        # Incorrect answer
                        new_options = [f"{option} ❌" if i == idx else option for i, option in enumerate(options)]
                        answer_text = f"Incorrect! 😕 \n{explanation}"

                    print('Updating the buttoms and Sending the explanation')
                    self.edit_message_with_keyboard(message_id, question_text, new_options, question_id)
                    self.answer_callback_query(query['id'], answer_text, show_alert=True)

                else:
                    print('Question was not found')
            
        except Exception as e:
            print(f"Error processing callback query: {e}")

   

    def send_message_with_keyboard(self, question_id, question_text, options):
        print("Sending the question...")
        keyboard = [[{"text": option, "callback_data": f"answer_{idx}_{question_id}"}] for idx, option in enumerate(options)]
        payload = {
            "chat_id": self.chat_id,
            "text": question_text,
            "reply_markup": {"inline_keyboard": keyboard},
            'question_id': question_id
        }
        response = self.send_telegram_request("sendMessage", payload)
        return response is not None

        

    def send_random_question(self):
        print("Preparing a random question...")
        question = self.get_random_question_from_db()
        question_id = question[0]
        question_text = question[1]
        options = question[2]
        if self.send_message_with_keyboard(question_id, question_text, options):
            print(f"Successfully sent question ID {question_id}. Marking as sent.")
            try:
                self.ensure_db_connection()
                with self.db_conn.cursor() as cur:
                    cur.execute("UPDATE questions SET is_sent = 1 WHERE id = %s;", (question_id,))
                    self.db_conn.commit()
            except Exception as e:
                print(f"Failed to mark question ID {question_id} as sent: {e}")

        else:
            print(f"Failed to send question {question_id} to Telegram.")



    def edit_message_with_keyboard(self, message_id, question_text, options, question_id):
        keyboard = [[{"text": option, "callback_data": f"answer_{idx}_{question_id}"}] for idx, option in enumerate(options)]
        payload = {
            "chat_id": self.chat_id,
            "message_id": message_id,
            "text": question_text,
            "reply_markup": {"inline_keyboard": keyboard},
        }
        return self.send_telegram_request("editMessageText", payload)

    

    def answer_callback_query(self, callback_query_id, text, show_alert=False):
        payload = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert
        }
        return self.send_telegram_request("answerCallbackQuery", payload)


    
    def get_updates(self, offset=None):
        payload = {"offset": offset} if offset else {}
        response = self.send_telegram_request("getUpdates", payload)
        return response.get('result', [])



    def run(self):
        print('Bot is starting...')
        #Coordinated Universal Time (UTC)
        schedule.every().day.at("7:00").do(self.send_random_question)
        while True:
            try:
                # Get updates from Telegram
                updates = self.get_updates(offset=self.update_offset)
                for update in updates:
                    self.handle_button_click(update)
                    # Update the offset to avoid processing the same update multiple times
                    self.update_offset = update['update_id'] + 1

                # Run pending scheduled jobs
                schedule.run_pending()
                # Sleep for a short time to avoid excessive API requests
                time.sleep(1)

            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(5)  


if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()



