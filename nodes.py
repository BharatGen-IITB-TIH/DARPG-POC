import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)
import json
from utils import make_prompt, format_messages, detect_language, extract_standalone_question, get_category, generate_category_list
from prompts import (
    prompts,
    field_extraction_examples
)
from all_fields_data import fields_data
from fuzzywuzzy import process # type: ignore
from mistral_ccm import CCM_mistral
import numpy as np
from typing import List
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import warnings
import re
warnings.filterwarnings('ignore')
import torch

llm = CCM_mistral()

with open("ministries_data_desc.json", 'r') as file:
    data = json.load(file)
fields_data = {key.lower(): value for key, value in fields_data.items()}
### Find User query language--------------------------------------------------------------------

def find_language(state):
    """
    Find the language of the input query.

    Args:
        state (dict): The current graph state
    
    Returns:
        state (dict): Updates State with the user's language.
    """

    query = state["input_msg"]
    lang = detect_language(query)

    if state["dlg_state"] is None:
        dlg_state = {"ministry": "", "categories": [], "fields": {}}
    else:
        dlg_state = state["dlg_state"]


    return {"messages": [HumanMessage(query)], "lang": lang, "dlg_state" : dlg_state, "askUser":False}


### Transform----------------------------------------------------------------------------------
transform_prompt = make_prompt(prompts["transform"]["system"], prompts["transform"]["human"])

question_rewriter = transform_prompt | llm | StrOutputParser()

def transform_grievance(state):
    """
    Transform the grievance to produce a better grievance.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates state with a re-phrased grievance.
    """
    grievance = state["messages"][-1].content
    messages = state["messages"]
    chat_history = format_messages(messages[:-1])

    if state.get("Quesloops") is None:
        state["Quesloops"] = 0

    transformed_grievance = grievance
    if len(messages) > 1:
        transformed_grievance = question_rewriter.invoke({"question": grievance, "chat_history":chat_history})

    transformed_grievance = extract_standalone_question(transformed_grievance)

    return {"transformed_grievance": transformed_grievance, "Quesloops": state["Quesloops"]}


### Category Classifier---------------------------------------------------------------------------------------
category_prompt = make_prompt(prompts["classify_category"]["system"], prompts["classify_category"]["human"])

category_classifier = category_prompt | llm

def classify_category(state):
    """
    Classify the category of the grievance.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates the category_path key in dialog state.
    """

    transformed_grievance = state["transformed_grievance"]
    dlg_state = state["dlg_state"]
    category_path = dlg_state["categories"]
    askUser = False
    classified_all = False

    categories_desc = []
    if len(category_path) == 0:
        for i in data:
            categories_desc.append((i["Ministry"], i["Ministry_Desc"])) 

    else:
        ministry = category_path[0]
        high_lev_obj = None
        for obj in data:
            if obj["Ministry"] == ministry:
                high_lev_obj = obj
                break

        low_lev_obj = get_category(high_lev_obj, category_path[1:])
        
        if "Categories" in low_lev_obj.keys():
            for i in low_lev_obj["Categories"]:
                categories_desc.append((i["Category_Name"], i["Category_Desc"]))
    
    if len(categories_desc) != 0:
        total_categories = generate_category_list(categories_desc)

        cat = category_classifier.invoke({"total_categories": total_categories, "grievance": transformed_grievance})
    
        try:
            json_cat = json.loads(cat.content)
            cat = json_cat["category"]

            if "Not classified" in cat:
                askUser = True
            
            else:
                categories_list = [i[0] for i in categories_desc]
                closest_match, score = process.extractOne(cat, categories_list)
                category_path.append(closest_match)
        
        except Exception as e:
            print("In classify_category", e)
    
        dlg_state["categories"] = category_path

        return {"dlg_state" : dlg_state, "askUser": askUser, "classified_all": classified_all}
    
    else:
        classified_all = True
        return {"dlg_state":dlg_state, "classified_all": classified_all, "askUser": askUser}



### Fields Identifier-----------------------------------------------------------------------------------------
fields_prompt = make_prompt(prompts["extract_field"]["system"], prompts["extract_field"]["human"])

fields_extracter = fields_prompt | llm

