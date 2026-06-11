from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


def split_documents(documents):

    return splitter.split_documents(documents)




'''
Chunk Size
Chunk Overlap
Token Budget
Recall
Latency
'''