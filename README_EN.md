# Lumina Cinema - Movie Ticket & Review System

![Lumina Cinema](lumina_preview.png)

> [🇨🇳 中文文档 (Chinese)](README_CN.md)

## 🌟 Project Overview

**Lumina Cinema** is a modern, premium movie ticket booking and review system built with Flask. It features the "Lumina" design language—a dark, cinematic aesthetic with glassmorphism effects and fluid animations, designed to offer an immersive user experience similar to top-tier streaming platforms.

This project was developed for a Database Analysis course, demonstrating a full-stack implementation of a relational database system.

### 🎨 Lumina Design System
The "Lumina" design concept represents **"Light in the Darkness"**. 
- **Cinematic Atmosphere**: Deep black backgrounds (`#0a0a0a`) paired with vibrant orange-red gradients (`#ff4b1f`) evoke the feeling of a movie theater.
- **Glassmorphism**: Translucent, blurred layers create depth and a modern interface hierarchy.
- **Fluid Motion**: Smooth transitions and micro-interactions (fade-ins, scale effects) enhance usability and delight.

---

## ✨ Key Features

- **User System**: Secure registration, login, and profile management (avatar, real name).
- **Immersive Browsing**: 
  - Hero banner showcasing trending movies.
  - Responsive grid layout for movie lists.
  - Advanced filtering by genre and year.
- **Interactive Booking**:
  - Visual seat selection with a realistic theater screen perspective.
  - Real-time price calculation and seat status (Available/Selected/Sold).
- **Review Ecosystem**:
  - Star rating system (1-5 stars).
  - User reviews with like/interaction functionality.
- **Order Management**: 
  - Complete lifecycle tracking (Pending -> Paid -> Cancelled).
  - Order history and details.
- **Automated Maintenance**: Background tasks automatically clean up expired screenings to keep the database optimized.

## 🛠 Tech Stack

**Backend**
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Security**: Werkzeug (Password Hashing), CSRF Protection

**Frontend**
- **Template Engine**: Jinja2
- **Styling**: Custom CSS3 (Lumina Design System), Flexbox/Grid
- **Icons**: FontAwesome 6
- **Responsiveness**: Mobile-first design

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd movie-ticket-system
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Initialize Database & Test Data**
   ```bash
   python init_test_data.py
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the App**
   Open your browser and visit: `http://localhost:5001`

### Test Accounts
- **Username**: user1
- **Password**: password123

---

## 📂 Project Structure

```
movie-ticket-system/
├── backend/                  # Backend Core Code
│   ├── static/               # Static Resources
│   │   ├── css/              # Lumina Stylesheets
│   │   ├── images/           # Posters & Avatars
│   │   └── js/               # Frontend Logic
│   ├── templates/            # Jinja2 HTML Templates
│   ├── app.py                # App Entry & Routing
│   ├── models.py             # Database Models
│   ├── init_test_data.py     # Data Initialization Script
│   └── requirements.txt      # Dependencies
└── database/                 # Database Docs
    └── movie_ticket_system.sql
```

## 📄 License

This project is for educational purposes only.

## 👨‍💻 Author

**ChrisHAO**

