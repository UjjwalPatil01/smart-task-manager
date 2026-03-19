# 🚀 Smart Task Manager (AI-Powered)

A modern, AI-powered task management web application built using **Flask** and **Google Gemini AI**, designed to help users efficiently manage and prioritize tasks.

🔗 **Live Demo:**  
https://smart-task-manager-ri8k.onrender.com/

---

## ✨ Features

### 🧠 AI-Powered Priority Detection
Automatically classifies tasks into:
- 🔥 High (urgent, exam, deadline)
- ⚡ Medium (project, meeting)
- 🟢 Low (others)

Uses **Google Gemini API** for intelligent predictions.

---

### 📋 Task Management
- Add tasks with:
  - Title  
  - Due Date  
  - Priority (Manual or AI-suggested)  
- ✅ Mark tasks as completed  
- ✏️ Edit existing tasks  
- 🗑️ Delete tasks  

---

### 🔍 Smart Filtering & Search
- Filter tasks by status:
  - All / Pending / Completed  
- Filter tasks by priority  
- Search tasks by keywords  

---

### 📊 Sorting & Live Statistics
- Sort tasks by:
  - Due Date  
  - Priority  
- Ascending / Descending order  
- View live statistics:
  - Total tasks  
  - Completed tasks  
  - Pending tasks  

---

### 🎨 UI/UX
- Clean dark theme  
- Smooth interactions  
- Fully mobile-friendly and responsive design  

---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)  
- **Frontend:** HTML, CSS (Jinja2 Templates)  
- **AI Integration:** Google Gemini API (`gemini-2.5-flash`)  
- **Database:** JSON (lightweight local storage)  
- **Deployment:** Render  

---

## 📂 Project Structure

```
smart-task-manager/
│
├── app.py # Main Flask application logic
├── tasks.json # Local database for storing tasks
├── requirements.txt # Python dependencies
├── .env # Environment variables (API Key)
├── .gitignore # Files to ignore in Git
│
├── templates/
│ ├── index.html # Main dashboard UI
│ └── edit.html # Task editing UI
│
├── static/
│ └── main.css # Custom styling
│
└── README.md # Project documentation
```

---

## ⚙️ Setup & Installation

#### 1. Clone the Repository

- ```git clone https://github.com/UjjwalPatil01/smart-task-manager.git```

- ```cd smart-task-manager```

#### 2. Install Dependencies
- ```pip install -r requirements.txt```

#### 3. Setup Environment Variables

- Create a .env file in the root directory:

  - ```GOOGLE_API_KEY=your_api_key_here```

#### 4. Run Locally
- ```python app.py```

Open in browser:

- ```http://127.0.0.1:5000```


## 🌍 Deployment (Render)

This project is deployed using Render.

- Steps:

  - Push code to GitHub
  - Create a new Web Service on Render
  - Connect your repository
  - Add environment variable:
    - ```GOOGLE_API_KEY```
  - Set start command:
    - ```python app.py```

- ⚠️ Note: For production, using gunicorn app:app is recommended.

## 🔐 Security Note

- Never commit API keys
- Use environment variables
- Ensure ```.env``` is in ```.gitignore```

## 🚧 Future Improvements
- User authentication (Login / Signup)
-  Database integration (MongoDB / PostgreSQL)
- Task categories / tags
-  Notifications & reminders
-  Advanced AI insights

## 👨‍💻 Author

#### Ujjwal Pradip Patil

## ⭐ Support

If you like this project:
  - Star ⭐ the repository
  - Share it with others

## 🧠 Key Learnings

- Full-stack development using Flask
- AI API integration (LLMs)
- Real-world debugging & deployment
- Clean UI/UX design

