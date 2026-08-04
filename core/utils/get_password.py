def get_password(prompt: str, need_confirm: bool = True):
    while True:
        password = input(prompt)

        if not password:
            print("Value required!")
            continue

        if not need_confirm:
            return password

        if input("Confirm Password: ") == password:
            return password

        print("Passwords do not match!")
