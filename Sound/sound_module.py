import os
from dotenv import load_dotenv
from google.cloud import texttospeech
import vertexai
import google.auth
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
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

def complicated_record(file_path):
    # file_path = "C:/Users/SBA/Desktop/Proj/input.wav"
    with sf.SoundFile(file_path, mode='w', samplerate=16000, subtype='PCM_16', channels=1) as file:
        with sd.InputStream(samplerate=16000, dtype='int16', channels=1, callback=complicated_save):
            while recording:
                file.write(q.get())

def complicated_save(indata, frames, time, status):
    q.put(indata.copy())

# def start():
#     global recorder
#     global recording
#     recording = True
#     recorder = threading.Thread(target=complicated_record)
#     print('start recording')
#     recorder.start()
def start(file_path):
    global recorder
    global recording
    recording = True
    recorder = threading.Thread(target=complicated_record, args=(file_path,))
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


# start()
# time.sleep(8)  # 사용자 음성을 8초간 녹음
# stop()