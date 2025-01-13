from manim import config, Scene, Text, Write
from manim import *
from itertools import combinations
from model.k_party import k_party
from model.locc_operation import locc_operation
from model.entanglement_measures import EntanglementMeasures
from qiskit.quantum_info.operators import Operator


# TODO: visualization for default operation!! (that is, not a measurement, not a conditional, but a default op)
class VideoModel:
    def __init__(self):
        self.video_path = None  # Store the path of the generated video

    def generate_video(self, locc_protocol, k_party, execution_type, output_path: str = "manim_output.mp4"):
        """
        Generate a Manim video with the given text and save it to the specified path.
        """
        # Update Manim's configuration for the output file
        config.media_dir = "./media"
        config.output_file = output_path

        class VideoScene(ThreeDScene):
            def __init__(self, **kwargs):
                self.locc_protocol = locc_protocol
                self.k_party_obj = k_party
                self.execution_type = execution_type
                self.new_k_party_obj = None
                self.total_num_parties = k_party.k
                self.k_party_scale_factor = 1 / (self.total_num_parties ** 0.5) if self.total_num_parties > 1 else 1 # scale factor to ensure proper spacing for multiple parties
                self.k_party_mobjects = {} # k_party_mobjects[party_index] = (spheres_group, node_group, edge_group, edge_map)
                self.party_edges = {}
                self.removed_qudits = {party_index: set() for party_index in range(self.total_num_parties)}
                super().__init__(**kwargs)

            def construct(self):
                # self.set_camera_orientation(phi=75 * DEGREES, theta=45 * DEGREES)
                self.set_camera_orientation(phi=60*DEGREES, theta=-45*DEGREES)
                print(self.k_party_obj.q_state.data)
                self.create_k_party_system()
                self.wait(2)
                self.clear_scene()
                self.execute_protocol()
                self.clear_scene()
                self.create_k_party_system()

            def create_k_party_system(self):
                '''Creates the entire given k party obj'''
                print("IN CREATE K PARTY SYSTEM")
                party_positions = []

                for party_index in range(self.total_num_parties):
                    # calculate offset on x axis to fit all parties in one scene
                    offset_x = (party_index - (self.total_num_parties - 1) / 2) * (5 * self.k_party_scale_factor)
                    avg_position = self.create_party(party_index, offset_x, self.k_party_scale_factor)
                    
                    # Store the position of the center of the current party
                    party_positions.append(avg_position)

                # Drawing lines between the created parties
                for i, j in combinations(range(self.total_num_parties), 2):
                    # Ensure we have qudits to connect, here we could check if both parties have qudits before creating the line
                    if self.k_party_obj.state_desc[i][0] > 0 and self.k_party_obj.state_desc[j][0] > 0:  # Check if both parties have qudits
                        print(f"Connecting party {i} to party {j}")  # Debug print to see the pairs
                        # Create a line between the centers of the two parties
                        party_line = Line(party_positions[i], party_positions[j], color=WHITE)
                        self.party_edges[(i,j)] = party_line
                        self.play(Create(party_line))
            
            def create_party(self, party_index, offset_x, scale_factor):
                party_state_desc = self.k_party_obj.state_desc[party_index]
                party_num_qudits, party_qudit_dims = party_state_desc[0], party_state_desc[1]

                # Adjust the number of qudits based on removed qudits
                remaining_qudits = [
                    i for i in range(party_num_qudits)
                    if i not in self.removed_qudits[party_index]
                ]
                qudits = [Sphere(radius=0.3 * scale_factor, color=BLUE) for _ in remaining_qudits]
                coords = [
                    (2 * scale_factor * np.cos(angle), 2 * scale_factor * np.sin(angle), 0)
                    for angle in np.linspace(0, 2 * np.pi, len(remaining_qudits), endpoint=False)
                ]

                for qudit, coord in zip(qudits, coords):
                    qudit.move_to([coord[0] + offset_x, coord[1], coord[2]])

                qudit_dots = [Dot(point=[coord[0] + offset_x, coord[1], coord[2]]) for coord in coords]

                edges = []
                edge_map = {}
                for i in range(len(remaining_qudits)):
                    for j in range(i + 1, len(remaining_qudits)):
                        edge = DashedLine(qudit_dots[i].get_center(), qudit_dots[j].get_center())
                        edges.append(edge)
                        edge_map[(remaining_qudits[i], remaining_qudits[j])] = edge

                sphere_group = VGroup(*qudits)
                node_group = VGroup(*qudit_dots)
                edge_group = VGroup(*edges)

                self.k_party_mobjects[party_index] = (sphere_group, node_group, edge_group, edge_map)
                self.play(Create(sphere_group), Create(node_group), Create(edge_group))

                avg_x = np.mean([coord[0] for coord in coords]) + offset_x
                avg_y = np.mean([coord[1] for coord in coords])
                avg_z = np.mean([coord[2] for coord in coords])

                return np.array([avg_x, avg_y, avg_z])


                # add functionality to zoom into party that is being measured
            def clear_scene(self):
                print("IN CLEAR SCENE")
                # Iterate through all mobjects currently in the scene and "Uncreate" them
                for mobject in self.mobjects[:]:  # Make a copy of the list to avoid modifying it while iterating
                    self.remove(mobject)
                # Optionally clear the list of mobjects
                self.mobjects.clear()

            ''' have taken the execute_protocol() method from the locc_controller --> will be easier to create the script from here '''
            def execute_protocol(self):
                print("IN EXECUTE PROTOCOL")
                # Given self.k_party_mobjects, we need to be able to give this dictionary a party_index, and then create the party right in the center, nice and big
                # The issue is the sphere_group, node_group, and edge_group VGroups are all arranged in a specific spot in 3d space.
                # We nee to be able to take the sphere_group, node_group, and edge_group VGroups and center and scale it to be in the center of the screen.        

                # Get the number of parties in the k_party_obj (assuming it has an attribute `parties`)
                all_party_indices = set(range(self.k_party_obj.parties))  # Create a set of all party indices

                for locc_op in self.locc_protocol:
                    # Center and scale the party for the current LOCC operation
                    party_index = locc_op.party_index
                    '''
                    txt = Text(f" Party: {party_index}")
                    self.play(Create(txt))
                    self.wait(1)
                    self.play(Uncreate(txt))
                    '''

                    self.center_and_scale_party(party_index)
                    qudit_index = self.k_party_obj.get_qudit_index_in_state(locc_op.party_index, locc_op.qudit_index)

                    if locc_op.operation_type == "default": # IMPORTANT: This is where we deal with default operations in the protocol.
                        self.k_party_obj.q_state.evolve(Operator(locc_op.operator), [qudit_index])
                        default_txt = f"Deafault operation: Applying operator {locc_op.operator} on qudit index {qudit_index}"
                        self.play(Create(default_txt))
                        self.wait(2)
                        self.play(Uncreate(default_txt))
                        
                    elif locc_op.operation_type == "conditional":
                        print("IN CONDITION OPERATION")
                        #retrieve the measurement result and evaluate the 
                        cond_txt0 = Text(
                            f"CONDITIONAL OPERATION: Stored Measurement outcome for {locc_op.condition[0]}, {locc_op.condition[1]} =, {self.k_party_obj.measurement_result.get((locc_op.condition[0], locc_op.condition[1]))}",
                            font_size=20
                        )
                        cond_txt0.move_to(UP)
                        self.play(Create(cond_txt0))
                        self.wait(2)
                        self.play(Uncreate(cond_txt0))

                        # print("Stored Measurement outcome for ", locc_op.condition[0], locc_op.condition[1], " = ", self.k_party_obj.measurement_result.get((locc_op.condition[0], locc_op.condition[1])))
                        if self.k_party_obj.measurement_result.get((locc_op.condition[0], locc_op.condition[1])) == locc_op.condition[2]:
                            print("CONDITIONAL MEASUREMENT MATCH")
                            self.k_party_obj.q_state.evolve(Operator(locc_op.operator), [qudit_index])
                            # print("Applying operator = ", locc_op.operator)
                            
                            cond_txt1 = Text("Applying operator = ", locc_op.operator, font_size=24)
                            cond_txt1.move_to(UP)
                            self.play(Create(cond_txt1))
                            self.wait(2)
                            self.play(Uncreate(cond_txt1))

                            self.show_measurement(locc_op.party_index, locc_op.qudit_index)

                    elif locc_op.operation_type == "measurement":
                        print("IN MEASURE CONDITION")
                        print(f"qudit index: {qudit_index}")
                        print(self.k_party_obj.q_state.data.shape)
                        
                        # Normalize the state before measurement
                        self.k_party_obj.q_state = self.k_party_obj.q_state / np.linalg.norm(self.k_party_obj.q_state.data)

                        outcome, self.k_party_obj.q_state = self.k_party_obj.q_state.measure([qudit_index])
                        self.outcome = outcome
                        self.k_party_obj.measurement_result[(locc_op.party_index, qudit_index)] = outcome

                        '''
                        meas_txt0 = Text("MEASUREMENT OPERATION")
                        meas_txt0.move_to(UP)   
                        self.play(Create(meas_txt0))
                        self.wait(2)
                        self.play(Uncreate(meas_txt0))
                        '''

                        self.show_measurement(locc_op.party_index, locc_op.qudit_index)
                        
                        meas_txt1 = Text(f"Outcome is: {outcome}")
                        meas_txt1.move_to(UP)
                        self.play(Create(meas_txt1))
                        self.wait(2)
                        self.play(Uncreate(meas_txt1))

                    
                    # Set PartyA as the party involved in the current LOCC operation
                    partyA_indices = [locc_op.party_index]  # Wrap in a list to pass to the entanglement measures method

                    # Set PartyB as every other party (all parties except PartyA)
                    partyB_indices = list(all_party_indices - set(partyA_indices))  # Exclude PartyA from the set
                    
                    # Instantiate the entanglement_measures class (assuming it requires a state and parties as input)
                    entanglement_calculator = EntanglementMeasures(self.k_party_obj.parties-1, self.k_party_obj.q_state, locc_op.party_index)
                    
                    if self.execution_type == "upper bound":
                            entanglement_entropy = entanglement_calculator.get_le_upper_bound(self.k_party_obj, partyA_indices, partyB_indices)
                    elif self.execution_type == "lower bound":
                        entanglement_entropy = entanglement_calculator.get_le_lower_bound(self.k_party_obj, partyA_indices, partyB_indices)
                    
                    ee_txt = Text(f"Entanglement entropy between Party {partyA_indices[0]} and the rest: {entanglement_entropy}", font_size=24)
                    # Rotate the text to counteract the camera's phi and theta rotations
                    ee_txt.move_to(DOWN)
                    # ee_txt = Text("[This is where the entanglement entropy between party A and the rest will show up.]", font_size=24)
                    self.set_camera_orientation(phi=0* DEGREES, theta=-90* DEGREES)
                    self.play(Create(ee_txt))
                    self.wait(2)
                    self.play(Uncreate(ee_txt))
                    self.set_camera_orientation(phi=75 * DEGREES, theta=45 * DEGREES)                    

                    self.clear_scene()
                
                self.new_k_party_obj = self.k_party_obj

            ''' easy way to get a singluar party of interest nice and big in the center of the screen '''
            def center_and_scale_party(self, party_index):
                print("IN CENTER AND SCALE PARTY")
                sphere_group, node_group, edge_group, edge_map = self.k_party_mobjects[party_index]

                # Calculate the current center of the sphere group
                current_center = sphere_group.get_center()

                # Define the target center (center of the screen)
                target_center = ORIGIN

                # Calculate the shift vector to move the sphere group to the center
                shift_vector = target_center - current_center

                # Apply the shift to move all groups to the center
                sphere_group.shift(shift_vector)
                node_group.shift(shift_vector)
                edge_group.shift(shift_vector)

                # Scale the groups to make them bigger (adjust the scale factor as needed)
                scale_factor = 2.0  # Example scale factor
                self.play(
                    sphere_group.animate.scale(scale_factor),
                    node_group.animate.scale(scale_factor),
                    edge_group.animate.scale(scale_factor),
                    run_time=2
                )

            ''' Show measurement by deleting respective Line and Sphere mobjects '''
            def show_measurement(self, party_index, qudit_index):
                print("IN SHOW MEASUREMENT")
                # for reference: self.k_party_mobjects[party_index] = (sphere_group, node_group, edge_group, edge_map)
                # important: will need to clear the scene, or display this singluar party
                sphere_group, node_group, edge_group, edge_map = self.k_party_mobjects[party_index]
                
                # shrink sphere:
                sphere_to_remove = sphere_group[qudit_index]
                self.measurement_visualization(qudit_index)
                self.play(FadeOut(sphere_to_remove))
                
                print(f"party index in show_measurement: {party_index}")
                self.removed_qudits[party_index].add(qudit_index)

                # random_color = BLUE if np.random.randint(2) == 0 else RED
                random_color = BLUE if self.outcome == 0 else RED
                node_group[qudit_index].set_color(random_color)

                # delete edges: iterate over keys in the edge_map to find any edge involving qudit_index
                keys = list(edge_map.keys())

                for (i, j) in keys:
                    if qudit_index in (i, j):
                        # Get the edge using either (qudit_index, other_index) or (other_index, qudit_index)
                        edge_delete = edge_map.get((qudit_index, j)) or edge_map.get((i, qudit_index))
                        if edge_delete:
                            self.play(Uncreate(edge_delete))
                            # Optionally, remove the edge from the map and group after animating
                            edge_group.remove(edge_delete)
                            del edge_map[(i, j)]

                # make necessary changes to self.party_edges
                keys_to_remove = [(i,j) for (i,j) in self.party_edges if party_index in (i,j)]
                for key in keys_to_remove:
                    line = self.party_edges[key]
                    self.remove(line)
                    del self.party_edges[key]

            def measurement_visualization(self, state):
                print("IN MEASUREMENT VISUALIZATION")
                original_phi = self.camera.phi
                original_theta = self.camera.theta
                self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)

                top_left = np.array([-5, 0, 0])
                self.scale_factor = 0.75
                rectangle = Rectangle(width=4, height=3, color=WHITE).scale(self.scale_factor).move_to(ORIGIN)
                # sphere = Sphere(radius=1).scale(self.scale_factor).move_to(ORIGIN)
                letter_m = Text(f"M{state}", font_size=48, color=WHITE).scale(self.scale_factor).move_to(ORIGIN)

                self.play(Create(rectangle))
                self.play(Create(letter_m))
                
                self.play(Uncreate(letter_m), Uncreate(rectangle))

                self.set_camera_orientation(phi=original_phi, theta=original_theta)

        # Generate the video
        VideoScene().render()
        self.video_path = config.output_file
        return self.video_path