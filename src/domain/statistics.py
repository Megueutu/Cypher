from dataclasses import dataclass

@dataclass
class ExecutionMeasure:
    success:  bool
    elapsed:  float
    function: str
    accessed: list[str]
    
    def out(self):
        return {
            "success"  : self.success,
            "elapsed"  : self.elapsed,
            "function" : self.function,
            "accessed" : self.accessed,
        }
