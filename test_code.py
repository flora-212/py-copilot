def fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    """Calculate the factorial of n"""
    if n <= 1:
        return 1
    return n * factorial(n-1)

# Main program
if __name__ == "__main__":
    print("The first 10 Fibonacci numbers:")
    for i in range(10):
        print(f"F({i}) = {fibonacci(i)}")
    
    print("\nThe factorial of the first 5 numbers:")
    for i in range(1, 6):
        print(f"{i}! = {factorial(i)}")
