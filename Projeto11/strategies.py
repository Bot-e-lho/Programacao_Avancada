import math
import random
import pygame
from abc import *
import numpy as np
from RVO import RVO_update

class AvoidanceStrategy(ABC):
    @abstractmethod
    def compute_velocity(self, agent, desired_velocity, others, grid_adapter, params):
        pass

class NoCommunicationStrategy(AvoidanceStrategy):
    def compute_velocity(self, agent, desired_velocity, others, grid_adapter, params):
        steering = np.array([0.0, 0.0])
        count = 0
        for other in others:
            if other == agent: 
                continue
            
            diff = agent.pos.pos() - other.pos.pos()
            dist = np.linalg.norm(diff)
            
            if dist == 0:
                steering += np.random.uniform(-1, 1, 2)
                count += 1
                continue

            if dist < agent.radius * 2.5: 
                steering += (diff / (dist**2 + 0.0001)) 
                count += 1
        
        if count > 0:
            steering /= count
            
            steering_mag = np.linalg.norm(steering)
            if steering_mag > 0:
                steering = (steering / steering_mag) * agent.base_speed
        
        return desired_velocity + (steering * 2.0)
    

class IndirectCommunicationStrategy(AvoidanceStrategy):
    def compute_velocity(self, agent, desired_velocity, others, grid_adapter, params):
        off_x, off_y, block_size = params
        
        next_pos = agent.pos.pos() + desired_velocity
        grid_coords = grid_adapter.get_grid_coords(next_pos[0], next_pos[1], off_x, off_y, block_size)
        
        if grid_coords and grid_adapter.is_cell_reserved(grid_coords, agent.id):
            return np.array([0.0, 0.0])
        
        curr_coords = grid_adapter.get_grid_coords(agent.pos.x, agent.pos.y, off_x, off_y, block_size)
        if curr_coords:
            grid_adapter.reserve_cell(curr_coords, agent.id)
        if grid_coords:
            grid_adapter.reserve_cell(grid_coords, agent.id)

        return desired_velocity
    

class DirectCommunicationStrategy(AvoidanceStrategy):
    def compute_velocity(self, agent, desired_velocity, others, grid_adapter, params):
        if RVO_update is None:
            return desired_velocity

        sight_radius = agent.radius * 4.0 
        
        local_others = []
        for o in others:
            if o == agent: continue
            
            dist = np.linalg.norm(agent.pos.pos() - o.pos.pos())
            
            if dist < sight_radius:
                local_others.append(o)
        
        if not local_others:
            return desired_velocity

        relevant_agents = [agent] + local_others
        
        X = []
        V_curr = []
        V_des = []

        for a in relevant_agents:
            X.append([a.pos.x, a.pos.y])
            V_curr.append([a.velocity[0], a.velocity[1]])
            
            if a == agent:
                V_des.append([desired_velocity[0], desired_velocity[1]])
            else:
                V_des.append([a.velocity[0], a.velocity[1]])

        ws_model = {
            'robot_radius': agent.radius,
            'circular_obstacles': []
        }

        try:    
            V_opt = RVO_update(X, V_des, V_curr, ws_model)
            new_velocity = np.array(V_opt[0])
            
            if np.linalg.norm(new_velocity) < 0.01 and np.linalg.norm(desired_velocity) > 0:
                 return desired_velocity * 0.1 
                 
            return new_velocity
            
        except Exception as e:
            print(f"RVO falha: {e}")
            return desired_velocity