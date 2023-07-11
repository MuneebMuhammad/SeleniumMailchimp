import os
import openai
import pandas as pd


def valDataEvaluation():
    ft_model = 'ada:ft-personal-2023-06-27-06-24-04'
    correct = 0
    dir_path = "./errors/"

    count = 0

    test = pd.read_json('final_dataset1_prepared_valid.jsonl', lines=True)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    for i, text in enumerate(test['prompt']):

        try:
            res = openai.Completion.create(model=ft_model, prompt=test['prompt'][i], max_tokens=1, temperature=0)
            count += 1
        except:
            print(f"{i + 1} prompt greater")
            continue
        target = test['completion'][i]
        prediction = int(res['choices'][0]['text'])

        if target == prediction:
            correct += 1
            with open("./correct.txt", "a") as f:
                f.write(f"{i + 1}\n")
            print(f"i={i + 1}")
            continue

        lines = text.split('\n')
        # Check if start_line and end_line are within the bounds of the lines array
        if target <= len(lines):
            lines[target - 1] = '--------------------------> ' + lines[target - 1]
        if prediction <= len(lines):
            lines[prediction - 1] = 'xxxxxxxxxxxxxxxxxxxxxxxxxx> ' + lines[prediction - 1]
        else:
            lines[len(lines) - 1] = str(prediction) + " xxx " + lines[len(lines) - 1]

        # Create a new file for each text
        filename = f"text_{i + 1}.txt"
        with open(os.path.join(dir_path, filename), "w") as f:
            f.write('\n'.join(lines))

    print(f"Accuracy = {correct}/{len(test['prompt'])} = {correct / len(test['prompt'])}")


def formatCorrectPredictions():
    dir_path = "./corrects/"
    # Reading the indices from file
    with open('correct.txt', 'r') as f:
        indices = f.read().splitlines()

    indices = [int(idx)-1 for idx in indices]  # Convert indices to integers

    test = pd.read_json('final_dataset1_prepared_valid.jsonl', lines=True)

    for idx in indices:
        target = test['completion'][idx]
        text = test['prompt'][idx]
        lines = text.split('\n')
        lines[target - 1] = '--------------------------> ' + lines[target - 1]

        # Create a new file for each text
        filename = f"text_{idx+1}.txt"
        with open(os.path.join(dir_path, filename), "w") as f:
            f.write('\n'.join(lines))


def singleInferenceFromVal(index):
    ft_model = 'ada:ft-personal-2023-06-27-06-24-04'
    test = pd.read_json('../datasetV1/final_dataset1_prepared_train.jsonl', lines=True)
    try:
        res = openai.Completion.create(model=ft_model, prompt=test['prompt'][index-1], max_tokens=1, temperature=0)
    except:
        print(f"{index} prompt greater")
    target = test['completion'][index-1]
    text = test['prompt'][index-1]
    prediction = int(res['choices'][0]['text'])

    lines = text.split('\n')

    # Check if start_line and end_line are within the bounds of the lines array
    if target <= len(lines):
        lines[target - 1] = '--------------------------> ' + lines[target - 1]
    if prediction <= len(lines):
        lines[prediction - 1] = 'xxxxxxxxxxxxxxxxxxxxxxxxxx> ' + lines[prediction - 1]
    else:
        lines[len(lines) - 1] = str(prediction) + " xxx " + lines[len(lines) - 1]

    # Create a new file for each text
    filename = f"text_{index}.txt"
    with open("pred.txt", "w") as f:
        f.write('\n'.join(lines))


def inferenceOnDomV1(instruction, domPath):
    ft_model = 'ada:ft-personal-2023-06-27-06-24-04'
    with open(domPath, 'r') as f:
        dom = f.read().strip()
    prompt = instruction + '[SEP]' + dom + '\n\n###\n\n'
    print(prompt)
    res = openai.Completion.create(model=ft_model, prompt=prompt, max_tokens=1, temperature=0)
    print("response is", res['choices'][0]['text'])

def inferenceOnDomV2(instruction, domPath):
    ft_model = "ada:ft-personal-2023-07-04-13-52-51"
    with open(domPath, 'r') as f:
        dom = f.read().strip()
    prompt = "Select the line number in DOM which corresponds to the below instruction\nInstruction is "+instruction+"\nDOM\n"+dom + '\n\n###\n\n'
    print(prompt)
    res = openai.Completion.create(model=ft_model, prompt=prompt, max_tokens=1, temperature=0)
    print("response is", res['choices'][0]['text'])

inferenceOnDomV2('Create an email', './DOM.txt')







# ft_model = 'ada:ft-personal-2023-06-27-06-24-04'
# trains = pd.read_json('../datasetV1/final_dataset1_prepared_train.jsonl', lines=True)
# res = openai.Completion.create(model=ft_model, prompt=trains['prompt'][0], max_tokens=1, temperature=0)
# print(res['choices'][0]['text'])

