from AutoClass.Agent import Agent

class example:
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
    ex = example()
    ag = Agent()
    ag.register_class(ex, alias="example")
    methods = ag.list_methods()
    classes = ag.list_classes()
    ag.llm_choose_class("How do I add two numbers?")
