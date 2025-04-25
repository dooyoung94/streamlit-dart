import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import ta

# --- 사용자 입력 ---

st.title("사용자 입력 테스트")

stock_name = st.text_input("종목명")

my_value_input = st.text_input("기준 가격 (숫자만 입력)")
mean_days_input = st.text_input("평균 비교 시작 위치 (예: -2)")
total_value_input = st.text_input("총 비교 기준 금액 (원)")

# 입력값 유효성 확인
if my_value_input and mean_days_input and total_value_input:
    try:
        my_value = int(my_value_input)
        mean_days = int(mean_days_input)
        total_value = int(total_value_input)

        st.success(f"""
        ✅ 입력값 확인  
        - 기준 가격: {my_value:,}원  
        - 평균 비교일: {mean_days}일  
        - 총 비교 금액: {total_value:,}원
        """)
        
        # 여기에 분석 로직 연결
        # 예: 주가 불러오기, 계산, 출력 등

    except ValueError:
        st.error("❌ 숫자만 입력해주세요.")
else:
    st.info("입력값을 모두 작성해주세요.")

# --- 타이틀 동적 설정 ---
st.title(f"{stock_name} 주가 분석 및 비교 지표")

# --- 주가 코드 불러오기 ---
ticket = pd.read_csv('./ticket.csv')
try:
    ticket_code = ticket[ticket['Name'] == stock_name]['Code'].iloc[0]
    stock_val = fdr.DataReader(ticket_code)
    stock_val.dropna(inplace=True)

    # 기술 지표 추가
    stock_val['RSI'] = ta.momentum.RSIIndicator(close=stock_val['Close'], window=14).rsi()
    stoch = ta.momentum.StochasticOscillator(
        high=stock_val['High'],
        low=stock_val['Low'],
        close=stock_val['Close'],
        window=14,
        smooth_window=3
    )
    stock_val['Stoch_%K'] = stoch.stoch()
    stock_val['Stoch_%D'] = stoch.stoch_signal()

    # 비교 지표 계산
    mean_stock = int(my_value - stock_val['Close'][mean_days:].mean())
    tall = pd.DataFrame([{
        'mean': mean_stock,
        'put': int((1 - (my_value / (my_value - mean_stock))) * total_value),
        'call': int((1 - (my_value / (my_value + mean_stock))) * total_value)
    }])
    # 열별로 포맷 적용 (숫자 → 쉼표 구분 문자열)
    formatted_tall = tall.copy()
    for col in formatted_tall.columns:
        formatted_tall[col] = formatted_tall[col].map(
            lambda x: f"{x:,.2f}" if isinstance(x, float) else f"{x:,}"
        )

    # 출력
    st.subheader("최근 주가 및 기술 지표")
    st.dataframe(stock_val.tail(10))

    st.subheader("기준 가격 대비 평가 금액")
    st.dataframe(formatted_tall)

except Exception as e:
    st.error(f"데이터 처리 중 오류 발생: {e}")
