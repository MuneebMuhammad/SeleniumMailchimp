import json
from transformers import logging, AutoProcessor, MarkupLMForQuestionAnswering, MarkupLMProcessor, MarkupLMFeatureExtractor, MarkupLMTokenizer, MarkupLMTokenizerFast, TrainingArguments, Trainer,DefaultDataCollator
import torch

from datasets import load_dataset

# change markupLM offset into the offset of reqular tokenizer
def offsetCumulation(offset):
    et = 0
    for r, i in enumerate(offset):
        if offset[r][0] == torch.tensor([0]) and r !=0:
            et = offset[r-1][1]
        if offset[r][1] == torch.tensor([0]):
            et = 0
        offset[r][0] = et+offset[r][0]
        offset[r][1] = et+offset[r][1]
    return offset

def calculate_f1(prediction_start, prediction_end, target_start, target_end):
    prediction_range = set(range(prediction_start, prediction_end))
    target_range = set(range(target_start, target_end + 1))

    tp = len(prediction_range.intersection(target_range))
    fp = len(prediction_range.difference(target_range))
    fn = len(target_range.difference(prediction_range))

    if tp == 0:
        return 0,0,0

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * (precision * recall) / (precision + recall)

    return precision, recall, f1


dataset = load_dataset('json', data_files='../datasets/datasetV3/train.json')
validationData = load_dataset('json', data_files='../datasets/datasetV3/test.json')
# load pretrained model
feature_extractor = MarkupLMFeatureExtractor()
tokenizer = MarkupLMTokenizerFast.from_pretrained("my_qa_model")
processor = MarkupLMProcessor(feature_extractor, tokenizer)
data_collator = DefaultDataCollator()
model = MarkupLMForQuestionAnswering.from_pretrained("my_qa_model/checkpoint-12")

example = validationData["train"][1]

#inference
with torch.no_grad():
    inputs = processor(example["context"], questions=example["question"], return_tensors="pt", truncation=True, max_length=512, padding='max_length', return_offsets_mapping=True)
    offsets = inputs.pop("offset_mapping")
    outputs = model(**inputs)
answer_start_index = outputs.start_logits.argmax()
answer_end_index = outputs.end_logits.argmax()

offsets = offsetCumulation(offsets[0])

prediction_start_char = offsets[answer_start_index][0]
prediction_end_char = offsets[answer_end_index][1]

target_start_char = int(example["answers"]['answer_start'][0])
target_end_char = target_start_char + len(example["answers"]['text'][0])

print(f"Prediction:{prediction_start_char}, {prediction_end_char}")
print(f"Target:{target_start_char}, {target_end_char}")

pred, rec, f1 = calculate_f1(prediction_start_char, prediction_end_char, target_start_char, target_end_char)
print(pred, rec, f1)
predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]
print("Actual prediction:", processor.decode(predict_answer_tokens).strip())