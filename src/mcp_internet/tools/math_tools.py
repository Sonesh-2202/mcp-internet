"""
Math Tools - Safe mathematical expression evaluator.

Uses Python's ast module for safe evaluation without exec/eval.
"""

import logging
import ast
import operator
import math

logger = logging.getLogger(__name__)

# Safe operators
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Safe math functions
MATH_FUNCTIONS = {
    'abs': abs,
    'round': round,
    'min': min,
    'max': max,
    'sum': sum,
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'log': math.log,
    'log10': math.log10,
    'log2': math.log2,
    'exp': math.exp,
    'floor': math.floor,
    'ceil': math.ceil,
    'factorial': math.factorial,
    'pow': pow,
    'pi': math.pi,
    'e': math.e,
}


class SafeEvaluator(ast.NodeVisitor):
    """Safely evaluate mathematical expressions."""
    
    def visit_Expression(self, node):
        return self.visit(node.body)
    
    def visit_Constant(self, node):
        if isinstance(node.value, (int, float, complex)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value}")
    
    def visit_Num(self, node):  # For older Python versions
        return node.n
    
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(left, right)
    
    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op = OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(operand)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id.lower()
            if func_name in MATH_FUNCTIONS:
                func = MATH_FUNCTIONS[func_name]
                args = [self.visit(arg) for arg in node.args]
                
                # Handle constants (pi, e)
                if callable(func):
                    return func(*args)
                else:
                    return func
            raise ValueError(f"Unknown function: {func_name}")
        raise ValueError("Invalid function call")
    
    def visit_Name(self, node):
        name = node.id.lower()
        if name in MATH_FUNCTIONS:
            value = MATH_FUNCTIONS[name]
            if not callable(value):
                return value
        raise ValueError(f"Unknown variable: {node.id}")
    
    def visit_Tuple(self, node):
        return tuple(self.visit(el) for el in node.elts)
    
    def visit_List(self, node):
        return [self.visit(el) for el in node.elts]
    
    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression: {type(node).__name__}")


def safe_eval(expression: str) -> float | int:
    """Safely evaluate a mathematical expression."""
    try:
        tree = ast.parse(expression, mode='eval')
        evaluator = SafeEvaluator()
        return evaluator.visit(tree)
    except SyntaxError as e:
        raise ValueError(f"Syntax error: {e}")


async def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.
    
    Args:
        expression: Mathematical expression to evaluate
                   Supports: +, -, *, /, //, %, **
                   Functions: sqrt, sin, cos, tan, log, log10, exp, 
                             floor, ceil, abs, round, min, max, factorial
                   Constants: pi, e
        
    Returns:
        The result of the calculation
        
    Examples:
        calculate("2 + 2") -> 4
        calculate("sqrt(16)") -> 4.0
        calculate("sin(pi/2)") -> 1.0
        calculate("15% of 200") -> 30.0 (interprets "X% of Y")
    """
    if not expression.strip():
        return "❌ Error: Please provide a mathematical expression."
    
    original_expression = expression
    
    # Handle common natural language patterns
    expression = expression.lower().strip()
    
    # Handle "X% of Y" -> (X/100) * Y
    import re
    percent_of = re.match(r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)', expression)
    if percent_of:
        percent = float(percent_of.group(1))
        value = float(percent_of.group(2))
        result = (percent / 100) * value
        return f"""🔢 **Calculation Result**
{'=' * 40}

📝 Expression: {original_expression}
✨ Result: {result:,.4g}

💡 ({percent}% of {value} = {result:,.4g})
"""
    
    # Handle percentage conversions: "25%" -> 0.25
    expression = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'(\1/100)', expression)
    
    # Replace ^ with ** for exponents
    expression = expression.replace('^', '**')
    
    # Replace × and ÷ with * and /
    expression = expression.replace('×', '*').replace('÷', '/')
    
    try:
        result = safe_eval(expression)
        
        # Format the result nicely
        if isinstance(result, float):
            if result.is_integer():
                result_str = f"{int(result):,}"
            elif abs(result) < 0.0001 or abs(result) > 1e10:
                result_str = f"{result:.6e}"
            else:
                result_str = f"{result:,.10g}"
        else:
            result_str = f"{result:,}" if isinstance(result, int) else str(result)
        
        return f"""🔢 **Calculation Result**
{'=' * 40}

📝 Expression: {original_expression}
✨ Result: {result_str}
"""
        
    except ValueError as e:
        return f"❌ Error: {str(e)}"
    except ZeroDivisionError:
        return "❌ Error: Division by zero"
    except OverflowError:
        return "❌ Error: Result is too large"
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        return f"❌ Error: Unable to evaluate expression. Please check the syntax."
