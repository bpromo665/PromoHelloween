import project.modules.start as start
import project.modules.admin as admin


def start_command_check(func):  # This decorator requires with keyboard as middle handler to check commands
    def wrapper(message):
        if message.text == '/admin':
            admin.handle_admin(message)
        else:
            func(message)

    return wrapper

