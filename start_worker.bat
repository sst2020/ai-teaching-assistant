@echo off
cd /d G:\ai-chatglm-demo
call venv\Scripts\activate

echo Starting FastChat Model Worker...
python -m fastchat.serve.model_worker ^
    --model-path G:\ai-chatglm-demo\models\chatglm4-6b ^
    --model-names chatglm4-6b,gpt-3.5-turbo ^
    --controller-address http://localhost:21001 ^
    --worker-address http://localhost:31001 ^
    --host 0.0.0.0 ^
    --port 31001 ^
    --device cuda ^
    --num-gpus 1 ^
    --max-gpu-memory 7GiB ^
    --load-8bit ^
    > logs\worker.log 2>&1

pause

