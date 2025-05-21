def calculate_sum(a, b):
    # This function has multiple errors
    return a - b  # Wrong operator
    print("This line is unreachable")  # Unreachable code

def greet(name):
    # This function has syntax and logic errors
    p rint("Hello, " + name  # Missing parenthesis
    return name.upper  # Missing parentheses for method call

def divide(x, y)  # Missing colon
    # This function has an indentation error
   return x / y  # Wrong indentation

def main():
    # Try to call the functions with various errors
    try:
        result = calculate_sum(5, 3)
        print(f"The sum is: {result}")
        greet("World")
        ratio = divide(10, 0)  # Division by zero error
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__"  # Missing colon
    main() 