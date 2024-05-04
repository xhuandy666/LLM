import requests
import json

message = []

def get_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
        
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=T23ZRRjp17sYY2TfnbLItqS7&client_secret=0sNpDFW4Y2EmCHYXfIiUJaTKhl7htSqJ"
    
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

def get_reply(content):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-8k-0329?access_token=" + get_access_token()
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content":''' I want you to act as an AI prompt engineer. You are expert at writing Prompts to get the best results.

            To create efficient prompts that yield high-quality responses, consider the following principles and strategies: \
            1. Clear and Specific: Be as clear and specific as possible about what you want from the AI. If you want a certain type of response, outline that in your prompt. If there are specific constraints or requirements, make sure to include those as well.
            2. Open-ended vs. Closed-ended: Depending on what you're seeking, you might choose to ask an open-ended question (which allows for a wide range of responses) or a closed-ended question (which narrows down the possible responses). Both have their uses, so choose according to your needs.
            3. Contextual Clarity: Make sure to provide enough context so that the AI can generate a meaningful and relevant response. If the prompt is based on prior information, ensure that this is included.
            4. Creativity and Imagination: If you want creative output, encourage the AI to think outside the box or to brainstorm. You can even suggest the AI to imagine certain scenarios if it fits your needs.

            There is a well-written prompt delimited by <> for your reference: <Your task is to be my brainstorming partner and provide creative ideas and suggestions for a given topic or problem. Your response should include original, unique, and relevant ideas that could help solve the problem or further explore the topic in an interesting way. Please note that your response should also take into account any specific requirements or constraints of the task.>

            Your task is to write an effective  Prompt based on given keywords or to modify the given prompts. Answer in the Chinese please.
            
            Please help me to write an effective Prompt based on the following keywords or prompt:'''+content
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
   
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    return json.loads(response.text)["result"]
    

if __name__ == '__main__':
    get_reply()
    # return json.loads(response.text)["result"]


# def get_response(content):
    

#     url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-8k-0329?access_token=" + get_access_token()
    
#     message.append({
#         "role": "user",
#         "content": content
#     })

#     payload = json.dumps({
#         "messages": message
#     })

#     headers = {
#         'Content-Type': 'application/json'
#     }

#     response = requests.request("POST", url, headers=headers, data=payload)

#     message.append({
#         "role": "assistant",
#         "content": json.loads(response.text)["result"]
#     })

#     # print(message)

#     return message

# def clear_message():
#     message.clear()
