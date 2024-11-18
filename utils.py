import tiktoken
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
    AIMessage,
    SystemMessage
)
import string
from typing import List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from google.cloud import translate
import re
import json

ministries_data_file = "ministries_data_desc.json"

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def str_token_counter(text: str) -> int:
    enc = tiktoken.get_encoding("o200k_base")
    return len(enc.encode(text))


def detect_language(text):
    text = text.translate(str.maketrans('', '', string.punctuation))
    # print(text)

    english_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    hindi_chars = set('अआइईउऊऋएऐओऔअंअःकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')
    

    english_count = sum(1 for char in text if char in english_chars)
    hindi_count = sum(1 for char in text if char in hindi_chars)


    if english_count >= hindi_count:
        return "English"
    else:
        return "Hindi"

def tiktoken_counter(messages: List[BaseMessage]) -> int:
    """Approximately reproduce https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb

    For simplicity only supports str Message.contents.
    """
    num_tokens = 3  # every reply is primed with <|start|>assistant<|message|>
    tokens_per_message = 3
    tokens_per_name = 1
    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        elif isinstance(msg, ToolMessage):
            role = "tool"
        elif isinstance(msg, SystemMessage):
            role = "system"
        else:
            raise ValueError(f"Unsupported messages type {msg.__class__}")
        num_tokens += (
            tokens_per_message
            + str_token_counter(role)
            + str_token_counter(msg.content)
        )
        if msg.name:
            num_tokens += tokens_per_name + str_token_counter(msg.name)
    return num_tokens

def format_messages(messages):
    temp = """"""
    for i in range(0, len(messages)):
        input_str = ""
        if type(messages[i]).__name__ == "HumanMessage":
            content = messages[i].content

            input_str = f"""User - {content}\n"""   

        if type(messages[i]).__name__ == "AIMessage":
            content = messages[i].content

            input_str = f"""Assistant - {content}\n"""
    
        temp = temp + input_str

    return temp

def make_prompt(system, human, chat_history=False):

    if chat_history == True:
        prompt =  ChatPromptTemplate.from_messages(
                    [
                        ("system",system),    
                        MessagesPlaceholder("chat_history", optional=True),
                        ("human", human)
                    ]
                )
        
        return prompt

    else:

        prompt =  ChatPromptTemplate.from_messages(
                    [
                        ("system",system),    
                        ("human", human)
                    ]
                )
    return prompt 


# Initialize Translation client
def translate_text(text: str, source_lang:str, target_lang:str) -> translate.TranslationServiceClient:
    """Translating Text."""

    client = translate.TranslationServiceClient() #udaan APi key will come here 

    location = "global"

    parent = f"projects/avian-album-434618-k6/locations/{location}"

    # Detail on supported types can be found here:
    
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "source_language_code": source_lang,
            "target_language_code": target_lang,
        }
    )


    return response.translations[0].translated_text

def extract_standalone_question(text):
    # Define the regex pattern to match 'Standalone Grievance:' followed by any text
    pattern = r"Standalone Grievance:\s*(.*)"
    
    # Search for the pattern in the text
    match = re.search(pattern, text, re.DOTALL)
    
    # If a match is found, return the text after 'Standalone Grievance:', else return the whole text
    if match:
        return match.group(1).strip()  # Extract and return the standalone grievance
    else:
        return text.strip()
    

def get_ministries():
    with open(ministries_data_file, 'r') as file:
        data = json.load(file)
    return [(ministry_data["Ministry"], ministry_data["Ministry_Desc"]) for ministry_data in data]

########################################################
with open(ministries_data_file, 'r') as file:
    data = json.load(file)

def get_category(obj, category_path):

    if len(category_path) == 0:
        if "obj" in obj:
            return obj["obj"]
        else:
            return obj
    
    if "Categories" in obj.keys():
        for i in obj["Categories"]:
            if i["Category_Name"] == category_path[0]:
                return get_category(i, category_path[1:])
    
    if "obj" in obj.keys():
        obj = obj["obj"]
        if "Categories" in obj.keys():
            for i in obj["Categories"]:
                if i["Category_Name"] == category_path[0]:
                    return get_category(i, category_path[1:])
        else:
            return obj

############################################################### 

def get_next_level_categories(ministry_name, category_path):

    def search_next_level(categories, path_index):
        for category in categories:
            # Check if the current category matches the category path
            if category["Category_Name"] == category_path[path_index]:
                # If we've reached the last category in the path, return its subcategories
                if path_index == len(category_path) - 1:
                    # Return the next level of categories if available
                    return [(subcat["Category_Name"], subcat["Category_Desc"]) for subcat in category["obj"]["Categories"]] if "obj" in category and "Categories" in category["obj"] else []
                # Otherwise, continue down the hierarchy
                elif "obj" in category and "Categories" in category["obj"]:
                    return search_next_level(category["obj"]["Categories"], path_index + 1)
        return []

    # Find the specified ministry
    for ministry in data:
        if ministry["Ministry"] == ministry_name:
            # If category_path is empty, return the main categories under the ministry
            if not category_path:
                return [(cat["Category_Name"], cat["Category_Desc"]) for cat in ministry["Categories"]]
            # Otherwise, follow the specified path
            return search_next_level(ministry["Categories"], 0)

def get_fields(ministry_name, category_path, fields=True):
    with open(ministries_data_file, 'r') as file:
        data = json.load(file)

    def search_fields(categories, category_index):
        for category in categories:
            if category["Category_Name"] == category_path[category_index]:
                if category_index == len(category_path) - 1:
                    if "obj" in category:
                        if fields:
                            return [
                                key for key in category["obj"].keys()
                                if not (key.startswith("Please upload") or key.startswith("Attach relevant/supporting documents") or key == "Ministry/Organisation") # Excluding Ministry/Organisation till fetching options dynamically are handled
                            ]
                        else:
                            return [
                                key.split("Please upload :", 1)[-1].strip() 
                                for key in category["obj"].keys() 
                                if key.startswith("Please upload")
                            ]
                            # return ["Copy of first page of gas book", "LPG cash memos"]
                    return []
                elif "obj" in category and "Categories" in category["obj"]:
                    return search_fields(category["obj"]["Categories"], category_index + 1)
        return []

    for ministry in data:
        if ministry["Ministry"] == ministry_name:
            return search_fields(ministry["Categories"], 0)

def is_leaf_category(ministry_name, category_path):
    with open(ministries_data_file, 'r') as file:
        data = json.load(file)
        
    def check_leaf(categories, path_index):
        for category in categories:
            # Match the current category in the path
            if category["Category_Name"] == category_path[path_index]:
                # If we've reached the last category in the path, check if it has further subcategories
                if path_index == len(category_path) - 1:
                    # Return True if no subcategories exist, False otherwise
                    return not ("obj" in category and "Categories" in category["obj"])
                # Continue down the hierarchy if more path remains
                elif "obj" in category and "Categories" in category["obj"]:
                    return check_leaf(category["obj"]["Categories"], path_index + 1)
        return False

    if not category_path:
        return False
    
    # Find the specified ministry and start the leaf check from its top-level categories
    for item in data:
        if item["Ministry"] == ministry_name:
            return check_leaf(item["Categories"], 0)

    # Return False if ministry is not found
    return False

def generate_category_list(categories):
    return "\n".join([ f"- {cat_name}: {cat_desc}" for cat_name, cat_desc in categories ])
