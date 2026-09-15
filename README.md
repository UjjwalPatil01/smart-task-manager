# Smart Task Manager — AI-Powered Task Management

A full-stack task management application built with **Python, Flask, and Google Gemini**, combining everyday CRUD workflows with AI-assisted task-priority classification.

**Live Demo:** https://smart-task-manager-ri8k.onrender.com/

## Overview

Smart Task Manager is a practical application for creating, updating, completing, deleting, searching, filtering, and sorting tasks. Google Gemini is used to suggest task priority from the task description, turning a conventional CRUD application into a small applied-AI workflow.

## Key Features

- 🤖 **AI priority classification** using Google Gemini.
- ✅ **CRUD task management** — create, edit, complete, and delete tasks.
- 🔎 **Search and filtering** by status and priority.
- 📅 **Sorting** by due date and priority.
- 📊 **Live task statistics** for total, completed, and pending tasks.
- 📱 **Responsive UI** designed for desktop and mobile screens.
- ☁️ **Render deployment** for a publicly accessible demo.

## AI Workflow

```text
Task Title / Details
        ↓
Python / Flask Backend
        ↓
Google Gemini API
        ↓
AI Suggested Priority
   High / Medium / Low
        ↓
Task Stored + Displayed
```

## Technology Stack

| Area | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, Jinja2 templates |
| AI | Google Gemini API (`gemini-2.5-flash`) |
| Storage | JSON-based local persistence |
| Deployment | Render |

## Project Structure

```text
smart-task-manager/
├── app.py
├── tasks.json
├── requirements.txt
├── templates/
│   ├── index.html
│   └── edit.html
├── static/
│   └── main.css
└── README.md
```

## Run Locally

### 1. Clone

```bash
git clone https://github.com/UjjwalPatil01/smart-task-manager.git
cd smart-task-manager
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file and add your Gemini API key:

```env
GOOGLE_API_KEY=your_api_key_here
```

Never commit real API keys.

### 4. Run

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Deployment

The current project is deployed on Render. Configure the required environment variable and use the Flask application start command supported by the deployment configuration.

## What this project demonstrates

- Python and Flask backend development
- CRUD application design
- LLM API integration
- Practical AI-assisted decision workflows
- Responsive web application development
- Deployment and environment-variable management

## Future Improvements

Potential next steps include persistent database storage, authentication, task categories, reminders, and richer AI-assisted productivity features.

## Author

**Ujjwal Pradip Patil**

[GitHub](https://github.com/UjjwalPatil01) · [LinkedIn](https://www.linkedin.com/in/ujjwalpatil-ai) · [Portfolio](https://ujjwal-ai-portfolio.vercel.app)
