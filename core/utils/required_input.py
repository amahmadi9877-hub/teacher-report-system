def required_input(prompt: str):
    while True:
        if _input := input(prompt):
            return _input
        print("\tvalue required!")
