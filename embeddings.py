import numpy as np
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup, NavigableString
from ordered_set import OrderedSet
import tiktoken
import openai

from openai.embeddings_utils import get_embeddings

mainElements = []
xpaths = []

def get_xpath(element):
    path = []
    while element:
        if element.name:
            siblings = [sibling for sibling in element.previous_siblings if sibling.name == element.name]
            index = len(siblings) + 1
            if index > 1:
                path.append(f'{element.name}[{index}]')
            else:
                path.append(element.name)
        element = element.parent
    return '/'.join(reversed(path))

# recursive function to get the main elements
def find_text_tags(tag):
    if isinstance(tag, NavigableString):
        if tag.strip():
            if tag.parent.name not in ['script', 'style']:
                mainElements.append(tag.parent)
                xpaths.append(get_xpath(tag.parent))
    else:
        if tag.name == 'input':
            if tag.get("type") != "hidden":
                mainElements.append(tag)
                xpaths.append(get_xpath(tag))
        for child in tag.children:
            find_text_tags(child)


def hugginfaceEmbedding(chunks, question):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    embeddings = model.encode(chunks)
    queryEmbedding = model.encode([question])
    dotProducts = embeddings @ queryEmbedding.transpose()

    # Find the indices that would sort 'array'
    sorted_indices = dotProducts.argsort(axis=0).flatten()

    # Get the indices for the top 4 greatest elements in 'array'
    top_4_indices = sorted_indices[-4:][::-1]

    print(len(chunks))
    print(top_4_indices)
    # Retrieve the corresponding content from 'content_array' based on the indices
    for i in top_4_indices:
        print(chunks[i])
        print("-"*100)


def openaiEmbedding(chunks, question):
    # embedding model parameters
    embedding_model = "text-embedding-ada-002"
    embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
    max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191

    encoding = tiktoken.get_encoding(embedding_encoding)
    # tokens = encoding.encode("Hello there I am muneeb muhammad from bscs 10C")
    # print("tokens length:", len(tokens))

    chunkEmbeddings = openai.Embedding.create(
        input=chunks,
        model=embedding_model
    )
    embeddingArray = np.array([ce['embedding'] for ce in chunkEmbeddings['data']])

    queryEmbeddings = np.array([openai.Embedding.create(
        input=[question],
        model=embedding_model
    )['data'][0]['embedding']])



    dotProducts = embeddingArray @ queryEmbeddings.transpose()

    # Find the indices that would sort 'array'
    sorted_indices = dotProducts.argsort(axis=0).flatten()

    # Get the indices for the top 4 greatest elements in 'array'
    top_4_indices = sorted_indices[-4:][::-1]

    print(len(chunks))
    print(top_4_indices)
    # Retrieve the corresponding content from 'content_array' based on the indices
    for i in top_4_indices:
        print(chunks[i])
        print("-" * 100)


# get the dom and preprocess it
with open("../datasets/datasetV3/test1/2/DOM.txt") as f:
    dom = f.read()
soup = BeautifulSoup(dom, "html.parser")
for tag in soup.find_all(True):  # find_all(True) returns all tags in the soup
    tag.attrs = {}
# find_text_tags(soup.body)
data = '\n'.join(line.lstrip() for line in soup.prettify().splitlines())

question = "phones"
# dividing into chunks
chunks= []
max_length = 1000
stride = 950
start = 0
while start <len(data):
    chunks.append(data[start: max_length+start])
    start += stride
print(chunks)
hugginfaceEmbedding(chunks, question)
# openaiEmbedding(chunks, question)