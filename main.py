   import streamlit as st
   st.title("나의 데이터 과학 포트폴리오")
   st.write("반갑습니다! 이제부터 여기에 제 작업을 기록합니다.")
import datetime
import pandas as pd
import pytz
import requests
import streamlit as st

# 1. 페이지 기본 설정 (제목, 레이아웃)
st.set_page_config(
    page_title="어제 한국 박스오피스", page_icon="🎬", layout="wide"
)


# 2. API 호출 함수 (결과를 1시간 동안 기억하는 캐시 적용)
# target_date가 같으면 1시간(3600초) 동안은 API를 재호출하지 않고 저장된 데이터를 가져옵니다.
@st.cache_data(ttl=3600)
def fetch_box_office(api_key, target_date):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # 네트워크 에러 발생 시 예외 발생
    return response.json()


# 3. 날짜 계산 (배포 서버 시계와 무관하게 한국 시간 KST 기준 계산)
kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.datetime.now(kst)
yesterday_kst = now_kst - datetime.timedelta(days=1)

# API 요청용 날짜 형식 (YYYYMMDD)
target_dt = yesterday_kst.strftime("%Y%m%d")
# 화면 표시용 날짜 형식 (YYYY년 MM월 DD일)
display_dt = yesterday_kst.strftime("%Y년 %m월 %d일")


# 4. 앱 헤더 화면 구성
st.title("🎬 어제 일별 박스오피스")
st.caption(f"📅 기준 날짜: {display_dt} (한국 표준시 기준 어제)")


# 5. 비밀 금고(Secrets)에서 인증키 불러오기
api_key = st.secrets.get("KOBIS_KEY")

# 인증키 미설정 예외 처리
if not api_key:
    st.error("⚠️ 인증키(KOBIS_KEY)가 설정되지 않았습니다.")
    st.info(
        "💡 **확인 방법:** Streamlit Cloud 관리 화면의 **Secrets** 메뉴에 아래와 같이 입력해 주세요.\n\n"
        '```toml\nKOBIS_KEY = "발급받은_API_키"\n```'
    )
else:
    try:
        # API 데이터 요청
        data = fetch_box_office(api_key, target_dt)

        # 오류 상자(faultInfo) 응답 여부 확인
        if "faultInfo" in data:
            fault = data["faultInfo"]
            st.error("⚠️ 영화진흥위원회 API 서비스 응답 오류가 발생했습니다.")
            st.write(f"**오류 메시지:** {fault.get('message', '알 수 없음')}")
            st.info(
                "💡 **점검해 볼 사항:**\n"
                "1. Secrets에 등록된 `KOBIS_KEY`가 정확한지 확인해 주세요.\n"
                "2. 영화진흥위원회 오픈API 마이페이지에서 키 상태를 점검해 주세요."
            )

        # 데이터 구조 정상 여부 확인
        elif (
            "boxOfficeResult" not in data
            or "dailyBoxOfficeList" not in data["boxOfficeResult"]
        ):
            st.warning("⚠️ 박스오피스 데이터를 가져올 수 없습니다.")
            st.info(
                "💡 **점검해 볼 사항:**\n"
                "1. KOBIS 서버 일시 오류일 수 있으므로 잠시 후 다시 시도해 주세요.\n"
                "2. 해당 날짜 데이터 집계가 시작되었는지 확인해 주세요."
            )

        else:
            movie_list = data["boxOfficeResult"]["dailyBoxOfficeList"]

            # 목록이 비어 있는 경우 처리
            if not movie_list:
                st.warning("⚠️ 해당 날짜의 박스오피스 집계 데이터가 비어 있습니다.")
                st.info(
                    "💡 **점검해 볼 사항:**\n"
                    "아직 어제 박스오피스 집계가 완료되지 않았을 수 있습니다."
                )

            else:
                # 정상 데이터 처리 시작
                df = pd.DataFrame(movie_list)

                # 문자열로 온 숫자 컬럼들을 정수형(int)으로 변환
                numeric_cols = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

                # 순위 기준으로 오름차순 정렬
                df = df.sort_values("rank").reset_index(drop=True)

                # --- [시각화 1] 1위 영화 지표 카드 3개 ---
                top_1 = df.iloc[0]
                st.markdown("### 🏆 1위 영화 개요")

                col1, col2, col3 = st.columns(3)
                col1.metric(label="영화명", value=top_1["movieNm"])
                col2.metric(
                    label="어제 관객수", value=f"{top_1['audiCnt']:,} 명"
                )
                col3.metric(
                    label="누적 관객수", value=f"{top_1['audiAcc']:,} 명"
                )

                st.divider()

                # --- [시각화 2] 관객수 상위 5편 막대그래프 ---
                st.markdown("### 📊 관객수 TOP 5")
                top_5_df = df.head(5)

                # 막대그래프용 데이터 가공 (영화명을 인덱스로 지정)
                chart_data = top_5_df.set_index("movieNm")[["audiCnt"]]
                chart_data.columns = ["일일 관객수"]
                st.bar_chart(chart_data)

                st.divider()

                # --- [시각화 3] 전체 순위표 출력 ---
                st.markdown("### 📋 전체 순위 목록")

                # 필요한 칼럼만 선택 및 한글 이름 변경
                table_df = df[
                    ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
                ].copy()
                table_df.columns = [
                    "순위",
                    "영화명",
                    "개봉일",
                    "관객수",
                    "누적관객",
                    "스크린수",
                ]

                # 표 형태 출력 (숫자 콤마 포맷팅 적용)
                st.dataframe(
                    table_df.style.format(
                        {
                            "관객수": "{:,}명",
                            "누적관객": "{:,}명",
                            "스크린수": "{:,}개",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

    # 기타 네트워크 또는 런타임 예외 처리
    except Exception as e:
        st.error("⚠️ 데이터를 불러오는 도중 예상치 못한 오류가 발생했습니다.")
        st.caption(f"상세 에러 내용: {e}")
        st.info(
            "💡 **점검해 볼 사항:**\n"
            "1. 배포 환경의 인터넷 연결 상태를 확인해 주세요.\n"
            "2. `KOBIS_KEY`가 올바르게 Secrets에 등록되어 있는지 다시 확인해 주세요."
        )
