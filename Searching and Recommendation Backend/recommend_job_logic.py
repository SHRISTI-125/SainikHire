import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

#cleaning and optimizing job and user text
def clean_optimize(prompt):
    return prompt.lower().replace('\n', ' ').strip()

#embedding skills
def skill_embedding(skills):
    add = ', '.join(skills)
    return f"We are looking for a person skilled in {add} to work in our company."

#20% weightage to keywords
def keyword_overlap_boost(user_skills, job_skills):
    match_count = sum(skill.lower() in job_skills.lower() for skill in user_skills)
    return match_count / len(user_skills) if user_skills else 0

# recommendation logic
def recommend_jobs_logic(user_input,db, model, collection, top_k=6):
    if '@gmail.com' in user_input:
        user = db['users'].find_one({'email': user_input})
    #else:
    #    user = db['users'].find_one({'password': user_input})
    try:
        if not user or 'skills' not in user:
            return []
        user_skill_list = user['skills']
        user_skill_all = ' '.join(user_skill_list)
        user_skill = clean_optimize(user_skill_all)
        user_emb = model.encode(user_skill).reshape(1, -1)
    except Exception as e:
        return []

    results = []
    for job in collection.find({"skills": {"$exists": True}}):
        try:
            job_skill_all = skill_embedding(job["skills"])
            job_optimize = clean_optimize(job_skill_all)#converting into lower case->because sentence transformer will work well.
            job_emb = model.encode(job_optimize).reshape(1, -1)
            score = cosine_similarity(user_emb, job_emb)[0][0]

            keyword_boost = keyword_overlap_boost(user_skill_list, ' '.join(job["skills"]))
            final_score = score + keyword_boost * 0.2
            
            results.append({
                "_id": str(job["_id"]),
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "date_of_posting": job.get("date_of_posting", ""),
                "last_date": job.get("last_date", ""),
                "rank": job.get("rank", ""),
                "education": job.get("education", ""),
                "location": job.get("location", ""),
                "description": job.get("description", ""),
                "skills": job.get("skills", ""),
                "apply_link": job.get("apply_link", ""),
                "score": round(float(final_score), 4) #after giving 20% weight to keyword, beacuse it increase similarity%
            })
        except Exception as e:
            print("Skip job due to error:", e)
            continue

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
