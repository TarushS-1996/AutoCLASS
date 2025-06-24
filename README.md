# 🤖 AutoClass: Agentic Method Controller via MCP

**AutoClass** is a modular agent framework powered by the **Model Context Protocol (MCP)** that enables Python classes to self-describe and self-execute. By parsing structured docstrings and routing logic through LLM-powered decisions, AutoClass turns any standard Python class into a composable, query-driven agent interface.

---

## 🚀 Key Features

- 🧠 **Agentic Control via LLM**: Automatically selects and executes methods based on plain-text user queries.
- 📚 **Docstring-Driven Introspection**: Parses structured docstrings to extract method descriptions, input types, and outputs.
- 🔁 **Pipeline Execution**: Supports multi-step execution where methods can depend on results from others.
- 🔍 **Context-Aware Variable Resolution**: Fills in required inputs from the query, context memory, or results of prior steps.
- 📦 **Class-Agnostic**: Register any Python class and gain agentic control with zero custom wrappers.

---

## 🧩 Example Query

Perform the necessary operations for this: 5 * 2 + 6 / 4



AutoClass will:
1. Select the relevant `ArithmeticOperations` methods: `multiply`, `divide`, `add`.
2. Chain them as:
```
multiply(a=5, b=2)
divide(a=6, b=4)
add(a=multiply_result, b=divide_result)```

3. Execute in the correct order and return the final result.

---

## 🛠️ How It Works

1. **Class Registration**:
- You register any Python class via:
  ```python
  agent.register_class(instance, alias="MyClass")
  ```

2. **Structured Docstrings**:
- Each method should have a docstring using this format:
  ```python
  '''
  - Description: Adds two numbers.
  - List of parameters:
      - param a: First number :type: int or float
      - param b: Second number :type: int or float
  :return: Sum of a and b :rtype: int or float
  '''
  ```

3. **LLM-Based Routing**:
- `llm_choose_class_method(query)` determines which class methods are relevant.
- `llm_determine_input_parameters(query)` fills in argument values from the query.

4. **Pipeline Execution**:
- `run_pipeline_with_dependencies()` walks through all methods, resolving dependencies like:
  ```json
  {
    "a": "ArithmeticOperations.multiply"
  }
  ```

---

## 📂 Directory Structure

.
├── AutoClass
│   ├── Agent.py
│   └── ui.py
├── example.py
├── LICENSE.md
├── README.md
└── requirements.txt

---

## 🧪 Quick Start

```bash
git clone https://github.com/yourname/AutoClass.git
cd AutoClass
python3 -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

pip install -r requirements.txt
python example.py
```
---

## 📌 Roadmap
 LLM-powered class and method selection

 Dependency-aware execution engine

 Graph-based method and class selection and execution

 Web frontend or CLI pipeline inspector

---

## 🧠 MCP Philosophy
The Model Context Protocol allows external agents (LLMs, planners, tools) to introspect a class’s capabilities and contextually decide what to do next — making agents that are not just reactive, but strategically adaptive.

---

## 📝 License
MIT License

