# EngTest-Bot: A Daily English Grammar Quiz Bot for Telegram

A simple, automated Telegram bot that sends daily English grammar questions to user. User gets instant feedback with correct answers and explanations.

## Features

- **Automated Daily Quizzes**: Sends a new question every day.
- **Interactive & Instant Feedback**: Uses inline keyboards and provides immediate answers.
- **PostgreSQL Backend**: Manages the question bank in a robust database.

## Setup & Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/HamidehGH/EngTest-Bot.git
    cd EngTest-Bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt 
    ```

3.  **Configure your environment:**
    Create a `.env` file in the root directory and add your credentials.
    ```dotenv
    API_KEY="YOUR_TELEGRAM_BOT_TOKEN"
    CHAT_ID="YOUR_TELEGRAM_CHAT_ID"
    DB_HOST="your_db_host"
    DB_NAME="your_db_name"
    DB_USER="your_db_user"
    DB_PASSWORD="your_db_password"
    ```

4.  **Initialize the database:**
    Run this script **once** to create the table and insert the sample questions.
    ```bash
    python insert_questions.py
    ```

5.  **Run the bot:**
    ```bash
    python main_bot_v2.py
    ```

---

### Note on API Access for Restricted Regions

If you are in a region where direct access to `api.telegram.org` is blocked, you can use a reverse proxy to forward the requests. A free and popular way to do this is with **Cloudflare Workers**.

After deploying your own worker, you would simply update the `api_url` in your `main_bot_v2.py` file to point to your worker's URL.

---

## Question Dataset

This repository includes a sample of 11 questions for testing. The full, preprocessed dataset contains 500 grammar questions. If you are interested in obtaining the full dataset, please contact me at **hgh5310@gmail.com**.
