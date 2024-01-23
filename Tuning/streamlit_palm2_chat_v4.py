# 필요한 패키지 불러오기
import streamlit as st
import vertexai
from vertexai.preview.language_models import ChatModel, InputOutputTextPair, ChatMessage
import google.auth
import os
from dotenv import load_dotenv
from google.cloud import texttospeech
from langchain.chains import LLMMathChain
from langchain_google_vertexai import VertexAI
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
import re

from pydub import AudioSegment
import sounddevice as sd
import numpy as np
import soundfile as sf
import queue
import threading
from scipy.io.wavfile import write
import time

# 환경변수 설정
load_dotenv() 

# Google Cloud Platform 초기 설정
PROJECT_ID = os.environ['PROJECT_ID']
LOCATION = os.environ['LOCATION']
vertexai.init(project=PROJECT_ID, location=LOCATION)
credentials, project_id = google.auth.default()


# 마이크로 mp3 파일 생성(input)
q = queue.Queue()
recorder = False
recording = False

def complicated_record():
    file_path = "C:/Users/SBA/Desktop/Proj/input.wav"
    with sf.SoundFile(file_path, mode='w', samplerate=16000, subtype='PCM_16', channels=1) as file:
        with sd.InputStream(samplerate=16000, dtype='int16', channels=1, callback=complicated_save):
            while recording:
                file.write(q.get())

def complicated_save(indata, frames, time, status):
    q.put(indata.copy())

def start():
    global recorder
    global recording
    recording = True
    recorder = threading.Thread(target=complicated_record)
    print('start recording')
    recorder.start()

def stop():
    global recorder
    global recording
    recording = False
    recorder.join()
    print('stop recording')


# 구글 stt 함수 정의 -> 음성파일을 텍스트로 변환
def transcribe_file_v2(
    project_id,
    audio_file,
) -> cloud_speech.RecognizeResponse:
    # Instantiates a client
    client = SpeechClient()

    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        content = f.read()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["ko-KR"],
        model="long",
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{project_id}/locations/global/recognizers/_",
        config=config,
        content=content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)
    input = ""

    for result in response.results:
         input += result.alternatives[0].transcript

    return input


# 구글 tts 함수 정의 -> 텍스트를 mp3 파일로 생성
client = texttospeech.TextToSpeechClient(credentials=credentials)

def google_tts(response):
    synthesis_input = texttospeech.SynthesisInput(text=response)
    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Neural2-C",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
    )
    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        #audio_encoding=texttospeech.AudioEncoding.MP3
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response_voice = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open("output.mp3","wb") as out:
        # Write the response to the output file.
        out.write(response_voice.audio_content)
        print('Audio content written to file "output"')

# def google_tts(response):
#     synthesis_input = texttospeech.SynthesisInput(text=response)
#     voice = texttospeech.VoiceSelectionParams(
#         language_code="ko-KR",
#         name="ko-KR-Neural2-C",
#         ssml_gender=texttospeech.SsmlVoiceGender.MALE,
#     )
#     audio_config = texttospeech.AudioConfig(
#         audio_encoding=texttospeech.AudioEncoding.MP3
#     )
#     response_voice = client.synthesize_speech(
#         input=synthesis_input, voice=voice, audio_config=audio_config
#     )
    
#     # 파일명을 현재 시간으로 설정하여 중복을 방지
#     current_time = time.strftime("%Y%m%d-%H%M%S")
#     file_path = f"C:/Users/SBA/Desktop/Proj/output_{current_time}.mp3"

#     with open(file_path, "wb") as out:
#         out.write(response_voice.audio_content)
#         print(f'Audio content written to file "{file_path}"')


