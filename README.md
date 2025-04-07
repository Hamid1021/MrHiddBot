```markdown
# MrHidd : Telegram Bot with Pyrogram

This is a Telegram bot developed using the Pyrogram framework. The bot is designed to handle various functionalities and requires specific dependencies and configurations to operate.

## 📋 Requirements

To ensure the bot functions properly, the following dependencies must be installed:

```
annotated-types==0.7.0
anyio==4.9.0
cachetools==5.5.2
certifi==2025.1.31
charset-normalizer==3.4.1
google-auth==2.38.0
google-genai==1.9.0
h11==0.14.0
httpcore==1.0.7
httpx==0.28.1
idna==3.10
peewee==3.17.9
pyaes==1.6.1
pyasn1==0.6.1
pyasn1_modules==0.4.2
pydantic==2.11.2
pydantic_core==2.33.1
Pyrogram==2.0.106
PySocks==1.7.1
requests==2.32.3
rsa==4.9
sniffio==1.3.1
TgCrypto==1.2.5
typing-inspection==0.4.0
typing_extensions==4.13.1
urllib3==2.3.0
websockets==15.0.1
```

Install these dependencies by running the following command:
```bash
pip install -r requirements.txt
```

## 🔑 Getting Started

To get the bot up and running, you need to configure its API credentials and other settings. Follow these steps:

1. **Obtain API Credentials**
   - Go to [Telegram's official website](https://my.telegram.org/auth).
   - Log in with your Telegram account and navigate to the **API development tools** section.
   - Create a new application and note down the `API_ID` and `API_HASH`.

2. **Configure the `config.py` File**
   - Create a file named `config.py` and fill in the following details:
     ```python
     # API Settings
     API_ID = XXXXXXXX
     API_HASH = "your_api_hash"
     BOT_TOKEN = "your_bot_token"
     OWNER_ID = "owner_telegram_id"

     # Gemini Settings
     GEMINI_API_KEY = "your_gemini_api_key"
     GEMINI_MODEL = "gemini-2.0-flash"

     # Google Search Settings
     GOOGLE_API_KEY = "your_google_api_key"
     GOOGLE_CX = "your_google_cx"
     ```

   - Replace placeholder values with your actual credentials.

3. **Run the Bot**
   - Execute the `myapp.py` file to start the bot:
     ```bash
     python myapp.py
     ```

## ⚙️ Features

- **API Integration:** Integrates with Telegram's bot API using Pyrogram.
- **Gemini Integration:** Utilize advanced AI capabilities with Gemini.
- **Google Search:** Search functionality powered by Google API.

## 🤝 Contribution

If you want to contribute:
1. Fork the repository.
2. Create a new branch.
3. Submit a pull request with your changes.

## 🛠️ Troubleshooting

If you encounter any issues during setup or runtime, feel free to open an issue on this repository.

---

Enjoy building amazing bots with this framework! 🚀
```
