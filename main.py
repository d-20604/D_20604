import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("KOBIS 박스오피스 데이터를 바탕으로 영화의 다양한 분포와 관계를 시각적으로 살펴보는 도감입니다.")
st.markdown("---")

# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # 장르 열 처리: 세로막대 기호(|)가 있는 경우 첫 번째 장르만 추출
    if 'genre' in df.columns:
        df['genre'] = df['genre'].apply(lambda x: str(x).split('|')[0].strip() if pd.notnull(x) else '기타')
        
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# ==========================================
# 첫 번째 그래프: 장르별 영화 편수 도넛 그래프
# ==========================================
st.header("1. 장르별 영화 편수 분포")
st.markdown("수집된 영화 데이터에서 각 장르가 차지하는 비중과 편수를 도넛 형태로 나타냅니다.")

# 장르별 개수 집계
genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']

# Plotly 도넛 그래프 생성
fig_genre = px.pie(
    genre_counts,
    names='genre',
    values='count',
    hole=0.4, # 도넛 차트 설정
    color_discrete_sequence=px.colors.qualitative.Set3
)

# 호버 및 텍스트 레이블 설정
fig_genre.update_traces(
    textposition='inside', 
    textinfo='percent+label',
    hovertemplate='<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>'
)

fig_genre.update_layout(
    margin=dict(t=30, b=30, l=30, r=30),
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
)

st.plotly_chart(fig_genre, use_container_width=True)

# '이 그래프로 알 수 있는 것' 구역
st.markdown("---")
st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.info("전체 박스오피스 상위 영화 중 특정 장르(예: 드라마, 액션 등)가 주를 이루는지, 관객들의 선택을 받는 주력 장르가 무엇인지 편수와 비율을 통해 한눈에 파악할 수 있습니다.")

st.markdown("---")
