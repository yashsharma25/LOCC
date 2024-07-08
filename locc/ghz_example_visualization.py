from qiskit.quantum_info import Statevector
import numpy as np
from entanglement_measures import EntanglementMeasures
from k_party import k_party
from manim import *
from manim import Scene, Sphere, Line, interpolate, TAU
import copy

'''
to run visualization: manimce -pql ghz_example_visualization.py NodeGraphScene
or go to locc/media/videos/example_ghz/1080p60 for previously compiled video
'''

def GHZ(dims):
    psi = np.zeros((dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten(), (dims, dims, dims))
    # ghz = ghz.tensor(Statevector.from_label('0'))
    # print(ghz)
    return ghz
    #print("Norm of state =", norm(psi.flatten()))

def GHZ_4(dims):
    psi = np.zeros((dims, dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten(), (dims, dims, dims, dims))
    #print(ghz)
    return ghz

def GHZ_5(dims):
    psi = np.zeros((dims, dims, dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten(), (dims, dims, dims, dims, dims))
    #print(ghz)
    return ghz

def GHZ_tensored_another(dims):
    psi = np.zeros((dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten(), (dims, dims, dims))
    
    ghz_tensored_another = ghz.tensor(Statevector.from_label('0'))
    print(ghz_tensored_another)
    return ghz_tensored_another


# 1/sqrt(2) |00000> + |11110>
def GHZ_3_tensored_another(dims):
    psi = np.zeros((dims, dims, dims))

    np.fill_diagonal(psi, np.sqrt(1/dims))
    ghz = Statevector(psi.flatten(), (dims, dims, dims))
    ghz_tensored_another = ghz.tensor(Statevector.from_label('00'))

    #print(ghz)
    return ghz_tensored_another

em = EntanglementMeasures(2, GHZ_5(2), 4)
k_party_obj = k_party(5, 2, [(1, [2]), (1, [2]), (1, [2]), (1, [2]), (1, [2])], GHZ_5(2))

def bipartite_entropy_check():
    q_state_np = k_party_obj.q_state.data.reshape(2,2,2,2,2) # 5 state quantum system - 2 for the 2 dimensionality of qubits
    print("Shape before = ", q_state_np.shape)
    reshape_tuple = (1,4,0,2,3) # group 1,2 and 3,4,5 into two groups
    q_state_np = np.transpose(q_state_np, reshape_tuple)
    q_state_np = np.reshape(q_state_np, (4,8))

    print(q_state_np.shape)


class ThreeDPlay(ThreeDScene):
    def construct(self):
        # nice side angle to show 3D spheres
        self.move_camera(phi=65*DEGREES, theta=90*DEGREES)
        
        # create sphere1
        sphere1 = Sphere(radius = 0.5)
        sphere1.set_color(BLUE)
        sphere1_coords = [1, 0, 0]
        sphere1.move_to(sphere1_coords)
        self.play(Create(sphere1))

        # create sphere2
        sphere2 = Sphere(radius=0.5)
        sphere2.set_color(PINK)
        sphere2_coords = [-1, 0, 0]
        sphere2.move_to(sphere2_coords)
        self.play(Create(sphere2))
        
        # create edge between sphere1 and sphere2
        edge = Line(sphere1_coords, sphere2_coords)
        line = Line(LEFT, RIGHT)
        self.play(ApplyWave(edge, direction=UP, amplitude=0.5, wavelength=1, run_time=5))
        self.wait(3)

class WaveExample(Scene):
    def construct(self):
        # Create a Line object
        line = Line(start=[-3, 0, 0], end=[3, 0, 0], color=WHITE)

        # Add the Line object to the scene
        self.add(line)

        # Apply a wave effect to the Line
        self.play(ApplyWave(line, direction=UP, amplitude=0.3, wavelength=1))
        self.wait(2)

class ApplyingWaves(Scene):
    def construct(self):
        tex = Tex("WaveWaveWaveWaveWave").scale(2)
        self.play(ApplyWave(tex))
        self.play(ApplyWave(
            tex,
            direction=RIGHT,
            time_width=0.5,
            amplitude=0.3
        ))
        self.play(ApplyWave(
            tex,
            rate_func=linear,
            ripples=4
        ))

class PairWiseEntanglement(ThreeDScene):
    def construct(self):
####################################################################################################################
        # INITIALIZATION
        
        my_text = Text("Pair Wise Entanglement")
        my_text.scale(0.75).to_edge(ORIGIN)
        self.play(Create(my_text))
        self.wait(1)
        self.play(Uncreate(my_text))

        # nice side angle to show 3D spheres
        self.move_camera(phi=65*DEGREES, theta=45*DEGREES)
        
        # Define spheres
        numParties = k_party_obj.parties
        spheres = [Sphere(radius=0.3, color=BLUE) for _ in range(numParties)]

        # Specify numerical coordinates for the spheres
        coordinates = [(np.cos(angle), np.sin(angle), 0) for angle in np.linspace(0, 2 * np.pi, 5, endpoint=False)]
        
        # Scaling factor to adjust the spread
        scaling_factor = 2.0  # Adjust this value as needed
        
        # Apply scaling to the coordinates     
        coordinates = [(scaling_factor * x, scaling_factor * y, scaling_factor * z) for x, y, z in coordinates]

        # move nodes to coords
        for sphere, coord in zip(spheres, coordinates):
            sphere.move_to(coord) 

        # Create Manim objects for nodes
        nodes = [Dot(point=coord) for coord in coordinates]

        # initialize edgesAbout
        edges, self.edge_map = [], {}
        for i in range(numParties):
            for j in range(i+1, numParties):
                if (j,i) in self.edge_map: # to catch for repeat edges
                    continue
                else:
                    edge = Line(nodes[i].get_center(), nodes[j].get_center())
                    self.edge_map[(i,j)] = edge
                    edges.append(edge)
        
        # create VGroups
        sphere_group, node_group, edge_group = VGroup(*spheres), VGroup(*nodes), VGroup(*edges)
        sphere_group.scale(0.75)
        node_group.scale(0.75)
        edge_group.scale(0.75)
        sphere_group_copy, node_group_copy, edge_group_copy = copy.deepcopy(sphere_group), copy.deepcopy(node_group), copy.deepcopy(edge_group)
        # Display the grouped objects in the scene using self.play()
        self.play(Create(sphere_group), Create(node_group), Create(edge_group))

        # move camera to the normal "birds eye" view
        self.move_camera(phi=0*DEGREES, theta=-90*DEGREES)

        # Add a label to the nodes
        for i in range(numParties):
            label = Tex(f"{i}")
            if (i==3) or (i==4):
                label.next_to(nodes[i], DOWN)
            else:
                label.next_to(nodes[i], UP)
            
            # Add the label to the scene
            self.play(Create(label))

        # MODEL INVIDUAL EEs
        for i in range(0, numParties):
            for j in range(i+1, numParties):

                # text main loop
                my_text = Text(f"Entaglement entropy for nodes {i} and {j}")
                my_text.scale(0.75).to_edge(UP) # top of scene/screen
                self.play(Create(my_text))
                self.wait(1)
                self.play(Uncreate(my_text))
                
                # set up set for ee and get ee
                A, B = set([i,j]), set(np.arange(5))
                B = B.difference(A)
                print()
                ee = k_party_obj.bipartite_entropy(list(A), list(B))

                A_B_text = Text(f"A = {A}" + f" B = {B}")
                A_B_text.scale(0.50).move_to([0,3.5,0])
                self.play(Create(A_B_text))
                ee_string = f"EE: {ee:.4f}"
                ee_text = Text(ee_string)
                ee_text.scale(0.50).to_edge(DOWN)
                self.play(Create(ee_text))

                # measure each state in B, and show change in EE
                measured = []
                for state in B:
                    self.measure(sphere_group, node_group, state, self.edge_map)
                    measured.append(state)
                    self.eeChange(A, self.edge_map, measured, ee)
                    self.wait(1)
                self.play(Uncreate(A_B_text), Uncreate(ee_text))
                # reset for the next A set
                self.play(Create(sphere_group_copy), Create(node_group_copy), Create(edge_group_copy))
                self.wait(1)
                break # for initial testing purposes, just do 1 pair of groupings
            break
    
    '''simulates the act of measurement by shrinking respective sphere, representative of quantum state being measured 
    also incorporates randomness of measurement with np.random.randint()'''
    def measure(self, sphere_group, node_group, state, edge_map):
        sphere_measure = sphere_group[state]
        # self.measurement_visualization(state)
        # state = 1 # for testing purposes...
        scale_factor = 0.75

        # text main loop
        my_text = Text(f"Measurement of S" + str(state))
        my_text.to_edge(UL) # top of scene/screen
        my_text.scale(0.5)
        self.play(Create(my_text)) 

        self.set_camera_orientation(phi=0 * DEGREES, theta=-90* DEGREES)
        top_left = np.array([-5,0,0]) # just a reference coord

        # create a rectangle for the "mini-video" effect
        rectangle_width, rectangle_height = 2 * (1 + 1.05), 2 * (1 + 2)

        # Calculate the new position for the rectangle centered below the text
        # Position the rectangle directly below the text
        rectangle_center_x = my_text.get_center()[0]  # X-coordinate of text
        rectangle_center_y = my_text.get_center()[1] - rectangle_height / 2  # Y-coordinate of text - half height of rectangle

        # Create the rectangle
        rectangle = Rectangle(width=rectangle_width, height=rectangle_height, color=BLUE)
        rectangle.move_to([rectangle_center_x, rectangle_center_y - 0.5, 0])  # Set the new center position
        self.add(rectangle)

        # Create a sphere in 3D space
        sphere = Sphere(radius=1)
        sphere.scale(scale_factor)
        sphere.move_to(rectangle.get_center())
        self.play(Create(sphere))
        self.wait(1)

        # create standard basis for 0
        matrix0 = Matrix([[1,0], [0,0]])
        matrix0.set_color(WHITE)
        matrix0.scale(scale_factor-0.25)
        title0 = Text("Standard Basis for 0", font_size=24).scale(scale_factor).next_to(matrix0, UP)
        standard_basis_0 = VGroup(matrix0, title0)
        standard_basis_0.next_to(sphere, UP, buff=0.5)
        self.play(Create(standard_basis_0))
        # self.wait(2)

        matrix1 = Matrix([[0,0], [0,1]])
        matrix1.set_color(WHITE)
        matrix1.scale(scale_factor-0.25)
        title1 = Text("Standard Basis for 1", font_size=24).scale(scale_factor).next_to(matrix1, UP)
        standard_basis_1 = VGroup(matrix1, title1)
        standard_basis_1.next_to(sphere, DOWN, buff=0.5)
        self.play(Create(standard_basis_1))

        self.play(ScaleInPlace(sphere_measure, scale_factor=0.1, run_time=2)) # shrinks sphere in "graph"
        random_number = np.random.randint(2)
        if random_number == 0:
            self.play(Uncreate(standard_basis_1))
            node_group[state].set_color(BLUE)
        if random_number == 1:
            self.play(Uncreate(standard_basis_0))
            node_group[state].set_color(RED)
        self.play(Create(sphere_measure))
        for i in range(k_party_obj.parties): # check this
            if (state,i) in self.edge_map:
                edge_delete = self.edge_map[(state, i)]
            if (i, state) in self.edge_map:
                edge_delete = self.edge_map[(i, state)]
            self.play(Uncreate(edge_delete))
        self.play(Uncreate(standard_basis_0), Uncreate(standard_basis_1), Uncreate(sphere), Uncreate(rectangle), Uncreate(my_text))
        pass
    '''
    simulates change in entaglement entropy by changing
    the thickness of the edge between state i and state j
    '''
    def eeChange(self, A, edge_map, measured, ee):
        A_list = list(A)
        state1, state2 = A_list[0], A_list[1]
        # ee = getEEChange(state1, state2, measured) # state1 and state2 are states not being measured (set A) and measured is the set of states (in B) that have already been measured
        edge = self.edge_map[(state1, state2)] # get correct edge
        scaling_factor = ee * 2
        edge.set_stroke(width=scaling_factor * edge.get_stroke_width()) # Increase the thickness based on the scaling factor
        self.play(Create(edge))
        self.play(ApplyWave(edge, direction=UP, amplitude=0.5, wavelength=1, run_time=5))
        pass

    ''' "pop-up" rectangle screen to show applicaiton of measurement matrix'''
    def measurement_visualization(self, state):
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90* DEGREES)
        scale_factor = 0.75
        top_left = np.array([-5,0,0])

        # create a rectangle for the "mini-video" effect
        rectangle_width, rectangle_height = 2 * (1 + 1), 2 * (1 + 0.5)
        rectangle = Rectangle(width=rectangle_width, height=rectangle_height, color = WHITE)
        rectangle.scale(scale_factor)
        rectangle.move_to(top_left)
        self.play(Create(rectangle))

        # Create a sphere in 3D space
        sphere = Sphere(radius=1)
        sphere.scale(scale_factor)
        sphere.move_to(top_left)
        self.play(Create(sphere))
        self.wait(1)

        # Create a square
        square = Square(side_length=2)
        square.scale(scale_factor)

        # Create the letter 'M'
        letter_m = Text("M" + str(state) + " ", font_size=48, color=WHITE)
        letter_m.scale(scale_factor)

        # Position the letter 'M' at the center of the square
        letter_m.move_to(square)

        # Create a VGroup to combine the square and the letter 'M'
        square_with_m = VGroup(square, letter_m)
        square_with_m.move_to(top_left)
        self.play(Create(square_with_m))
        self.play(Uncreate(square_with_m), Uncreate(sphere), Uncreate(rectangle))


class ThreeColumnScene(Scene):
    def construct(self):
        # Define constants for column widths and heights
        column_width = config.frame_width / 3.0  # Assuming the frame width is divided into 3 equal columns
        column_height = config.frame_height  # Height of the columns (same as frame height)

        # Define padding values for top, bottom, left, and right sides of rectangles
        top_padding = 0.5  # Padding at the top of each rectangle
        bottom_padding = 0.5  # Padding at the bottom of each rectangle
        left_padding = 0.10 # Padding on the left side of each rectangle
        right_padding = 0.10  # Padding on the right side of each rectangle

        # Create rectangles for each column
        # Column 1 (left column)
        left_rectangle = Rectangle(
            width=column_width - left_padding - right_padding,
            height=column_height - top_padding - bottom_padding,
            color=BLUE
        )

        # Column 2 (middle column)
        middle_rectangle = Rectangle(
            width=column_width - left_padding - right_padding,
            height=column_height - top_padding - bottom_padding,
            color=BLUE
        )

        # Column 3 (right column)
        right_rectangle = Rectangle(
            width=column_width - left_padding - right_padding,
            height=column_height - top_padding - bottom_padding,
            color=BLUE
        )

        # Group rectangles into columns using VGroup (vertical grouping)
        left_column = VGroup(left_rectangle)
        middle_column = VGroup(middle_rectangle)
        right_column = VGroup(right_rectangle)

        # Position rectangles within columns with padding
        left_column.arrange(DOWN, buff=0)
        left_column.shift((column_height - top_padding - bottom_padding) / 2 * DOWN)  # Center vertically
        left_column.shift((column_width - left_padding - right_padding) / 2 * LEFT)  # Center horizontally
        middle_column.arrange(DOWN, buff=0)
        middle_column.shift((column_height - top_padding - bottom_padding) / 2 * DOWN)  # Center vertically
        right_column.arrange(DOWN, buff=0)
        right_column.shift((column_height - top_padding - bottom_padding) / 2 * DOWN)  # Center vertically
        right_column.shift((column_width - left_padding - right_padding) / 2 * RIGHT)  # Center horizontally

        # Position columns horizontally using HGroup (horizontal grouping)
        columns_group = Group(left_column, middle_column, right_column)
        columns_group.arrange(RIGHT, buff=0.1)  # Arrange columns horizontally with no buffer

        # Add columns (rectangles) to the scene
        self.add(columns_group)

        self.wait(2)  # Wait for 2 seconds in the animation



''' for testing purposes of above measurement_visualization method'''
class Measurement1NEW(ThreeDScene):
    def construct(self):
        state = 1 # for testing purposes...
        scale_factor = 0.75

        # text main loop
        my_text = Text(f"Measurement:")
        my_text.to_edge(UL) # top of scene/screen
        my_text.scale(scale_factor)
        self.play(Create(my_text)) 

        self.set_camera_orientation(phi=0 * DEGREES, theta=-90* DEGREES)
        top_left = np.array([-5,0,0]) # just a reference coord

        # create a rectangle for the "mini-video" effect
        rectangle_width, rectangle_height = 2 * (1 + 1.15), 2 * (1 + 2)

        # Calculate the new position for the rectangle centered below the text
        # Position the rectangle directly below the text
        rectangle_center_x = my_text.get_center()[0]  # X-coordinate of text
        rectangle_center_y = my_text.get_center()[1] - rectangle_height / 2  # Y-coordinate of text - half height of rectangle

        # Create the rectangle
        rectangle = Rectangle(width=rectangle_width, height=rectangle_height, color=BLUE)
        rectangle.move_to([rectangle_center_x, rectangle_center_y - 0.5, 0])  # Set the new center position
        self.add(rectangle)

        # Create a sphere in 3D space
        sphere = Sphere(radius=1)
        sphere.scale(scale_factor)
        sphere.move_to(rectangle.get_center())
        self.play(Create(sphere))
        self.wait(1)

        # state label
        state_label = Text("S" + str(state), font_size=48, color=WHITE)
        state_label.set_color(WHITE).scale(scale_factor).move_to(sphere.get_center())
        self.play(Create(state_label))

        # create standard basis for 0
        matrix0 = Matrix([[1,0], [0,0]])
        matrix0.set_color(WHITE)
        matrix0.scale(scale_factor-0.25)
        title0 = Text("Standard Basis for 0", font_size=24).scale(scale_factor).next_to(matrix0, UP)
        standard_basis_0 = VGroup(matrix0, title0)
        standard_basis_0.next_to(sphere, UP, buff=0.5)
        self.play(Create(standard_basis_0))
        # self.wait(2)

        matrix1 = Matrix([[0,0], [0,1]])
        matrix1.set_color(WHITE)
        matrix1.scale(scale_factor-0.25)
        title1 = Text("Standard Basis for 1", font_size=24).scale(scale_factor).next_to(matrix1, UP)
        standard_basis_1 = VGroup(matrix1, title1)
        standard_basis_1.next_to(sphere, DOWN, buff=0.5)
        self.play(Create(standard_basis_1))
        
        self.play(Uncreate(standard_basis_0), Uncreate(sphere), Uncreate(rectangle))
        self.play(Uncreate(my_text))


class NodeGraphScene(ThreeDScene):
    def construct(self):
        self.initialize_scene()
        self.create_nodes_and_edges()
        self.add_labels_to_nodes()
        self.model_individual_EEs()
    
    def initialize_scene(self):
        my_text = Text("Modeling Entanglement Entropy: GHZ State").to_edge(ORIGIN)
        self.play(Create(my_text))
        self.wait(1)
        self.play(Uncreate(my_text))
        self.move_camera(phi=65*DEGREES, theta=45*DEGREES)

    def create_nodes_and_edges(self):
        numParties = k_party_obj.parties
        nodes = [Sphere(radius=0.3, color=BLUE) for _ in range(numParties)]
        coordinates = [(2 * np.cos(angle), 2 * np.sin(angle), 0) for angle in np.linspace(0, 2 * np.pi, numParties, endpoint=False)]

        for node, coord in zip(nodes, coordinates):
            node.move_to(coord)

        node_dots = [Dot(point=coord) for coord in coordinates]
        edges, self.edge_map = self.initialize_edges(numParties, node_dots)

        self.sphere_group = VGroup(*nodes)
        self.node_group = VGroup(*node_dots)
        self.edge_group = VGroup(*edges)
        self.sphere_group_copy, self.node_group_copy, self.edge_group_copy = map(copy.deepcopy, [self.sphere_group, self.node_group, self.edge_group])

        self.play(Create(self.sphere_group), Create(self.node_group), Create(self.edge_group))
        self.move_camera(phi=0*DEGREES, theta=-90*DEGREES)

    def initialize_edges(self, numParties, node_dots):
        edges, self.edge_map = [], {}
        for i in range(numParties):
            for j in range(i + 1, numParties):
                if (j, i) not in self.edge_map:
                    edge = Line(node_dots[i].get_center(), node_dots[j].get_center())
                    self.edge_map[(i, j)] = edge
                    edges.append(edge)
        return edges, self.edge_map

    def add_labels_to_nodes(self):
        for i, dot in enumerate(self.node_group):
            label = Tex(f"{i}")
            label.next_to(dot, DOWN if i in [3, 4] else UP)
            self.play(Create(label))

    def model_individual_EEs(self):
        numParties = k_party_obj.parties
        for i in range(numParties):
            for j in range(i + 1, numParties):
                self.display_EE_info(i, j)
                A, B = set([i, j]), set(range(numParties)) - {i, j}
                ee = k_party_obj.bipartite_entropy(list(A), list(B))

                self.display_EE_results(A, B, ee)
                self.measure_and_visualize(A, B, ee)
                self.play(Create(self.sphere_group_copy), Create(self.node_group_copy), Create(self.edge_group_copy))
                self.wait(1)
                return  # For initial testing purposes, just do 1 pair of groupings

    def display_EE_info(self, i, j):
        my_text = Text(f"Entanglement entropy for nodes {i} and {j}").to_edge(UP)
        self.play(Create(my_text))
        self.wait(1)
        self.play(Uncreate(my_text))

    def display_EE_results(self, A, B, ee):
        A_B_text = Text(f"A = {A} B = {B}").scale(0.50).move_to([0, 3, 0])
        ee_text = Text(f"EE: {ee:.4f}").to_edge(DOWN)
        self.play(Create(A_B_text), Create(ee_text))
        self.play(Uncreate(A_B_text), Uncreate(ee_text))

    def measure_and_visualize(self, A, B, ee):
        measured = []
        for state in B:
            self.measure(state)
            measured.append(state)
            self.eeChange(A, measured, ee)
            self.wait(1)

    def measure(self, state):
        sphere = self.sphere_group[state]
        self.measurement_visualization(state)
        self.play(ScaleInPlace(sphere, scale_factor=0.1, run_time=2))
        random_color = BLUE if np.random.randint(2) == 0 else RED
        self.node_group[state].set_color(random_color)
        self.play(Create(sphere))
        self.remove_edges(state)

    def remove_edges(self, state):
        for i in range(k_party_obj.parties):
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


''' for testing purposes of above measurement_visualization method'''
class Measurement1(ThreeDScene):
    def construct(self):

        # create standard basis for 0
        matrix0 = Matrix([[1,0], [0,0]])
        matrix0.set_color(WHITE)
        matrix0.scale(0.5)
        title0 = Text("Standard Basis for 0", font_size=24).next_to(matrix0, UP)
        standard_basis_0 = VGroup(matrix0, title0)
        # self.play(Create(standard_basis_0))
        # self.wait(2)

        # create standard basis for 1
        matrix1 = Matrix([[0,0], [0,1]])
        matrix1.set_color(WHITE)
        matrix1.scale(0.5)
        title1 = Text("Standard Basis for 1", font_size=24).next_to(matrix1, UP)
        standard_basis_1 = VGroup(matrix1, title1)
        standard_basis_1.next_to(standard_basis_0, DOWN)
        # self.play(Create(standard_basis_1))
        # self.wait(2)

        # create standard bases together
        standard_bases = VGroup(standard_basis_0, standard_basis_1)
        self.play(Create(standard_bases))

        self.set_camera_orientation(phi=0 * DEGREES, theta=-90* DEGREES)
        scale_factor = 0.75
        top_left = np.array([-5,0,0])
        rectangle_width = 2 * (1 + 1)
        rectangle_height = 2 * (1 + 0.5)
        rectangle = Rectangle(width=rectangle_width, height=rectangle_height, color = WHITE)
        rectangle.scale(scale_factor)
        rectangle.move_to(top_left)
        self.play(Create(rectangle))

        # Create a sphere in 3D space
        sphere = Sphere(radius=1)
        sphere.scale(scale_factor)
        sphere.move_to(top_left)
        self.play(Create(sphere))
        self.wait(1)

        # Create a square
        square = Square(side_length=2)
        square.scale(scale_factor)

        # Create the letter 'M'
        letter_m = Text("M" + str(1) + " ", font_size=48, color=WHITE)
        letter_m.scale(scale_factor)

        # Position the letter 'M' at the center of the square
        letter_m.move_to(square)

        # Create a VGroup to combine the square and the letter 'M'
        square_with_m = VGroup(square, letter_m)
        square_with_m.move_to(top_left)
        self.play(Create(square_with_m))
        self.play(Uncreate(square_with_m), Uncreate(sphere), Uncreate(rectangle))
        self.play(Uncreate(standard_bases))

# Basic Single Node Quantum Measurement
class QuantumMeasurement(ThreeDScene):
    def construct(self):
        # text main
        my_text = Text("Modeling Quantum Measurement")
        my_text.to_edge(UP)
        self.play(Create(my_text))
        self.wait(2)
        self.play(Uncreate(my_text))

        self.set_camera_orientation(phi=65 * DEGREES, theta=45* DEGREES)

        # Create a sphere in 3D space
        sphere = Sphere(radius=1)
        self.play(Create(sphere))
        self.wait(1)

        self.move_camera(phi=90 * DEGREES, theta=0 * DEGREES)

        # Zoom in on the sphere
        self.begin_ambient_camera_rotation(rate=0.5)
        self.wait(5)  # Wait for a moment before zooming in for visual clarity

        # Stop camera rotation
        self.stop_ambient_camera_rotation()

        # Define the equation as a Text object
        equation = MathTex(
            r"\mathbf{|} \mathbf{\psi} \mathbf{\rangle} = \alpha \mathbf{|} \mathbf{0} \mathbf{\rangle} + \beta \mathbf{|} \mathbf{1} \mathbf{\rangle}",
            tex_to_color_map={"| \psi \rangle": YELLOW, "|0\rangle": BLUE, "|1\rangle": RED},
        ).scale(0.8)

        # Position the equation to the right of the rotating sphere
        equation.shift(RIGHT*4)  # Adjust the shift as needed

        # Add "Superposition:" text
        superposition_text = Text("Superposition:")
        superposition_text.next_to(equation, UP, buff=0.5)

        self.move_camera(phi=0*DEGREES, theta=-90*DEGREES)

        # Display the equation and "Superposition:" text in the scene
        # self.add(superposition_text, equation)
        self.play(Create(superposition_text))
        self.play(Create(equation))

        # Rotate the sphere to align with the equation
        self.play(Rotate(sphere, angle=PI/2, axis=RIGHT))

        # Add the sphere after rotation
        self.add(sphere)

        # Wait for a few seconds
        self.wait(3)

        # Create a square
        square = Square(side_length=2)
        square.color(BLUE)

        # Create the letter 'M'
        letter_m = Text("M", font_size=48, color=WHITE)

        # Position the letter 'M' at the center of the square
        letter_m.move_to(square)

        # Create a VGroup to combine the square and the letter 'M'
        square_with_m = VGroup(square, letter_m)
        
        square_with_m.to_edge(LEFT)

        measurement_text = Text("Measurement", font_size=30)
        measurement_text.next_to(square_with_m, UP, buff=0.5)

        matrix_text = Text("Matrix", font_size=30)
        matrix_text.next_to(square_with_m, DOWN, buff=0.5)
    
        measurement_matrix_text = VGroup(measurement_text, matrix_text)
        
        # Display the square and the letter 'M'
        self.play(Create(measurement_matrix_text))
        self.play(Create(square_with_m))
        self.add(measurement_text, matrix_text, square_with_m)
        self.wait(1)
        self.play(Uncreate(measurement_matrix_text))
        
        self.play(Create(square_with_m.move_to(ORIGIN)))

        # self.remove(superposition_text, equation)
        self.play(Uncreate(superposition_text))
        self.play(Uncreate(equation))
        self.wait(2)

        self.play(Uncreate(square_with_m))

        text = Text("Qubit collapses with probability 1/2 to 0 or 1:")
        text.to_edge(UP)
        self.play(Create(text))

        self.play(ScaleInPlace(sphere, scale_factor=0.1, run_time=2))

        # Generate a single random number (0 or 1) with probability 1/2
        random_number = np.random.randint(2)
        if random_number == 0:
            color = BLUE
            equation = MathTex(r"\mathbf{|} \mathbf{0} \mathbf{\rangle}").scale(1.5)
        if random_number == 1:
            color = RED
            equation = MathTex(r"\mathbf{|} \mathbf{1} \mathbf{\rangle}").scale(1.5)
        dot = Dot(ORIGIN, color=color)

        equation.next_to(dot, UP, buff=0.5)

        self.add(dot, equation)
        self.play(Uncreate(text))
        self.wait(2)
        self.remove(dot)
        dot = Dot(ORIGIN, radius=1.5, color=color)
        self.add(dot)
        self.wait(1)
        self.remove(equation)

        self.move_camera(phi=65*DEGREES, theta=45*DEGREES)

        # Show the scene
        self.wait(2)