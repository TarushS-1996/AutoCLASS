from AutoClass.Agent import Agent
import json
import streamlit as st
import json
from AutoClass.Agent import Agent
# from example import ArithmeticOperations, StringUtils  # Your example classes
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from uuid import uuid4
import random

class StringUtils:
    """
    This class provides a set of methods for common string manipulation operations such as formatting, case conversion, and analysis.
    """

    def __init__(self):
        self.name = "string_utilities"

    def to_upper(self, text):
        '''
        - Description: Converts the input string to uppercase.
        - List of parameters:
            - param text: Input string :type: str
        :return: Uppercase version of the input string :rtype: str
        '''
        return text.upper()

    def to_lower(self, text):
        '''
        - Description: Converts the input string to lowercase.
        - List of parameters:
            - param text: Input string :type: str
        :return: Lowercase version of the input string :rtype: str
        '''
        return text.lower()

    def count_words(self, text):
        '''
        - Description: Counts the number of words in the input string.
        - List of parameters:
            - param text: Input string :type: str
        :return: Total number of words in the input string :rtype: int
        '''
        return len(text.split())

    def reverse_string(self, text):
        '''
        - Description: Reverses the characters in the input string.
        - List of parameters:
            - param text: Input string :type: str
        :return: Reversed string :rtype: str
        '''
        return text[::-1]

    def contains_substring(self, text, substring):
        '''
        - Description: Checks whether the input string contains the specified substring.
        - List of parameters:
            - param text: Input string :type: str
            - param substring: Substring to check :type: str
        :return: True if the substring is found in the text, else False :rtype: bool
        '''
        return substring in text


class ArithmeticOperations:
    """
    This example cass contains a set of methods designed to perform basic arithmetic operations.
    """
    def __init__(self):
        self.name = "example"

    def add(self, a, b):
        '''
        - Description: This method adds two numbers.
        - List of parameters:
            - param a: First number :type: int or float
            - param b: Second number :type: int or float
        :return: Sum of a and b :rtype: int or float
        '''
        return a + b
    

    def subtract(self, a, b):
        '''
        - Description: This method subtracts two numbers.
        - List of parameters:
            - param a: First number :type: int or float
            - param b: Second number :type: int or float
        :return: Difference of a and b :rtype: int or float
        '''
        return a - b
    

    def multiply(self, a, b):
        '''
        - Description: This method multiplies two numbers.
        - List of parameters:
            - param a: First number :type: int or float
            - param b: Second number :type: int or float
        :return: Product of a and b :rtype: int or float
        '''
        return a * b
    

    def divide(self, a, b):
        '''
        - Description: This method divides two numbers.
        - List of parameters:
            - param a: First number :type: int or float
            - param b: Second number :type: int or float
        :return: Quotient of a and b :rtype: int or float
        '''
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
def generate_flow_nodes_and_edges(pipeline, results):
    nodes = []
    edges = []
    used_positions = set()

    for i, cls in enumerate(pipeline.get("classes", [])):
        class_name = cls["class_name"]
        for j, method in enumerate(cls["methods"]):
            node_id = f"{class_name}.{method['method']}"
            label = f"{method['method']}\n({class_name})"
            inputs = method.get("inputs", {})
            content = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
            result = results.get(node_id, "⏳ Not executed")

            # Assign random but spread out positions
            while True:
                pos = (i * 250 + random.randint(0, 50), j * 150 + random.randint(0, 50))
                if pos not in used_positions:
                    used_positions.add(pos)
                    break

            node = StreamlitFlowNode(
                id=node_id,
                pos=pos,
                data={"content": f"{content}\n\nResult: {result}"},
                node_type="default",
                source_position="right",
                target_position="left"
            )
            nodes.append(node)

            for val in inputs.values():
                if isinstance(val, str) and "." in val:
                    edge = StreamlitFlowEdge(
                        id=str(uuid4()),
                        source=val,
                        target=node_id
                    )
                    edges.append(edge)

    return nodes, edges

# ---------------- Streamlit App Setup ---------------- #

st.set_page_config(page_title="🧠 MCP Pipeline UI", layout="wide")
st.sidebar.title("MCP Agent 🔧")

query = st.sidebar.text_area("💬 Enter your natural language query", height=150)
run_btn = st.sidebar.button("🚀 Run Agent")
show_json = st.sidebar.checkbox("📄 Show raw pipeline JSON")

# ---------------- Session State Init ---------------- #

if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
    st.session_state.results = None
    st.session_state.flow_nodes = []
    st.session_state.flow_edges = []

if "should_run_query" not in st.session_state:
    st.session_state.should_run_query = False

# ---------------- Run Trigger ---------------- #

if run_btn and query:
    st.session_state.should_run_query = True
    st.session_state.query_text = query
    st.rerun()

# ---------------- Main Pipeline Logic ---------------- #

if st.session_state.get("should_run_query", False):
    ag = Agent()
    ag.register_class(ArithmeticOperations(), alias="ArithmeticOperations")
    ag.register_class(StringUtils(), alias="StringUtils")

    ag.llm_choose_class_method(query=st.session_state.query_text)
    ag.llm_determine_input_parameters(query=st.session_state.query_text)

    pipeline = ag.get_current_pipeline()
    results = ag.run_pipeline_with_dependencies()

    nodes, edges = generate_flow_nodes_and_edges(pipeline, results)

    st.session_state.pipeline = pipeline
    st.session_state.results = results
    st.session_state.flow_nodes = nodes
    st.session_state.flow_edges = edges

    st.session_state.should_run_query = False
    st.rerun()

# ---------------- Display UI ---------------- #

if st.session_state.pipeline:
    st.header("📊 MCP Pipeline Flow")
    state = StreamlitFlowState(
        nodes=st.session_state.flow_nodes,
        edges=st.session_state.flow_edges
    )
    streamlit_flow("flow", state)

    st.subheader("✅ Execution Results")
    st.json(st.session_state.results)

    if show_json:
        st.subheader("🧾 Raw Pipeline JSON")
        st.json(st.session_state.pipeline)
else:
    st.info("Please enter a query in the sidebar to begin.")