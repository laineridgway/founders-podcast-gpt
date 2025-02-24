# Founders Podcast GPT

AI-powered search & chat for [Founders Podcast](https://founderspodcast.com).

All code & data used is 100% open source.

## How It Works

This project:
1. Uses a free API to get YT transcripts for Founders Podcast's videos
2. Creates a Chroma Vector DB (using OpenAI's embeddings API)
3. Creates the chatbot (streamlit) that uses Founders' transcripts for information (Anthropic API).

## How to Run It

1. Make sure you have all the API keys
    - [Supadata.ai](https://supadata.ai/) (100 Credits free)
    - OpenAI
    - Anthropic

2. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/laineridgway/founders-podcast-gpt.git
   cd founders-podcast-gpt
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Then edit `backend/.env` with your own API Keys.

4. Get Transcripts:
   ```bash
   python backend/01_scraper.py
   ```

5. Populate ChromaDB:
   ```bash
   python backend/02_vector_storage.py
   ```

5. Run FastAPI backend:
   ```bash
   python backend/main.py
   ```

6. In another terminal, run the Streamlit frontend:
   ```bash
   streamlit run frontend/app.py
   ```

7. Your chatbot is now accessible locally in the browser.

## Credits

Huge thanks to [Founders Podcast](https://founderspodcast.com) for the brilliant biography reviews.

## Contact

Feel free to fork, open issues, or submit PRs to help improve the project.
