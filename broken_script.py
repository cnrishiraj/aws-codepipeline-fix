def calculate_sum(a, b):
    # This function has an error - it should be a + b
    return a - b

def greet(name):
    # This function has a syntax error - missing parenthesis
    print("Hello, " + name
    
def main():
    # Try to call the functions
    try:
        result = calculate_sum(5, 3)
        print(f"The sum is: {result}")
        greet("World")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main() 