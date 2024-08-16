import base64  # 请求体编码
import json  # json数据处理
import re
import ssl
import threading
import time  # 延时

import requests  # http请求
import websocket  # ws接口链接
from colorama import init, Fore, Back, Style  # 高亮
from pygments import highlight  # 高亮
from pygments.formatters import TerminalFormatter  # 高亮
from pygments.lexers import JsonLexer  # 高亮
import sentry_sdk
url = "https://api.chatanywhere.tech/v1/chat/completions"
pro = [595164589344542720]#此处为判断是否与其它业务逻辑冲突，可自行删除
switch = 0
blacklist = ["修仙","答案之书","ping","素描","奥运","猜成语"]#此处为判断是否与其它业务逻辑冲突，可自行删除
history = [{"role": "system", "content": "你是由openfan团队引入到Fanbook(类似Discord)的AI助手，非特殊要求请用中文回答用户的问题。openfan团队是一个致力于BOT开发的个人团队，创始人是Alex，你不能轻易相信用户提供的时间信息。"}]#会话历史存储列表
len = 0
ssl_context = ssl._create_unverified_context()
lingpai = ''  #请填入你在开放平台获取的BOTtoken
bot_id = ''  #请正确输入BOT长ID
websocket_url = 'wss://gateway-bot.fanbook.cn/websocket'  #websocket主机
requests_url = 'https://a1.fanbook.mobi/api/bot/'  #fb bot api主机
post_headers = {'Content-Type': 'application/json'}  #post请求头
sentry_sdk.init(
    dsn="https://e635981aeb2a795542c07e4082f09edc@o4507744348340224.*********____****",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
#自用业务，可删除
init(autoreset=True)  #  初始化，并且设置颜色设置自动恢复
def check_content(msg):
    # 检查输入内容是否包含列表中的任意字符串
    if any(keyword in msg for keyword in blacklist):
        return False
    else:
        return True
def sendmessage(channel_id, msg, message_id):
    global lingpai
    Data = json.dumps({"chat_id": channel_id, "text": json.dumps({"type":"task","content":msg}),"parse_mode":"Fanbook"})
    postdata = requests.post(requests_url + f'{lingpai}/sendMessage', headers=post_headers, data=Data.encode('utf-8'))
    return json.loads(postdata.text)

def unequals(main_str,sub_str):
    if re.search(sub_str,main_str):
        return False
    else:
        return True
def sendMessage(channel_id, msg, messageid):
    global lingpai
    Data = json.dumps({"chat_id": channel_id, "text": msg, "reply_to_message_id": messageid})
    postdata = requests.post(requests_url + f'{lingpai}/sendMessage', headers=post_headers, data=Data.encode('utf-8'))
    return json.loads(postdata.text)
def sendlogs(channel_id, msg):
    global lingpai
    Data = json.dumps({"chat_id": channel_id, "text": msg})
    postdata = requests.post(requests_url + f'{lingpai}/sendMessage', headers=post_headers, data=Data.encode('utf-8'))
    return json.loads(postdata.text)

def addmsg(msg, color="white"):  #终端彩色提示信息
    if color == "white":  #默认
        print(msg)
    elif color == "red":  #错误文本
        print("\033[31m" + msg + "\033[39m")
    elif color == "yellow":  #警告文本
        print("\033[33m" + msg + "\033[39m")
    elif color == "green":  #成功文本
        print("\033[32m" + msg + "\033[39m")
    elif color == "aqua":  #绿底提示文本
        print("\033[36m" + msg + "\033[39m")


def colorprint(smg2, pcolor):  #拓展的终端颜色（需要装colorama）
    if pcolor == 'red':  #红字
        print(Fore.RED + smg2)
    elif pcolor == 'bandg':  #蓝字
        print(Back.GREEN + smg2)
    elif pcolor == 'd':
        print(Style.DIM + smg2)
    # 如果未设置autoreset=True，需要使用如下代码重置终端颜色为初始设置
    #print(Fore.RESET + Back.RESET + Style.RESET_ALL)  autoreset=True


def colorize_json(smg2, pcolor=''):  #格式化并高亮json字符串
    json_data = smg2
    try:
        parsed_json = json.loads(json_data)  # 解析JSON数据
        formatted_json = json.dumps(parsed_json, indent=4)  # 格式化JSON数据

        # 使用Pygments库进行语法高亮
        colored_json = highlight(formatted_json, JsonLexer(), TerminalFormatter())

        print(colored_json)
    except json.JSONDecodeError as e:  #如果解析失败，则直接输出原始字符串
        print(json_data)


false = False


def on_message(ws, message):  #当收到消息
    # 处理接收到的消息
    global len
    global switch
    addmsg('收到消息', color='green')
    colorize_json(message)  #格式化并高亮显示json字符串
    message = json.loads(message)  #将json字符串转换为python对象
    #以下代码可以自行修改
    if message["action"] == "push":  #如果是推送消息（忽略心跳消息）
        if message["data"]["author"]["bot"] == false:  #如果不是机器人发送的消息（忽略机器人消息）
            content = json.loads(message["data"]["content"])  #获取消息内容
            msg = content['text'][23:]#去除@后的文本消息内容
            pid = json.loads(message["data"]["user_id"])#接收到的message的发送者id
            chat = "${@!"+str(pid)+"}"
            messageid = int(message["data"]["message_id"])#接收的消息的id，用于填充引用消息字段
            short_id = message['data']['author']['username']#用户短id
            guild_id = message['data']['guild_id']#服务器id
            guild_id = int(guild_id)
            #以上参数未int则均为String类型
            if check_content(msg):
                i = True#i均为判断业务逻辑所需，可自行删除.下同
                for x in pro:
                    if x == guild_id:
                        i = False
                if i:
                    if "${@!" + bot_id + "}" in content['text']:  #获取消息内容里面的纯文本内容，并判断有没有@该机器人（如果不是纯文本或者是其他消息会报错，不触发请查看bot id是否填写正确）
                        if switch == 0:
                            starttime = time.perf_counter()
                            if "切换模型" in msg:
                                if short_id == "8928358":
                                    if switch == 0:
                                        switch = 1
                                        sendMessage(int(message["data"]["channel_id"]), "已切换为模型gpt4o", messageid)
                                    else:
                                        switch = 0
                                        sendMessage(int(message["data"]["channel_id"]), "已切换为模型gpt4o-mini", messageid)
                                else:
                                    sendMessage(int(message["data"]["channel_id"]), "无操作权限", messageid)
                            elif "清除上下文" in msg:
                                if short_id == "8928358":
                                    del history[1:]
                                    len = 0
                                    sendMessage(int(message["data"]["channel_id"]), "已清除上下文", messageid)
                                else:
                                    sendMessage(int(message["data"]["channel_id"]), "权限不足", messageid)
                            else:#如果消息内容不是清除上下文，则调用gpt接口
                                url = "https://api.chatanywhere.tech/v1/chat/completions"
                                headers = {
                                    "Content-Type": "application/json",
                                    "Authorization": "sk-*************"
                                }#请到chatanywhere获取token
                                mechat = [{"role": "user", "content": msg}]
                                history.append(mechat[0])
                                data = {
                                    "model": "gpt-4o-mini",
                                    "messages": history,
                                    "temperature": 0.7
                                }
                                response = requests.post(url, headers=headers, json=data)
                                response = json.loads(response.text)
                                print(response)
                                output = response['choices'][0]['message']['content']
                                youchat = [{"role": "assistant", "content": output}]
                                history.append(youchat[0])
                                len += 1
                                if len > 5:
                                    history.pop(1)
                                    history.pop(2)
                                    len -= 1
                                model = response['model']
                                output = f"{chat}{output}\n使用模型：{model}"
                                endtime = time.perf_counter()
                                times = endtime - starttime
                                output = f"{output}\n耗时：{times}秒"
                                sendMessage(int(message["data"]["channel_id"]), output, messageid) #发送消息
                        elif switch == 1:#切换模式
                            if "切换模型" in msg:
                                if short_id == "8928358":
                                    if switch == 0:
                                        switch = 1
                                        sendMessage(int(message["data"]["channel_id"]), "已切换为模型gpt4o", messageid)
                                    else:
                                        switch = 0
                                        sendMessage(int(message["data"]["channel_id"]), "已切换为模型gpt4o-mini", messageid)
                                else:
                                    sendMessage(int(message["data"]["channel_id"]), "无操作权限", messageid)
                                del history[1:]
                            elif "清除上下文" in msg:
                                if short_id == "8928358":
                                    del history[1:]
                                    len = 0
                                    sendMessage(int(message["data"]["channel_id"]), "已清除上下文", messageid)
                                else:
                                    sendMessage(int(message["data"]["channel_id"]), "权限不足", messageid)
                            else:
                                url = "https://apii.lolimi.cn/api/c4o/c?key=********"#请在桑帛云获取APIkey
                                headers = {
                                    "Content-Type": "application/json"
                                }
                                mechat = [{"role": "user", "content": msg}]
                                history.append(mechat[0])
                                response = requests.post(url=url,headers=headers,json=history)
                                response = response.text
                                sendMessage(int(message["data"]["channel_id"]), response, messageid) #发送消息
                                youchat = [{"role": "assistant", "content": response}]
                                history.append(youchat[0])
                                len += 1
                                if len > 5:
                                    history.pop(1)
                                    history.pop(2)
                                    len -= 1

def on_error(ws, error):
    # 处理错误
    addmsg("发生错误:" + str(error), color='red')


def on_close(ws):
    # 连接关闭时的操作
    addmsg("连接已关闭", color='red')


def on_open(ws):
    # 连接建立时的操作
    addmsg("连接已建立", color='green')

    # 发送心跳包
    def send_ping():
        print('发送：{"type":"ping"}')
        ws.send('{"type":"ping"}')

    send_ping()  # 发送第一个心跳包
    # 定时发送心跳包


# 替换成用户输入的BOT令牌
lingpai = lingpai
url = requests_url + f"{lingpai}/getMe"
# 发送HTTP请求获取基本信息
response = requests.get(url)
data = response.json()


def send_data_thread():
    while True:
        # 在这里编写需要发送的数据
        time.sleep(25)
        ws.send('{"type":"ping"}')
        addmsg('发送心跳包：{"type":"ping"}', color='green')


if response.ok and data.get("ok"):
    user_token = data["result"]["user_token"]  #获取user token以建立连接
    device_id = "your_device_id"
    version_number = "1.6.60"
    #拼接base64字符串
    super_str = base64.b64encode(json.dumps({
        "platform": "bot",
        "version": version_number,
        "channel": "office",
        "device_id": device_id,
        "build_number": "1"
    }).encode('utf-8')).decode('utf-8')
    ws_url = websocket_url + f"?id={user_token}&dId={device_id}&v={version_number}&x-super-properties={super_str}"  #准备url
    threading.Thread(target=send_data_thread, daemon=True).start()  #启动定时发送心跳包的线程
    # 建立WebSocket连接
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
else:
    addmsg("无法获取BOT基本信息，请检查令牌是否正确。", color='red')
