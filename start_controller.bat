@echo off
cd /d G:\ai-chatglm-demo
call venv\Scripts\activate

echo Starting FastChat Controller...
python -m fastchat.serve.controller ^
    --host 0.0.0.0 ^
    --port 21001 ^
    > logs\controller.log 2>&1

pause

