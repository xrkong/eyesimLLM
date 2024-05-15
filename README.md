# eyesimLLM
Integrate LLM with eyebot simulator

## Introduction
Using LLM (local or cloud) to control eyebots in the simulator. 

## Roadmap
- [ ] Create a environment ```.sim``` file
- [ ] Design a demo to control an eyebot
- [ ] Get camera images from eyebots
- [ ] Get lidar sensors from eyebots
- [ ] Call OpenaiAPI / llama2 to get responses (text-to-action)
- [ ] Design some missions for eyebots


## 1. Set up the demo using docker

 - Set up docker
   ```bash
   docker build -f Dockerfile -t eyesim1.5.2:latest .
   ```
 - Set up virtual environment
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
 - ~~Create .env file and put `REMOTE_API_TOKEN` or `OPENAI_API_KEY` into it.~~

 - Execute the demo
   ```bash
   docker compose up
   docker exec -it eyesim bash
   cd ws/src/scripts
   # HARD CODED VERSION
   python3.9 finder.py
   # LLM
   python3.9 finder_llm.py
   ```

## 2. Set up the demo not using docker

 - set up virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

 - start eyesim
   ```bash
   eyesim
   ```

 - Execute the demo
   ```bash
   python run.py
   ```


## References

[API Documentation](https://api.nlp-tlp.org/redoc/#tag/queue_task)

[Self-hosted LLMs at UWA](https://uwa-nlp-tlp.gitbook.io/llm-tutorial)
