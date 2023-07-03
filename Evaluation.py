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

formatCorrectPredictions()