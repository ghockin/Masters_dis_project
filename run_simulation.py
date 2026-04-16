import ast
import csv
import os

class SimulationState:
    def __init__(self, scenario):
        self.scenario = scenario  # ⭐ needed for reset
        self.tick_count = 0
        self.finished = False
        # 🔥 NEW: movement accumulators
        self.enemy_progress = 0.0
        self.friendly_progress = 0.0
        self.load_scenario(scenario)
        self.log_file = f"logs/sim_{scenario['id']}.csv"
        os.makedirs("logs", exist_ok=True)

        with open(self.log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "tick",
                "enemy_x", "enemy_y",
                "friendly_x", "friendly_y",
                "enemy_speed",
                "friendly_speed"
            ])

    def load_scenario(self, s):
        self.enemy = list(ast.literal_eval(s["enemy_last_seen"]))
        self.friendly = list(ast.literal_eval(s["start_coord"]))

        self.enemy_destination = tuple(ast.literal_eval(s["enemy_predicted"]))
        self.friendly_destination = tuple(ast.literal_eval(s["destination_coord"]))

        self.enemy_class = s["enemy_class"]
        self.friendly_class = s["friendly_class"]

        self.enemy_speed = int(s["enemy_speed"])
        self.friendly_speed = int(s["friendly_speed"])
        
        # ✅ ADD THESE
        self.mission_brief = s["mission_brief"]
        self.intel_summary = s["intel_summary"]
        self.date = s["date"]

    def tick(self):
        if self.finished:
            return

        self.tick_count += 1

        # add "movement energy"
        self.enemy_progress += self.enemy_speed / 10
        self.friendly_progress += self.friendly_speed / 10

        # move enemy if enough progress
        while self.enemy_progress >= 1:
            self.step_towards(self.enemy, self.enemy_destination)
            self.enemy_progress -= 1

        # move friendly if enough progress
        while self.friendly_progress >= 1:
            self.step_towards(self.friendly, self.friendly_destination)
            self.friendly_progress -= 1

        # check completion
        enemy_done = tuple(self.enemy) == self.enemy_destination
        friendly_done = tuple(self.friendly) == self.friendly_destination

        if enemy_done and friendly_done:
            self.finished = True
            
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                self.tick_count,
                self.enemy[0], self.enemy[1],
                self.friendly[0], self.friendly[1],
                self.enemy_speed,
                self.friendly_speed
            ])

    def move_towards(self, pos, target, speed):
        if pos == list(target):
            return

        # move only ONE step per tick (ignore speed for now)
        if pos[0] < target[0]:
            pos[0] += 1
        elif pos[0] > target[0]:
            pos[0] -= 1

        if pos[1] < target[1]:
            pos[1] += 1
        elif pos[1] > target[1]:
            pos[1] -= 1
            
            
    def step_towards(self, pos, target):
        if pos[0] < target[0]:
            pos[0] += 1
        elif pos[0] > target[0]:
            pos[0] -= 1

        if pos[1] < target[1]:
            pos[1] += 1
        elif pos[1] > target[1]:
            pos[1] -= 1