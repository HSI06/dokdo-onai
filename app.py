import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
import base64
import requests
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from rag import load_rag, search_docs

load_dotenv(dotenv_path=".env")

st.set_page_config(page_title="독도 ON-AI", page_icon="🏝️", layout="wide")

def load_image_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Noto+Serif+KR:wght@700&display=swap');

[data-testid="stAppViewContainer"] { background: #f4f6f8 !important; }
[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; }

.topbar {
    background: #fff;
    border-bottom: 3px solid #cd2e3a;
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
}
.logo-text { font-family: 'Noto Sans KR', sans-serif; font-size: 20px; font-weight: 700; color: #111; }
.logo-text span { color: #cd2e3a; }
.topnav { display: flex; gap: 2rem; }
.topnav a { font-size: 13px; color: #555; text-decoration: none; font-family: 'Noto Sans KR'; }

.hero {
    position: relative;
    height: 360px;
    overflow: hidden;
    background: #1a3a5c;
}
.hero img { width: 100%; height: 100%; object-fit: cover; display: block; }
.hero-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(to bottom, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.65) 100%);
}
.hero-content {
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 2rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(205,46,58,0.9);
    color: #fff; font-size: 11px; letter-spacing: 3px;
    padding: 4px 14px; border-radius: 14px; margin-bottom: 0.6rem;
    font-family: 'Noto Sans KR';
}
.hero-title {
    font-family: 'Noto Serif KR', serif;
    font-size: 40px; font-weight: 700; color: #fff;
    letter-spacing: -1px; line-height: 1.2;
    text-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.hero-sub { font-size: 13px; color: rgba(255,255,255,0.8); margin-top: 6px; letter-spacing: 2px; font-family: 'Noto Sans KR'; }

.widget {
    background: #fff;
    border-radius: 10px;
    border: 0.5px solid #e0e3e8;
    padding: 1.2rem;
    margin-bottom: 12px;
}
.w-title {
    font-family: 'Noto Sans KR'; font-size: 14px; font-weight: 700; color: #222;
    display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;
}
.dot-red { width: 7px; height: 7px; border-radius: 50%; background: #cd2e3a; display: inline-block; }
.dot-blue { width: 7px; height: 7px; border-radius: 50%; background: #003478; display: inline-block; }

.weather-temp { font-size: 40px; font-weight: 700; color: #111; font-family: 'Noto Sans KR'; }
.weather-info { font-size: 12px; color: #888; line-height: 1.9; font-family: 'Noto Sans KR'; }
.wtag {
    background: #f0f4ff; color: #003478;
    font-size: 11px; padding: 4px 12px; border-radius: 14px;
    display: inline-block; margin: 3px 3px 0 0; font-family: 'Noto Sans KR';
}

.footer {
    background: #fff; border-top: 1px solid #e8eaed;
    padding: 1rem 2rem; display: flex; justify-content: space-between;
    font-size: 11px; color: #bbb; font-family: 'Noto Sans KR';
    margin-top: 1rem;
}

.stTabs [data-baseweb="tab-list"] {
    background: #fff !important;
    border-bottom: 2px solid #e0e3e8 !important;
    padding: 0 1rem !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Noto Sans KR' !important;
    font-size: 14px !important;
    color: #888 !important;
    padding: 12px 20px !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #cd2e3a !important;
    border-bottom: 2px solid #cd2e3a !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 1.2rem 1.5rem !important;
    background: #f4f6f8 !important;
}

.stButton > button {
    background: #fff !important; color: #555 !important;
    border: 0.5px solid #e0e3e8 !important; border-radius: 20px !important;
    padding: 4px 8px !important; font-family: 'Noto Sans KR' !important;
    font-size: 12px !important;
}
.stButton > button:hover {
    background: #fdecea !important; color: #cd2e3a !important;
    border-color: #f5b8b8 !important;
}
.stChatInput > div { border-radius: 24px !important; border-color: #e0e3e8 !important; }
.stRadio label { font-family: 'Noto Sans KR' !important; font-size: 13px !important; }
[data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ===================== 상단바 =====================
st.markdown("""
<div class="topbar">
    <div class="logo-text">독도 <span>ON-AI</span></div>
    <div class="topnav">
        <a>역사·영유권</a>
        <a>자연·생태</a>
        <a>날씨</a>
        <a>지도</a>
        <a>AI 챗봇</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ===================== 히어로 이미지 =====================
if os.path.exists("dokdo_hero.jpg"):
    hero_b64 = load_image_b64("dokdo_hero.jpg")
    hero_img_tag = f'<img src="data:image/jpeg;base64,{hero_b64}" alt="독도" />'
else:
    hero_img_tag = '<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Dokdo_from_air.jpg/1280px-Dokdo_from_air.jpg" alt="독도 항공사진" />'

st.markdown(f"""
<div class="hero">
    {hero_img_tag}
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-badge">대한민국의 섬 · DOKDO</div>
        <div class="hero-title">독도 ON-AI</div>
        <div class="hero-sub">AI로 만나는 우리 땅 독도</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ===================== RAG 로딩 =====================
@st.cache_resource
def get_retriever():
    return load_rag()

retriever = get_retriever()

# ===================== 날씨 =====================
def get_weather():
    try:
        now = datetime.now()
        base_date = now.strftime("%Y%m%d")
        hour = now.hour if now.minute >= 10 else now.hour - 1
        base_time = f"{hour:02d}00"
        url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
        params = {
            "serviceKey": os.getenv("WEATHER_API_KEY"),
            "numOfRows": 10, "pageNo": 1, "dataType": "JSON",
            "base_date": base_date, "base_time": base_time, "nx": 144, "ny": 123
        }
        res = requests.get(url, params=params, timeout=5)
        items = res.json()["response"]["body"]["items"]["item"]
        weather = {item["category"]: item["obsrValue"] for item in items}
        return {
            "temp": weather.get("T1H", "?"),
            "humidity": weather.get("REH", "?"),
            "wind": weather.get("WSD", "?"),
            "rain": weather.get("RN1", "?")
        }
    except:
        return None

# ===================== session state 초기화 =====================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "example_prompt" not in st.session_state:
    st.session_state.example_prompt = ""

# ===================== 언어 선택 (탭 밖) =====================
language = st.radio("언어 / Language", ["한국어", "English"], horizontal=True, label_visibility="collapsed")
is_korean = language == "한국어"

if is_korean:
    placeholder = "독도에 대해 무엇이든 물어보세요!"
    system_prompt = "당신은 독도 전문 AI 가이드입니다. 독도의 역사, 자연환경, 생태계, 지리적 특성, 날씨, 기후에 대해 정확하고 친절하게 안내해주세요. 반드시 한국어로만 답변하세요. 한국어 외의 다른 언어 문자(한자, 중국어, 일본어, 영어 단어 등)를 절대 섞지 마세요. 오직 한글과 숫자, 기호만 사용하세요. 숫자 범위를 표현할 때는 반드시 '~' 하나만 사용하세요. 독도와 관련없는 질문이나 대화를 하면 '저는 독도 전문 AI 가이드입니다. 독도와 관련된 질문만 답변드릴 수 있어요 😊 독도의 역사, 자연환경, 관광 정보 등 궁금한 점을 물어보세요!' 라고 답변하세요."
else:
    placeholder = "Ask me anything about Dokdo!"
    system_prompt = "You are an AI guide specializing in Dokdo Island. Please provide accurate and friendly information about Dokdo's history, natural environment, ecosystem, geographical features, weather, and climate. Always respond in English only. When expressing number ranges, always use only one tilde (~). Keep your answers concise and clear, within 3-4 sentences. If the user asks questions unrelated to Dokdo, respond with: 'I am a Dokdo specialist AI guide. I can only answer questions related to Dokdo 😊 Please ask about Dokdo\'s history, natural environment, tourism information, etc.'"

llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile")

# ===================== 탭 구조 =====================
tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI 챗봇", "🌤️ 날씨", "🗺️ 지도", "📸 계절별 사진"])

# ===================== 탭1: AI 챗봇 =====================
with tab1:
    # 예시 질문 버튼
    st.markdown("**💬 예시 질문**" if is_korean else "**💬 Example Questions**")
    questions = [
    ("독도 가는 방법", "How to visit?"),
    ("입도 예약 방법", "How to reserve?"),
    ("방문 시 주의사항", "Precautions"),
    ("최적 방문 시기", "Best time to visit"),
    ("독도에서 볼거리", "What to see?"),
    ("울릉도→독도 소요시간", "Travel time?")
]
    cols = st.columns(len(questions), gap="small")
    for i, (q_ko, q_en) in enumerate(questions):
        q = q_ko if is_korean else q_en
        with cols[i]:
            if st.button(q, key=f"q{i}"):
                st.session_state.example_prompt = q
                st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 예시 질문 처리
    if st.session_state.example_prompt:
        prompt = st.session_state.example_prompt
        st.session_state.example_prompt = ""
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
        st.rerun()

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

# ===================== 탭2: 날씨 =====================
with tab2:
    weather = get_weather()
    if weather:
        st.markdown(f"""
        <div class="widget">
            <div class="w-title"><span class="dot-blue"></span>{"실시간 날씨 · 독도" if is_korean else "Real-time Weather · Dokdo"}</div>
            <div style="display:flex; align-items:center; gap:14px; margin-bottom:10px;">
                <div class="weather-temp">{weather['temp']}°</div>
                <div class="weather-info">{"현재 기온" if is_korean else "Current Temp"}<br>{"독도 · 기상청 연동" if is_korean else "Dokdo · KMA API"}</div>
            </div>
            <div>
                <span class="wtag">💧 {"습도" if is_korean else "Humidity"} {weather['humidity']}%</span>
                <span class="wtag">💨 {"풍속" if is_korean else "Wind"} {weather['wind']}m/s</span>
                <span class="wtag">🌧️ {"강수" if is_korean else "Rain"} {weather['rain']}mm</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("날씨 정보를 불러올 수 없습니다." if is_korean else "Unable to load weather data.")

# ===================== 탭3: 지도 =====================
with tab3:
    lang = "ko" if is_korean else "en"
    map_html = f"""
    <!DOCTYPE html><html><head>
    <meta charset="utf-8"/>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
    * {{ margin:0; padding:0; }}
    html, body {{ width:100%; height:100%; }}
    #map {{ width:100%; height:500px; }}
    </style>
    </head><body>
    <div id="map"></div>
    <script>
    var lang = "{lang}";
    window.addEventListener('load', function() {{
        var map = L.map('map').setView([37.2413, 131.8673], 14);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
        var red = L.divIcon({{className:'', html:'<div style="background:#cd2e3a;width:12px;height:12px;border-radius:50%;border:2px solid #fff;"></div>'}});
        var blue = L.divIcon({{className:'', html:'<div style="background:#003478;width:12px;height:12px;border-radius:50%;border:2px solid #fff;"></div>'}});
        L.marker([37.2408, 131.8696], {{icon: red}}).addTo(map).bindPopup(lang=='ko' ? '<b>🏝️ 동도</b>' : '<b>🏝️ East Islet (Dongdo)</b>').openPopup();
L.marker([37.2418, 131.8652], {{icon: blue}}).addTo(map).bindPopup(lang=='ko' ? '<b>🏝️ 서도</b>' : '<b>🏝️ West Islet (Seodo)</b>');
    }});
    </script></body></html>
    """
    components.html(map_html, height=500)

# ===================== 탭4: 계절별 사진 =====================
with tab4:
    island_options = ["동도", "서도"] if is_korean else ["East Islet (Dongdo)", "West Islet (Seodo)"]
    season_options = ["봄", "여름", "가을", "겨울"] if is_korean else ["Spring", "Summer", "Autumn", "Winter"]

    island_col, season_col = st.columns([1, 2])
    with island_col:
        island = st.radio("섬 선택" if is_korean else "Select Islet", island_options, horizontal=True, label_visibility="collapsed")
    with season_col:
        season = st.radio("계절" if is_korean else "Season", season_options, horizontal=True, label_visibility="collapsed")

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

# 푸터
st.markdown(f"""
<div class="footer">
    <div>독도 ON-AI · IT스마트관광플랫폼 · 황사익</div>
    <div>🇰🇷 {"대한민국의 섬, 독도" if is_korean else "Dokdo, Beautiful Island of Korea"}</div>
</div>
""", unsafe_allow_html=True)