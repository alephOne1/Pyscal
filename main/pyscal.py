import sys

class Constants:
    ASSIGNMENT_OPERATOR = ":="
    ADDITION_OPERATOR = "+"
    SUBTRACTION_OPERATOR = "-"

    UNARY = "unary",
    BINARY = "binary"

    CONTAINER_OBJECT = "CONTAINER"


class Operation:
    def __init__(self, operation_string, operation_type):
        self.operator = operation_string
        self.type = operation_type


class Parser:
    const = Constants()

    def __init__(self, code_text, available_operations):
        rows = self.get_code_rows(code_text)

        self.operations = available_operations

        self.actions = []

        for row in rows:
            self.actions.append(
                self.get_action_from_row(row)
            )

    def get_code_rows(self, any_code):
        return [code_row for code_row in any_code.split("\n") if code_row]

    def get_action_from_row(self, any_code_row, level=0):
        for operation_item in self.operations.items():
            if operation_item[1].operator in any_code_row:
                if operation_item[1].type == self.const.UNARY:
                    current_row_parts = [
                        row_part.strip() for row_part in any_code_row.split(
                            operation_item[1].operator
                        )
                    ]

                    if len(current_row_parts) > 2:
                        raise SyntaxError("There must be only one assignment in the row")

                    if operation_item[1].operator == self.const.ASSIGNMENT_OPERATOR:
                        if level > 0:
                            raise SyntaxError("There must be only one assignment in the row")
                        else:
                            return {
                                operation_item[0]: [
                                    current_row_parts[0],
                                    self.get_action_from_row(
                                        current_row_parts[1],
                                        level + 1
                                    )
                                ]
                            }
                else:
                    current_row_parts = [
                        row_part.strip() for row_part in any_code_row.split(
                            operation_item[1].operator
                        )
                    ]
                    if operation_item[1].operator == self.const.ADDITION_OPERATOR:
                        pass

        return any_code_row


class Executor:
    const = Constants()

    def __init__(self, algorithm):
        self.data = {self.const.CONTAINER_OBJECT: None}

        for action in algorithm:
            self.run(action)

    def run(self, action):
        action_items = action.items()[0]
        
        getattr(self, action_items[0])(
            *action_items[1]
        )

    def assign(self, variable_name, value):
        self.data[variable_name] = value

    def add(self, first_object, second_object):
        self.data[
            self.const.CONTAINER_OBJECT
        ] = first_object + second_object

    def subtract(self, first_object, second_object):
        return first_object - second_object


class Pyscal:
    const = Constants()

    assignment = Operation(
        const.ASSIGNMENT_OPERATOR,
        const.UNARY
    )
    addition = Operation(
        const.ADDITION_OPERATOR,
        const.BINARY
    )
    subtraction = Operation(
        const.SUBTRACTION_OPERATOR,
        const.BINARY
    )

    OPERATIONS = {
        "assign": assignment,
        "add": addition,
        "subtract": subtraction
    }

    def __init__(self, arguments):
        file_path = arguments[1]

        code = self.read_file(file_path)
        code_parser = Parser(
            code,
            self.OPERATIONS
        )

        code_executor = Executor(code_parser.actions)

        print(code_executor.data)

    def read_file(self, any_file_path):
        with open(any_file_path, "r") as code_file:
            code_text = code_file.read().strip()

        return code_text


if __name__ == "__main__":
    app = Pyscal(sys.argv)
