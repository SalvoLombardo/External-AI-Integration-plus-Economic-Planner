# External AI Integration plus Economic Planner

## Description

This application is divided in two sections with two frameworks which communicate with each other:  

**Economic Planner (Core Application)**  
This is a forward-looking financial planning app designed to help users manage and forecast their budget over a very flexible period of time. Unlike traditional budget apps that focus only on current balances and immediate expenses, this planner emphasizes planned vs actual transactions, allowing users to track predicted spending and income against real outcomes.

**Key features:**
- Planned Transactions: record intended expenses or income in advance.
- Actual Transactions: confirm what was really spent or earned.
- Is Completed Flag: tracks whether a planned transaction has been realized, ensuring accurate future forecasts.
- Recurring transactions: daily, weekly, monthly, or yearly, for precise future planning.

---

**External AI Integration (FastAPI Module)**  
This project demonstrates how an external AI module can be integrated into an existing application without modifying its core logic, especially for frameworks that do not optimally support asynchronous operations required for AI, such as Flask. The AI component is hosted via FastAPI, providing asynchronous endpoints that can enhance the app with advanced features, such as data analysis or smart suggestions.

**Highlights:**
- Fully decoupled from the main Flask app, making it reusable for other projects.
- Enables AI-powered features even in apps built with frameworks that lack robust async support.
- Serves as a portfolio-ready example of extending existing software with AI services.

---

## Routing of the information and how the two frameworks talk to each other

```text
       ┌─────────────┐
       │  Frontend   │
       │ (User Input)│
       └─────┬───────┘
             │ token + task
             ▼
   ┌──────────────────────┐
   │  FastAPI (AI Gateway)│
   │  - receives task     │
   │  - async processing  │
   └─────┬────────────────┘
         │ HTTP async request (token + prompt)
         ▼
   ┌──────────────────────────┐
   │  Flask App (Core Logic)  │
   │  - endpoint validation   │
   │  - generates JSON data   │
   └─────┬────────────────────┘
         │ JSON response
         ▼
   ┌──────────────────────┐
   │  FastAPI             │
   │  - process data      │
   │  - prepare for LLM   │
   └─────┬────────────────┘
         │ prompt + processed data
         ▼
       ┌───────────────┐
       │     LLM       │
       │  - generates  │
       │    final      │
       │   response    │
       └─────┬─────────┘
             │ final result
             ▼
       ┌─────────────┐
       │  Frontend   │
       │ (Display)   │
       └─────────────┘



Legend (summary)
	•	task → keyword + prompt for the LLM associated with an endpoint
	•	token → JWT used for security validation
	•	processed data → JSON processed and prepared for the LLM
	•	LLM → Large Language Model that generates the final response based on the prompt and data






How to start :
1st terminal: - cd FASTAPI_APP 
              - uvicorn run:app --reload

2nd terminal: - cd FLASK_APP
              - python3 run.py

![Login](Media/Login1.png)







