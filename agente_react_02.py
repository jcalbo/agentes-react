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


"""
El problema con multiplica() es que tool_input se pasa como una cadena «(3.14, 4)\n», pero multiplica2() espera dos argumentos numéricos (a y b).
El campo tool_input de AgentAction contiene una representación de cadena similar a una tupla, que debe analizarse antes de pasarla a la función.
"""

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

    tools = [get_text_length, multiplica2]

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

    input = "Cual es la longitud de la palabra: CYBERSEGURIDAD"
    input = "Cuanto es 3.14 multiplicado por 4?"

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

            # To properly unpack the tuple:
            tool_input_parsed = ast.literal_eval(tool_input) if isinstance(tool_input, str) else tool_input
#            observation = tool_to_use.func(str(tool_input))
            observation = tool_to_use.func(*tool_input_parsed)  # Unpack tuple

            print(f"{observation=}")
            intermediate_steps.append((agent_step, str(observation)))

    if isinstance(agent_step, AgentFinish):
        print(agent_step.return_values)