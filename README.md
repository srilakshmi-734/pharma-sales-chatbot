# 💊 Pharma Sales Chatbot

A **production-ready AI chatbot** that translates natural language queries into SQL, retrieves data from a PostgreSQL database, and presents results in a clean, structured format.

This project demonstrates **end-to-end system design** combining AI, backend engineering, and scalable architecture.

---

# 🎯 What This Project Solves

Business users often struggle to query databases using SQL.

This system allows users to ask questions like:

* *“Which products have offers?”*
* *“What is the highest discount?”*

👉 And get **accurate, database-driven answers instantly**

---

# 🧠 System Overview

```text
User Query
   ↓
LLM (Text → SQL)
   ↓
SQL Validation Layer
   ↓
PostgreSQL Database
   ↓
Python Formatter
   ↓
Frontend Chat UI
```

---

# ⚙️ Key Features

### 🤖 AI-Powered Querying

* Converts natural language → SQL queries
* Eliminates need for manual SQL writing

### 🛡️ Safe & Controlled Execution

* Only SELECT queries allowed
* Prevents invalid or harmful queries
* Enforces strict schema usage

### 📊 Business-Aware Intelligence

* Understands terms like:

  * **offer → combo_type / scheme**
  * **discount → sales_price - purchase_price**
* Handles real-world pharma logic

### ⚡ High Performance

* Redis caching for repeated queries
* Fast response times

### 🧾 Clean Output Formatting

* Deterministic formatting (not LLM-based)
* Example:

  ```
  • Mucolite Drops → 10+1 (Net Rate)
  • Antibiotic Capsules → 20+2 (Bulk Offer)
  ```

### 🐳 Fully Containerized

* One-command setup using Docker
* No manual configuration required

---

# 🏗️ Tech Stack

| Layer      | Technology       |
| ---------- | ---------------- |
| Frontend   | React            |
| Backend    | FastAPI (Python) |
| Database   | PostgreSQL       |
| Caching    | Redis            |
| AI Model   | Groq (LLaMA)     |
| Deployment | Docker           |

---

# 📁 Project Structure

```text
backend/     → FastAPI + AI logic + SQL engine  
frontend/    → React chat interface  
db/          → Schema + seed data  
docker-compose.yml → Full system orchestration  
```

---

# 🚀 How to Run

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/pharma-sales-chatbot.git
cd pharma-sales-chatbot
```

---

### 2️⃣ Add Environment Variables

Create `.env`:

```env
GROQ_API_KEY=your_api_key_here
```

---

### 3️⃣ Run with Docker

```bash
docker-compose up --build
```

---

### 4️⃣ Open Application

* Frontend → http://localhost:3000
* Backend → http://localhost:8000

---

# 💬 Example Queries

Try asking:

* “Show products with offers”
* “Which product has highest discount?”
* “List all products without offers”
* “Average sales price”

---

# 🛡️ Engineering Highlights

* ✔ Strict SQL generation (no hallucination)
* ✔ Query validation before execution
* ✔ Redis fail-safe caching
* ✔ Retry mechanism for DB connections
* ✔ Clean separation of concerns (AI / DB / UI)

---

# 📌 Why This Project Stands Out

This is not just a chatbot.

It demonstrates:

* **System design thinking**
* **AI + Backend integration**
* **Production-ready architecture**
* **Real-world business logic handling**

---

# 🔮 Future Scope

* Dashboard with charts (Power BI style)
* Role-based access (Admin/User)
* Cloud deployment (AWS / Render)
* Query analytics & insights

---

# 👩‍💻 Author

**Sri Lakshmi Elluri**

---

# ⭐ Support

If you found this useful, give it a ⭐ on GitHub!
