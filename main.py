import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import requests
import streamlit as st

# 1. 페이지 제목 및 기본 레이아웃 설정
st.set_page_config(
    page_title="어제 박스오피스 순위", page_icon="🎬", layout="wide"
)


# 2. API 데이터 가져오기 함수 (1시간 캐싱 적용)
@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key: str, target_date: str):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


# 3. 파이썬 내장 zoneinfo를 활용한 한국 시간(KST) 기준 '어제' 날짜 계산
now_kst = datetime.datetime.now(ZoneInfo("Asia/Seoul"))
yesterday_kst = now_kst - datetime.timedelta(days=1)

# API 요청용 날짜 형식 (YYYYMMDD)
target_dt = yesterday_kst.strftime("%Y%m%d")
# 화면 출력용 날짜 형식 (YYYY년 MM월 DD일)
display_dt = yesterday_kst.strftime("%Y년 %m월 %d일")

# 화면 상단 제목 표시
st.title("🎬 어제 일별 박스오피스")
st.caption(f"기준 날짜: {display_dt} (한국 시간 기준)")


# 4. secrets에서 API 키 불러오기
if "KOBIS_KEY" not in st.secrets or not st.secrets["KOBIS_KEY"]:
    st.error("⚠️ API 키가 설정되지 않았습니다.")
    st.markdown(
        """
    **확인해야 할 사항:**
    1. Streamlit Cloud 앱 관리 페이지의 **Secrets** 메뉴로 이동하세요.
    2. 아래와 같이 `KOBIS_KEY` 이름으로 발급받은 인증키를 추가해 주세요.
    ```toml
    KOBIS_KEY = "여기에_발급받은_키_입력"
