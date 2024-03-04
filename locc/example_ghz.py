from qiskit.quantum_info import Statevector
import numpy as np
from entanglement_measures import EntanglementMeasures
from k_party import k_party
from manim import *

# to run visualization: manimce -pql example_ghz.py NodeGraphScene
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

# em = EntanglementMeasures(3, GHZ(3), 3)

# k_party_obj1 = k_party(3, 3, [(1, [3]), (1, [3]), (1, [3])], GHZ(3))
# k_party_obj2 = k_party(3, 3, [(1, [3]), (1, [3]), (1, [3])], GHZ(3))

# em.get_le_upper_bound_evolving([k_party_obj1, k_party_obj2], 0, 1)

#now we compute the nursing numbers for this state
# k_party_obj = k_party(2, 2, [(1, [2]), (1, [2]), (1, [2])], GHZ(2))

# em = EntanglementMeasures(2, GHZ(2), 2)
# em.get_le_upper_bound(k_party_obj, 0, 1)

# k_party_obj = k_party(3, 3, [(1, [3]), (1, [3]), (1, [3])], GHZ(3))

# em = EntanglementMeasures(3, GHZ(3), 2)
# em.get_le_upper_bound(k_party_obj, 0, 1)
# em.get_le_upper_bound(k_party_obj, 1, 2)
# em.get_le_upper_bound(k_party_obj, 0, 1)


# em.get_le_lower_bound(k_party_obj, 0, 2)
# em.get_le_lower_bound(k_party_obj, 0, 1)
# em.get_le_lower_bound(k_party_obj, 1, 2)

# em.get_le_lower_bound(k_party_obj, 0, 2)

# em = EntanglementMeasures(2, GHZ_tensored_another(2), 2)
# k_party_obj = k_party(2, 3, [(1, [2]), (1, [2]), (2, [2, 2])], GHZ_tensored_another(2))

# em.get_le_multiple(k_party_obj, 0, 1)


em = EntanglementMeasures(2, GHZ_5(2), 4)
k_party_obj = k_party(5, 2, [(1, [2]), (1, [2]), (1, [2]), (1, [2]), (1, [2])], GHZ_5(2))

def bipartite_entropy_check():
    q_state_np = k_party_obj.q_state.data.reshape(2,2,2,2,2) # 5 state quantum system - 2 for the 2 dimensionality of qubits
    print("Shape before = ", q_state_np.shape)
    reshape_tuple = (1,4,0,2,3) # group 1,2 and 3,4,5 into two groups
    q_state_np = np.transpose(q_state_np, reshape_tuple)
    q_state_np = np.reshape(q_state_np, (4,8))

    print(q_state_np.shape)


# em = EntanglementMeasures(2, GHZ_4(2), 3)
# k_party_obj = k_party(4, 2, [(1, [2]), (1, [2]), (1, [2]), (1, [2])], GHZ_4(2))

# em.get_le_upper_bound(k_party_obj, 0, 1)


# for i in range(0, 4):
#     for j in range(i+1, 4):
#         print("i = ", i)
#         print("j = ", j)
#         # em.get_le_upper_bound(k_party_obj, i, j)
#         # em.get_le_lower_bound(k_party_obj, i, j)
#         A = set([i,j])
#         B = set(np.arange(4))

#         # Get new set with elements that are only in a but not in b
#         B = B.difference(A)
#         print("A = ", A, " B = ", B)
#         ee = k_party_obj.bipartite_entropy(list(A), list(B))
#         print('EE = ', ee)

