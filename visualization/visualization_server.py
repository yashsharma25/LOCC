import math
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import qiskit
import json

import os
import requests
import mimetypes
from flask import Flask
from flask import Response

import webbrowser
import threading
import time

from entanglement_measures import EntanglementMeasures
from k_party import k_party


alice_nodes=1
bob_nodes=1
cecil_nodes=1
n=alice_nodes+bob_nodes+cecil_nodes
graph = nx.Graph()
graph.add_nodes_from(list(range(n)))
graph.add_edges_from([(0,1), (1,2)])

#GHZ state
def ghz_state_from_qiskit():
    circuit = qiskit.QuantumCircuit(3)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(0, 2)
    circuit.draw("text")
    results=qiskit.quantum_info.Statevector(circuit)
    return results

#W state
def w_state_from_qiskit():
    a=np.sqrt(1/3)
    v=[0,a,a,0,a,0,0,0]
    return qiskit.quantum_info.Statevector(v)

def graph_state_from_qiskit(graph):
    adj_matrix=nx.to_numpy_matrix(graph)
    circuit= qiskit.circuit.library.GraphState(adj_matrix)
    circuit.draw("text")
    results=qiskit.quantum_info.Statevector(circuit)
    return results
    


def prepare_state_data(state_vector):
    tri_party=k_party(3,2,[(1,[2]),(1,[2]),(1,[2])],state_vector)
    state_obj=[{"re":x.real,"im":x.imag} for x in state_vector]
    dims=state_vector.dims()
    e_stats={}
    o={"state":state_obj,"parties":len(dims),"dims":dims,
   "e_stats":e_stats}
    em = EntanglementMeasures(2, tri_party, 2)
    for i in range(len(dims)):
        for j in range(i):
            if i==j: 
                continue
            max_e=em.get_le_upper_bound(tri_party, i, j)
            min_e=em.get_le_lower_bound(tri_party, i, j)
            e_stats[str(i)+","+str(j)]={"max":max_e,"min":min_e}
    result=json.dumps(o)
    return result

        
state_vector=ghz_state_from_qiskit()
#state_vector=w_state_from_qiskit() 
#state_vector=graph_state_from_qiskit(graph)

state_data=prepare_state_data(state_vector)

app = Flask(__name__,static_url_path='')


@app.route('/')
def index(): 
    return app.send_static_file('index.html')

@app.route("/state.json")
def send_state():
    return Response(state_data, mimetype='application/json')

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:3000/")

thread = threading.Thread(target=open_browser, args=())
thread.daemon = True  
thread.start() 
        

app.run(host='0.0.0.0', port=3000)

