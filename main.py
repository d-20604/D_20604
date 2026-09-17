import matplotlib.pyplot as plt
import pandas as pd

# 가정: 네 번째 그래프에서 사용한 '기준일자별 전체 관객수 합계' 데이터프레임이 df_daily 형태라고 가정
# df_daily는 '기준일자'(datetime 또는 str)와 '전체관객수'(합계) 컬럼을 가진다고 가정
# 예: df_daily = df.groupby('기준일자')['관객수'].sum().reset_index()

# 1. 기준일자를 datetime 형식으로 변환 (이미 되어있다면 생략 가능)
df_daily['기준일자'] = pd.to_datetime(df_daily['기준일자'])

# 2. '연-월'(YYYY-MM) 컬럼 생성
df_daily['연월'] = df_daily['기준일자'].dt.to_period('M')

# 3. 월(연-월) 단위로 다시 묶어서 관객수 합산
df_monthly = (
    df_daily.groupby('연월')['전체관객수'].sum().reset_index()
)  # '전체관객수'는 실제 컬럼명에 맞게 수정
df_monthly['연월'] = df_monthly['연월'].astype(str)  # 시각화를 위해 문자열로 변환

# 4. 월별 막대그래프 시각화
plt.figure(figsize=(12, 6))
plt.bar(
    df_monthly['연월'],
    df_monthly['전체관객수'],
    color='skyblue',
    edgecolor='black',
)
plt.title('월별 전체 관객수 합계', fontsize=14, fontweight='bold')
plt.xlabel('월 (연-월)', fontsize=12)
plt.ylabel('전체 관객수', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# 그래프 출력
plt.show()
