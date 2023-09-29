import pydantic

# Print the current version
print(f"Current version of pydantic: {pydantic.__version__}")

# Check if the version is 2.4.1 or above
if pydantic.VERSION >= (2, 4, 1):
    print("The installed version of pydantic is 2.4.1 or above.")
else:
    print("The installed version of pydantic is below 2.4.1.")
