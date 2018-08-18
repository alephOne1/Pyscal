import sys
import re
import json

class Constants:
    ASSIGNMENT_OPERATOR = ":="
    ADDITION_OPERATOR = "+"
    SUBTRACTION_OPERATOR = "-"

    ASSIGNMENT_METHOD = "assign"
    ADDITION_METHOD = "add"
    SUBTRACTION_METHOD = "subtract"

    UNARY = "unary",
    BINARY = "binary"

    CONTAINER_OBJECT = "CONTAINER"

    RESERVED_WORDS = (
        "true",
        "false",
        "none"
    )


class Operation:
    def __init__(self, operation_string,
        operation_type, operation_method):
        self.operator = operation_string
        self.type = operation_type
        self.method = operation_method


class Parser:
    const = Constants()

    def __init__(self, code_text, available_operations):
        rows_objects = self.get_code_rows(code_text)

        self.operations = available_operations

        self.actions = []

        for row_object in rows_objects:
            self.actions.append(
                self.get_action_from_row(
                    row_object[1],
                    line_number=row_object[0]
                )
            )

    def get_code_rows(self, any_code):
        return [
            code_row for code_row in enumerate(any_code.split("\n"), 1) if code_row[1]
        ]

    def get_action_from_row(self, any_code_row, level=0, line_number=None):
        for operation in self.operations:
            if operation.operator in any_code_row:
                if operation.type == self.const.UNARY:
                    current_row_parts = [
                        row_part.strip() for row_part in any_code_row.split(
                            operation.operator
                        )
                    ]
                    for part in current_row_parts:
                        if not part:
                            raise SyntaxError(
                                "Assignment wrong syntax ({line} line)".format(line=line_number)
                            )

                    if len(current_row_parts) > 2:
                        raise SyntaxError(
                            "There must be only one assignment in the row ({line} line)".format(line=line_number)
                        )

                    if operation.operator == self.const.ASSIGNMENT_OPERATOR:
                        if level > 0:
                            raise SyntaxError(
                                "There must be only one assignment in the row ({line} line)".format(line=line_number)
                            )
                        else:
                            return {
                                operation.method: [
                                    current_row_parts[0],
                                    self.get_action_from_row(
                                        current_row_parts[1],
                                        level + 1,
                                        line_number
                                    )
                                ]
                            }
                else:
                    current_row_parts = [
                        row_part.strip() for row_part in any_code_row.split(
                            operation.operator
                        )
                    ]
                    if operation.operator == self.const.ADDITION_OPERATOR or operation.operator == self.const.SUBTRACTION_OPERATOR:
                        return {
                            operation.method: [
                                self.get_action_from_row(
                                    row_part,
                                    level + 1,
                                    line_number
                                ) for row_part in current_row_parts
                            ]
                        }
            else:
                continue

        return any_code_row


class Executor:
    const = Constants()

    def __init__(self, algorithm):
        self.data = {
            self.const.CONTAINER_OBJECT: None
        }

        for action in algorithm:
            self.run(action, operation=list(action.keys())[0])

    def run(self, action, operation=0):
        action_items = list(action.items()[0])
        action_items[1] = sorted(
            action_items[1],
            key=lambda element: type(element) == dict
        )

        for item in action_items[1]:
            if type(item) == dict:
                self.run(item, list(action.keys())[0])
        
        getattr(self, action_items[0])(
            *action_items[1],
            operation=operation
        )

    def process_string_variable(self, variable_value):
        if variable_value is None:
            return variable_value
        elif type(variable_value) == str:
            if variable_value.isdigit():
                return int(variable_value)
            elif len(re.findall(r'''"[^\n]*"''', variable_value)) == 1:
                return variable_value.replace('"', "")
            elif len(re.findall(r'''\d*\.\d+''', variable_value)) == 1:
                return float(variable_value)
            elif len(re.findall(r'''[a-zA-Z_]+[\da-zA-Z_]*''', variable_value)) == 1 and variable_value not in self.const.RESERVED_WORDS:
                if variable_value in self.data and variable_value != "CONTAINER":
                    return self.data[variable_value]
            elif variable_value == "true":
                return True
            elif variable_value == "false":
                return False
            elif variable_value == "none":
                return None
        elif type(variable_value) == dict:
            return self.data[self.const.CONTAINER_OBJECT]
        else:
            return variable_value

    def assign(self, variable_name, value, operation):
        if type(value) == dict:
            self.data[variable_name] = self.data[self.const.CONTAINER_OBJECT]
        else:
            self.data[variable_name] = self.process_string_variable(value)

        self.data[self.const.CONTAINER_OBJECT] = None


    def add(self, *args, **kwargs):
        if type(args[0]) == dict:
            result = 0
        else:
            result = self.process_string_variable(args[0])

        for arg in args[1:]:
            if type(arg) == dict:
                break
            else:
                result += self.process_string_variable(arg)

        if self.data[self.const.CONTAINER_OBJECT] is not None:
            result += self.data[self.const.CONTAINER_OBJECT]
        
        self.data[self.const.CONTAINER_OBJECT] = result

    def subtract(self, *args, **kwargs):
        result = self.process_string_variable(args[0])

        for arg in args[1:]:
            result -= self.process_string_variable(arg)

        if kwargs["operation"] == "add":
            if self.data[self.const.CONTAINER_OBJECT] is not None:
                self.data[self.const.CONTAINER_OBJECT] += result
            else:
                self.data[self.const.CONTAINER_OBJECT] = result
        else:
            self.data[self.const.CONTAINER_OBJECT] = result


class Pyscal:
    const = Constants()

    assignment = Operation(
        const.ASSIGNMENT_OPERATOR,
        const.UNARY,
        const.ASSIGNMENT_METHOD
    )
    addition = Operation(
        const.ADDITION_OPERATOR,
        const.BINARY,
        const.ADDITION_METHOD
    )
    subtraction = Operation(
        const.SUBTRACTION_OPERATOR,
        const.BINARY,
        const.SUBTRACTION_METHOD
    )

    OPERATIONS = (
        assignment,
        addition,
        subtraction
    )

    def __init__(self, arguments):
        file_path = arguments[1]

        code = self.read_file(file_path)
        code_parser = Parser(
            code,
            self.OPERATIONS
        )

        code_executor = Executor(code_parser.actions)

        
        print(
            json.dumps(
                code_executor.data,
                ensure_ascii=False,
                indent=4
            )
        )

    def read_file(self, any_file_path):
        with open(any_file_path, "r") as code_file:
            code_text = code_file.read().strip()

        return code_text


if __name__ == "__main__":
    app = Pyscal(sys.argv)
