import pandas as pd
from rapidfuzz import process

try:
    data =pd.read_csv("symptom_database.csv.csv")
    df=pd.DataFrame(data)
    df['Symptom']=df['Symptom'].str.title()
except:
    print("Database is Missing")


def Matcher(inp):
    match=process.extractOne(inp,df['Symptom'],score_cutoff=70)
    if match:
        symptom,confidence,idx=match
        return idx
    else:
        return None
def Chatbot():
    print("Welcome to the AI Health Adviser ")
    print("Please enter the Symptoms you are getting or Type 'exit' to quit")
    while True:
        inp=input("Enter Your Response: ")
        clean_input=inp.strip().title()
        if clean_input =="Exit":
            print("Goodbye")
            print("Thank you for using the AI Health Advisor. Stay healthy! 💪")
            break
        else:
            idx=Matcher(clean_input)
            if idx is not None:
                print("------Advice for Health based on your given Symptoms------")
                print(f"Detected Symptom :  {df.loc[idx,'Symptom']}")
                print(f"Possible Causes :  {df.loc[idx, 'Possible Causes']}")
                print(f"Remedies :  {df.loc[idx, 'Remedies']}")
                print(f"Foods to Avoid :  {df.loc[idx, 'Foods to Avoid']}")
                print(f"Tips/ General Medicine :  {df.loc[idx, 'Tips / General Medicine']}")
                print(f"Screen time Link :  {df.loc[idx, 'Screen Time Link']}")
                print(f"Sleep Cycle Link : {df.loc[idx,'Sleep Cycle Link']}")
                print(f"Preferred Meals : {df.loc[idx,'Preferred Indian Meal']}")
                print(f"Quick Home Remedy Options : {df.loc[idx,'Home Remedy Option']}")
                print(f"Time To Relief : {df.loc[idx,'Time to Relief']}")
                print("Follow these advices and GET WELL SOON")
                print("----------------------------------------")
                print("Consult to Doctor if the problem persists")
            else:
                print("--> I couldn't find a close match for that symptom. Could you please rephrase or check your spelling?")


Chatbot()