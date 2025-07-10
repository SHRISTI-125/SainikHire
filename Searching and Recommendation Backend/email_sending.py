from secret import password
import schedule
import smtplib
from email.message import EmailMessage
from pymongo import MongoClient
from datetime import datetime, timedelta
import time
import threading
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

password=password()
# Email 
SENDER_EMAIL = "shristikumarisingh125@gmail.com"
APP_PASSWORD = password

client = MongoClient("mongodb://localhost:27017/")
db = client["SainikHire"]
users_col = db["new_user"]
jobs_col = db["database1"]

def send_job_reminders():
    print(f"Today is : [{datetime.now()}]") 

    today = datetime.now().date()
    time_left = today + timedelta(days=5) # job ending in 5 days

    ending_jobs = list(jobs_col.find({
        "last_date": {
            "$gte": today.strftime('%Y-%m-%d'),
            "$lte": time_left.strftime('%Y-%m-%d')
        }
    }))

    if not ending_jobs:
        print("No upcoming jobs found.")
        return
    userupdating_recommendations = {}

    # summary
    job_lines = []
    job_skills = []
    for job in ending_jobs:
        job_title = job['title']
        job_link = job.get('apply_link', 'http://localhost:5173/')
        job_last_date = job['last_date']
        job_skill_text = job.get('skills', []) 

        job_skills_list = job.get('skills', [])
        job_skill_text = " ".join(job_skills_list)  
        job_embedding = model.encode(job_skill_text, convert_to_tensor=False) #converting job skills into embedding

        matching_users = []

        for user in users_col.find():
            user_email = user.get('email')
            user_skills_list = user.get('skills', [])
            
            user_skill_text = " ".join(user_skills_list)
            user_embedding = model.encode(user_skill_text, convert_to_tensor=False)

            user_embedding = np.array(user_embedding).reshape(1, -1)
            job_embedding = np.array(job_embedding).reshape(1, -1)

            similarity = cosine_similarity(user_embedding, job_embedding)[0][0] #finding similarity

            if similarity >= 0.4:  #if more similar then; take user's email with message
                matching_users.append(user_email)
                if user_email not in userupdating_recommendations:
                    userupdating_recommendations[user_email] = []
                userupdating_recommendations[user_email].append(f"{job_title} (Last Date: {job_last_date})\nApply: {job_link}\n")


        if not matching_users:
            print(f"No matching users for job: {job_title}")
            continue
            

    subject = "Upcoming Job Deadlines within Next 5 Days"
#body = f"""Hi there,
    #Here are some jobs whose last dates are coming soon, apply as soon as possible
    
    #{job_title}
    #This job is ending at {job_last_date}.
    #Apply Here: {job_link}
    
    #Regards,
    #SainikHire
    #"""


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, APP_PASSWORD)
        for email,job_list in userupdating_recommendations.items():
            list_of_jobs = "\n".join(job_list)
            body = f"""Hi There,
            The following jobs matched your skills and are ending in next 5 days.
            
            {list_of_jobs}
            
            Apply now!

            Regards,
            SainikHire
            """
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = SENDER_EMAIL
            msg['To'] = email
            msg.set_content(body)
            smtp.send_message(msg)
            print(f"Sent to: {email}")

#send_job_reminders() 
#schedule.every(1).days.do()

#print("Scheduler started. Waiting to send reminders every 1 days...")

def run_scheduler():
    send_job_reminders() 
    schedule.every(1).days.do(send_job_reminders)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Run scheduler in background
t = threading.Thread(target=run_scheduler)
t.start()
