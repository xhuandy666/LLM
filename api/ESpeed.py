import requests
import json
import markdown2

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


def get_response(content):

    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-128k?access_token=" + get_access_token()
    
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": content+"。注意,请不要加任何多余的文字描述。"
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    # print(json.loads(response.text)["result"])
    # html_table = markdown2.markdown(json.loads(response.text)["result"])
    # return json.loads({'html_table': html_table})

    return json.loads(response.text)["result"]
    

# if __name__ == '__main__':
#     main()