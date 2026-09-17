import pandas as pd
import plotly.express as px
import streamlit as st

# --- [페이지 설정] ---
# 웹앱의 레이아웃을 넓게(wide) 설정합니다.
st.set_page_config(
    page_title="영화 박스오피스 분석 웹앱", page_icon="🎬", layout="wide"
)


# --- [1. 데이터 불러오기 및 전처리] ---
# @st.cache_data 데코레이터를 사용하여 데이터를 한 번만 불러오고 캐시(저장)합니다.
# 이렇게 하면 앱이 다시 실행되거나 조작할 때마다 데이터를 새로 읽지 않아 속도가 빨라집니다.
@st.cache_data
def load_data():
  url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"

  # pandas로 CSV 파일을 읽어옵니다.
  df = pd.read_csv(url)

  # [2. 날짜 전처리]
  # 결측치(데이터가 빈 칸인 행)가 포함된 행은 삭제합니다.
  df = df.dropna()

  # "기준일자" 컬럼을 날짜(datetime) 형식으로 변환합니다.
  df["기준일자"] = pd.to_datetime(df["기준일자"])

  # 전체 데이터를 기준일자 순서(오름차순)대로 정렬합니다.
  df = df.sort_values(by="기준일자")

  return df


# 데이터 불러오기 함수 실행
df = load_data()


# --- [사이드바: 영화 선택 기능] ---
st.sidebar.header("🔍 검색 및 필터")

# [3. 영화 선택 기능]
# "영화명" 컬럼에서 중복을 제거한 영화 이름 목록을 준비합니다.
# 영화별 총 누적관객수를 구하기 위해 그룹화한 뒤, 관객수 합계가 큰 순서(내림차순)로 정렬합니다.
# (여기서는 데이터프레임의 '누적관객수' 컬럼을 사용하거나 '해당일관객수'의 누적 합을 기준으로 정렬할 수 있습니다.)
movie_total_audience = (
    df.groupby("영화명")["누적관객수"].max().reset_index()
)  # 영화별 최종 누적관객수 기준
sorted_movies_df = movie_total_audience.sort_values(
    by="누적관객수", ascending=False
)
movie_list = sorted_movies_df["영화명"].tolist()

# 사이드바에 셀렉트박스(목록 선택)를 생성합니다.
selected_movie = st.sidebar.selectbox(
    "영화를 선택하세요 (누적관객수 순)", movie_list
)


# --- [메인 화면 구성] ---
st.title("🎬 영화 일별 관객수 분석 대시보드")
st.markdown("선택한 영화의 관객수 변화 추이를 확인할 수 있습니다.")
st.markdown("---")  # 구역을 나누는 수평선


# --- [4. 선그래프 그리기] ---
# 사용자가 사이드바에서 고른 영화의 데이터만 필터링합니다.
movie_df = df[df["영화명"] == selected_movie]

# Plotly를 이용해 선 그래프를 생성합니다.
fig = px.line(
    movie_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}' 일별 관객수 변화",
    labels={"기준일자": "날짜", "해당일관객수": "관객수"},
    markers=True,  # 데이터 포인트마다 점 표시
)

# 웹앱 화면에 Plotly 그래프 출력
st.plotly_chart(fig, use_container_width=True)


# --- [5. 기타: 그래프 해석 문구 자리] ---
# [구역 나눔] 그래프 아래에 해석을 넣을 수 있는 박스를 만듭니다.
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 상영 기간 동안 관객수가"
    " 가장 많았던 날(peak)과 흥행 추이(입소문 여부, 하락세 등)를 한눈에 파악할"
    " 수 있습니다."
)

# (추후 새로운 그래프를 이 아래에 계속 추가하실 수 있습니다.)
