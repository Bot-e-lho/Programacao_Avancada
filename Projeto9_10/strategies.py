import math
import random
import pygame
from abc import *
import numpy as np

class DetectionStrategy(ABC):
    @abstractmethod
    def detect(self, agent, others):
        pass

class ResolutionStrategy(ABC):
    @abstractmethod
    def resolve(self, agent):
        pass

class RadiusDetectionStrategy(DetectionStrategy):
    def __init__(self, radius=5):
        self.radius = radius

    def detect(self, agent, others):
        agent.is_colliding = False
        agent.in_warning = False        

        for other in others:
            if other == agent:
                continue
            
            dx = agent.pos.x - other.pos.x
            dy = agent.pos.y - other.pos.y
            distance = math.sqrt(dx * dx + dy * dy)

            collision_distance = agent.radius * 2.0 
            warning_distance = agent.radius * 4.0
            

            if distance < collision_distance:
                agent.is_colliding = True
                return
            elif distance < warning_distance:
                agent.in_warning = True


        return agent.is_colliding


class RandomWalkResolutionStrategy(ResolutionStrategy):
    def __init__(self, step_size):
        self.step_size = step_size

    def resolve(self, agent):
        if agent.avoidance_cooldown > 0:
            agent.avoidance_cooldown -= 1
            return
        
        if agent.is_colliding or agent.in_warning:
            agent.avoidance_cooldown = random.randint(40, 60)
            agent.speed = random.uniform(0.5, 2.5)
            angle = random.uniform(0, 2 * math.pi)
            force_magnitude = self.step_size * 2 if agent.is_colliding else self.step_size
            force = math.cos(angle) * force_magnitude
            agent.drift_vector = np.array([math.cos(angle) * force, math.sin(angle) * force])

        else:
            agent.speed = agent.base_speed
            agent.drift_vector = np.array([0.0, 0.0])
