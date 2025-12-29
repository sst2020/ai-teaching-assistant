@echo off
cd /d G:\ai-chatglm-demo
call venv\Scripts\activate

echo Starting FastChat OpenAI API Server...
python -m fastchat.serve.openai_api_server ^
    --controller-address http://localhost:21001 ^
    --host 0.0.0.0 ^
    --port 8000 ^
    > logs\api.log 2>&1

pause

