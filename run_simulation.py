import ast
import csv
import os
import random


class SimulationState:
    def __init__(self, scenario):
        self.scenario = scenario
        self.tick_count = 0
        self.finished = False
        self.friendly_destroyed = False

        self.enemy_progress = 0.0
        self.friendly_progress = 0.0
        self.friendly_move_counter = 0
        self.last_evasion_trigger = 0

        self.load_scenario(scenario)

        # trail history
        self.friendly_path = [tuple(self.friendly)]

        os.makedirs("logs", exist_ok=True)
        self.log_file = f"logs/sim_{scenario['id']}.csv"

        with open(self.log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "scenario_id",
                "scenario_name",
                "is_mutation",
                "tick",
                "enemy_x", "enemy_y",
                "friendly_x", "friendly_y",
                "enemy_chase_target_x", "enemy_chase_target_y",
                "friendly_destination_x", "friendly_destination_y",
                "enemy_speed",
                "friendly_speed",
                "friendly_evasion_interval",
                "friendly_destroyed"
            ])

    def load_scenario(self, s):
        self.enemy = list(ast.literal_eval(s["enemy_last_seen"]))
        self.friendly = list(ast.literal_eval(s["start_coord"]))

        self.friendly_destination = tuple(ast.literal_eval(s["destination_coord"]))

        self.enemy_class = s["enemy_class"]
        self.friendly_class = s["friendly_class"]

        self.enemy_speed = float(s["enemy_speed"])
        self.friendly_speed = float(s["friendly_speed"])
        self.friendly_evasion_interval = int(s["friendly_evasion_interval"] or 0)

        self.mission_brief = s["mission_brief"]
        self.intel_summary = s["intel_summary"]
        self.date = s["date"]
        self.scenario_name = s["scenario_name"]
        self.is_mutation = s["is_mutation"]

    def tick(self):
        if self.finished:
            return

        self.tick_count += 1

        # speed accumulator model
        self.enemy_progress += self.enemy_speed / 10.0
        self.friendly_progress += self.friendly_speed / 10.0

        while self.enemy_progress >= 1.0 or self.friendly_progress >= 1.0:
            # enemy always chases current friendly position
            if self.enemy_progress >= 1.0:
                self.move_step(self.enemy, tuple(self.friendly))
                self.enemy_progress -= 1.0

                if self.enemy == self.friendly:
                    self.friendly_destroyed = True
                    self.finished = True
                    self.log_state()
                    return

            # friendly moves toward its target
            if self.friendly_progress >= 1.0:
                moved = self.move_step(self.friendly, self.friendly_destination)
                self.friendly_progress -= 1.0

                if moved:
                    self.friendly_move_counter += 1
                    self.add_friendly_path_point()

                    # ✅ if friendly reaches destination, stop immediately
                    if tuple(self.friendly) == self.friendly_destination:
                        self.finished = True
                        self.log_state()
                        return

                # every N friendly moves, do one random evasive step
                if (
                    self.friendly_evasion_interval > 0
                    and self.friendly_move_counter > 0
                    and self.friendly_move_counter % self.friendly_evasion_interval == 0
                    and self.friendly_move_counter != self.last_evasion_trigger
                    and tuple(self.friendly) != self.friendly_destination
                ):
                    self.last_evasion_trigger = self.friendly_move_counter

                    evasive_moved = self.random_friendly_step()
                    if evasive_moved:
                        self.add_friendly_path_point()

                    if self.enemy == self.friendly:
                        self.friendly_destroyed = True
                        self.finished = True
                        self.log_state()
                        return

                if self.enemy == self.friendly:
                    self.friendly_destroyed = True
                    self.finished = True
                    self.log_state()
                    return

        # friendly wins if it reaches destination alive
        if tuple(self.friendly) == self.friendly_destination:
            self.finished = True

        self.log_state()

    def move_step(self, pos, target):
        if tuple(pos) == target:
            return False

        old_pos = tuple(pos)

        if pos[0] < target[0]:
            pos[0] += 1
        elif pos[0] > target[0]:
            pos[0] -= 1

        if pos[1] < target[1]:
            pos[1] += 1
        elif pos[1] > target[1]:
            pos[1] -= 1

        return tuple(pos) != old_pos

    def random_friendly_step(self):
        direction = random.choice([
            (1, 0),    # right
            (-1, 0),   # left
            (0, 1),    # down
            (0, -1),   # up
        ])

        new_x = self.friendly[0] + direction[0]
        new_y = self.friendly[1] + direction[1]

        if 0 <= new_x < 10 and 0 <= new_y < 10:
            old_pos = tuple(self.friendly)
            self.friendly[0] = new_x
            self.friendly[1] = new_y
            return tuple(self.friendly) != old_pos

        return False

    def add_friendly_path_point(self):
        point = tuple(self.friendly)
        if not self.friendly_path or self.friendly_path[-1] != point:
            self.friendly_path.append(point)

    def log_state(self):
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                self.scenario["id"],
                self.scenario_name,
                self.is_mutation,
                self.tick_count,
                self.enemy[0], self.enemy[1],
                self.friendly[0], self.friendly[1],
                self.friendly[0], self.friendly[1],
                self.friendly_destination[0], self.friendly_destination[1],
                self.enemy_speed,
                self.friendly_speed,
                self.friendly_evasion_interval,
                "Y" if self.friendly_destroyed else "N"
            ])