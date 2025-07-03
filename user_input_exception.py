class UserInputError(Exception):
    def __init__(self, user_input, misc_elements):
        self.err = user_input
        super().__init__(f"User input '{self.err}' is invalid. Missing the following elements for the invoice: "
                         f"{misc_elements}")