import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.title("영화 관객수 데이터 분석 리포트")

# 1. 파일 불러오기 (실제 파일명이 다를 경우 'your_data.csv'를 수정하세요)
file_name = 'your_data.csv'  # <--- 본인의 데이터 파일명으로 변경 (예: 'movie.csv')

try:
  if file_name.endswith('.csv'):
    df = pd.read_csv(file_name)
  elif file_name.endswith(('.xls', '.xlsx')):
    df = pd.read_excel(file_name)
  else:
    st.error(
        "지원하지 않는 파일 형식입니다. CSV 또는 엑셀 파일명을 입력해주세요."
    )
    st.stop()
except Exception as e:
  st.error(
      f"파일을 읽어오는 중 에러가 발생했습니다: {e}\n현재 폴더에 '{file_name}'"
      " 파일이 있는지 확인해 주세요."
  )
  # 파일이 없을 경우 도움을 위해 현재 폴더 파일 목록을 보여줍니다.
  st.write("📁 **현재 폴더의 파일 목록:**", os.listdir("."))
  st.stop()

# -------------------------------------------------------------
# 2. 네 번째 그래프의 데이터('기준일자별 전체 관객수 합계') 생성하기
# (실제 데이터의 컬럼명이 '기준일자', '관객수'가 아닐 경우 아래를 수정하세요)
# -------------------------------------------------------------
try:
  # 기준일자별 관객수 합계 구하기
  df_daily = df.groupby("기준일자")["관객수"].sum().reset_index()
except KeyError as e:
  st.error(
      f"컬럼을 찾을 수 없습니다: {e}. 데이터의 실제 컬럼명(예: '기준일자',"
      " '관객수' 등)을 확인해 주세요."
  )
  st.stop()

# -------------------------------------------------------------
# 3. 다섯 번째 그래프를 위한 월(연-월) 단위 데이터 가공
# -------------------------------------------------------------
df_daily["기준일자"] = pd.to_datetime(df_daily["기준일자"])
df_daily["연월"] = df_daily["기준일자"].dt.to_period("M")

# 월별로 관객수 다시 묶어서 합산
df_monthly = df_daily.groupby("연월")["관객수"].sum().reset_index()
df_monthly["연월"] = df_monthly["연월"].astype(str)  # X축 출력을 위해 문자열 변환

# -------------------------------------------------------------
# 4. 다섯 번째 그래프 시각화 (월별 막대그래프)
# -------------------------------------------------------------
st.subheader("📊 다섯 번째 그래프: 월별 전체 관객수 합계")

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(
    df_monthly["연월"], df_monthly["관객수"], color="skyblue", edgecolor="black"
)

ax.set_title("월별 전체 관객수 합계", fontsize=14, fontweight="bold")
ax.set_xlabel("월 (연-월)", fontsize=12)
ax.set_ylabel("전체 관객수", fontsize=12)
plt.xticks(rotation=45)
ax.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

# Streamlit 환경에서 그래프 출력
st.pyplot(fig)

# -------------------------------------------------------------
# 5. 그래프 아래에 '이 그래프로 알 수 있는 것' 추가
# -------------------------------------------------------------
st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.markdown(
    """
* **계절별 및 월별 관객 수요 집중 구간 파악:** 특정 월(성수기 시즌인 방학 기간이나 연말 등)에 관객수가 집중되는 패턴을 확인할 수 있습니다.
* **거시적 트렌드 및 증감 추세:** 월 단위의 관객 수 흐름을 비교하여 전년 대비 성장세나 하락세를 한눈에 파악할 수 있습니다.
* **외부 요인 분석의 기준점 제공:** 관객수가 급감하거나 급증한 특정 월의 배경(대작 영화 개봉 여부, 사회적 이슈 등)을 심층적으로 분석하는 출발점이 됩니다.
"""
)
