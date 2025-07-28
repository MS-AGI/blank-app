import streamlit as st
import datetime
import pickle
import os

DATA_FILE = 'progress.pkl'

# Task list
tasks = [
    "Book Reading",
    "Path (Spiritual Practice)",
    "Studying (≥3h)",
    "Excursion and Sports (≥45min)"
]

def initialize_data():
    return {"Mankrit": {}, "Seerat": {}}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            return pickle.load(f)
    return initialize_data()

def save_data(data):
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

TM = 120

def calculate_marks(data):
    return {child: sum(len(t) for t in data[child].values()) for child in data}

def gift_quality(score):
    if score >= ((80*TM)/100):
        return "🎁 Excellent Gift"
    elif score >= ((50*TM)/100):
        return "🎁 Good Gift"
    elif score >= ((30*TM)/100):
        return "😊 Average Gift"
    else:
        return "🎈 Small Token"

# Inject OneSignal JS
def inject_onesignal(app_id):
    onesignal_script = f"""
    <script src="https://cdn.onesignal.com/sdks/OneSignalSDK.js" async=""></script>
    <script>
      window.OneSignal = window.OneSignal || [];
      OneSignal.push(function() {{
        OneSignal.init({{
          appId: "{app_id}",
          notifyButton: {{
            enable: true,
          }},
          promptOptions: {{
            slidedown: {{
              prompts: [
                {{
                  type: "push",
                  autoPrompt: true,
                  text: {{
                    actionMessage: "Allow reminders to mark kids' tasks.",
                    acceptButton: "Allow",
                    cancelButton: "No Thanks"
                  }},
                }}
              ]
            }}
          }}
        }});
      }});
    </script>
    """
    st.components.v1.html(onesignal_script, height=0)

# Streamlit UI
st.set_page_config(page_title="M & S Task Tracker", layout="centered")
st.title("📘 M & S Daily Tracker")

# Inject OneSignal (Replace this with your actual app ID)
inject_onesignal("YOUR-ONESIGNAL-APP-ID")  # <-- Replace with your actual App ID

data = load_data()
today = datetime.date.today().isoformat()

mode = st.sidebar.radio("Choose Mode", ["Parent (Mark Tasks)", "Child (View Progress)"])

if mode == "Parent (Mark Tasks)":
    st.header("✅ Log Completed Tasks")
    selected_date = st.date_input("Choose Date", datetime.date.today())
    date_str = selected_date.isoformat()

    for child in ["Mankrit", "Seerat"]:
        st.subheader(f"Tasks done by {child}")
        selected_tasks = st.multiselect(f"Select tasks for {child}", tasks, key=f"{child}_{date_str}")
        if selected_tasks:
            data[child][date_str] = selected_tasks

    if st.button("💾 Save Tasks"):
        save_data(data)
        st.success("Tasks saved!")

elif mode == "Child (View Progress)":
    st.header("📊 Progress")
    marks = calculate_marks(data)
    for child in ["Mankrit", "Seerat"]:
        st.subheader(f"{child}'s Stats")
        st.write(f"Total Marks: **{marks[child]}**")
        last_days = sorted(data[child].keys())[-7:]
        for day in last_days:
            st.markdown(f"- `{day}`: {', '.join(data[child][day])}")

    if st.button("📅 Show Winner & Gifts"):
        st.subheader("🎉 Monthly Result")
        st.write(f"M: {marks['Mankrit']} → {gift_quality(marks['Mankrit'])}")
        st.write(f"S: {marks['Seerat']} → {gift_quality(marks['Seerat'])}")
        if marks["Mankrit"] > marks["Seerat"]:
            st.success("🏆 Winner: Mankrit")
        elif marks["Seerat"] > marks["Mankrit"]:
            st.success("🏆 Winner: Seerat")
        else:
            st.info("It's a tie!")

# Sidebar Reminder Instructions
st.sidebar.markdown("### 🔔 About Reminders")
st.sidebar.info("""
You'll get a **notification daily** (9 PM) to log children's tasks.

Please **allow notifications** when prompted. This works on Android and modern browsers on iPhone (Safari).
""")
