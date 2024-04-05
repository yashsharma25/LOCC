from qiskit.quantum_info import Statevector
import numpy as np
from entanglement_measures import EntanglementMeasures
from k_party import k_party
from manim import *
import copy

# to run visualization: manimce -pql ghz_example_visualization.py NodeGraphScene
# or go to locc/media/videos/example_ghz/1080p60 for prev compiled video

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


class NodeGraphScene(ThreeDScene):
    def construct(self):
####################################################################################################################
        # INITIALIZATION
        my_text = Text("Modeling Entaglement Entropy: GHZ State")
        my_text.to_edge(ORIGIN)
        self.play(Create(my_text))
        self.wait(1)
        self.play(Uncreate(my_text))

        # nice side angle to show 3D spheres
        self.move_camera(phi=65*DEGREES, theta=45*DEGREES)
        
        # Define nodes
        numParties = k_party_obj.parties
        nodes = [Sphere(radius=0.3, color=BLUE) for _ in range(numParties)]

        # Specify numerical coordinates for the nodes
        coordinates = [(np.cos(angle), np.sin(angle), 0) for angle in np.linspace(0, 2 * np.pi, 5, endpoint=False)]
        
        # Scaling factor to adjust the spread
        scaling_factor = 2.0  # Adjust this value as needed
        
        # Apply scaling to the coordinates     
        coordinates = [(scaling_factor * x, scaling_factor * y, scaling_factor * z) for x, y, z in coordinates]

        # move nodes to coords
        for node, coord in zip(nodes, coordinates):
            node.move_to(coord) 

        # Create Manim objects for nodes
        node_dots = [Dot(point=coord) for coord in coordinates]

        # initialize edges
        edges, edge_map = [], {}
        for i in range(numParties):
            for j in range(i+1, numParties):
                if (j,i) in edge_map: # to catch for repeat edges
                    continue
                else:
                    edge = Line(node_dots[i].get_center(), node_dots[j].get_center())
                    edge_map[(i,j)] = edge
                    edges.append(edge)
        
        # create VGroups
        sphere_group, node_group, edge_group = VGroup(*nodes), VGroup(*node_dots), VGroup(*edges)
        sphere_group_copy, node_group_copy, edge_group_copy = copy.deepcopy(sphere_group), copy.deepcopy(node_group), copy.deepcopy(edge_group)
        # Display the grouped objects in the scene using self.play()
        self.play(Create(sphere_group), Create(node_group), Create(edge_group))

        # move camera to the normal "birds eye" view
        self.move_camera(phi=0*DEGREES, theta=-90*DEGREES)

        # Add a label to the nodes
        for i in range(numParties):
            label = Tex(f"{i}")
            if (i==3) or (i==4):
                label.next_to(node_dots[i], DOWN)
            else:
                label.next_to(node_dots[i], UP)
            
            # Add the label to the scene
            self.play(Create(label))

        # MODEL INVIDUAL EEs
        for i in range(0, numParties):
            for j in range(i+1, numParties):

                # text main loop
                my_text = Text(f"Entaglement entropy for nodes {i} and {j}")
                my_text.to_edge(UP) # top of scene/screen
                self.play(Create(my_text))
                self.wait(1)
                self.play(Uncreate(my_text))
                
                # set up set for ee and get ee
                A, B = set([i,j]), set(np.arange(5))
                B = B.difference(A)
                print()
                ee = k_party_obj.bipartite_entropy(list(A), list(B))

                A_B_text = Text(f"A = {A}" + f" B = {B}")
                A_B_text.move_to([0,3,0])
                self.play(Create(A_B_text))
                ee_string = f"EE: {ee:.4f}"
                ee_text = Text(ee_string)
                ee_text.to_edge(DOWN)
                self.play(Create(ee_text))

                # measure each state in B, and show change in EE
                measured = []
                for state in B:
                    self.measure(sphere_group, node_group, state, edge_map)
                    measured.append(state)
                    self.eeChange(A, edge_map, measured, ee)
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
        sphere = sphere_group[state]
        self.measurement_visualization(state)
        self.play(ScaleInPlace(sphere, scale_factor=0.1, run_time=2))
        random_number = np.random.randint(2)
        if random_number == 0:
            node_group[state].set_color(BLUE)
        if random_number == 1:
            node_group[state].set_color(RED)
        self.play(Create(sphere))
        for i in range(k_party_obj.parties): # check this
            if (state,i) in edge_map:
                edge_delete = edge_map[(state, i)]
            if (i, state) in edge_map:
                edge_delete = edge_map[(i, state)]
            self.play(Uncreate(edge_delete))
        pass
    '''
    simulates change in entaglement entropy by changing
    the thickness of the edge between state i and state j
    '''
    # 
    def eeChange(self, A, edge_map, measured, ee):
        A_list = list(A)
        state1, state2 = A_list[0], A_list[1]
        # ee = getEEChange(state1, state2, measured) # state1 and state2 are states not being measured (set A) and measured is the set of states (in B) that have already been measured
        edge = edge_map[(state1, state2)] # get correct edge
        scaling_factor = ee * 2
        edge.set_stroke(width=scaling_factor * edge.get_stroke_width()) # Increase the thickness based on the scaling factor
        self.play(Create(edge))
        pass

    ''' "pop-up" rectangle screen to show applicaiton of measurement matrix'''
    def measurement_visualization(self, state):
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
        letter_m = Text("M" + str(state) + " ", font_size=48, color=WHITE)
        letter_m.scale(scale_factor)

        # Position the letter 'M' at the center of the square
        letter_m.move_to(square)

        # Create a VGroup to combine the square and the letter 'M'
        square_with_m = VGroup(square, letter_m)
        square_with_m.move_to(top_left)
        self.play(Create(square_with_m))
        self.play(Uncreate(square_with_m), Uncreate(sphere), Uncreate(rectangle))



''' for testing purposes of above measurement_visualization method'''
class Measurement1(ThreeDScene):
    def construct(self):
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