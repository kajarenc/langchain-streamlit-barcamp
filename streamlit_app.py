from pathlib import Path

import streamlit as st

st.set_page_config(page_title="MRKL", page_icon="🦜", layout="wide")
st.title("BARCAMP LANGCHAIN + STREMLIT DEMO!!!")

openai_api_key = st.secrets["openai_api_key"]
serpapi_api_key = st.secrets["serpapi_api_key"]

# LangChain imports
from langchain import (
    LLMMathChain,
    OpenAI,
    SerpAPIWrapper,
    SQLDatabase,
    SQLDatabaseChain,
)
from langchain.agents import AgentType
from langchain.agents import initialize_agent, Tool

from langchain.callbacks.streamlit import StreamlitCallbackHandler

# Tools setup
DB_PATH = (Path(__file__).parent / "Chinook.db").absolute()

llm = OpenAI(temperature=0, openai_api_key=openai_api_key, streaming=True)
search = SerpAPIWrapper(serpapi_api_key=serpapi_api_key)
llm_math_chain = LLMMathChain(llm=llm, verbose=True)
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events. You should ask targeted questions",
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math",
    ),
    Tool(
        name="Chinook DB",
        func=db_chain.run,
        description="useful for when you need to answer questions about Chinook database. Input should be in the form of a question containing full context",
    ),
]
print("JJJJJJJJ")

# Initialize agent
mrkl = initialize_agent(
    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,
)
# To run the agent, use `mrkl.run(mrkl_input)`

if "latest_user_input" not in st.session_state:
    st.session_state["latest_user_input"] = ""

if "latest_user_input_executed" not in st.session_state:
    st.session_state["latest_user_input_executed"] = False

if "dirty_state" not in st.session_state:
    st.session_state["dirty_state"] = "initial"

user_input = st.chat_input("ASK SOMETHING!")

if user_input:
    st.session_state["latest_user_input"] = user_input
    st.session_state["latest_user_input_executed"] = False

if st.session_state["dirty_state"] == "dirty":
    st.session_state["dirty_state"] = "initial"
    for i in range(10):
        st.empty()
    st.experimental_rerun()

if not st.session_state["latest_user_input_executed"] and st.session_state["dirty_state"] == "initial":
    if st.session_state["latest_user_input"]:
        st.chat_message("user").write(st.session_state["latest_user_input"])

        result_container = st.chat_message("assistant")
        streamlit_callback_handler = StreamlitCallbackHandler(result_container)

        answer = mrkl.run(st.session_state["latest_user_input"], callbacks=[streamlit_callback_handler])
        result_container.write(f"**Answer:** {answer}")
        st.session_state["dirty_state"] = "dirty"
        st.session_state["latest_user_input_executed"] = True

print("LAST COMMAND OF THE SCRIPT!!")
print(st.session_state)

for i in range(10):
    st.empty()