import streamlit as st
from typing import Union, List
import re
import ast

from langchain.agents import tool
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import Tool
from langchain.tools.render import render_text_description
from langchain_community.tools.tavily_search import TavilySearchResults

from callbacks import AgentCallbackHandler
from dotenv import load_dotenv

load_dotenv()


from mis_tools import get_text_length, multiplica2, math_operation, web_search_tool, find_tool_by_name


# ---- Define the tools ----



# ---- Setup Streamlit UI ----

st.set_page_config(page_title="Agente LangChain con Memoria", layout="wide")
st.title("🤖 Agente LangChain REACT con Memoria")

st.markdown("### Chat con un Agente de IA con Memoria Conversacional! 🚀")
st.markdown("Este agente recuerda las conversaciones anteriores. Escribe tu pregunta y pulsa Enter.")

# ---- Initialize Memory ----
if "memory" not in st.session_state:
    # Inicializar la memoria conversacional
    st.session_state["memory"] = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=False  # Retornar como string, no como lista de mensajes
    )

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ---- Define Agent ----

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

Previous conversation history (use this context to understand references to previous messages):
{chat_history}

Current Question: {input}
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

# Pipeline del agente - NO acceder a st.session_state dentro de lambdas
# El chat_history se pasa directamente cuando se invoca el agente
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(x["agent_scratchpad"]),
        "chat_history": lambda x: x.get("chat_history", ""),  # Obtener del input, no de session_state
    }
    | prompt
    | llm
    | ReActSingleInputOutputParser()
)

# ---- User Input Box ----
user_input = st.text_input("Tu pregunta:", key="input")
st.markdown("### Chat con un Agente de IA con Memoria! 🚀")
if user_input:
    with st.spinner("Pensando..."):
        intermediate_steps = []
        agent_step = ""

        while not isinstance(agent_step, AgentFinish):
            # Obtener el historial actual de la memoria
            memory_vars = st.session_state["memory"].load_memory_variables({})
            chat_history = memory_vars.get("chat_history", "")
            
            agent_step: Union[AgentAction, AgentFinish] = agent.invoke(
                {
                    "input": user_input,                
                    "agent_scratchpad": intermediate_steps,
                    "chat_history": chat_history,
                }
            )
            
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
                        observation = tool_to_use.run(tool_input)  # Use `.run()` for TavilySearchResults

                    else:  # Default case (e.g., get_text_length)
                        observation = tool_to_use.func(tool_input)

                except Exception as e:
                    observation = f"Tool execution failed: {str(e)}"

                intermediate_steps.append((agent_step, str(observation)))

                # Fallback: If no answer was found, use web search
                if "I don't know" in str(observation) or "Tool execution failed" in str(observation):
                    observation = web_search_tool.run(user_input)  # Call TavilySearchResults tool

        if isinstance(agent_step, AgentFinish):
            agent_response = agent_step.return_values["output"]
            
            # Almacenar historial de conversación para visualización
            st.session_state["messages"].append({"role": "user", "content": user_input})
            st.session_state["messages"].append({"role": "assistant", "content": agent_response})

            # Actualizar memoria con la nueva interacción
            # Esto permite que el agente recuerde conversaciones previas
            st.session_state["memory"].save_context(
                {"input": user_input},
                {"output": agent_response}
            )

# ---- Display Chat History ----
st.markdown("## Historial de Conversación")
for message in st.session_state["messages"]:
    if message["role"] == "user":
        st.markdown(f"👤 **Tú:** {message['content']}")
    else:
        st.markdown(f"🤖 **Agente:** {message['content']}")

# Mostrar información de memoria (opcional, para depuración)
with st.expander("🔍 Información de Memoria (Debug)"):
    memory_vars = st.session_state["memory"].load_memory_variables({})
    st.text(f"Memoria activa: {len(memory_vars.get('chat_history', '')) > 0}")
    if memory_vars.get("chat_history"):
        st.text_area("Contenido de la memoria:", memory_vars["chat_history"], height=200)

