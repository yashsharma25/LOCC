from manim import *
from qiskit.quantum_info.operators import Operator
from entanglement_measures import entanglement_measures
import copy

# MeasurementScene(self.locc_protocol self.k_party, self.ee_strings, self.new_k_party_obj).render(self.output_file)
class MeasurementScene(ThreeDScene):
    '''
    Args:

    locc_protocol: an array of locc_op objects
    k_party: an object of class k_party
    ee_strings: array of strings where each string corresponds to the resulting ee between party involved in measurement and the rest of the k party system
    new_k_party_obj: the resulting k party obj after the given locc protocol has been executed on the given k party
    '''
        
    def __init__(self, locc_protocol, k_party_obj, execution_type, **kwargs):
        self.locc_protocol = locc_protocol
        self.k_party_obj = k_party_obj
        self.execution_type = execution_type
        self.new_k_party_obj = None
        self.total_num_parties = k_party_obj.k
        self.k_party_scale_factor = 1 / (self.total_num_parties ** 0.5) if self.total_num_parties > 1 else 1 # scale factor to ensure proper spacing for multiple parties
        self.k_party_mobjects = {} # k_party_mobjects[party_index] = (spheres_group, node_group, edge_group, edge_map)
        # self.measure_obj = (self.locc_protocol[0].party_index, self.locc_protocol[0].qudit_index) # tuple containing (party index, qudit index)
        super().__init__(**kwargs)

    def construct(self):
        print("IN CONSTRUCT")
        self.create_k_party_system()
        self.wait(2)
        self.clear_scene()
        self.execute_protocol()
        self.clear_scene()
    
    ''' To create the entire given k party obj '''
    def create_k_party_system(self):
        print("IN CREATE K PARTY SYSTEM")
        for party_index in range(self.total_num_parties):
            # calculate offset on x axis to fit all parties in one scene
            offset_x = (party_index - (self.total_num_parties - 1) / 2) * (5 * self.k_party_scale_factor)
            self.create_party(party_index, offset_x, self.k_party_scale_factor)
    
    ''' To create a singular party at a given offset_x location'''
    def create_party(self, party_index, offset_x, scale_factor):
        print("IN CREATE PARTY")
        # get basic information of current party
        party_state_desc = self.k_party_obj.state_desc[party_index]
        party_num_qudits, party_qudit_dims = party_state_desc[0], party_state_desc[1]

        # initialize qudits of party and related coordinates for the placing of those qudits
        qudits = [Sphere(radius=0.3 * scale_factor, color=BLUE) for _ in range(party_num_qudits)]
        coords = [(2 * scale_factor * np.cos(angle), 2 * scale_factor * np.sin(angle), 0) for angle in np.linspace(0, 2 * np.pi, party_num_qudits, endpoint=False)]
        for qudit, coord in zip(qudits, coords):
            qudit.move_to([coord[0] + offset_x, coord[1], coord[2]])

        # qudit_dots will be used in the context of measurement -- they exist "under" the qudits (spheres)
        qudit_dots = [Dot(point=[coord[0] + offset_x, coord[1], coord[2]]) for coord in coords]

        # initialize edges of party -- currently, edges represent the entanglement between qudits of the current party
        # edge --> there is some degree of entanglement between given 2 qudits
        # no edge --> there is NO entanglement between given 2 qudits
        
        edges = [] # to collect all edge objects, allows for easy creation of mobject
        edge_map = {} # edge_map[(i,j)] = edge --> easy access to the mobject edge that connects qudits 'i' and 'j' # need to add functionality to access a parties edge map at any time
        for i in range(party_num_qudits):
            for j in range(i + 1, party_num_qudits):
                if (j, i) not in edge_map: # to avoid creating repeat edges
                    edge = Line(qudit_dots[i].get_center(), qudit_dots[j].get_center())
                    edges.append(edge)
                    edge_map[(i, j)] = edge

        sphere_group = VGroup(*qudits)
        node_group = VGroup(*qudit_dots)
        edge_group = VGroup(*edges)

        self.k_party_mobjects[party_index] = (sphere_group, node_group, edge_group, edge_map)

        self.play(Create(sphere_group), Create(node_group), Create(edge_group))

        # add functionality to zoom into party that is being measured

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

            if locc_op.operation_type == "default":
                self.k_party_obj.q_state.evolve(Operator(locc_op.operator), [qudit_index])

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
                outcome, self.k_party_obj.q_state = self.k_party_obj.q_state.measure([qudit_index])
                self.k_party_obj.measurement_result[(locc_op.party_index, qudit_index)] = outcome

                meas_txt0 = Text("MEASUREMENT OPERATION")
                meas_txt0.move_to(UP)   
                self.play(Create(meas_txt0))
                self.wait(2)
                self.play(Uncreate(meas_txt0))

                self.show_measurement(locc_op.party_index, locc_op.qudit_index)
                
                meas_txt1 = Text(f"Outcome is: {outcome}")
                meas_txt1.move_to(UP)
                self.play(Create(meas_txt1))
                self.wait(2)
                self.play(Uncreate(meas_txt1))

            '''
            # Set PartyA as the party involved in the current LOCC operation
            partyA_indices = [locc_op.party_index]  # Wrap in a list to pass to the entanglement measures method

            # Set PartyB as every other party (all parties except PartyA)
            partyB_indices = list(all_party_indices - set(partyA_indices))  # Exclude PartyA from the set
            
            # Instantiate the entanglement_measures class (assuming it requires a state and parties as input)
            entanglement_calculator = entanglement_measures(self.k_party_obj.q_state, partyA_indices, partyB_indices)
            
            if self.execution_type == "upper bound":
                    entanglement_entropy = entanglement_calculator.get_le_upper_bound(self.k_party_obj, partyA_indices, partyB_indices)
            elif self.execution_type == "lower bound":
                entanglement_entropy = entanglement_calculator.get_le_lower_bound(self.k_party_obj, partyA_indices, partyB_indices)
            
            ee_txt = Text(f"Entanglement entropy between Party {partyA_indices[0]} and the rest: {entanglement_entropy}")
            '''

            ee_txt = Text("[This is where the entanglement entropy between party A and the rest will show up.]", font_size=24)
            ee_txt.move_to(UP)
            self.play(Create(ee_txt))
            self.wait(2)
            self.play(Uncreate(ee_txt))

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
        sphere = sphere_group[qudit_index]
        self.measurement_visualization(qudit_index)
        self.play(ScaleInPlace(sphere, scale_factor=0.1, run_time=2))
        random_color = BLUE if np.random.randint(2) == 0 else RED
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

    def clear_scene(self):
        print("IN CLEAR SCENE")
        # Iterate through all mobjects currently in the scene and "Uncreate" them
        for mobject in self.mobjects[:]:  # Make a copy of the list to avoid modifying it while iterating
            self.remove(mobject)
        # Optionally clear the list of mobjects
        self.mobjects.clear()

    ''' Modify or add a method to get the new_k_party_obj '''
    def get_new_k_party_obj(self):
        print("IN GET NEW K PARTY OBJ")
        return self.new_k_party_obj