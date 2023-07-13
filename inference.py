import json
from transformers import logging, AutoProcessor, MarkupLMForQuestionAnswering, MarkupLMProcessor, MarkupLMFeatureExtractor, MarkupLMTokenizer, MarkupLMTokenizerFast, TrainingArguments, Trainer,DefaultDataCollator
import torch

from datasets import load_dataset

dataset = load_dataset('json', data_files='data.json')

feature_extractor = MarkupLMFeatureExtractor()
tokenizer = MarkupLMTokenizerFast.from_pretrained("my_qa_model")
processor = MarkupLMProcessor(feature_extractor, tokenizer)

data_collator = DefaultDataCollator()
model = MarkupLMForQuestionAnswering.from_pretrained("my_qa_model/checkpoint-12")

#inference
with torch.no_grad():
    inputs = processor(dataset["train"][3]["context"], questions=dataset["train"][0]["question"], return_tensors="pt", truncation=True, max_length=512, padding=True)
    outputs = model(**inputs)
answer_start_index = outputs.start_logits.argmax()
answer_end_index = outputs.end_logits.argmax()

predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]
print(processor.decode(predict_answer_tokens).strip())