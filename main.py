import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    # 1년간 박스오피스 10위권에 든 영화 216편의 요약표를 불러옵니다
    df = pd.read_csv(DATA_URL)
    # 장르가 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 씁니다
    df["장르"] = df["genre"].str.split("|").str[0]
    return df


df = load_data()

# ──────────────────────────────────────────
# 그래프 1. 장르별 영화 편수 도넛
# ──────────────────────────────────────────
st.header("1. 장르별 영화 편수 (도넛)")
genre_count = df["장르"].value_counts().reset_index()
genre_count.columns = ["장르", "편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.45,  # 가운데 구멍을 뚫어 도넛 모양으로
)
fig1.update_traces(hovertemplate="%{label}<br>%{value}편 (%{percent})<extra></extra>")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info("박스오피스 상위권에 가장 많이 진입한 주력 영화 장르가 무엇인지, 전체 장르 중 어떤 장르가 높은 편수 비중을 차지하는지 한눈에 확인할 수 있습니다.")

st.divider()

# ──────────────────────────────────────────
# 그래프 2. 장르별 영화 트리맵 (총 관객 기준)
# ──────────────────────────────────────────
st.header("2. 장르 및 영화별 총 관객 분포 (트리맵)")
st.markdown("큰 사각형은 장르를, 내부의 작은 칸들은 해당 장르의 개별 영화를 나타내며, **칸의 크기**는 **총 관객수**를 의미합니다.")

fig2 = px.treemap(
    df,
    path=["장르", "movieNm"],
    values="total_audi",
    color="total_audi",
    color_continuous_scale="Viridis",
)

fig2.update_traces(
    hovertemplate="<b>장르:</b> %{parent}<br><b>영화명:</b> %{label}<br><b>총 관객수:</b> %{value:,}명<extra></extra>"
)

fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=600)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info("특정 장르 안에서 어떤 영화가 압도적인 관객 동원력을 기록했는지, 그리고 장르 전체의 파급력과 개별 히트작의 규모를 동시에 비교할 수 있습니다.")

st.divider()

# ──────────────────────────────────────────
# 그래프 3. 총 관객 수 히스토그램
# ──────────────────────────────────────────
st.header("3. 총 관객 수 분포 (히스토그램)")
st.markdown("영화별 총 관객 수의 빈도 분포를 구간별로 살펴봅니다.")

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    labels={"total_audi": "총 관객수", "count": "영화 편수"},
    color_discrete_sequence=["#3366CC"]
)

fig3.update_traces(
    hovertemplate="관객수 구간: %{x:,}명<br>영화 편수: %{y}편<extra></extra>"
)
fig3.update_layout(xaxis_title="총 관객 수", yaxis_title="영화 편수 (편)")
st.plotly_chart(fig3, use_container_width=True)

# 데이터 계산 (가장 관객이 많은 영화)
max_movie_row = df.loc[df["total_audi"].idxmax()]
max_movie_name = max_movie_row["movieNm"]
max_movie_audi = max_movie_row["total_audi"]

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info(
    f"대부분의 영화들이 저조~중하위 관객 구간에 집중되어 있으며, "
    f"이 기간 박스오피스 10위권 진입 영화 중 **가장 관객이 많은 영화**는 "
    f"**'{max_movie_name}'**(약 {max_movie_audi:,}명)으로 나타났습니다."
)

st.divider()
