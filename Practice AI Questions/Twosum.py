def twoSum(nums: list[int], target: int) -> list[int]:
    # Dictionary to map the value to its index
    seen = {}
    
    for index, num in enumerate(nums):
        # Calculate the required partner value
        complement = target - num
        
        # Check if the partner value has already been seen
        if complement in seen:
            return [seen[complement], index]
        
        # Otherwise, track the current number and its index
        seen[num] = index
        
    return []  # Return empty list if no solution is found

# Example Usage:
nums = [2, 7, 11, 15]
target = 9
print(twoSum(nums, target))  # Output: [0, 1]
