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
movie_total_audience = df.groupby("영화명")["누적관객수"].max().reset_index()
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
    f"현재 선택된 개별 영화: **{selected_movie}** / 전체 박스오피스 종합 분석"
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

st.plotly_chart(fig_line, use_container_width=True)

# [첫 번째 그래프 해석 문구 자리]
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
fig_area = px.area(
    movie_df,
    x="기준일자",
    y="누적관객수",
    title=f"'{selected_movie}' 누적관객수 변화",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수"},
)

st.plotly_chart(fig_area, use_container_width=True)

# [두 번째 그래프 해석 문구 자리]
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'가 상영되는 동안"
    " 관객이 꾸준히 누적되어 최종 흥행 규모가 완성되는 과정을 완만한 곡선"
    " 형태로 확인할 수 있습니다."
)


# ==========================================
# [세 번째 구역: 조건별 Top 5 영화 다중 선그래프]
# ==========================================
st.markdown("---")  # 구역을 나누는 수평선
st.subheader("🏆 장기 흥행(20일 이상 등장) Top 5 영화 비교")

movie_stats = (
    df.groupby("영화명")
    .agg(appear_days=("기준일자", "count"), max_audience=("누적관객수", "max"))
    .reset_index()
)
filtered_movies = movie_stats[movie_stats["appear_days"] >= 20]
top_5_filtered = filtered_movies.sort_values(
    by="max_audience", ascending=False
).head(5)
top_5_movie_names = top_5_filtered["영화명"].tolist()

top_5_df = df[df["영화명"].isin(top_5_movie_names)]
fig_multi_line = px.line(
    top_5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="장기 흥행 Top 5 영화 누적관객수 비교 (20일 이상 등장)",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수", "영화명": "영화 제목"},
)

st.plotly_chart(fig_multi_line, use_container_width=True)

# [세 번째 그래프 해석 문구 자리]
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 단기성 흥행작을 제외하고, 20일 이상 꾸준히"
    " 순위에 오르며 장기 흥행한 상위 5개 영화들의 관객 누적 속도와 최종 흥행"
    " 규모를 비교할 수 있습니다."
)


# ==========================================
# [네 번째 구역: 전체 관객수 합계 및 7일 이동평균선]
# ==========================================
st.markdown("---")  # 구역을 나누는 수평선
st.subheader("📉 전체 박스오피스 일별 관객수 및 7일 이동평균")

daily_total_df = (
    df.groupby("기준일자")["해당일관객수"].sum().reset_index()
)
daily_total_df["7일이동평균"] = (
    daily_total_df["해당일관객수"].rolling(window=7).mean()
)

fig_ma = px.line(
    daily_total_df,
    x="기준일자",
    y=["해당일관객수", "7일이동평균"],
    title="전체 박스오피스 일별 관객수 총합 및 7일 이동평균 추이",
    labels={"기준일자": "날짜", "value": "관객수", "variable": "지표 구분"},
)
fig_ma.update_traces(selector=dict(name="해당일관객수"), opacity=0.3)
fig_ma.update_traces(selector=dict(name="7일이동평균"), line=dict(width=3))

st.plotly_chart(fig_ma, use_container_width=True)

# [네 번째 그래프 해석 문구 자리]
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 요일별 변동(주말 효과 등)이 심한 일별"
    " 관객수 원본 데이터 속에서, 7일 이동평균선을 통해 전체 극장가의 전반적인"
    " 관객 수요 흐름과 추세(상승세 및 하락세)를 매끄럽게 파악할 수 있습니다."
)


# ==========================================
# [다섯 번째 구역: 월별 전체 관객수 합계 막대그래프]
# ==========================================
st.markdown("---")  # 구역을 나누는 수평선
st.subheader("📊 월별 박스오피스 총 관객수 비교")

daily_total_df["연월"] = daily_total_df["기준일자"].dt.strftime("%Y-%m")
monthly_total_df = (
    daily_total_df.groupby("연월")["해당일관객수"].sum().reset_index()
)

fig_bar = px.bar(
    monthly_total_df,
    x="연월",
    y="해당일관객수",
    title="월별 전체 박스오피스 관객수 합계",
    labels={"연월": "월 (Year-Month)", "해당일관객수": "총 관객수"},
    text_auto=".2s",
)

st.plotly_chart(fig_bar, use_container_width=True)

