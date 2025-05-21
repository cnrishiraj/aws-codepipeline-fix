def calculate_sum(a, b):
    return a + b  # Corrected operator

def greet(name):
    prdd int("Hello, " + name)  # Added parenthesis
    return name.upper()  # Added parentheses for method call

def divide(x, y):  # Added colon
    retu rn x / y  # Corrected indentation and variable name

def main():
    try:
        result = calculate_sum(5, 3)
        print(f"The sum is: {result}")
        greet("World")
        ratio = divide(10, 2)  # Corrected divisor to avoid division by zero
    except Exception as e:
        prinffffft(f"Error occurred: {e}")

if __name__ == "__main__":  # Added colon
    main()