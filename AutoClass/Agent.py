import langchain, langchain_openai
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate
import inspect

import inspect
import re

class Agent:
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        #self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.context = {}
        self.registered_class = {}
        self.method_docs = {}

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
    
    def get_context(self):
        """
        Returns the context which contains all registered classes and their methods.
        """
        return self.context
    
    def llm_choose_class(self, query):
        prompt = PromptTemplate(
            input_variables=["classes","user_query"],
            template="""

            You are an AI assistant that can choose a class to handle a user query.
            
            List of classes:
            {classes}
            
            User query: {user_query}
            
            Instructions:
            - Choose the most relevant class from the list.
            - If a class is not relevant do not include it in the answer
            - You are provided with classes and their descriptions about what the classes are supposed to do. 
            - The expected response is just a list of class names. Not their desctiption. 
            - The expected output is a list of type string representing the class names.

            Example:
            User query: "How do I add two numbers?"
            Classes: ["example"]
            """


        )
        classes_desc = "\n".join(
            [f"{cls['class_name']}: {cls['class_description']}" for cls in self.context.get("classes", [])]
        )
        message = HumanMessage(
                content = prompt.format(user_query = query, classes = classes_desc)
            )
        
        print(message.content)