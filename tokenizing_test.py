import glob
from transformers import BertTokenizer, BertModel, Trainer, TrainingArguments

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# print(len(tokenizer("Your hub on the internet. A one-stop-shop for your subscribers to find all you r content adn prducts")['input_ids']))
files = glob.glob("../final_dataset1/*/*")
print(len(files))
sum = 0
count = 0
sumInstructions = 0
for i in files:
    if i.split('/')[-1] == "DOM.txt":
        f = open(i, "r", encoding='ISO-8859-1')
        try:
            d = f.read()
            f.close()
            sum += len(tokenizer(d)['input_ids'])
            count += 1
            if (len(tokenizer(d)['input_ids']) > 2000):
                print(i, len(tokenizer(d)['input_ids']))
        except:
            print("error:", i)

    # if i.split('/')[-1] == "instruction.txt":
    #     f = open(i, "r")
    #     d = f.readlines()
    #     f.close()
    #     sumInstructions += len(d)




# print(f"{sumInstructions}")
