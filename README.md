# FanAIPro
Fanbook平台上的AI机器人，支持多种模型，上下文，系统提示词

结构:
1-14:导入必要库
15-131:定义了许多功能函数及用于websocket连接的函数与json,ws高亮显示函数
132-254:为主要业务逻辑,接收消息后的操作全部在这里(嵌套有点多请慢慢食用)
255-326:构建了websocket发送心跳包,处理错误与断开连接的函数
温馨提示:
本代码仅可在Fanbook平台使用,开发野生QQBOT的话可以借鉴下逻辑.
