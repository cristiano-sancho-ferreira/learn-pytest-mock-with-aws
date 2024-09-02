class Function:
    
    def my_function(x: int):
        if not isinstance(x, int):
            raise ValueError("Variable x not is int")
        return x * 2