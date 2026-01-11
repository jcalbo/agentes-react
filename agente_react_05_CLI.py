
from typing import Union, List
import re

from langchain.agents import tool
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish

from langchain.tools import Tool
from langchain.tools.render import render_text_description

from callbacks import AgentCallbackHandler

# Incluimos la busqueda con TAVILY
from langchain_community.tools.tavily_search import TavilySearchResults

from dotenv import load_dotenv
load_dotenv()

import ast   # para el parsing de la tupla de numeros

@tool
def get_text_length(text: str) -> int:
    """
    Description: Returns the length of a text by characters
    Input: text: str
    Output: int
    Example:
        Input: "Hello"
        Output: 5
    """
    print(f"get_text_length enter with {text=}")
    text = text.strip("'\n").strip(
        '"'
    )  # stripping away non alphabetic characters just in case

    return len(text)

@tool
def multiplica2(a:Union[float, int], b:Union[float, int]) -> float:
    """
    Description: Multiply two numbers, they can be integers or float numbers
    Input: a: Union[float, int], b: Union[float, int]
    Output: float
    Example:
        Input: (3.14, 4)
        Output: 12.56
    """
    return a*b


def math_operation_old(expression: str) -> float:
    """
    Evaluates a mathematical expression given as a string.
    Supports operations like addition, subtraction, multiplication, and division.
    Example: "3.14 * 4", "10 / 2", "2 ** 3"
    """
    return eval(expression)  # Use eval to evaluate math expressions


@tool
def math_operation(expression: str) -> float:
    """
    Description: Evaluates a mathematical expression given as a string.
    Input: expression: str
    Output: float
    Example:
        Input: "3.14 * 4"
        Output: 12.56
    Supports operations like addition, subtraction, multiplication, division, and exponentiation.
    """
    # Remove unwanted characters like extra quotes or newlines
    expression = expression.strip().strip('"').strip("'").strip("\n")

    # Validate input: only allow numbers, operators, and spaces
    if not re.match(r'^[\d\s+\-*/().]+$', expression):
        raise ValueError(f"Invalid characters in expression: {expression}")

    return eval(expression)  # Safe evaluation of the cleaned expression


# Initialize Tavily search tool with k=3 (fetch top 3 results)
# Since TavilySearchResults is already a LangChain tool, we don't need to wrap it in a @tool decorator.
web_search_tool = TavilySearchResults(k=3)

def find_tool_by_name(tools: List[Tool], tool_name: str) -> Tool:
    for tool in tools:
        if tool.name == tool_name:
            return tool
    raise ValueError(f"Tool with name {tool_name} not found")




##############################################################################################
##                                          MAIN                                            ##
##############################################################################################

if __name__ == "__main__":
    print("--------------------- LangChain con REACT  -------------------------------\n\n")
    print('En que puedo ayudarte? Envia tu pregunta. Para terminar envia "END".')

    tools = [get_text_length, multiplica2, math_operation, web_search_tool]

    template = """
    Answer the following questions as best you can. You have access to the following tools:

    {tools}
    
    Use the following format:
    
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of the following [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this sequence of Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    
    Begin!
    
    Question: {input}
    Thought: {agent_scratchpad}
    """

    prompt = PromptTemplate.from_template(template=template).partial(
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools]),
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0, 
        stop=["\nObservation", "Observation"], 
        callbacks=[AgentCallbackHandler()]
    )

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_str(x["agent_scratchpad"]),
        }
        | prompt
        | llm
        | ReActSingleInputOutputParser()
    )

    while True:
        # Get user input
        user_input = input("\nUsuario (o sea tu): ")
        
        # Exit if the user types "END"
        if user_input.strip().upper() == "END":
            print("Saliendo del agente de LangChain...")
            break

        intermediate_steps = []
        agent_step = ""

        

        while not isinstance(agent_step, AgentFinish):
            agent_step: Union[AgentAction, AgentFinish] = agent.invoke(
                {
                    "input": user_input,                
                    "agent_scratchpad": intermediate_steps,
                }
            )
            print("---------------------------------------------------------------------")
            print(f"---- len(intermediate_steps): {len(intermediate_steps)}")
            print(f"---- agent step: {agent_step}")

            if isinstance(agent_step, AgentAction):
                tool_name = agent_step.tool
                tool_to_use = find_tool_by_name(tools, tool_name)
                tool_input = agent_step.tool_input

                try:
                    # Different parsing for each tool
                    if tool_name == "multiplica2":
                        tool_input_parsed = eval(tool_input) if isinstance(tool_input, str) else tool_input
                        observation = tool_to_use.func(*tool_input_parsed)  # Unpack tuple

                    elif tool_name == "math_operation":
                        tool_input_cleaned = str(tool_input).strip().strip('"').strip("'").strip("\n")
                        observation = tool_to_use.func(tool_input_cleaned)  # Pass cleaned expression

                    elif tool_name == "tavily_search_results_json":  # Web search tool
                        print("Using Tavily web search tool...")
                        observation = tool_to_use.run(tool_input)  # Use `.run()` for TavilySearchResults

                    else:  # Default case (e.g., get_text_length)
                        observation = tool_to_use.func(tool_input)

                except Exception as e:
                    observation = f"Tool execution failed: {str(e)}"

                print(f"{observation=}")
                intermediate_steps.append((agent_step, str(observation)))

                # Fallback: If no answer was found, use web search
                if "I don't know" in str(observation) or "Tool execution failed" in str(observation):
                    print("Agent could not answer. Using web_search as fallback.")
                    observation = web_search_tool.run(user_input)  # Call TavilySearchResults tool
                    print(f"Web Search Result: {observation}")        

        if isinstance(agent_step, AgentFinish):
            print("\nAgent Final Answer:", agent_step.return_values)
