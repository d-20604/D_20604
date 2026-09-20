import pandas as pd
import plotly.express as px
import streamlit as st

# 예시: 데이터 불러오기 (실제 경로에 맞게 수정)
# df = pd.read_csv('your_data.csv')

# --- 네 번째 그래프: 개봉일 스크린수(first_scrn) vs 총 관객수(total_audi) 산점도 ---
st.subheader("영화 개봉일 스크린수와 총 관객수 관계")

fig = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",  # 장르별 색상 구분
    hover_name="movie_name",  # 마우스 오버 시 영화명 표시
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "genre": "장르",
    },
    title="개봉일 스크린수 vs 총 관객수 산점도",
)

fig.update_traces(marker=dict(size=10, opacity=0.8))
fig.update_layout(
    xaxis_title="개봉일 스크린수", yaxis_title="총 관객수", legend_title="장르"
)

# Streamlit에 그래프 출력
st.plotly_chart(fig, use_container_width=True)
