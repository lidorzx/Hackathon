# Hackathon
first : pip install -r requirements.txt - to install all dependencies for hosting the model. we will use Llama 3.3-70B which is very good for these kind of calculations.
-------------------------------------------------------------------
1. python3 -m vllm.entrypoints.openai.api_server \
  --model /home/lidor/vLLM-Project/models/llama-3.3-70B-Instruct \
  --tensor-parallel-size 8 \
  --max-model-len 8192
-------------------------------------------------------------------
2. Now Check with curl - curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "/home/lidor/vLLM-Project/models/llama-3.3-70B-Instruct",
    "messages": [
      {"role": "user", "content": "What is the difference between a VM snapshot and a clone in VMware?"}
    ],
    "temperature": 0.3
  }'


3. under vmware-ai-agent - collector - collect_vms.py  - 
export GOVC_URL='x.x.x.x'
export GOVC_USERNAME='administrator@vsphere.local'
export GOVC_PASSWORD='xxx!'
export GOVC_INSECURE=1


than : 
curl -LO https://github.com/vmware/govmomi/releases/latest/download/govc_Linux_x86_64.tar.gz
chmod +x govc
sudo mv govc /usr/local/bin/
python3 collect_vms.py

