import time
from abc import *

class Command(ABC):

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class MoveAgentCommand(Command):
    def __init__(self, agent):
        self.agent = agent
        self.timestamp = time.time()
        self.step_taken = False

    def execute(self):
        if self.agent.path and self.agent.current_step_index < len(self.agent.path) - 1:
            self.agent.current_step_index += 1
            self.step_taken = True
        else:
            pass

    def undo(self):
        if self.step_taken and self.agent.current_step_index > 0:
            self.agent.current_step_index -= 1

class CommandHistory:
    def __init__(self):
        self.history = []

    def execute_command(self, command):
        command.execute()
        self.history.append(command)

    def undo_last(self):
        if self.history:
            cmd = self.history.pop()
            cmd.undo()
