# Python에서 OpenAI API를 호출해서 GPT에게 질문을 보내고, GPT의 답변을 출력하는 코드

# OpenAI에서 제공하는 Python 라이브러리 중 OpenAI라는 기능 가져오기
from openai import OpenAI

# client = OpenAI(api_key="YOUR_API_KEY")
# response=client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role": "system", "content": "You are a heplful assistant."}, 
#     ]
# )
# print(response.choices[0].message.content)

# GPT를 호출하는 기능을 함수로 만들어둠
def ask_llm(api_key, model, question):
    client=OpenAI(api_key=api_key)
    response=client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "친절한 도우미"},
            {"role": "user", "content": question}
        ]
    )    

    # GPT 답변 + 사용량 정보 --> 이 두 가지를 반환
    return response.choices[0].message.content, response.usage

my_api_key="YOUR_API_KEY"
answer, usage=ask_llm(
    my_api_key, 
    "gpt-4o-mini", 
    "안녕하세요. 오늘 날씨가 어떤가요?")

print("Answer:", answer)