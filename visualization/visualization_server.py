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

alice_nodes=1
bob_nodes=1
cecil_nodes=1
n=alice_nodes+bob_nodes+cecil_nodes
graph = nx.Graph()
graph.add_nodes_from(list(range(n)))

graph.add_edges_from([(0,1), (1,2)])
nx.draw(graph)
plt.show()


#GHZ state
def ghz_state_from_qiskit():
    circuit = qiskit.QuantumCircuit(3)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(0, 2)
    circuit.draw("text")
    results=qiskit.quantum_info.Statevector(circuit)
    return results


def graph_state_from_qiskit(graph):
    #print graph circuit
    adj_matrix=nx.to_numpy_matrix(graph)#adjacency_matrix(graph)
    circuit= qiskit.circuit.library.GraphState(adj_matrix)
    circuit.draw("text")
    results=qiskit.quantum_info.Statevector(circuit)
    return results
    
    
state_vector=ghz_state_from_qiskit() 
#state_vector=graph_state_from_qiskit(graph)
state_obj=[{"re":x.real,"im":x.imag} for x in state_vector]
json.dumps(state_obj) 
    


app = Flask(__name__,static_url_path='')

@app.route('/')
def index(): 
    return app.send_static_file('index.html')

@app.route("/state.json")
def send_state():
    state_obj=[{"re":x.real,"im":x.imag} for x in state_vector]
    dims=state_vector.dims()
    o={"state":state_obj,"parties":len(dims),"dims":dims}
    result=json.dumps(o)
    return Response(result, mimetype='application/json')

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:3000/")

thread = threading.Thread(target=open_browser, args=())
thread.daemon = True  
thread.start() 
        

app.run(host='0.0.0.0', port=3000)


