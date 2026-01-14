# RepoLens

RepoLens is a powerful tool designed to provide deep insights into GitHub repositories. By combining the GitHub API with Google's Gemini AI, RepoLens delivers comprehensive summaries, health checks, and statistical data, helping developers quickly understand any codebase.

## Features

-   **Deep Repository Analysis**: Get instant access to key metrics like stars, forks, issues, contributors, and detailed language breakdowns.
-   **AI-Powered Insights**: Utilizes Google's Gemini AI to generate human-readable summaries, identify the technology stack, and explain the repository's core purpose.
-   **Health & Maintenance Checks**: Automatically evaluates repository health based on recent commit activity, issue management, and release frequency.
-   **User Profiling**: Analyze GitHub user profiles to see their top languages, recent activity, and contribution stats.
-   **Repository Search**: Search for repositories directly within the application.
-   **User Authentication**: Secure login and registration powered by Firebase.

## Prerequisites

Before running the application, ensure you have the following:

-   Python 3.8+
-   A GitHub Account (for Personal Access Token)
-   A Google Cloud Account (for Gemini API Key)
-   A Firebase Project (for Authentication)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Sujitha-1005/RepoLens.git
    cd repolens
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**

    Create a `.env` file in the root directory and add your API keys:

    ```env
    GITHUB_TOKEN=your_github_pat_here
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

    *Note: Ensure you have your Firebase configuration set up in `static/js/firebase-config.js`.*

## Usage

1.  **Start the application:**

    ```bash
    python app.py
    ```

2.  **Access the dashboard:**

    Open your web browser and navigate to `http://localhost:5000`.

3.  **Analyze a Repo:**
    -   Log in to your account.
    -   Paste a GitHub repository URL (e.g., `https://github.com/flask/flask`) into the analysis bar.
    -   View detailed AI-driven insights and statistics.

## Tech Stack

-   **Backend**: Flask (Python)
-   **Frontend**: HTML, CSS, JavaScript
-   **AI Model**: Google Gemini 2.0 via `google-genai`
-   **Authentication**: Google Firebase
-   **APIs**: GitHub REST API