class NodeGraphScene(ThreeDScene):
    def construct(self):
        # text main
        my_text = Text("Modeling Entaglement Entropy: GHZ State")
        my_text.to_edge(UP)
        self.play(Create(my_text))
        self.wait(2)
        self.play(Uncreate(my_text))

        self.move_camera(phi=65*DEGREES, theta=45*DEGREES)
        
        # Define nodes
        numParties = k_party_obj.parties
        nodes = [Sphere(radius=0.3, color=YELLOW) for _ in range(numParties)]

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
        edge_indices, edges = [], []
        for i in range(numParties):
            for j in range(i+1, numParties):
                edge_indices.append((i,j)) # append edge as tuple
                edges.append(Line(node_dots[i].get_center(), node_dots[j].get_center()))
        
        # Add nodes and edges to the scene
        self.play(*[Create(node) for node in nodes])
        self.play(*[Create(dot) for dot in node_dots])
        self.play(*[Create(edge) for edge in edges])

        # move camera
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

        # model individual EEs
        edge_index = 0 # for obtaining correct edge
        for i in range(0, numParties):
            for j in range(i+1, numParties):

                # text main loop
                text_str = f"Entaglement entropy for nodes {i} and {j}"
                my_text = Text(text_str)
                my_text.to_edge(UP) # top of scene/screen
                self.play(Create(my_text))
                self.wait(2)
                self.play(Uncreate(my_text))
                
                # set up calcs for ee
                A = set([i,j])
                B = set(np.arange(5))
                B = B.difference(A)

                # get ee
                ee = k_party_obj.bipartite_entropy(list(A), list(B))

                # intialization for new edges
                for x in range(len(edges)):
                    
                    # get mob for line/edge
                    line = edges[x]
                    if x == edge_index: # make this line bigger - using ee as scale factor

                        # save thickness to revert back after visuals
                        prev_width_main = line.get_stroke_width()
                        
                        # Set the scaling factor
                        scaling_factor = ee * 3 # since ee = 0.9999 will work for now, but later may need to divide raw ee value by some # to scale correctly

                        # Increase the thickness based on the scaling factor
                        line.set_stroke(width=scaling_factor * line.get_stroke_width())

                        # line.scale(3)
                    else: # temporarily delete line -- maybe change it's color to black?
                        
                        # save thickness to revert back after visuals
                        prev_width_others = line.get_stroke_width()

                        # Set the scaling factor
                        scaling_factor = 0.2

                        # decrease the thickness (almost completely based on the scaling factor
                        line.set_stroke(width=scaling_factor * line.get_stroke_width())
                
                # add updated edges to scene
                self.play(*[Create(edge) for edge in edges])

                '''
                for x in range(len(edges)): # attempt at apply wave - still in progress
                    line = edges[x]
                    if  x == edge_index:
                        self.play(*[Create(line)])
                        self.play(ApplyWave(line, rate_func=linear, ripples=5))
                    else:
                        self.play(*[Create(line)])
                '''

                # text AB
                A_str, B_str= f"A = {A}", f" B = {B}"
                A_B_str = A_str + B_str
                A_B_text = Text(A_B_str)
                A_B_text.move_to([0,3,0])
                A_B_text.to_edge(UP)
                self.play(Create(A_B_text))
                self.wait(1)

                # text ee
                ee_str = f"Entaglement Entropy: {ee}"
                ee_text = Text(ee_str)
                ee_text.to_edge(DOWN)
                self.add(ee_text)
                self.play(Create(ee_text))
                self.wait(2)

                # remove AB, ee text
                # self.remove(A_B_text)
                # self.remove(ee_text)
                self.play(Uncreate(A_B_text))
                self.play(Uncreate(ee_text))
                
                
                # intialization for new edges
                for x in range(len(edges)):
                    
                    # get mob for line/edge
                    line = edges[x]
                    if x == edge_index: # make this line bigger - using ee as scale factor
                        # revert width to original
                        line.set_stroke(width=prev_width_main)
                    else: # temporarily delete line -- maybe change it's color to black?
                        line.set_stroke(width=prev_width_others)
                
                # add updated edges to scene --don't know if we need to do this; doesn't look clean
                self.play(*[Create(edge) for edge in edges])
                
                edge_index += 1
'''
                if j == 2:
                    break
            if i == 1:
                break
'''
'''
for i in range(0, 5):
    for j in range(i+1, 5):
        print("i = ", i)
        print("j = ", j)
        # em.get_le_upper_bound(k_party_obj, i, j)
        # em.get_le_lower_bound(k_party_obj, i, j)
        A = set([i,j])
        B = set(np.arange(5))

        # Get new set with elements that are only in a but not in b
        B = B.difference(A)
        print("A = ", A, " B = ", B)
        ee = k_party_obj.bipartite_entropy(list(A), list(B))
        print('EE = ', ee)
'''

#em.get_le_lower_bound(k_party_obj, 0, 1)