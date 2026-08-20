# Business FAQ & Lead-Capture Chatbot

## English

### What this project is
This project is a small-business chatbot demo built for a restaurant, **Maple & Thyme Bistro**. Its purpose is not only to answer common customer questions, but also to capture leads such as table bookings, catering inquiries, and callback requests.

### What it does
- Answers common FAQs like opening hours, reservations, menu, parking, location, and catering.
- Detects when a user wants to book, contact the team, or request catering.
- Collects the visitor's name and phone/email.
- Saves leads into a database.
- Provides a simple admin view to check captured leads.

### How it works
1. A visitor opens the website and uses the floating chat widget.
2. The widget sends messages to the FastAPI backend using the `/chat` API.
3. The backend checks the message using rule-based logic and fuzzy FAQ matching.
4. If the message matches a known FAQ, the bot returns the relevant answer.
5. If the message shows lead intent, the bot starts a step-by-step lead capture flow.
6. The conversation state is stored per session, so the bot remembers whether it is waiting for a name or contact detail.
7. Captured lead data is stored in SQLite and can be viewed in the admin dashboard.

### Main technical parts
- **Frontend**: embeddable chat widget built with HTML, CSS, and JavaScript
- **Backend**: FastAPI
- **Database**: SQLite
- **Validation**: Pydantic
- **Chat logic**: rule-based intent detection with fuzzy matching using `rapidfuzz`

### Why this project is useful
- Reduces repetitive customer support questions
- Captures leads even outside business hours
- Gives small businesses a simple way to turn website visitors into inquiries
- Can be embedded into a real client website with a single script

### Example flow
User: "What are your hours?"  
Bot: replies with restaurant opening hours

User: "I want to book a table"  
Bot: asks for the user's name  
User: "Rahul"  
Bot: asks for phone number or email  
User: "rahul@gmail.com"  
Bot: saves the lead and confirms follow-up

---

## Hindi

### Ye project kya hai
Ye ek **small business chatbot demo** hai jo restaurant use-case ke liye banaya gaya hai, specifically **Maple & Thyme Bistro** ke liye. Iska kaam sirf customer ke common questions ka answer dena nahi hai, balki booking aur inquiry ko **lead me convert karna** bhi hai.

### Ye kya karta hai
- Common FAQs ka answer deta hai, jaise:
  - opening hours
  - reservations
  - menu
  - parking
  - location
  - catering
- Detect karta hai ki user booking karna chahta hai ya team se contact karna chahta hai.
- User ka naam aur contact details collect karta hai.
- Lead ko database me save karta hai.
- Admin ko captured leads dekhne ke liye simple dashboard deta hai.

### Ye kaise kaam karta hai
1. Website visitor floating chat widget open karta hai.
2. Widget user ka message backend ke `/chat` endpoint par bhejta hai.
3. Backend FastAPI par bana hua hai aur message ko process karta hai.
4. Bot message ko check karta hai:
   - greeting hai ya nahi
   - FAQ match ho rahi hai ya nahi
   - booking/catering/contact intent hai ya nahi
5. Agar FAQ match milti hai, bot predefined answer bhej deta hai.
6. Agar user lead intent show karta hai, bot step-by-step name aur contact collect karta hai.
7. Session state save hoti hai, isliye bot yaad rakhta hai ki abhi wo name ka wait kar raha hai ya contact ka.
8. Final lead SQLite database me save ho jati hai aur admin panel se dekhi ja sakti hai.

### Main technical parts
- **Frontend**: HTML, CSS, JavaScript based embeddable widget
- **Backend**: FastAPI
- **Database**: SQLite
- **Validation**: Pydantic
- **Chat logic**: rule-based intent detection aur fuzzy matching using `rapidfuzz`

### Is project ki business value
- Repetitive customer questions ko automate karta hai
- Business band hone ke baad bhi leads capture karta hai
- Website visitors ko booking/inquiry me convert karne me help karta hai
- Real client website me easily embed kiya ja sakta hai

### Example flow
User: "What are your hours?"  
Bot: restaurant ke opening hours bata deta hai

User: "I want to book a table"  
Bot: user ka naam poochta hai  
User: "Rahul"  
Bot: phone number ya email poochta hai  
User: "rahul@gmail.com"  
Bot: lead save karke confirmation de deta hai

---

## Suggested Use
You can use this file:
- in your portfolio project description
- in a client proposal
- in project documentation
- while explaining the project in an interview