def extract_field(state):
    """
    Extract the fields from a given query.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates the dlg_state key in graph.
    """

    transformed_grievance = state["transformed_grievance"]
    dlg_state = state["dlg_state"]
    category_path = dlg_state["categories"]

    ministry = category_path[0]
    high_lev_obj = None
    for obj in data:
        if obj["Ministry"] == ministry:
            high_lev_obj = obj
            break

    all_fields = get_category(high_lev_obj, category_path[1:])
    all_fields = {key.lower(): value for key, value in all_fields.items()}

    try:
        all_fields.pop('Text of grievance (Remarks)'.lower())
        all_fields.pop('Attach relevant/supporting documents (if any)Only PDF file upto 4MB is allowed.'.lower()) 
    except:
        print("In extract_field No keys found (for text and attachement)") 

    
    fields_with_info = ""
    for field in all_fields:
        field_desc = fields_data[field]["field_desc"]
        fields_with_info += f"{field}: {field_desc}\n"

    fields = fields_extracter.invoke({"field_info": fields_with_info, "field_extraction_examples": field_extraction_examples, "grievance": transformed_grievance})
    
    try:
        fields = json.loads(fields.content)

    except Exception as e:
        fields=  {}
        print(e)
    
    fields = {key.lower(): value for key, value in fields.items() if not (value is None or (type(value) == str and value.lower() in ["not provided", "not specified", "n/a", "unknown", "not given"]))}

    dlg_state["fields"].update(fields)

    return {"dlg_state" : dlg_state, "classified_all": True}



# Question Generator with Fields-----------------------------------------------------------------------------
ques_prompt_fields = make_prompt(prompts["question_generate_fields"]["system"], prompts["question_generate_fields"]["human"])

q_generator_fields = ques_prompt_fields | llm | StrOutputParser()

def question_generator_fields(state):
    """
    Generate the counter question based on missing fields.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a counter question.
    """
    if state["Quesloops"] is None:
        state["Quesloops"] = 0

    state["Quesloops"] = state["Quesloops"] + 1

    dlg_state = state["dlg_state"]
    category_path = dlg_state["categories"]
    curr_fields = dlg_state["fields"]

    ministry = category_path[0]
    high_lev_obj = None
    for obj in data:
        if obj["Ministry"] == ministry:
            high_lev_obj = obj
            break

    all_fields = get_category(high_lev_obj, category_path[1:])
    all_fields = {key.lower(): value for key, value in all_fields.items()}

    try:
        all_fields.pop('Text of grievance (Remarks)'.lower())
        all_fields.pop('Attach relevant/supporting documents (if any)Only PDF file upto 4MB is allowed.'.lower()) 
    except:
        print("In ques_gen_fields No keys found (for text and attachement)") 

    missing_fields = []
    all_fields_keys = {key.lower() for key in all_fields.keys()}
    for i in all_fields_keys:
        if i not in curr_fields.keys():
            missing_fields.append(i)

    field_info = ""
    for i in missing_fields:
        field_desc = fields_data[i]["field_desc"]
        field_info += f"{i} : {field_desc}\n"

    new_question = q_generator_fields.invoke({"field_info": field_info})
    new_question = new_question.replace("\"", "")

    return {"Quesloops": state["Quesloops"], "messages": [AIMessage(new_question)], "askUser": False}



# Question Generator with Classify-----------------------------------------------------------------------------
ques_prompt_classify = make_prompt(prompts["question_generate_classify"]["system"], prompts["question_generate_classify"]["human"])

q_generator_classify = ques_prompt_classify | llm | StrOutputParser()

def question_generator_classify(state):
    """
    Generate the counter question based on categories to aid classification.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a counter question.
    """
    if state["Quesloops"] is None:
        state["Quesloops"] = 0

    state["Quesloops"] = state["Quesloops"] + 1

    dlg_state = state["dlg_state"]
    category_path = dlg_state["categories"]

    categories_desc = []
    if len(category_path) == 0:
        for i in data:
            categories_desc.append((i["Ministry"], i["Ministry_Desc"]))
    else: 
        ministry = category_path[0]
        high_lev_obj = None
        for obj in data:
            if obj["Ministry"] == ministry:
                high_lev_obj = obj
                break

        low_lev_obj = get_category(high_lev_obj, category_path[1:])
        
        if "Categories" in low_lev_obj.keys():
            for i in low_lev_obj["Categories"]:
                categories_desc.append((i["Category_Name"], i["Category_Desc"]))
    
    total_categories = generate_category_list(categories_desc)

    new_question = q_generator_classify.invoke({"total_categories": total_categories, "grievance": state["transformed_grievance"]})
    new_question = new_question.replace("\"", "")

    return {"Quesloops": state["Quesloops"], "messages": [AIMessage(new_question)], "askUser": False}

