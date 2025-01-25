# Blogs Maker

A Python-based tool for generating and managing blog content using AI assistance. This project leverages modern AI capabilities to help streamline the blog creation process.

## Features

- AI-powered blog content generation
- Clean and modern web interface
- Secure API key management
- Easy-to-use interface

## Prerequisites

- Python 3.12+
- pip (Python package manager)
- An Anthropic API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/williavs/blogs-maker.git
cd blogs-maker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
   - Create a `.streamlit/secrets.toml` file
   - Add your Anthropic API key:
     ```toml
     ANTHROPIC_API_KEY = "your-api-key-here"
     ```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided URL (typically http://localhost:8501)

3. Follow the on-screen instructions to generate blog content

## Security Notes

- Never commit your API keys or sensitive information to the repository
- Always use environment variables or secure secrets management for API keys
- The `.streamlit` directory is included in `.gitignore` to prevent accidental exposure of secrets

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Streamlit
- Powered by Anthropic's Claude API
- Special thanks to all contributors 