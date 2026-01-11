from typing import Union, List
import re
from langchain.agents import tool
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults 


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




