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

# ──────────────────────────────────────────
# 그래프 4. 개봉일 스크린수와 총 관객 수 산점도
# ──────────────────────────────────────────
st.header("4. 개봉일 스크린수와 총 관객 수의 관계 (산점도)")
st.markdown("개봉일 스크린수(`first_scrn`)가 총 관객수(`total_audi`)에 미치는 영향을 장르별 색상으로 구분하여 살펴봅니다.")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객수"},
    custom_data=["movieNm", "first_scrn", "total_audi"]
)

fig4.update_traces(
    hovertemplate="<b>영화명:</b> %{customdata[0]}<br>개봉일 스크린수: %{customdata[1]:,}개<br>총 관객수: %{customdata[2]:,}명<extra></extra>"
)

fig4.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객수",
    height=600
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info("일반적으로 개봉일 스크린수가 많을수록 총 관객 수도 비례해서 증가하는 경향을 보이며, 장르별로 스크린 확보 규모와 흥행 효율성을 비교할 수 있습니다.")

st.divider()

# ──────────────────────────────────────────
# 그래프 5. 영화 10편 이상 장르의 총 관객 수 박스플롯
# ──────────────────────────────────────────
st.header("5. 주요 장르별 총 관객 수 분포 (박스플롯)")
st.markdown("영화 편수가 10편 이상인 주요 장르들을 대상으로 총 관객 수의 분포와 이상치(흥행 대작)를 살펴봅니다.")

genre_counts_s5 = df["장르"].value_counts()
valid_genres = genre_counts_s5[genre_counts_s5 >= 10].index
df_filtered = df[df["장르"].isin(valid_genres)]

fig5 = px.box(
    df_filtered,
    x="장르",
    y="total_audi",
    color="장르",
    hover_data=["movieNm"],
    labels={"장르": "장르", "total_audi": "총 관객수"},
    custom_data=["movieNm"]
)

fig5.update_traces(
    hovertemplate="<b>영화명:</b> %{customdata[0]}<br>장르: %{x}<br>총 관객수: %{y:,}명<extra></extra>"
)

fig5.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객수",
    showlegend=False,
    height=600
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info("장르별 전체 관객 수의 중앙값과 분포 편차를 비교할 수 있으며, 박스 바깥으로 튀어나온 이상치 점들을 통해 각 장르 내에서 유독 대성공을 거둔 블록버스터 영화가 무엇인지 확인할 수 있습니다.")

st.divider()

# ──────────────────────────────────────────
# 그래프 6. 개봉일 스크린수와 총 관객 수 버블 그래프
# ──────────────────────────────────────────
st.header("6. 스크린수·총 관객수·첫 주 관객수 관계 (버블 그래프)")
st.markdown("산점도에 **첫 주 관객수(`first_week_audi`)** 크기를 반영한 버블을 적용하여, 초기 화력과 최종 흥행의 관계를 입체적으로 살펴봅니다.")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="장르",
    hover_name="movieNm",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객수", "first_week_audi": "첫 주 관객수"},
    custom_data=["movieNm", "first_scrn", "total_audi", "first_week_audi"]
)

fig6.update_traces(
    hovertemplate="<b>영화명:</b> %{customdata[0]}<br>개봉일 스크린수: %{customdata[1]:,}개<br>총 관객수: %{customdata[2]:,}명<br>첫 주 관객수: %{customdata[3]:,}명<extra></extra>"
)

fig6.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객수",
    height=600
)

st.plotly_chart(fig6, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info("버블의 크기(첫 주 관객수)를 통해 개봉 초기 화력이 거세었던 영화가 최종 총 관객수와 스크린수 규모에 어떤 영향을 미치는지 다차원적으로 파악할 수 있습니다.")

st.divider()

# ──────────────────────────────────────────
# 그래프 7. 제작 국가-장르 계층 선버스트 그래프
# ──────────────────────────────────────────
st.header("7. 제작 국가 및 장르별 영화 편수 (선버스트)")
st.markdown("안쪽 원의 **제작 국가(`nation`)**에서 바깥쪽 원의 **장르(`장르`)**로 이어지는 계층 구조를 통해, 국가별 주력 장르와 영화 편수를 원형 비중으로 살펴봅니다.")

fig7 = px.sunburst(
    df,
    path=["nation", "장르"],
    color="nation",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig7.update_traces(
    hovertemplate="<b>분류:</b> %{label}<br><b>영화 편수:</b> %{value}편<extra></extra>"
)

fig7.update_layout(
    margin=dict(t=10, b=10, l=10, r=10),
    height=600
)

st.plotly_chart(fig7, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info("각 제작 국가(한국, 외국 등)에서 박스오피스 상위권에 진입한 영화들이 주로 어떤 장르에 집중되어 있는지 전체적인 구성 비율과 편수를 직관적으로 파악할 수 있습니다.")

st.divider()

# ──────────────────────────────────────────
# 그래프 8. 제작 국가별 영화 편수 비율 파이 그래프
# ──────────────────────────────────────────
st.header("8. 제작 국가별 영화 편수 비율 (파이)")
st.markdown("제작 국가(`nation`)별 전체 영화 편수의 점유율과 비율을 파이 차트로 살펴봅니다.")

nation_count = df["nation"].value_counts().reset_index()
nation_count.columns = ["nation", "편수"]

fig8 = px.pie(
    nation_count,
    names="nation",
    values="편수",
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig8.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>제작 국가:</b> %{label}<br><b>영화 편수:</b> %{value}편<br><b>비율:</b> %{percent}<extra></extra>"
)

fig8.update_layout(
    margin=dict(t=30, b=30, l=30, r=30),
    height=500
)

st.plotly_chart(fig8, use_container_width=True)

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info("박스오피스 10위권에 오른 전체 영화 중 국내 영화와 해외(외국) 영화 간의 제작 편수 비율과 점유 차이를 명확하게 확인할 수 있습니다.")

st.divider()
