from manim import *
import copy

class MeasurementScene(ThreeDScene):
    def __init__(self, locc_op, k_party_obj, res, execution_type, ee_string, new_k_party_obj, **kwargs):
        self.locc_op = locc_op
        self.k_party_obj = k_party_obj
        self.res = res
        self.execution_type = execution_type
        self.ee_string = ee_string
        self.total_num_parties = k_party_obj.k
        self.new_k_party_obj = new_k_party_obj
        self.measure_obj = (self.locc_op[0].party_index, self.locc_op[0].qudit_index) # tuple containing (party index, qudit index)
        super().__init__(**kwargs)

    def construct(self):
        self.create_graph # new way to create graph to handle k > 1
        # self.model_individual_EEs()

    def create_graph(self):
        scale_factor = 1 / (self.total_num_parties ** 0.5) if self.total_num_parties > 1 else 1

        for party_index in range(self.total_num_parties):
            party = self.k_party_obj.state_desc[party_index]
            party_num_qudits, party_qudit_dims = party[0], party[1]
            nodes = [Sphere(radius=0.3 * scale_factor, color=BLUE) for _ in range(party_num_qudits)]
            coordinates = [(2 * scale_factor * np.cos(angle), 2 * scale_factor * np.sin(angle), 0) for angle in np.linspace(0, 2 * np.pi, party_num_qudits, endpoint=False)]
            
            # calculate the position offset for this party
            if self.total_num_parties > 1:
                offset_x = (party_index - (self.total_num_parties - 1) / 2) * (5 * scale_factor)
            else:
                offset_x = 0

            for node, coord in zip(nodes, coordinates):
                node.move_to([coord[0] + offset_x, coord[1], coord[2]])

            node_dots = [Dot(point=[coord[0] + offset_x, coord[1], coord[2]]) for coord in coordinates]

            # Initialize edges
            edges, edge_map = [], {} # might need to keep a global variable so that this doesn't get overwritten everytime we're dealing with a new party
            for i in range(party_num_qudits):
                for j in range(i + 1, party_num_qudits):
                    if (j, i) not in edge_map:
                        edge = Line(node_dots[i].get_center(), node_dots[j].get_center())
                        edge_map[(i, j)] = edge
                        edges.append(edge)

            sphere_group = VGroup(*nodes)
            node_group = VGroup(*node_dots)
            edge_group = VGroup(*edges)

            self.play(Create(sphere_group), Create(node_group), Create(edge_group))

        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES)

        # Add labels to nodes
        for i, dot in enumerate(node_group):
            label = Tex(f"{i}")
            label.next_to(dot, DOWN if i in [3, 4] else UP)  # Avoid sphere-label overlap
            self.play(Create(label))
        
        # add functionality to zoom into party that is being measured

    def ee_models(self):
        num_parties = len(self.k_party_obj.state_desc)
        print(num_parties)
        parties = []
        for i in range(num_parties):
            parties.append(self.k_party_obj.state_desc[i])

        # 
    
    def model_individual_EEs(self):
        party_one = self.k_party_obj.state_desc[0] # VERY IMPORTANT!! UNDERSTAND STATE_DESC ATTRIBUTE -- ATM HARD CODED FOR ONE PARTY
        num_qudits = party_one[0]
        for i in range(num_qudits):
            for j in range(i + 1, num_qudits):
                try:
                    print(f"Processing nodes {i} and {j}")

                    # Display EE information
                    my_text = Text(f"Entanglement entropy for nodes {i} and {j}").to_edge(UP)
                    self.play(Create(my_text))
                    self.wait(1)
                    self.play(Uncreate(my_text))

                    # Calculate bipartite entropy
                    A, B = set([i, j]), set(range(num_qudits)) - {i, j}
                    ee = self.k_party_obj.bipartite_entropy(list(A), list(B))
                    
                    '''
                    if self.execution_type == "upper bound":
                        ee = self.entanglement_measures.get_le_lower_bound(self.k_party_obj, A, B)
                    if self.execution_type == "lower bound":
                        ee = self.entanglement_measures.get_le_upper_bound(self.k_party_obj, A, B)
                    '''

                    # Measure and visualize
                    measured = []
                    for state in B:
                        self.measure(state)
                        measured.append(state)
                        self.eeChange(A, measured, ee)
                        self.wait(1)

                    # Display EE results
                    self.display_EE_results(A, B, ee)

                    # Reset the groups for the next iteration
                    self.sphere_group_copy, self.node_group_copy, self.edge_group_copy = map(copy.deepcopy, [self.sphere_group, self.node_group, self.edge_group])

                    # Create the copied groups
                    self.play(Create(self.sphere_group_copy), Create(self.node_group_copy), Create(self.edge_group_copy))

                    # Wait for a moment
                    self.wait(1)
                except Exception as e:
                    print(f"Error processing nodes {i} and {j}: {e}")
                    break  # Break the loop if there is an error, remove this if you want to continue to the next pair

    def display_EE_results(self, A, B, ee):
        A_B_text = Text(f"A = {A} B = {B}").scale(0.50).move_to([0, 3, 0])
        ee_text = Text(f"EE: {ee:.4f}").to_edge(DOWN)
        self.play(Create(A_B_text), Create(ee_text))
        self.play(Uncreate(A_B_text), Uncreate(ee_text))

    def measure(self, state):
        sphere = self.sphere_group[state]
        self.measurement_visualization(state)
        self.play(ScaleInPlace(sphere, scale_factor=0.1, run_time=2))
        random_color = BLUE if np.random.randint(2) == 0 else RED
        self.node_group[state].set_color(random_color)
        self.play(Create(sphere))
        self.remove_edges(state)

    def remove_edges(self, state):
        for i in range(self.k_party_obj.parties):
            if (state, i) in self.edge_map or (i, state) in self.edge_map:
                edge_delete = self.edge_map.get((state, i)) or self.edge_map.get((i, state))
                self.play(Uncreate(edge_delete))

    def eeChange(self, A, measured, ee):
        state1, state2 = list(A)
        edge = self.edge_map[(state1, state2)]
        edge.set_stroke(width=ee * 2 * edge.get_stroke_width())
        self.play(Create(edge))

    def measurement_visualization(self, state):
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        top_left = np.array([-5, 0, 0])
        scale_factor = 0.75
        rectangle = Rectangle(width=4, height=3, color=WHITE).scale(scale_factor).move_to(top_left)
        sphere = Sphere(radius=1).scale(scale_factor).move_to(top_left)
        letter_m = Text(f"M{state}", font_size=48, color=WHITE).scale(scale_factor).move_to(Square(side_length=2).scale(scale_factor))

        self.play(Create(rectangle), Create(sphere))
        self.play(Create(letter_m))
        self.play(Uncreate(letter_m), Uncreate(sphere), Uncreate(rectangle))