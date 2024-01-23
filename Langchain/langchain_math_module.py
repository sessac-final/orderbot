from langchain.chains import LLMMathChain
from langchain_google_vertexai import VertexAI
import re

# langchain llm math 함수 정의
def langchainmath(response):
    llm = VertexAI()
    llm_math = LLMMathChain.from_llm(llm, verbose=True)

    if "총 가격" in response:
        
        menu = '''<메뉴> 아메리카노(HOT) 2000원
    아메리카노(ICE) 2000원
    카페라떼(HOT) 3000원
    카페라떼(ICE) 3000원
    카라멜 마끼아또(HOT) 3500원
    카라멜 마끼아또(ICE) 3500원

    레몬에이드 2500원
    녹차 2000원
    수박주스 3500원

    베이글(Plain) 3000원
    베이글(Blueberry) 3500원
    케이크(strawberry) 4000원
    케이크(chocolate) 4000원
    크로플 3000원</메뉴>.
    '''
        
        sentences = response.split('.')
        print(response)
        res_str = ""
        price_value_numbers = ""
        for i in range(len(sentences)):
            if ("주문하" in sentences[i]) or ("추가" in sentences[i]):
                price = llm_math.invoke( menu + "다음 괄호 안에 해당하는 문장만 주문한 내역이다. [" + sentences[i] + "].\
                                         메뉴에 있는 가격을 참조하여 주문한 금액이 총 얼마인지 계산하라")
                price_value = list(price.values())[1]
                price_value_numbers = re.sub(r'[^0-9]', '', price_value)
                
            if "총 가격" in sentences[i]:
                sentences[i] = " 총 가격은 "+ price_value_numbers +"원입니다"
            res_str = res_str + sentences[i] + "."
            
        response = res_str

    return response


