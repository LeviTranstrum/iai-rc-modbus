class Error:
    def __init__(self, msg):
        self.msg = str(msg)
        print(msg)

    def wrap(self, msg: str):
        self.msg = f'{msg}:\n    {self.msg}' 
        print(msg)
        return self
    
    def __str__(self) -> str:
        return f'Error: {self.msg}'
    
    def __repr__(self) -> str:
        return f'Error: {self.msg}'