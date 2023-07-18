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
    prediction_range = set(range(prediction_start, prediction_end+1))
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


model_path = "/scratch/muneebm/NLP/actionTransformers/weights/my_qa_model/checkpoint-3055"
print(model_path)
dataset = load_dataset('json', data_files='/scratch/muneebm/NLP/actionTransformers/datasets/v3/train.json')
validationData = load_dataset('json', data_files='/scratch/muneebm/NLP/actionTransformers/datasets/v3/test.json')

# load pretrained model
feature_extractor = MarkupLMFeatureExtractor()
tokenizer = MarkupLMTokenizerFast.from_pretrained("/scratch/muneebm/NLP/actionTransformers/weights/my_qa_model")
processor = MarkupLMProcessor(feature_extractor, tokenizer)
data_collator = DefaultDataCollator()
model = MarkupLMForQuestionAnswering.from_pretrained(model_path)

pred_sum = 0
rec_sum = 0
f1_sum = 0
exact_match = 0
incorrect = 0
for single in validationData["train"]:
    # inference
    with torch.no_grad():
        inputs = processor(single["context"], questions=single["question"],
                           return_tensors="pt", truncation=True, max_length=512, padding='max_length',
                           return_offsets_mapping=True)
        offsets = inputs.pop("offset_mapping")
        outputs = model(**inputs)
    answer_start_index = outputs.start_logits.argmax()
    answer_end_index = outputs.end_logits.argmax()

    offsets = offsetCumulation(offsets[0])

    prediction_start_char = offsets[answer_start_index][0]
    prediction_end_char = offsets[answer_end_index][1]

    target_start_char = int(single["answers"]['answer_start'][0])
    target_end_char = target_start_char + len(single["answers"]['text'][0])

    pred, rec, f1 = calculate_f1(prediction_start_char, prediction_end_char, target_start_char, target_end_char)
    pred_sum += pred
    rec_sum += rec
    f1_sum += f1
    if f1 == 1: exact_match += 1
    if f1 == 0: incorrect += 1
    print(f"Prediction:{prediction_start_char}, {prediction_end_char}")
    print(f"Target:{target_start_char}, {target_end_char}")
    print(f"pred:{pred}, rec:{rec}, f1:{f1}")

print(f"Aggregate\nPrediction:{pred_sum/len(validationData['train'])}, Recall:{rec_sum/len(validationData['train'])}, f1:{f1_sum/len(validationData['train'])}")
print(f"exact match:{exact_match}/{len(validationData['train'])}={exact_match/len(validationData['train'])}")
print(f"Accuracy:{(len(validationData['train'])-incorrect)/len(validationData['train'])}")