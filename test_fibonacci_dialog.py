# Test file - auto-generated for dialog handling test
def fibonacci(n):
    """Recursively calculate Fibonacci sequence"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def fibonacci_optimized(n, memo={}):
    """Optimized version of Fibonacci sequence calculation"""
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_optimized(n-1, memo) + fibonacci_optimized(n-2, memo)
    return memo[n]

# Calculate first 15 Fibonacci numbers
print("Original recursive version:")
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")

print("\nOptimized version:")
for i in range(15):
    print(f"F({i}) = {fibonacci_optimized(i)}")
