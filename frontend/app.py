import os
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_mongo_uri() -> str:
    mongo_uri = os.getenv("MONGODB_URI", "").strip()
    if not mongo_uri:
        raise RuntimeError("MONGODB_URI is missing. Add your Atlas connection string first.")
    return mongo_uri


def get_collection():
    client = MongoClient(get_mongo_uri())
    database_name = os.getenv("MONGODB_DB_NAME", "bmi_calculator")
    collection_name = os.getenv("MONGODB_COLLECTION_NAME", "bmi_records")
    return client[database_name][collection_name]


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 2)


def get_bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal weight"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def save_record(name: str, age: int, height_cm: float, weight_kg: float) -> dict:
    bmi = calculate_bmi(height_cm, weight_kg)
    record = {
        "name": name.strip(),
        "age": age,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "bmi": bmi,
        "category": get_bmi_category(bmi),
        "created_at": datetime.now(timezone.utc),
    }

    collection = get_collection()
    result = collection.insert_one(record)
    record["_id"] = str(result.inserted_id)
    return record


def load_history() -> list[dict]:
    collection = get_collection()
    records = []
    for record in collection.find().sort("created_at", -1):
        records.append(
            {
                "id": str(record["_id"]),
                "name": record["name"],
                "age": record["age"],
                "height_cm": record["height_cm"],
                "weight_kg": record["weight_kg"],
                "bmi": record["bmi"],
                "category": record["category"],
                "created_at": record["created_at"],
            }
        )
    return records


def check_connection() -> None:
    client = MongoClient(get_mongo_uri())
    client.admin.command("ping")


st.set_page_config(page_title="BMI Calculator", page_icon="⚖️", layout="centered")
st.title("BMI Calculator")
st.caption("Calculate BMI, save records directly to MongoDB Atlas, and review history.")

with st.form("bmi_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
    height_cm = st.number_input("Height (cm)", min_value=1.0, value=170.0, step=0.5)
    weight_kg = st.number_input("Weight (kg)", min_value=1.0, value=70.0, step=0.5)
    submitted = st.form_submit_button("Calculate and Save")

if submitted:
    if not name.strip():
        st.error("Please enter a name.")
    else:
        try:
            record = save_record(name, int(age), float(height_cm), float(weight_kg))
            st.success(
                f"BMI saved for {record['name']}. BMI: {record['bmi']} ({record['category']})"
            )
        except Exception as exc:
            st.error(f"Could not save the record to MongoDB Atlas. Details: {exc}")

st.subheader("Connection Check")
if st.button("Test MongoDB Connection"):
    try:
        check_connection()
        st.success("MongoDB Atlas connection is working.")
    except Exception as exc:
        st.error(f"MongoDB connection failed. Details: {exc}")

st.subheader("Saved Records")
if st.button("Refresh History"):
    st.rerun()

try:
    history = load_history()
    if history:
        st.dataframe(history, use_container_width=True)
    else:
        st.info("No BMI records saved yet.")
except Exception as exc:
    st.warning(f"History will appear here once MongoDB Atlas is connected. Details: {exc}")