# 스피커 출력(mp3 출력) 함수 정의
def play_mp3_file(file_path):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    abs_file_path = os.path.abspath(os.path.join(script_dir, file_path))

    sound = AudioSegment.from_mp3(abs_file_path)
    audio_data = sound.raw_data
    frame_rate = sound.frame_rate

    # Convert audio_data to int16
    audio_data_int16 = np.frombuffer(audio_data, dtype=np.int16)

    # Stop and close the stream before starting a new one
    sd.stop()

    # Play audio
    sd.play(audio_data_int16, samplerate=frame_rate)
    # sd.play(audio_data_int16, samplerate=frame_rate, dtype='int16')
    sd.wait()




# Streamlit 프레임워크로 챗봇을 웹 서비스로 구현하기
st.set_page_config(page_title="Palm2 Chatbot")
st.header("Palm2 LLM Application :books:")


# 대화 기록(history) 기능 구현하기
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

messages = []

# 스트림릿 히스토리 저장소(st.session_state['chat_history'])에서 대화내용을 ctext에 저장
if st.session_state['chat_history']:
    for i in range(len(st.session_state['chat_history'])//2):
        user_message = ChatMessage(author="user", content=st.session_state['chat_history'][2*i][1])
        messages.append(user_message)
        bot_message = ChatMessage(author="llm", content=st.session_state['chat_history'][2*i+1][1])
        messages.append(bot_message)
      

start()
time.sleep(8)  # 사용자 음성을 8초간 녹음
stop()

# # 스트림릿 히스토리 저장소(st.session_state['chat_history'])에서 대화내용을 ctext에 저장
# if st.session_state['chat_history']:
    
#     for i in range(len(st.session_state['chat_history'])):
#         if i%2==0:
#           messages[i] = dict(author='USER', content=st.session_state['chat_history'][i][1])
#         else :  
#           messages[i] = dict(author='AI', content=st.session_state['chat_history'][i][1])

#         # a=st.session_state['chat_history'][2*i][1]
#         # messages.append({"author": "USER", "content": a})
#         # b=st.session_state['chat_history'][2*i+1][1]
#         # messages.append({"author": "AI", "content": b})
                  

input_voice=transcribe_file_v2(PROJECT_ID,"input.wav")

# 입력 프롬프트 기능 구현하기
# input=st.text_input("입력: ",key="input")
input_text=st.chat_input("Chat!")
# submit=st.button("Chat!")
               
print(messages)

# Palm2 모델 불러와서 프롬프트에 응답하는 챗봇 구현하기
model = ChatModel.from_pretrained("chat-bison-32k@002")

parameters = {
    "max_output_tokens": 1024,
    "temperature": 0,
    "top_p": 1
}

context = """
<지시사항>
당신은 스타포트 커피숍의 직원입니다.
스타포트 커피숍에서 판매하는 상품은 <메뉴>에 리스트 되어 있습니다.
당신은 스타포트 커피숍 주문과 관련된 질문에만 응답합니다.
당신은 스타포트 커피숍 주문과 무관한 질문이나 요청을 받으면 "죄송하지만 저는 스타포트 커피숍 주문과 관련된 질문에만 응답할 수 있습니다."라고 출력하고 주문을 이어서 받는다.
손님이 <메뉴>에 없는 상품을 요청하면 "죄송하지만 손님이 요청하신 메뉴는 스타포트 커피숍에 없습니다. 다른 메뉴를 주문해주세요."라고 출력하고 주문을 거절한다.
샷 추가, 토핑 추가, 사이즈 변경 등 퍼스널 옵션을 요청 받으면 "죄송하지만 저희 카페는 커피의 온도를 제외한 추가 옵션은 지원하지 않습니다."라고 출력하고 주문을 이어서 받는다.
당신은 손님에게 친절하게 답변합니다.

step 1. 손님이 방문하면 "어서오세요 손님, 스타포트 커피숍에 오신 것을 환영합니다. 원하시는 메뉴를 말씀해주세요."라고 인사한다.
step 2. 주문 받은 메뉴를 반드시 <메뉴> 리스트에 있는 상품으로 바꾸어 물어본다. 손님에게 질문할 때는 한번에 한가지의 질문만 할 수 있다. 손님이 상품 수량을 말하지 않으면 1개로 간주한다.
step 3. 추가로 주문할 상품이 있는지 물어본다. 추가로 주문하는 상품이 있으면 step 2로 돌아가서 주문을 이어서 받는다.
step 4. 모든 주문이 끝나면 주문 받은 상품과 총 가격이 얼마인지 알려주고 확인을 받는다. 주문 받은 상품은 반드시 <메뉴> 리스트에 있는 상품의 형식으로 바꾸어서 알려준다.
step 5. 확인을 받으면 "포장과 매장 중 식사 장소를 선택해 주세요."라고 출력하고 확인을 받는다. 애매하게 장소를 말하면 다시 물어본다.
step 6. 손님의 선택을 확인하면 결제방식을 요청한다. 결제방식에는 '카드', '기프티콘', '간편결제'만 있으며 다른 결제방식은 지원하지 않는다.
step 7. 손님이 결제방식을 선택하면 영수증 출력여부를 물어본다.
step 8. 모든 대화가 끝나면 '이용해 주셔서 감사합니다. 다음에 또 오세요.'라고 출력하고 {message_history}를 초기화한다.
</지시사항>

<메뉴>
-커피	
1. 아메리카노(HOT) 2000원
2. 아메리카노(ICE) 2000원
3. 카페라떼(HOT) 3000원
4. 카페라떼(ICE) 3000원
5. 카라멜 마끼아또(HOT) 3500원
6. 카라멜 마끼아또(ICE) 3500원

-음료
1. 레몬에이드(ICE) 2500원
2. 녹차(HOT) 2000원
3. 수박주스(ICE) 3500원

-디저트
1. 베이글(Plain) 3000원
2. 베이글(Blueberry) 3500원
3. 케이크(Strawberry) 4000원
4. 케이크(Chocolate) 4000원
5. 크로플 3000원
</메뉴>
"""

ctext = [
        InputOutputTextPair(
            input_text="""라떼랑 케이크 주세요""",
            output_text="""라떼는 카페라떼(HOT)과 카페라떼(ICE) 중 어떤 것을 주문하시겠어요?"""
        ),
        InputOutputTextPair(
            input_text="""아이스""",
            output_text="""케이크는 케이크(Strawberry)와 케이크(Chocolate) 중 어떤 것을 주문하시겠어요?"""
        ),
        InputOutputTextPair(
            input_text="""블루베리""",
            output_text="""죄송하지만 케이크(Blueberry)는 판매하지 않습니다. 케이크(Strawberry)와 케이크(Chocolate) 중 어떤 것을 주문하시겠어요?"""
        ),
        InputOutputTextPair(
            input_text="""딸기""",
            output_text="""현재까지 주문하신 메뉴는 카페라떼(ICE) 1잔, 케이크(Strawberry) 1개 입니다. 추가로 주문하실 메뉴가 있으신가요?"""
        ),
        InputOutputTextPair(
            input_text="""베이글 주세요""",
            output_text="""베이글은 베이글(Plain)과 베이글(Blueberry) 중 어떤 것을 주문하시겠어요?"""
        ),
        InputOutputTextPair(
            input_text="""블루베리""",
            output_text="""현재까지 주문하신 메뉴는 카페라떼(ICE) 1잔, 케이크(Strawberry) 1개, 베이글(Blueberry) 1개 입니다. 추가로 주문하실 메뉴가 있으신가요?"""
        ),
        InputOutputTextPair(
            input_text="""아니오""",
            output_text="""주문하신 메뉴는 카페라떼(ICE) 1잔, 케이크(Strawberry) 1개 입니다. 총 가격은 7000원 입니다. 맞으신가요?"""
        ),
        InputOutputTextPair(
            input_text="""네""",
            output_text="""포장과 매장 중 식사 장소를 선택해 주세요."""
        ),
        InputOutputTextPair(    
            input_text="""포장""",
            output_text="""결제방식을 선택해주세요. 카드, 기프티콘, 간편결제 중 선택 가능합니다."""
        ),
        InputOutputTextPair(
            input_text="""카드""",
            output_text="""카드로 결제하겠습니다. 영수중을 출력하시겠습니까?"""
        ),
        InputOutputTextPair(
            input_text="""아니요""",
            output_text="""이용해 주셔서 감사합니다. 다음에 또 오세요."""
        ),
        InputOutputTextPair(
            input_text="""녹차 주세요""",
            output_text="""녹차는 녹차(HOT)만 판매하고 있습니다. 녹차(HOT) 1잔으로 주문하시겠어요?"""
        ),
        InputOutputTextPair(
            input_text="""아이스 카페라떼 주세요""",
            output_text="""카페라떼(ICE) 1잔으로 주문하시겠어요?"""
        ),
        InputOutputTextPair(
            input_text="""라떼 차가운걸로 주세요""",
            output_text="""카페라떼(ICE) 1잔으로 주문하시겠어요?"""
        ),
    ]


chat = model.start_chat(context=context, examples=ctext, message_history=messages, **parameters)


def get_palm2_response(question):
    response_text = chat.send_message(question, **parameters)
    return response_text.text



llm = VertexAI()
llm_math = LLMMathChain.from_llm(llm, verbose=True)

global response
response = ""

# 챗봇 답변 내용 출력하고 대화 기록에 사용자가 입력한 프롬프트와 챗봇 답변 내용 저장하기
if input_voice:
    input = input_voice
    response = get_palm2_response(input)

elif input_text:
    input = input_text
    response = get_palm2_response(input)

if response:   
# 가격 정확히 출력하는 코드 추가
# sentence를 계속 불러와야 하므로 하드코딩보단 for문 이용
    
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
                price = llm_math.invoke( menu + "다음 괄호 안에 해당하는 문장만 주문한 내역이다. [" + sentences[i] + "]. 메뉴에 있는 가격을 참조하여 주문한 금액이 총 얼마인지 계산하라")
                price_value = list(price.values())[1]
                price_value_numbers = re.sub(r'[^0-9]', '', price_value)
                
            if "총 가격" in sentences[i]:
                sentences[i] = " 총 가격은 "+ price_value_numbers +"원입니다"
            res_str = res_str + sentences[i] + "."
            
        response = res_str
    
    google_tts(response)

    st.session_state['chat_history'].append((":smile:User", input))
    # st.subheader("답변: ")
    # st.markdown(response)
    st.session_state['chat_history'].append((":computer:Bot", response))
    
    # 스트림릿 대화 기록 출력하기
    # st.subheader("채팅 내역: ")
    for role, text in st.session_state['chat_history']:
        st.markdown(f"**{role}:**")
        st.markdown(text)

    if os.path.isfile("C:/Users/SBA/Desktop/Proj/output.mp3"):
        play_mp3_file("output.mp3")

    st.experimental_rerun()
    

    




# https://cloud.google.com/vertex-ai/docs/generative-ai/chat/chat-prompts
    
# https://wongcyrus.medium.com/google-cloud-voice-activated-chatbot-for-student-workshop-a7a304b52797

# File "C:\Users\USER\anaconda3\envs\FlaskTest\lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 534, in _run_script
#     exec(code, module.__dict__)
#   File "C:\Users\USER\Desktop\ChatBot\test.py", line 132, in <module>
#     response = get_palm2_response(input)
#   File "C:\Users\USER\Desktop\ChatBot\test.py", line 125, in get_palm2_response
#     response_text = chat.send_message(question, **parameters)
#   File "C:\Users\USER\AppData\Roaming\Python\Python39\site-packages\vertexai\language_models\_language_models.py", line 2315, in send_message
#     prediction_request = self._prepare_request(
#   File "C:\Users\USER\AppData\Roaming\Python\Python39\site-packages\vertexai\language_models\_language_models.py", line 2200, in _prepare_request
#     "author": past_message.author,

# 구글 검색 start_chat() message_history