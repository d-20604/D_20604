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
# 그래프 1: 장르별 영화 편수 (도넛 그래프)
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
# 그래프 2: 장르 및 영화별 총 관객수 (트리맵)
# -------------------------------------------------------------------
st.subheader("2. 장르별 영화 관객수 트리맵")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체 영화"), "genre", "movieNm"],
    values="total_audi",
    color="genre",
    title="장르 및 영화별 총 관객수(total_audi) 분포",
)

fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,.0f}명<extra></extra>"
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("> **💡 이 그래프로 알 수 있는 것**")
st.write(
    "장르 전체의 총 관객 규모뿐만 아니라 각 장르 내에서 어떤 영화가 관객수를 독점하거나 크게 기여했는지 개별 영화별 비중을 직관적으로 비교할 수 있습니다."
)

st.divider()

# -------------------------------------------------------------------
# 그래프 3: 총 관객수 히스토그램
# -------------------------------------------------------------------
st.subheader("3. 총 관객수(total_audi) 분포 히스토그램")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="총 관객수 분포 히스토그램",
    labels={"total_audi": "총 관객수", "count": "영화 수"},
)

fig_hist.update_traces(
    hovertemplate="<b>관객수 구간</b>: %{x}<br><b>영화 수</b>: %{y}개<extra></extra>"
)

st.plotly_chart(fig_hist, use_container_width=True)

# 최다 관객 영화 정보 동적 자동 추출
top_movie = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie["movieNm"]
top_movie_audi = top_movie["total_audi"]

st.markdown("> **💡 이 그래프로 알 수 있는 것**")
st.write(
    f"대부분의 영화는 초반 저관객 구간(약 100만~200만 명 이하)에 집중 분포되어 있는 오른쪽으로 긴 꼬리 모양을 나타냅니다. "
    f"또한, 이 데이터셋에서 가장 관객 수가 많은 영화는 **'{top_movie_name}'**(총 {top_movie_audi:,.0f}명)입니다."
)
