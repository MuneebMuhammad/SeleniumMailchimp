import json
from transformers import logging, AutoProcessor, MarkupLMForQuestionAnswering, MarkupLMProcessor, MarkupLMFeatureExtractor, MarkupLMTokenizer, MarkupLMTokenizerFast, TrainingArguments, Trainer,DefaultDataCollator
import torch
from datasets import load_dataset

dataset = load_dataset('json', data_files='/scratch/muneebm/NLP/actionTransformers/datasets/v3/train.json')
validationData = load_dataset('json', data_files='/scratch/muneebm/NLP/actionTransformers/datasets/v3/correctTest.json')
new_max_position_embeddings = 1026
save_weights_dir = "/scratch/muneebm/NLP/actionTransformers/weights/mad_markupLM_seq1024"

feature_extractor = MarkupLMFeatureExtractor()
tokenizer = MarkupLMTokenizerFast.from_pretrained("microsoft/markuplm-base-finetuned-websrc")
processor = MarkupLMProcessor(feature_extractor, tokenizer)

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

# preprocess the dataset
def preprocessFunction(examples):
    questions = examples["question"].strip()
    inputs = processor(examples["context"], questions=questions, return_tensors="pt", truncation=True, return_offsets_mapping=True, return_special_tokens_mask=True, max_length=new_max_position_embeddings-2, padding='max_length'
                       )
    offset = inputs.pop("offset_mapping")
    offset = offset[0]
    offset = offsetCumulation(offset)
    torch.set_printoptions(profile="default")
    special_tokens_mask = inputs.pop("special_tokens_mask")
    special_tokens_mask = special_tokens_mask[0]
    answers = examples["answers"]
    start_positions = 0
    end_positions = 0
    start_char = int(answers["answer_start"][0])
    end_char = start_char + len(answers["text"][0])

    idx = 1
    while special_tokens_mask[idx] != 1:
        idx += 1
    context_start = idx
    idx += 1
    while special_tokens_mask[idx] != 1:
        idx += 1
    context_end = idx-1

    if offset[context_start][0] > end_char or offset[context_end][1] < start_char:
        start_positions = 0
        end_positions = 0
    else:
        idx = context_start
        while idx<context_end and offset[idx][0] <=start_char:
            idx += 1
        start_positions = idx-1

        idx = context_end
        while idx >= context_start and offset[idx][1] >= end_char:
            idx -= 1
        end_positions = idx + 1

    inputs["start_positions"] = start_positions
    inputs["end_positions"] = end_positions

    inputs["input_ids"] = inputs["input_ids"].squeeze(0)
    inputs["token_type_ids"] = inputs["token_type_ids"].squeeze(0)
    inputs["attention_mask"] = inputs["attention_mask"].squeeze(0)
    inputs["xpath_tags_seq"] = inputs["xpath_tags_seq"].squeeze(0)
    inputs["xpath_subs_seq"] = inputs["xpath_subs_seq"].squeeze(0)

    return inputs

tokenized_dataset = dataset.map(preprocessFunction, remove_columns=dataset["train"].column_names)
tokenized_test_data = validationData.map(preprocessFunction, remove_columns=validationData["train"].column_names)
data_collator = DefaultDataCollator()
model = MarkupLMForQuestionAnswering.from_pretrained("microsoft/markuplm-base-finetuned-websrc")

old_max_position_embeddings = model.config.max_position_embeddings
if new_max_position_embeddings > old_max_position_embeddings:
    print("increasing sequence length")
    # Resize the positional embeddings
    old_embeddings = model.markuplm.embeddings.position_embeddings.weight
    new_embeddings = old_embeddings.new_empty((new_max_position_embeddings, old_embeddings.size(1)))
    new_embeddings[:old_max_position_embeddings] = old_embeddings
    model.markuplm.embeddings.position_embeddings.weight = torch.nn.Parameter(new_embeddings)
    model.config.max_position_embeddings = new_max_position_embeddings

# Training model
training_args = TrainingArguments(
    output_dir = save_weights_dir,
    evaluation_strategy = "epoch",
    learning_rate = 2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs = 100,
    weight_decay = 0.01,
    save_strategy="epoch",
)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_test_data["train"],
    tokenizer=tokenizer,
    data_collator = data_collator
)
trainer.train()

tokenizer.save_pretrained(save_weights_dir)
print(f"training data:{len(dataset['train'])}\nvalidation data:{len(validationData['train'])}")
