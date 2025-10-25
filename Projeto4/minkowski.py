## Miguel Rodrigues Botelho -- 21202191
## Trabalho 4: Soma de Minkowski 

import pygame
import sys
import math
from ponto import Ponto

W, H = 1000, 700
tela = pygame.display.set_mode((W, H))
pygame.display.set_caption("Soma de Minkowski")
clock = pygame.time.Clock()
pygame.font.init()

robot_color = (200, 0, 0)
obstacle = (0, 0, 200)
text = (8, 8, 8) 

cspace = (0, 0, 200)
polygon = (52, 52, 52) 


obstacles = []
robot = []
config_spaces = []
current_polygon_points = []
current_mode = 1 
status_message = "Modo: Obstaculo (1) - Enter confirma"


def jarvis_march(points_list):
    if len(points_list) < 3:
        return points_list
    
    start_point = min(points_list, key=lambda p: (p.x, p.y))
    
    hull = []
    current_point = start_point
    
    while True:
        hull.append(current_point)
        endpoint = points_list[0]
        
        if endpoint == current_point:
            if len(points_list) > 1:
                endpoint = points_list[1]
            else:
                break

        for next_point in points_list:
            if next_point == current_point:
                continue
            
            orientation = (endpoint.x - current_point.x) * (next_point.y - current_point.y) - \
                          (endpoint.y - current_point.y) * (next_point.x - current_point.x)
            
            if orientation < 0:
                endpoint = next_point
            elif orientation == 0:
                dist_sq_endpoint = (endpoint.x - current_point.x)**2 + (endpoint.y - current_point.y)**2
                dist_sq_next = (next_point.x - current_point.x)**2 + (next_point.y - current_point.y)**2
                if dist_sq_next > dist_sq_endpoint:
                    endpoint = next_point
        
        current_point = endpoint
        if current_point == hull[0]:
            break
            
    return hull


def find_centroid(points):
    if not points:
        return Ponto(0, 0)
    num_points = len(points)
    sum_x = sum(p.x for p in points)
    sum_y = sum(p.y for p in points)
    return Ponto(sum_x / num_points, sum_y / num_points)

def get_reflected_shape(points):
    return [Ponto(-p.x, -p.y) for p in points]

def get_shape_at_origin(points):
    center = find_centroid(points)
    return [p - center for p in points]

def compute_minkowski_sum(poly_P, poly_Q):
    if not poly_P or not poly_Q:
        return []
    
    all_vertex_sums = []
    
    for p in poly_P:
        for q in poly_Q:
            all_vertex_sums.append(p + q)
    
    return jarvis_march(all_vertex_sums)


def draw_text(surface, text_str, x, y, color=text, font_size=14):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text_str, True, color)
    surface.blit(text_surface, (x, y))

def draw_polygon_outline(poly_points, color, width=2, closed=True):
    if len(poly_points) < 2:
        return
    point_tuples = [p.int_pos() for p in poly_points]
    pygame.draw.lines(tela, color, closed, point_tuples, width)

def draw_all():
    tela.fill((173, 216, 230))
    
    for cs_poly in config_spaces:
        if len(cs_poly) > 2: 
            point_tuples = [p.int_pos() for p in cs_poly]
            pygame.draw.polygon(tela, cspace, point_tuples)

    for obs_poly in obstacles:
        if len(obs_poly) > 2:
            point_tuples = [p.int_pos() for p in obs_poly]
            pygame.draw.polygon(tela, polygon, point_tuples)
            
    draw_polygon_outline(robot, robot_color, 3) 

    for p in current_polygon_points:
        p.draw(tela, obstacle, 5)
    draw_polygon_outline(current_polygon_points, obstacle, 1, closed=False)

    draw_text(tela, status_message, 10, 10)
    draw_text(tela, "[1] Modo Obstaculuo", 10, H - 70)
    draw_text(tela, "[2] Modo Robo", 10, H - 50)
    draw_text(tela, "[ESPAÇO] Calcular Configuration Space | [ENTER] Criar Poligono", 10, H - 30)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = pygame.mouse.get_pos()
                current_polygon_points.append(Ponto(pos[0], pos[1]))

        elif event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_1:
                current_mode = 1
                status_message = "Modo: Obstaculo (1) - ENTER para criar"
            
            elif event.key == pygame.K_2:
                current_mode = 2
                status_message = "Modo: Robo (2) - ENTER para criar"

            elif event.key == pygame.K_c:
                obstacles = []
                robot = []
                config_spaces = []
                current_polygon_points = []
                status_message = f"Modo atual: {'Obstaculo' if current_mode == 1 else 'Robo'} ({current_mode})."

            elif event.key == pygame.K_RETURN:
                if len(current_polygon_points) < 3:
                    status_message = "Pontos insuficientes"
                else:
                    new_convex_poly = jarvis_march(current_polygon_points)
                    
                    if current_mode == 1:
                        obstacles.append(new_convex_poly)
                        status_message = f"Obstaculo salvo ({len(new_convex_poly)} vertices)"
                    elif current_mode == 2:
                        robot = new_convex_poly
                        status_message = f"Robo salvo ({len(new_convex_poly)} vertices)"
                    
                    current_polygon_points = []

            elif event.key == pygame.K_SPACE:
                if not robot:
                    status_message = "Tem que criar um robo antes de calcular"
                elif not obstacles:
                    status_message = "Tem que ter pelo menos um obstaculo"
                else:
                    status_message = "Calculando"
                    config_spaces = []
                    
                    reflected_robot_shape = get_reflected_shape(robot)
                    
                    robot_form_for_sum = get_shape_at_origin(reflected_robot_shape)
                    
                    for obs_poly in obstacles:
                        cs_poly = compute_minkowski_sum(obs_poly, robot_form_for_sum)
                        config_spaces.append(cs_poly)
                    
                    status_message = f"Calculo concluido {len(config_spaces)}"

    draw_all()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
