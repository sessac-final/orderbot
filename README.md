# :information_desk_person: 음성인식 주문 챗봇

### 키오스크 사용의 불편함 해결 프로젝트

![image](https://github.com/sessac-final/orderbot/assets/145187337/1cb6a2b6-fed6-4058-8881-2d0dbfc8737e)

<br>

# 목차
1. 프로젝트 소개
2. 기술 스택
3. 주요 기능 소개
4. 시연 영상
5. 요약 및 소감

<br>

# 1. 프로젝트 소개
- 프로젝트 이름
    - 음성인식 주문 챗봇
- 프로젝트 소개
    - LLM을 이용한 오더봇에 관심이 있어 관련 서비스를 찾아보던 중 키오스크가 주문 방식 및 조작의 어려움으로 인해 불편하다는 점을 인지하고 점원에게 주문하듯이 주문 가능한 '사람 같은 챗봇' 즉 말로 주문을 받고 답변을 들을 수 있으며 필요 시 레시피 기반 추천 기능이 있는 챗봇을 만들어 해결하고자 함
- 프로젝트 목표
    - 고객 응대부터 계산까지의 자연스럽고 정확한 주문 수행
- 구현 기능
    - LLM 튜닝 : Google Palm2 모델의 프롬프트 튜닝, 파인 튜닝을 통해 고객 맞춤 주문 서비스 구현
    - 음성 인식 및 합성 : Google STT, TTS API 사용하여 음성 인식 및 합성 가능
    - 보조 기능 : Streamlit, Cloud SQL, Gemini Pro Vision 사용하여 웹 서비스 구현
- 기간
    - 2024.01.02 ~ 2024.02.16
- 팀원
    - 정지석, 임재용, 양한수
- 팀노션
    - [Notion](https://busy-dart-75b.notion.site/6b2c4f5d42bc4ed3835a9c42dcb614d2)

<br>

# 2. 기술 스택
- OS : windows 11 <br>
- Language : Python 3.9 <br>
- IDE : Visual Studio Code <br>
- Back-End : Streamlit <br>
- DB : Cloud SQL <br>
- Data : Own Data <br>

<br>

# 3. 주요 기능 소개
![image](https://github.com/sessac-final/orderbot/assets/145187337/438202f4-720a-49f5-b182-b67970d01e06)

![image](https://github.com/sessac-final/orderbot/assets/145187337/1e7b092d-0322-481d-ac19-d15a0c5c0af4)

![image](https://github.com/sessac-final/orderbot/assets/145187337/592306c6-9396-4487-a836-f9fbafb9ac5b)

![image](https://github.com/sessac-final/orderbot/assets/145187337/f0e18726-6e60-4390-ab45-b574dc4568ff)

![image](https://github.com/sessac-final/orderbot/assets/145187337/73f458c3-719b-401a-8738-4168dd2faae5)

<br>

# 4. 시연 영상
- 참조 : readme 파일이라 음성이 없습니다.

- ## 일반 주문
![일반주문](https://github.com/sessac-final/orderbot/assets/145187337/09534d2f-2d69-4463-a34d-302af9f9e80c)

- ## 취향 주문
![취향주문](https://github.com/sessac-final/orderbot/assets/145187337/e6093ec6-11e7-47d6-8daf-0c01390b07de)

<br>

# 5. 요약 및 소감
- 프롬프트 튜닝은 섬세한 작업이 필요하다.
- 컨텍스트를 잘 작성하면 파인 튜닝까지 가지 않고 유의미한 결과를 도출해 낼 수 있다.
- 음성인식 시 주변 소음 차단 기능이 필요하다.
- 서버와의 데이터 전송 속도 개선이 필요하다.
- 프로젝트는 기술 만으로는 이루어지지 않고 외적 역량(문제 해결 능력, 의사 소통 능력)도 중요하고 필요하다.
