import time
import random
from training_objects import TrainingObject


class PlanManager:

    def __init__(self, input_map_dir):
        self.input_map_dir = input_map_dir
        self.training_plan_1_list = []
        self.training_plan_2_list = []
        self.training_plan_3_list = []
        self.warmup_list = []
        self.plans = []
        self.n_plans = 0
        self.largest_plan_dims = 0
        self.reset_training_objects(self.input_map_dir)

    def change_map_dir(self, new_map_dir):
        self.reset_training_objects(new_map_dir)

    def reset_training_objects(self, input_directory):
        self.training_plan_1_list = ["Training Plan 1", [
            TrainingObject(input_directory, training_type="Pack", category="General Shooting", name="Strength and Accuracy", exercise_time=10),
            TrainingObject(input_directory, training_type="Pack", category="General Shooting", exercise_time=5),
            TrainingObject(input_directory, training_type="Map", category="Dribble", exercise_time=10),
            TrainingObject(input_directory, training_type="Pack", category="Other", exercise_time=5),
            TrainingObject(input_directory, training_type="Map", category="Rings", exercise_time=10),
            TrainingObject(input_directory, training_type="Freeplay", exercise_time=5),
            ]]
        self.training_plan_2_list = ["Training Plan 2", [
            TrainingObject(input_directory, training_type="Map", category="Rings", exercise_time=10),
            TrainingObject(input_directory, training_type="Pack", category="General Shooting", name="Biddles Consistency", exercise_time=10),
            TrainingObject(input_directory, training_type="Map", category="Dribble", exercise_time=5),
            TrainingObject(input_directory, training_type="Pack", category="Rebounds", exercise_time=5),
            TrainingObject(input_directory, training_type="Freeplay", exercise_time=5)
            ]]

        self.training_plan_3_list = ["Training Plan 3", [
            TrainingObject(input_directory, training_type="Map", category="Rings", exercise_time=0.1),
            TrainingObject(input_directory, training_type="Pack", category="General Shooting", name="Biddles Consistency", exercise_time=0.1),
            TrainingObject(input_directory, training_type="Map", category="Dribble", exercise_time=5),
            TrainingObject(input_directory, training_type="Pack", category="Rebounds", exercise_time=5),
            TrainingObject(input_directory, training_type="Freeplay", exercise_time=5)
        ]]

        self.warmup_list = ["Warmup", [
            TrainingObject(input_directory, training_type="Pack", category="General Shooting", exercise_time=5),
            TrainingObject(input_directory, training_type="Map", category="Rings", exercise_time=5),
            TrainingObject(input_directory, training_type="Map", category="Dribble", exercise_time=5)
        ]]

        # list of all the training plans available
        self.plans = [
            self.training_plan_1_list,
            self.training_plan_2_list,
            self.training_plan_3_list,
            self.warmup_list
        ]
        self.n_plans = len(self.plans)

        self.largest_plan_dims = 0
        for single_plan in self.plans:
            exercise_list = single_plan[1]
            if len(exercise_list) > self.largest_plan_dims:
                self.largest_plan_dims = len(exercise_list)



