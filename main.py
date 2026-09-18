import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="영화 데이터 그래프 - 분포와 관계", layout="wide")

st.title("영화 데이터 그래프 - 분포와 관계")


# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르 열 전처리: 세로막대(|)로 구분된 경우 첫 번째 장르만 추출
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .apply(lambda x: x.split("|")[0].strip())
    )
    return df


df = load_data()

# -------------------------------------------------------------------
# 그래프 1: 장르별 영화 편수 (분포)
# -------------------------------------------------------------------
st.subheader("1. 장르별 영화 편수 분포")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "편수"]

fig_donut = px.pie(
    genre_counts,
    values="편수",
    names="장르",
    hole=0.4,
    title="장르별 영화 편수 비율",
)

# 마우스 호버 시 편수와 비율 표기
fig_donut.update_traces(
    textinfo="percent+label",
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)

st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("> **💡 이 그래프로 알 수 있는 것**")
st.write(
    "박스오피스 상위권 영화들 중에서 어떤 장르가 가장 큰 비중을 차지하고 있는지 장르별 편수 분포와 상대적 비율을 한눈에 파악할 수 있습니다."
)

st.divider()

# -------------------------------------------------------------------
# 그래프 2: 개봉 첫 주 관객수와 총 관객수 (관계)
# -------------------------------------------------------------------
st.subheader("2. 개봉 첫 주 관객수와 총 관객수의 관계")

fig_scatter = px.scatter(
    df,
    x="first_week_audi",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    labels={
        "first_week_audi": "개봉 첫 주 관객수",
        "total_audi": "총 관객수",
        "genre": "장르",
    },
    title="개봉 첫 주 관객수 vs 총 관객수 상관관계",
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("> **💡 이 그래프로 알 수 있는 것**")
st.write(
    "개봉 첫 주 관객수가 많은 영화일수록 최종 총 관객수도 높게 나타나는 강한 양의 상관관계가 있음을 알 수 있습니다."
)
