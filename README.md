# Setup
Step 1: Clone repository

Step 2:
`pip install -r requirements.txt`

Step 3: Make modifications in `gptforjob_v2.ipynb` and run

# Modifications before running
- Change `url` to whatever job you want to apply to
- Change `filename` to resume (filetype=pdf only) you want to check

# Disclaimer
- It is meant as a helping hand to reduce the effort required to finetune resumes for jobs, not a do-all solution.
- It is based on [Cohere LLM](https://cohere.com/), or simply put AI which *may not always* be (ironically) intelligent, so the outputs are sometimes generic.
- The AI is *not* specifically trained for resume matching, but does a fair job, but then again, may not always be perfect.
- The code uses my personal API key

# Roadmap
(If  I still remain interested)
- [ ] v3 (nonfunctional right now) - Will have [GUI](https://github.com/hoffstadt/DearPyGui) or may be a locally hosted webpage as GUI, idk
- [ ] v4 - [Training an LLM for resume matching](https://huggingface.co/datasets/cnamuangtoun/resume-job-description-fit) 
