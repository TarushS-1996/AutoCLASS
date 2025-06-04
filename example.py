from AutoClass.Agent import Agent
import json

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
    

if __name__ == "__main__":
    query = input("Query")
    ex = ArithmeticOperations()
    st = StringUtils()
    ag = Agent()
    ag.register_class(ex, alias="ArithmeticOperations")
    ag.register_class(st, alias='StringUtils')
    methods = ag.list_methods()
    classes = ag.list_classes()
    ag.llm_choose_class_method(query=query)
    ag.llm_determine_input_parameters(query = query)
    print(json.dumps(ag.get_current_pipeline(), indent = 4))

