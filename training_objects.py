import random
import os

# map_path = "C:\\users\conno\PycharmProjects\RocketTrainer\maps"
# dictionary of all training packs. To add more, simply add another element to the dic
training_packs = {
            "Goal Keeping": [
                ("Advanced Goalie", "776F-E2BB-2993-78D7"),
                ("Goal Roof Saves", "8100-D918-13C7-394F"),
                ("Uncomfortable Saves", "5CB2-6D82-1B52-47B7"),
                ("Backboard Defence", "99E5-4AA3-60D5-44BD"),
                ("Shadow Defence", "29E9-E595-D6CD-0599"),
                ("Shadow Defence 2", "5CCE-FB29-7B05-A0B1"),
                ("Saves", "2E23-ABD5-20C6-DBD4"),
                ("Goal Line Saves", "57C9-D284-39D8-2C9B"),
                ("Retreating Saves", "0D36-86AA-52CF-2D30"),
                ("Difficult Saves ", "3420-F216-ED7C-8011")
            ],
            "Rebounds": [
                ("Backboard Therapy", "D7F8-FD53-98D1-DAFE"),
                ("Advanced Backboard Double Taps", "0BFE-2943-AC6C-E032"),
                ("Double Touch Consistency", "01DC-0717-23F6-E5E7"),
                ("Double Touch Consistency", "01DC-0717-23F6-E5E7"),
                ("Double touches", "D545-35A7-72E0-C59C"),
                ("Advanced Rebounds", "A33B-12BA-9F5E-EBD4"),
                ("Double Tap Playground", "CAFC-FB3E-3C0F-B8F1"),
                ("Fast aerials/redirects", "24A2-849A-610E-C67C"),
                ("Self Set Double Touches", "7062-B853-1C87-9D16")
            ],
            "Aerials": [
                ("Backwards Aerials", "9A54-0D10-1717-7F4F"),
                ("Biddles Insane Aerials", "4352-185A-E719-98D3"),
                ("Ceiling Shots", "AFC9-2CCC-95EC-D9D4"),
                ("Advanced Aerials", "6CE4-7D20-7BD5-C800"),
                ("Air Dribbles", "6D84-3B06-1FA9-CAB8"),
                ("Realistic Air Dribbles", "D74D-FB19-06F3-CC67"),
                ("Advanced Ceiling Shots", "86BB-9444-FFD6-D610"),
                ("Fast aerials/redirects", "24A2-849A-610E-C67C"),
                ("Wall to Air Dribble", "5A65-4073-F310-5495"),
                ("Double Jump Aerials", "F269-B159-0BAC-AC2E")
            ],
            "Redirects": [
                ("Advanced Redirects (14-26)", "382B-6321-161F-5E98"),
                ("Passing (Infield)", "CDBB-8953-C052-654F"),
                ("Pass redirects", "B584-8606-10A5-00E1"),
                ("Wall Redirects", "399A-A83A-5D48-9D57"),
                ("Underside Redirects", "4C9D-1E98-80E4-2AEF"),
                ("Topside Redirects", "6468-C527-DE04-5514"),
                ("Easy redirects and Backboard Shots", "7D8F-A579-6A47-4DFA"),
                ("The Flying Pancake", "6903-A754-8D6A-878B"),
                ("Grand Champion Redirects", "34AF-5323-A9EF-E80D"),
                ("Redirect Consistency", "410E-0170-C52F-E8A0"),
                ("Tips and Doinks", "8BED-540E-E0DE-7409"),
                ("General Redirects", "8D93-C997-0ACD-8416")
            ],
            "Other": [
                ("Driving Backwards", "A60C-4CD2-80FF-C932"),
                ("Catches", "A85F-0C53-A1BE-75EB"),
                ("Falling Dodge Timing", "F1B4-5009-14A7-D22B"),
                ("Pinching", "447F-E68A-DD0C-CB6F"),
                ("Doinks", "D0BF-3B8E-0264-1FAF"),
                ("Cancel/Half Flip Shots", "306E-237A-053E-BE1E"),
                ("Wave Dash Shots", "F9EF-2D99-BA51-9E8A"),
                ("Wall Stop Shots", "4D75-FCFE-4D1D-9E70"),
                ("Pre-Jumping", "2BA6-DB20-F66F-9B25"),
                ("Uncomfortable Wall Touches", "A4CB-CBCD-E11F-8A51"),
                ("Goal Roof Saves", "8100-D918-13C7-394F"),
                ("Wall Speed", "8FCC-C1CA-0117-B015")
            ],
            "General Shooting": [
                ("Shots you shouldnt miss", "42BF-686D-E047-574B"),
                ("Shooting Consistency", "4912-A5C9-9A56-555D"),
                ("Strength and Accuracy", "6CF3-4C0B-32B4-1AC7"),
                ("Ground Shots", "6EB1-79B2-33B8-681C"),
                ("Air Roll Shots", "8D13-FFB7-AC37-7089"),
                ("All Kinds of Shots", "A867-51D6-322F-3063"),
                ("Powershot Training", "7EB0-B25B-689D-3413 "),
                ("Biddles Consistency", "55C9-36FE-613D-7F12"),
                ("Biddles Progression", "7E96-B9C7-3AC0-9B70"),
                ("Wall Shots", "9F6D-4387-4C57-2E4B"),
                ("Bounce Dribble 1", "9A02-8D65-4923-0A11")
            ],
            "Kick Offs": [
                ("Fast Kickoff", "BFAA-45A5-7A56-73CC"),
                ("Musty - Speedflip Kickoff Test", "A503-264C-A7EB-D282"),
                ("Kickoffs (Normal ones)", "7EE0-F697-7453-7123")
            ]

        }
