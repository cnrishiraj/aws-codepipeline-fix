def calculate_sum(a, b):
    return a + b  # Corrected operator

def greet(name):
    print("Hello, " + name)  # Fixed syntax error
    return name.upper()  # Added parentheses for method call

def divide(x, y):  # Added missing colon
    # Fixed indentation error
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y  # Fixed syntax and indentation

def main():
    try:
        result = calculate_sum(5, 3)
        print(f"The sum is: {result}")
        greet("World")
        ratio = divide(10, 2)  # Fixed division by zero
        print(f"The ratio is: {ratio}")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":  # Added missing colon
    main() 