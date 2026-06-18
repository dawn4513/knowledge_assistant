# -*- encoding: utf-8 -*-
"""
@File    : hello.py
@Time    : 2026/6/14 18:00
@Desc    : 调用大模型接口，进行一次对话
            使用模型为百度智能云中模型（免费额度）
            可用模型地址：https://console.bce.baidu.com/qianfan/modelcenter/model/buildIn/list 2026年07月20日到期
"""
import time
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

url = "https://qianfan.baidubce.com/v2"
api_key = os.environ.get("QIANFAN_API_KEY")
if not api_key:
    raise RuntimeError("请在项目根目录的 .env 文件中设置 QIANFAN_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url=url
)

PROMPTS = {"中文": "用一句话描述一只猫在做什么。", "English": "Describe in one sentence what a cat is doing."}

for label, prompt in PROMPTS.items():
    t0 = time.time()
    output_tokens = []
    latencies = []
    for _ in range(3):
        print(f"Prompt: {prompt}, times: {_+1}")
        response = client.chat.completions.create(
            model="ernie-x1-turbo-32k",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        output_tokens.append(response.usage.completion_tokens)
        latencies.append(time.time() - t0)
    avg_latency = sum(latencies) / len(latencies)
    print(f"3 次 latency (sec): min={min(latencies):.2f} max={max(latencies):.2f} mean={avg_latency:.2f}")
    print(f"[{label}] input={response.usage.prompt_tokens} output min/max/mean={min(output_tokens)}/{max(output_tokens)}/{sum(output_tokens)/len(output_tokens):.1f}")


# text = response.choices[0].message.content
# print("回应：", text)
# print("usage:", response.usage)

# assert response.choices[0].finish_reason in ["stop", "length"], f"unexpected finish reason: {response.choices[0].finish_reason}"
# assert text is not None, "response text is None"
# assert len(text) > 0, "response text is empty"