all_packs = []
for pack_list in list(training_packs.values()):
    for single_pack in pack_list:
        all_packs.append(single_pack)


def map_name_cleaner(input_name):
    cut_index = input_name.rfind("\\")
    return input_name[cut_index+1:-4]


class TrainingObject:
    # the idea is that both map and training pack exercises are both created using this class, which are then exectuted
    # using the run_exercise command, such that they can be shuffled in MyTrainer. This class can be instantiated in a
    # number of different ways. If no args are passed, then a completely random training pack is created that can be either
    # a map or pack, for a random time. If just training_type is passed as either "map" or "pack" then it will randomise
    # from that selected. If a catagory is selected, then it will randomly choose from within that, and finally if the
    # name is specified then that specific pack will be ran.
    def __init__(self, input_map_directory, training_type=None, category=None, name=None, exercise_time=None, ):

        # first we want a list of all the folders, which correspond to the different types of training maps.
        map_categories = os.listdir(input_map_directory)
        map_navigator = {}

        # for each type of map, we append the pathstring to the dict
        for map_category in map_categories:
            category_path = os.path.join(input_map_directory, str(map_category))  # example: maps/rings/
            map_files = os.listdir(category_path)  # list all udk files within rings
            txt_str = []
            for single_map in map_files:
                txt_str.append(input_map_directory + "\\" + str(map_category) + "\\" + str(single_map))
            map_navigator[map_category] = txt_str

        self.category = category
        self.training_type = training_type
        self.exercise_time = exercise_time
        self.run_command = None

        def create_commmand_from_map(input_map_path):
            self.run_command = "load_workshop " + "\'" + input_map_path + "\'"

        def create_commmand_from_pack(input_pack):
            self.run_command = "load_training " + input_pack[1]

        def create_commmand_from_freeplay():
            self.run_command = "load_freeplay random"

        # randomly select a time if no time is passed
        if exercise_time is None:
            exercise_time = random.randrange(5, 15)
            self.exercise_time = exercise_time

        # randomly select the training_type
        if training_type is None:
            training_type = random.choice(["Map", "Pack"])

        # create a training exercise from a map
        if training_type == "Map":
            if name is None:
                # select a completely random map
                if category is None:
                    cat = random.choice(map_navigator)
                    map_choice = random.choice(cat)
                    map = map_choice
                    self.name = map_name_cleaner(map)
                    create_commmand_from_map(map)

                # select a random map from the category specified.
                elif category in map_categories:
                    cat = map_navigator[category]
                    map_choice = random.choice(cat)
                    map = map_choice
                    self.name = map_name_cleaner(map)
                    create_commmand_from_map(map)
                else:
                    raise ValueError("No such category exists")
            else:
                self.name = name
                name = name + ".udk"
                #name = "SpeedRings3.udk"
                for map_category in map_categories:
                    for map_file in map_category:
                        if str(map_file) == name:
                            map = input_map_directory + "\\" + str(map_category) + "\\" + str(name)
                            create_commmand_from_map(map)
                            break

        # create a training exercise from a pack
        elif training_type == "Pack":
            if name is None:
                # select a completely random training pack from a random category
                if category is None:
                    random_pack = random.choice(all_packs)
                    self.name = random_pack[0]
                    create_commmand_from_pack(random_pack)

                # select a random training pack from the category specified
                elif category in training_packs.keys():
                    random_pack = random.choice(training_packs[category])
                    self.name = random_pack[0]
                    create_commmand_from_pack(random_pack)

                else:
                    raise ValueError("Training pack category not found")

            else:
                # print("name: {}".format(name))
                for single_training_pack in all_packs:
                    if single_training_pack[0] == name:
                        pack = single_training_pack
                        self.name = pack[0]
                        create_commmand_from_pack(pack)
                        break

        # creates the free-play
        elif training_type == "Freeplay":
            self.name = "Freeplay"
            self.category = "Freeplay"
            create_commmand_from_freeplay()



