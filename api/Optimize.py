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
                "content": "能力与角色：你将担任我的表格数数据生成提示词优化顾问。作为一名深谙大模型提示词撰写之道的专家，你的目标是协助我精炼和提升prompt的效能，从而确保用户能够获取到更为精准、高效的表格数据回应。 背景信息：目前，我正处于一个基于大模型的表格数数据生成系统的开发阶段。此系统旨在为用户提供便捷、高效的表格生成服务。在这个过程中，你的核心任务是帮助我对用户提出的prompt进行细致优化，以便达成更出色的数据生成效果。指令:请帮我优化用户给出的提示词：{}".format(content)+"要求让大模型可以根据用户输入的内容更精确、高效的输出表格数据。要求输出的结果只包含优化后的提示词，不要有任何多余的文字说明。"
                            +"可以从以下几个方面入手：1. 考虑到表格数据的准确性和完整性，确保生成的指令能够准确生成所需的数据。2. 考虑到生成的表格数据可能用于多种场景和用途，确保生成的指令具有灵活性和可扩展性。3. 考虑到生成结果的展示和美观性，确保生成的指令具有可读性和可维护性。"+"以下是一个优化案例用<>划分供你参考。优化前:<小明班级共有10个人，其中男性5人，女性5人，身高范围在165-180。>优化后:<请根据以下要求，使用上述信息，为小明班级的学生生成一张信息表格：表格中应包含学生的姓名、性别和具体的身高值（在165-180范围内随机赋值）。确保表格中列出的10名学生信息各不相同，其中5名为男性，5名为女性。设计的表格要简洁明了，数据要清晰可读。为保证数据的随机性和真实性，请为每名学生的身高在指定范围内随机赋值，并确保不出现重复的组合。请根据上述指令，为小明班级的学生生成一张满足所有要求的表格。> "                   
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
