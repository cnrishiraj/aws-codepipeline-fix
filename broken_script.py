def calculate_sum(a, b):
    return a + b

def greet(name):
    print("Hello, " + name)
    return name.upper()

def divide(x, y):
    return x / y

def main():
    try:
        result = calculate_sum(5, 3)
        print(f"The sum is: {result}")
        greet("World")
        ratio = divide(10, 2)
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()