import time
import pandas as pd
from datetime import datetime

class Log:
    def __init__(self, filename_prefix="log"):
        self.filename_prefix = filename_prefix
        self.mouse_path = []
        self.clicks = []          # guarda todos os clicks 
        self.object_clicks = []   # clique que acertou objetos
        self.start_time = time.time()
        self.start_datetime = datetime.utcnow().isoformat()
        self._last_mouse_log_time = self.start_time
        self._last_pos = None
        self._last_vel = (0, 0)
        self.mouse_sample_interval = 1/60.0 

    def log_mouse_movement(self, pos):
        now = time.time()
        if now - self._last_mouse_log_time < self.mouse_sample_interval:
            return
        if self._last_pos is not None:
            dt = now - self._last_mouse_log_time
            if dt > 0:
                vel_x = (pos[0] - self._last_pos[0]) / dt
                vel_y = (pos[1] - self._last_pos[1]) / dt

                acc_x = (vel_x - self._last_vel[0]) / dt
                acc_y = (vel_y - self._last_vel[1]) / dt

                self.mouse_path.append({
                    "time_rel": now - self.start_time,
                    "time_abs": datetime.utcnow().isoformat(),
                    "x": int(pos[0]),
                    "y": int(pos[1]),
                    "vel_x": vel_x,
                    "vel_y": vel_y,
                    "acc_x": acc_x,
                    "acc_y": acc_y
                })
                self._last_vel = (vel_x, vel_y)
            
        self._last_pos = pos
        self._last_mouse_log_time = now

    def log_click(self, pos, clicked_objects):
        now = time.time()
        click_id = len(self.clicks) + 1
        entry = {
            "click_id": click_id,
            "time_rel": now - self.start_time,
            "time_abs": datetime.utcnow().isoformat(),
            "x": int(pos[0]),
            "y": int(pos[1]),
            "objects": ";".join(clicked_objects) if clicked_objects else ""
        }
        self.clicks.append(entry)
        if clicked_objects:
            self.object_clicks.append(entry)

    def export_data(self):
        end_time = time.time()
        runtime = end_time - self.start_time
        end_datetime = datetime.utcnow().isoformat()

        df_mouse = pd.DataFrame(self.mouse_path)
        df_clicks = pd.DataFrame(self.clicks)

        df_mouse.to_csv(f"{self.filename_prefix}_mouse_path.csv", index=False)
        df_clicks.to_csv(f"{self.filename_prefix}_clicks_all.csv", index=False)

        with open(f"{self.filename_prefix}_summary.txt", "w") as f:
            f.write("--- Resumo ---\n")
            f.write(f"Start: {self.start_datetime}\n")
            f.write(f"End: {end_datetime}\n")
            f.write(f"Duracao (s): {runtime:.2f}\n")
            f.write(f"Total cliques: {len(self.clicks)}\n")
            f.write(f"Cliques nos objetos: {len(self.object_clicks)}\n")
