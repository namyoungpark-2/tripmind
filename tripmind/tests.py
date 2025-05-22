from tripmind.agents.itinerary_agent_graph import run_travel_agent

# Create your tests here.

def test_travel_agent():
    """TripMind 테스트"""
    print("===== TripMind 테스트 =====")
    
    # 초기 상태
    state = None
    session_id = "test_session"
    
    # 대화 시뮬레이션
    conversations = [
        "안녕하세요, 여행 계획을 도와주세요",
        "오사카에 대해 알려주세요",
        "오사카로 3박 4일 여행을 가려고 합니다. 4명이 갈 예정이에요",
        "일정을 만들어주세요"
    ]
    
    # 대화 진행
    for user_input in conversations:
        print(f"\n사용자: {user_input}")
        
        # 에이전트 실행
        state, response = run_travel_agent(user_input, session_id, state)
        
        # 응답 출력 (긴 응답은 축약)
        if len(response) > 200:
            print(f"에이전트: {response[:200]}...\n")
        else:
            print(f"에이전트: {response}\n")
        
        # 상태 정보 출력
        print(f"목적지: {state.get('destination')}")
        print(f"기간: {state.get('duration')}")
        print("=" * 50)