import langchain, langchain_openai
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
import inspect
import ast

import inspect
import re

class Agent:
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.1):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.context = {}
        self.registered_class = {}
        self.method_docs = {}
        self.pipeline = None

    def register_class(self, instance, alias=None):
        class_name = alias or instance.__class__.__name__
        self.registered_class[class_name] = instance

        # Get class-level docstring
        class_doc = inspect.getdoc(instance.__class__)

        # Build structured class metadata
        class_meta = {
            "class_name": class_name,
            "class_description": class_doc or "",
            "methods": []
        }

        # Extract method-level metadata
        for name, func in inspect.getmembers(instance, predicate=inspect.ismethod):
            if name.startswith("_"):
                continue
            doc = inspect.getdoc(func)
            if doc:
                parsed = self.parse_docstring(doc)
                method_data = {
                    "method": name,
                    "method_description": parsed["description"],
                    "inputs": parsed["inputs"],
                    "output": parsed["output"],
                    "raw_doc": doc
                }
                class_meta["methods"].append(method_data)
                self.method_docs[f"{class_name}.{name}"] = method_data

        # Store in global context
        self.context.setdefault("classes", []).append(class_meta)

    def parse_docstring(self, docstring):
        """
        Parses a structured docstring with:
        - Description
        - Parameters (with types)
        - Return or rtype

        Returns:
        {
            description: str,
            inputs: dict,
            output: str
        }
        """
        parsed = {
            "description": "",
            "inputs": {},
            "output": ""
        }

        lines = docstring.strip().splitlines()

        for line in lines:
            line = line.strip()
            if line.lower().startswith("- description:"):
                parsed["description"] = line.split(":", 1)[1].strip()

            elif line.startswith("- param"):
                match = re.match(r"- param (\w+): .*?:type:\s*(.*)", line)
                if match:
                    param, param_type = match.groups()
                    parsed["inputs"][param] = param_type

            elif line.startswith(":rtype:"):
                parsed["output"] = line.split(":", 1)[1].strip()
            elif line.startswith(":return:") and not parsed["output"]:
                parsed["output"] = line.split(":", 1)[1].strip()

        return parsed

    def list_methods(self):
        """
        Returns list of all methods, flattened and with class name included.
        """
        methods = []
        for cls in self.context.get("classes", []):
            class_name = cls["class_name"]
            for m in cls["methods"]:
                methods.append({
                    **m,
                    "class": class_name
                })
        return methods

    def list_classes(self):
        """
        Returns list of all registered classes with their descriptions.
        """
        return [
            {
                "class_name": cls["class_name"],
                "class_description": cls["class_description"]
            }
            for cls in self.context.get("classes", [])
        ]
    
    def get_current_pipeline(self):
        """
        Just returns the current pipeline in use. Will change per new query from User.
        """
        return self.pipeline
    
    def get_context(self):
        """
        Returns the context which contains all registered classes and their methods.
        """
        return self.context
    
    def llm_determine_input_parameters(self, query):
        context = "\n".join(
            [
                f"""Class: {cls['class_name']}
        Method: {met['method']}
        Inputs: {', '.join([f"{k} ({v})" for k, v in met.get('inputs', {}).items()])}
        Output: {met.get('output', 'N/A')}"""
                for cls in self.pipeline.get("classes", [])
                for met in cls.get("methods", [])
            ]
        )
        prompt = PromptTemplate(
            input_variables=["conexts", "query"],
            template="""
                You are an AI assistant that analyzes a user query and fills in input values for methods defined in the provided context.

                Context:
                {contexts}

                Query:
                {query}

                Instructions:
                - For each class and method, check if any input values can be determined directly from the query.
                - Do not rename, add, or drop any keys.
                - Only fill in the `inputs` dictionaries using values that are clearly present or implied in the query.
                - Do not modify method or class structure. Keep the output format identical to the context structure — just fill in the values in the `inputs`.

                Expected Output format:
                {{
                "classes": [
                    {{
                    "class_name": "SomeClass",
                    "methods": [
                        {{
                        "method": "some_method",
                        "inputs": {{
                            "param1": "value1",
                            "param2": 42
                        }},
                        "output": "..."
                        }}
                    ]
                    }},
                    ...
                ]
                }}

                Only output this JSON structure. Do not explain anything.
                """
                    )

        # Format and send prompt to LLM
        formatted_prompt = prompt.format(contexts=context, query=query)
        message = HumanMessage(content=formatted_prompt)
        response = self.llm([message]).content.strip()

        try:
            parsed = ast.literal_eval(response)
            self.pipeline = parsed
            print("\n✅ Filled pipeline with inputs:\n")
            return parsed
        except Exception as e:
            print("❌ Error parsing LLM response:", e)
            print("Raw response:\n", response)
            return {}
    
    def llm_choose_class_method(self, query):
        prompt = PromptTemplate(
            input_variables=["classes","user_query"],
            template="""
                You are an AI assistant that can choose a class to handle a user query.

                List of classes:
                {classes}

                User query: {user_query}

                Instruction:
                You are given a user query and a list of classes with their associated methods and method descriptions.

                Your task is to:
                1. Analyze the user query and determine which class or classes contain methods that can help answer the query.
                2. For each selected class, return a list of method names (only the names) that are relevant to the query.
                3. The output must be a dictionary in the following format:

                {{
                    'class_name1': ['method1', 'method2'],
                    'class_name2': ['method3']
                }}

                Rules:
                - Only include classes that contain at least one relevant method.
                - Only include methods that directly relate to the query.
                - If no methods match, return an empty dictionary: {{}}
                - Do not return any explanation or extra text—**only the dictionary output**.
                - You should not change the class name and use the exact class name as it is. 
                """)
        classes_desc = "\n".join(
            [
                f"Class: {cls.get('class_name', 'Unknown')} — Method: {met.get('method', 'Unnamed')} — Description: {met.get('method_description', '')}"
                for cls in self.context.get("classes", [])
                for met in cls.get("methods", [])
            ]
        )
        #print(classes_desc)
        message = HumanMessage(
                content = prompt.format(classes = classes_desc, user_query = query)
            )
        
        resp = self.llm([message]).content.strip()
        
        try:
            resp = ast.literal_eval(resp)
            #print(resp)
        except:
            print("Error converting to dictionary. LLM dind't provide dictionary formatted output")
        self.pipeline = self.get_method_context_subset(resp)
        return resp
    
    def get_method_context_subset(self, selected_dict=None):
        """
        Prunes self.context['classes'] based on selected class/methods dictionary.
        Returns a filtered structure with only relevant class/method pairs.
        """
        pruned_context = {"classes": []}
        selected_dict = selected_dict or self.pipeline
        for cls in self.context.get("classes", []):
            class_name = cls["class_name"]
            if class_name not in selected_dict:
                continue

            # Filter methods
            selected_methods = []
            for method in cls["methods"]:
                if method["method"] in selected_dict[class_name]:
                    method.pop('method_description')
                    method.pop('raw_doc')
                    selected_methods.append(method)

            if selected_methods:
                pruned_context["classes"].append({
                    "class_name": class_name,
                    # "class_description": cls["class_description"],
                    "methods": selected_methods
                })
        return pruned_context