# Esto es solo una extension del codigo de Eden para el React 
# con la idea de practicar la creación de TOOLS y AGENTES
# en esta version agrego la TOOL evaluate, generalizando un poco lo anterior

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

from dotenv import load_dotenv
load_dotenv()


import ast   # para el tema del parsing de la tupla de numeros --> # Safe way to evaluate literals

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

def find_tool_by_name(tools: List[Tool], tool_name: str) -> Tool:
    for tool in tools:
        if tool.name == tool_name:
            return tool
    raise ValueError(f"Tool wtih name {tool_name} not found")


##############################################################################################
##                                          MAIN                                            ##
##############################################################################################

if __name__ == "__main__":
    print("Hola ReAct LangChain!")

    tools = [get_text_length, multiplica2, math_operation]

    template = """
    Answer the following questions as best you can. You have access to the following tools:

    {tools}
    
    Use the following format:
    
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    
    Action Input: the input to the action

    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
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

    llm = ChatOpenAI(model="gpt-4o-mini",
                     temperature=0, stop=["\nObservation", "Observation"], 
                     callbacks=[AgentCallbackHandler()]
                     )

    intermediate_steps = []

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_str(x["agent_scratchpad"]),
        }
        | prompt
        | llm
        | ReActSingleInputOutputParser()
    )

    input = "Please, calculate the following  expression: 3 * 56.9 / 3 "

    agent_step = ""

    while not isinstance(agent_step, AgentFinish):
        agent_step: Union[AgentAction, AgentFinish] = agent.invoke(
            {
                "input": input,                
                "agent_scratchpad": intermediate_steps,
            }
        )
        print(agent_step)

        if isinstance(agent_step, AgentAction):
            tool_name = agent_step.tool
            tool_to_use = find_tool_by_name(tools, tool_name)
            tool_input = agent_step.tool_input

            # Different parsing for each tool
            if tool_name == "multiplica2":
                tool_input_parsed = eval(tool_input) if isinstance(tool_input, str) else tool_input
                observation = tool_to_use.func(*tool_input_parsed)  # Unpack tuple
            elif tool_name == "math_operation":
                tool_input_cleaned = str(tool_input).strip().strip('"').strip("'").strip("\n")
                observation = tool_to_use.func(tool_input_cleaned)  # Pass cleaned expression
            else:  # Default case (e.g., get_text_length)
                observation = tool_to_use.func(tool_input)

            print(f"{observation=}")
            intermediate_steps.append((agent_step, str(observation)))

    if isinstance(agent_step, AgentFinish):
        print(agent_step.return_values)