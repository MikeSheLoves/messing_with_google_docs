class UserInputError(Exception):
    def __init__(self, misc_elements):
        for i in range(len(misc_elements)):
            misc_elements[i] = ''.join(' ' if char == '_' else char for char in misc_elements[i])
        misc_elements = ", ".join(misc_elements).strip(", ")
        super().__init__(f"Sorry, it seems you are missing a few things: {misc_elements}.")