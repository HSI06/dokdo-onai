import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from rag import load_rag, search_docs

load_dotenv(dotenv_path=".env")

st.set_page_config(page_title="독도 ON-AI", page_icon="🏝️")

@st.cache_resource
def get_retriever():
    return load_rag()

retriever = get_retriever()

language = st.radio("언어를 선택하세요 / Select Language", ["한국어", "English"], horizontal=True)

is_korean = language == "한국어"

st.title("🏝️ 독도 ON-AI")
st.caption("AI 기반 독도 가상 체험 플랫폼" if is_korean else "AI-based Dokdo Virtual Experience Platform")

def get_weather():
    try:
        now = datetime.now()
        base_date = now.strftime("%Y%m%d")
        hour = now.hour if now.minute >= 10 else now.hour - 1
        base_time = f"{hour:02d}00"
        url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
        params = {
            "serviceKey": os.getenv("WEATHER_API_KEY"),
            "numOfRows": 10,
            "pageNo": 1,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": 144,
            "ny": 123
        }
        res = requests.get(url, params=params, timeout=5)
        items = res.json()["response"]["body"]["items"]["item"]
        weather = {}
        for item in items:
            weather[item["category"]] = item["obsrValue"]
        temp = weather.get("T1H", "?")
        rain = weather.get("RN1", "?")
        wind = weather.get("WSD", "?")
        humidity = weather.get("REH", "?")
        if is_korean:
            return f"🌡️ 기온 {temp}°C  💧 습도 {humidity}%  💨 풍속 {wind}m/s  🌧️ 강수 {rain}mm"
        else:
            return f"🌡️ Temp {temp}°C  💧 Humidity {humidity}%  💨 Wind {wind}m/s  🌧️ Rain {rain}mm"
    except:
        return "날씨 정보를 불러올 수 없습니다." if is_korean else "Unable to load weather data."

st.info(get_weather())

map_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style> body { margin:0; } #map { width:100%; height:300px; } </style>
</head>
<body>
<div id="map"></div>
<script>
var map = L.map('map').setView([37.2426, 131.8597], 10);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
L.marker([37.2426, 131.8597]).addTo(map).bindPopup('🏝️ Dokdo').openPopup();
</script>
</body>
</html>
"""
components.html(map_html, height=310)

st.subheader("🗓️ 계절별 독도" if is_korean else "🗓️ Dokdo by Season")

island_options = ["동도", "서도"] if is_korean else ["East Islet (Dongdo)", "West Islet (Seodo)"]
island = st.radio("섬 선택" if is_korean else "Select Islet", island_options, horizontal=True)

season_options = ["봄", "여름", "가을", "겨울"] if is_korean else ["Spring", "Summer", "Autumn", "Winter"]
season = st.radio("계절 선택" if is_korean else "Select Season", season_options, horizontal=True)

season_map = {"봄": "spring", "여름": "summer", "가을": "autumn", "겨울": "winter",
              "Spring": "spring", "Summer": "summer", "Autumn": "autumn", "Winter": "winter"}
island_map_dict = {"동도": "dongdo", "서도": "seodo",
                   "East Islet (Dongdo)": "dongdo", "West Islet (Seodo)": "seodo"}

img_path = f"{island_map_dict[island]}_{season_map[season]}1.jpg"

def get_caption(island, season):
    is_dongdo = island in ["동도", "East Islet (Dongdo)"]
    is_winter = season in ["겨울", "Winter"]
    if is_dongdo and is_winter:
        return "하늘에서 바라본 동도" if is_korean else "Aerial view of Dongdo"
    elif is_dongdo:
        return "서도 정상에서 바라본 동도" if is_korean else "Dongdo viewed from Seodo"
    else:
        return "동도 정상에서 바라본 서도" if is_korean else "Seodo viewed from Dongdo"

if os.path.exists(img_path):
    st.image(img_path, caption=f"{get_caption(island, season)} ({season})", use_container_width=True)
else:
    st.warning("해당 사진이 없습니다." if is_korean else "Photo not available.")

st.subheader("💬 독도 AI 가이드" if is_korean else "💬 Dokdo AI Guide")

if is_korean:
    placeholder = "독도에 대해 무엇이든 물어보세요!"
    system_prompt = "당신은 독도 전문 AI 가이드입니다. 독도의 역사, 자연환경, 생태계, 지리적 특성, 날씨, 기후에 대해 정확하고 친절하게 안내해주세요. 반드시 한국어로만 답변하세요. 한국어 외의 다른 언어 문자(한자, 중국어, 일본어 등)를 절대 섞지 마세요. 숫자 범위를 표현할 때는 반드시 '~' 하나만 사용하세요. 독도와 관련없는 질문이나 대화를 하면 '저는 독도 전문 AI 가이드입니다. 독도와 관련된 질문만 답변드릴 수 있어요 😊 독도의 역사, 자연환경, 관광 정보 등 궁금한 점을 물어보세요!' 라고 답변하세요."
else:
    placeholder = "Ask me anything about Dokdo!"
    system_prompt = "You are an AI guide specializing in Dokdo Island. Please provide accurate and friendly information about Dokdo's history, natural environment, ecosystem, geographical features, weather, and climate. Always respond in English only. When expressing number ranges, always use only one tilde (~). If the user asks questions unrelated to Dokdo, respond with: 'I am a Dokdo specialist AI guide. I can only answer questions related to Dokdo 😊 Please ask about Dokdo's history, natural environment, tourism information, etc.'"

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input(placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    context = search_docs(retriever, prompt)

    response = llm.invoke([
        SystemMessage(content=f"{system_prompt}\n\n참고 문서:\n{context}"),
        HumanMessage(content=prompt)
    ])

    with st.chat_message("assistant"):
        st.write(response.content.replace("~~", "~"))
    st.session_state.messages.append({"role": "assistant", "content": response.content})