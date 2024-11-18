from dotenv import load_dotenv
import os
import nodes
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from typing import Annotated, TypedDict, List, Union, Dict
from langchain.docstore.document import Document
from langgraph.graph.message import add_messages
import warnings

warnings.filterwarnings('ignore')

load_dotenv("config.env")

class GrievanceState(TypedDict):
    categories: List[str]
    fields: dict

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        context: context
    """
    dlg_state: GrievanceState
    messages: Annotated[list, add_messages]
    transformed_grievance: str
    input_msg: str
    lang: str
    Quesloops: int
    classified_all: bool
    askUser: bool
    askDetails:bool

def make_workflow():

    workflow = StateGraph(GraphState)

    # Nodes
    workflow.add_node("find_lang", nodes.find_language)

    workflow.add_node("transform", nodes.transform_grievance)

    workflow.add_node("casual_response", nodes.casual_generate)
    
    workflow.add_node("category_classifier", nodes.classify_category)
    workflow.add_node("question_generator_classify", nodes.question_generator_classify)

    workflow.add_node("field_extractor", nodes.extract_field)
    workflow.add_node("question_generator_field", nodes.question_generator_fields)
    workflow.add_node("ask_details", nodes.ask_detail)
    workflow.add_node("final_response_generator", nodes.generate_final_response)


    # Build graph
    workflow.add_edge(START, "find_lang")

    workflow.add_edge("find_lang", "transform")


    workflow.add_conditional_edges(
        "transform",
        nodes.route_question,
        {
            "classify": "category_classifier",
            "casual":"casual_response"
        },
    )

    workflow.add_conditional_edges(
        "category_classifier",
        nodes.decide_to_ask_or_classify,
        {
            "asktoUser": "question_generator_classify",
            "further_classify": "category_classifier",
            "reached_leaf": "field_extractor"
        },
    )

    workflow.add_conditional_edges(
        "field_extractor",
        nodes.decide_to_proceed,
        {
            "asktoUser": "question_generator_field",
            "askDetails": "ask_details",
        },
    )

    workflow.add_conditional_edges(
        "ask_details", 
        nodes.decide_to_end,
        {
            "done":"final_response_generator",
            "ask":END
        })
    workflow.add_edge("question_generator_classify", END)
    workflow.add_edge("question_generator_field", END)
    
    workflow.add_edge("final_response_generator", END)

    workflow.add_edge("casual_response", END)
    

    return workflow