# [다섯 번째 그래프 해석 문구 자리]
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 월 단위로 극장가 전체의 관객 수요와"
    " 흥행 규모를 거시적으로 비교할 수 있으며, 성수기(방학 시즌, 명절 등)와"
    " 비수기 시즌의 극장가 활성도를 한눈에 파악할 수 있습니다."
)


# ==========================================
# [여섯 번째 구역: 요일별·주차별 캘린더 히트맵]
# ==========================================
st.markdown("---")  # 구역을 나누는 수평선
st.subheader("📅 요일별·주차별 관객수 히트맵")

# 1. 원본 데이터에서 날짜별 일관객 합계 데이터 준비 (Top10 기준일자별 합산 데이터 활용 또는 전체 원본 기준)
# 여기서는 날짜별 정확한 yyyy-mm-dd와 요일을 매칭하기 위해 일별 합산 데이터를 사용합니다.
heatmap_df = daily_total_df.copy()

# 2. 연-월, 요일, 주차(월 내 주차) 컬럼 생성
heatmap_df["연월"] = heatmap_df["기준일자"].dt.strftime("%Y-%m")
heatmap_df["요일"] = heatmap_df["기준일자"].dt.day_name()

# 월 내 주차 계산 (해당 일의 날짜 - 1을 7로 나눈 몫 + 1)
heatmap_df["주차"] = (
    (heatmap_df["기준일자"].dt.day - 1) // 7 + 1
).astype(str) + "주차"
heatmap_df["월_주차"] = heatmap_df["연월"] + " (" + heatmap_df["주차"] + ")"

# 3. 요일 순서를 월요일부터 일요일 순으로 정렬하기 위한 카테고리 지정
days_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
days_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

heatmap_df["요일_영문"] = pd.Categorical(
    heatmap_df["요일"], categories=days_order, ordered=True
)

# 요일을 한글 이름으로 매핑 (선택사항이나 보기에 편하도록 변환)
day_mapping = {
    "Monday": "월요일",
    "Tuesday": "화요일",
    "Wednesday": "수요일",
    "Thursday": "목요일",
    "Friday": "금요일",
    "Saturday": "토요일",
    "Sunday": "일요일",
}
heatmap_df["요일명"] = heatmap_df["요일"].map(day_mapping)
heatmap_df["요일명"] = pd.Categorical(
    heatmap_df["요일명"], categories=days_kr, ordered=True
)

# 4. 피벗 테이블 형태로 변환 (Y축: 월_주차, X축: 요일명, 값: 해당일관객수, 날짜 정보 유지를 위해 집계 시 날짜는 첫번째 값 유지 등 처리)
# 히트맵 셀에 마우스를 올렸을 때 정확한 yyyy-mm-dd를 보여주기 위해 pivot_table 구성
pivot_df = heatmap_df.pivot_table(
    index="월_주차",
    columns="요일명",
    values="해당일관객수",
    aggfunc="sum",
    observed=False,
)
pivot_date = heatmap_df.pivot_table(
    index="월_주차",
    columns="요일명",
    values="기준일자",
    aggfunc=lambda x: x.dt.strftime("%Y-%m-%d").iloc[0] if len(x) > 0 else "",
    observed=False,
)

# 5. Plotly imshow를 이용한 히트맵 생성
# 색이 진할수록 관객이 많도록 color_continuous_scale 적용
fig_heatmap = px.imshow(
    pivot_df,
    labels=dict(x="요일", y="월 및 주차", color="관객수"),
    x=days_kr,
    y=pivot_df.index,
    color_continuous_scale="Blues",
    aspect="auto",
)

# 마우스 호버 시 yyyy-mm-dd 날짜가 보이도록 커스텀 텍스트(호버템플릿) 설정
# z값(관객수)과 날짜 정보를 함께 표시합니다.
fig_heatmap.update_traces(
    hovertemplate=(
        "날짜: %{customdata}<br>요일: %{x}<br>관객수: %{z:,}명<extra></extra>"
    ),
    customdata=pivot_date.values,
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# [여섯 번째 그래프 해석 문구 자리]
st.info(
    "💡 **이 그래프로 알 수 있는 것:** 월별 주차와 요일에 따른 관객 집중도를"
    " 히트맵 색상의 진한 정도를 통해 한눈에 파악할 수 있으며, 주말(토, 일요일)"
    "이나 특정 요일에 관객이 얼마나 몰리는지 시각적으로 확인할 수 있습니다."
)