### Ask Details from User------------------------------------------------------------------------------------
ask_details_prompt = make_prompt(prompts["ask_details"]["system"], prompts["ask_details"]["human"], True)

detail_generator = ask_details_prompt | llm | StrOutputParser()

def ask_detail(state):
    """
    Ask the details from user about grievance if there is no details.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates the messages list with new message. 
    """

    transformed_grievance = state["transformed_grievance"]

    res = detail_generator.invoke({"grievance": transformed_grievance})
    res = res.replace("\"", "")
    
    if "sufficient details" in res.lower():
        return {"askDetails": False} 
    
    else:
        return {"messages": [AIMessage(res)], "askDetails": True}



### Casual response Generator--------------------------------------------------------------------------------
casual_prompt = make_prompt(prompts["casual_generate"]["system"], prompts["casual_generate"]["human"], True)

cas_ans_generator = casual_prompt | llm | StrOutputParser()

def casual_generate(state):
    """
    Generates LLM response.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates the messages list with new message 
    """
    question = state["messages"][-1].content
    messages = state["messages"]

    generation = cas_ans_generator.invoke({"chat_history":messages[:-1], "question": question})

    generation = generation.replace("\"", "")

    return {"messages":[AIMessage(generation)], "Quesloops":0}



### Final response Generator-------------------------------------------------------------------------------------------
final_prompt = make_prompt(prompts["final_generate"]["system"], prompts["final_generate"]["human"], True)

final_ans_generator = final_prompt | llm | StrOutputParser()

def generate_final_response(state):
    """
    Generate final LLM response

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates the messages list with new message
    """
    tf_griev = state["transformed_grievance"]
    dlg_state = state["dlg_state"]

    generation = final_ans_generator.invoke({"grievance": tf_griev, "categories": dlg_state["categories"]})
    
    generation = generation.replace("\"", "")

    # return {"messages":[AIMessage(generation)], "Quesloops":0, "classified_all": False, "attachments": []}
    return {"messages":[AIMessage(generation)], "Quesloops":0, "classified_all": False, "askUser": False}


### Router and Decider (Function for Conditional Edges)-------------------------------------------------------------
router_prompt = make_prompt(prompts["route"]["system"], prompts["route"]["human"])

ques_router = router_prompt | llm | StrOutputParser()

def route_question(state):
    """
    Route question to web search or classification.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    transformed_grievance = state["transformed_grievance"]
    
    source = ques_router.invoke({"question": transformed_grievance})
    
    if "classify" in source.lower():
        return "classify"
    
    else:
        return "casual"



def decide_to_ask_or_classify(state):
    """
    Determines whether
    - to ask user for additional information for classification
    - LLM has already classified and we need to further classify
    - classification completed move to field extraction

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """
    
    flag = state["classified_all"]
    ask_user = state["askUser"]

    if flag == True:
        return "reached_leaf"
    elif ask_user == True:
        return "asktoUser"
    else:
        return "further_classify"

def decide_to_proceed(state):
    """
    Determines whether all fields are extracted.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    dlg_state = state["dlg_state"]
    category_path = dlg_state["categories"]
    curr_fields = dlg_state["fields"]

    ministry = category_path[0]
    high_lev_obj = None
    for obj in data:
        if obj["Ministry"] == ministry:
            high_lev_obj = obj
            break
    

    all_fields = get_category(high_lev_obj, category_path[1:])
    all_fields = {key.lower(): value for key, value in all_fields.items()}


    try:
        all_fields.pop('Text of grievance (Remarks)'.lower())
        all_fields.pop('Attach relevant/supporting documents (if any)Only PDF file upto 4MB is allowed.'.lower()) 
    except:
        print("In decide_to_end No keys found (for text and attachement)")

    missing_fields = []
    all_fields_keys = {key.lower() for key in all_fields.keys()}
    for i in all_fields_keys:
        if i not in curr_fields.keys():
            missing_fields.append(i)
    
    if len(missing_fields) == 0:
        return "askDetails"
    elif len(missing_fields) > 0:
        return "asktoUser"

def decide_to_end(state):
    """
    Routes to final response generator or ask details.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    askDetails = state["askDetails"]

    if askDetails == True:
        return "ask"
    elif askDetails == False:
        return "done"