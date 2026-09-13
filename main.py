import streamlit as st
import pandas as pd
import plotly.express as px

# 웹앱 기본 설정 (페이지 제목 및 레이아웃 넓게)
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")

st.title("🎬 영화 박스오피스 데이터 분석")

# [1. 데이터 불러오기 및 2. 날짜 전처리]
# @st.cache_data를 사용하여 데이터 불러온 결과를 메모리에 저장(캐싱)
# 웹앱이 새로고침되거나 다시 실행되어도 매번 데이터를 다운로드하지 않음
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    
    # CSV 파일 읽어오기
    df = pd.read_csv(url)
    
    # 결측치(빈 값)가 포함된 행을 모두 삭제
    df = df.dropna()
    
    # '기준일자' 컬럼을 문자열에서 날짜(datetime) 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])
    
    # 전체 데이터를 '기준일자' 오름차순(과거->최근)으로 정렬
    df = df.sort_values("기준일자")
    
    return df

# 데이터 불러오기 함수 호출
df = load_data()

# [3. 영화 선택 기능]
# 영화별 누적관객수의 최대값을 기준으로 내림차순 정렬하여 영화 목록 생성
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index
    .tolist()
)

# 사이드바 메뉴 생성
st.sidebar.header("🔍 영화 선택")
selected_movie = st.sidebar.selectbox("분석할 영화를 선택하세요", movie_order)

# 사용자가 선택한 영화 데이터만 추출
filtered_df = df[df["영화명"] == selected_movie]

# [5. 기타 - 구역 나누기]
# 탭(Tab)을 생성하여 여러 그래프 및 분석 항목을 나눌 구역 생성
tab1, tab2 = st.tabs(["📈 일별 관객수 추이", "📊 추가 분석 (예정)"])

# 첫 번째 구역: 선택한 영화의 관객수 변화 그래프
with tab1:
    st.subheader(f"'{selected_movie}' 일별 관객수 변화")
    
    # [4. 선그래프 그리기]
    # Plotly를 활용하여 '기준일자'별 '해당일관객수' 선그래프 그리기
    fig = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"{selected_movie} - 일별 관객수 추이 그래프",
        labels={"기준일자": "날짜", "해당일관객수": "관객수 (명)"},
        markers=True  # 데이터 점 표시
    )
    
    # 화면에 Plotly 그래프 출력 (가로 폭에 맞춰 크기 조정)
    st.plotly_chart(fig, use_container_width=True)
    
    # 그래프 하단 설명 문구 자리
    st.caption("💡 이 그래프로 알 수 있는 것: 개봉 일자별 관객수의 흥행 추이와 관객수가 가장 많이 몰린 날을 한눈에 파악할 수 있습니다.")

# 두 번째 구역: 향후 추가될 그래프를 위한 공간
with tab2:
    st.subheader("📊 추가 시각화 구역")
    st.info("이 구역에는 추후 새로운 분석 그래프가 추가될 예정입니다.")
