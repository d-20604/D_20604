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
st.title("🎬 영화 관객수 분석 대시보드")
st.markdown(
    f"현재 선택된 영화: **{selected_movie}**의 관객수 추이를 분석합니다."
)


# --- [사용자 고른 영화 데이터 필터링] ---
movie_df = df[df["영화명"] == selected_movie]


# ==========================================
# [첫 번째 구역: 일별 관객수 선 그래프]
# ==========================================
st.markdown("---")  # 구역을 나누는 수평선
st.subheader("📈 일별 관객수 추이")

# [4. 선그래프 그리기]
fig_line = px.line(
    movie_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}' 일별 관객수 변화",
    labels={"기준일자": "날짜", "해당일관객수": "해당일 관객수"},
    markers=True,  # 데이터 포인트마다 점 표시
)

# 웹앱 화면에 선 그래프 출력
st.plotly_chart(fig_line, use_container_width=True)

# [5. 기타: 첫 번째 그래프 해석 문구 자리]
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 상영 기간 중 관객수가"
    " 가장 높았던 특정 날짜나 주말 효과, 흥행 추이의 급증/급감 시점을 한눈에"
    " 파악할 수 있습니다."
)


# ==========================================
# [두 번째 구역: 누적관객수 영역 차트]
# ==========================================
st.markdown("---")  # 구역을 나누는 수평선
st.subheader("📊 누적관객수 추이")

# [영역차트 그리기]
# Plotly area chart를 이용해 누적관객수의 변화를 면적으로 시각화합니다.
fig_area = px.area(
    movie_df,
    x="기준일자",
    y="누적관객수",
    title=f"'{selected_movie}' 누적관객수 변화",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수"},
)

# 웹앱 화면에 영역 차트 출력
st.plotly_chart(fig_area, use_container_width=True)

# [두 번째 그래프 해석 문구 자리]
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'가 상영되는 동안"
    " 관객이 꾸준히 누적되어 최종 흥행 규모가 완성되는 과정을 완만한 곡선"
    " 형태로 확인할 수 있습니다."
)
