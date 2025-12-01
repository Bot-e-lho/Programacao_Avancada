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
        self.prev_index = agent.current_step_index
        self.step_taken = False

    def execute(self):
        self.prev_index = self.agent.current_step_index
        if self.agent.path and self.agent.current_step_index < len(self.agent.path) - 1:
            self.agent.current_step_index += 1
            self.step_taken = True
            return True
        else:
            self.step_taken = False
            return False 

    def undo(self):
        if self.step_taken:
            if 0 <= self.prev_index <= len(self.agent.path) - 1:
                self.agent.current_step_index = self.prev_index
            else:
                self.agent.current_step_index = max(0, self.agent.current_step_index - 1)

class CommandHistory:
    def __init__(self):
        self.history = []

    def execute_command(self, command):
        executed = command.execute()
        if executed:
            self.history.append(command)

    def undo_last(self):
        if self.history:
            cmd = self.history.pop()
            cmd.undo()
