
import os
import sys
module_path = os.path.abspath(os.path.join('../locc'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
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
from flask import request

import webbrowser
import threading
import time

from k_party import k_party
from entanglement_measures import EntanglementMeasures



#custom state
def custom_state_with_dims(vec,dims):
    s=0
    for x in vec: s=s+abs(x)*abs(x)#complex x
    a=np.sqrt(s)
    v=[x/a for x in vec]
    return qiskit.quantum_info.Statevector(v,dims)


graph = nx.Graph()
graph.add_nodes_from(list(range(3)))
graph.add_edges_from([(0,1),(0,2),(1,2)])

def graph_state_from_qiskit(graph):
    adj_matrix=nx.to_numpy_matrix(graph)
    circuit= qiskit.circuit.library.GraphState(adj_matrix)
    results=qiskit.quantum_info.Statevector(circuit)
    return results
    


def prepare_state_data(state_vector,name):
    dims=state_vector.dims()
    k_party_dims=[ (1,[x]) for x in dims ]
    N=max(dims)
    k_party_obj=k_party(len(dims),N,k_party_dims,state_vector)
    state_obj=[{"re":x.real,"im":x.imag} for x in state_vector]
    
    e_stats={}
    o={"state":state_obj,"name":name,"parties":len(dims),"dims":dims,
   "e_stats":e_stats}
    
    em = EntanglementMeasures(N, k_party_obj, 2)
    for i in range(len(dims)):
        for j in range(i):
            if i==j: 
                continue
            max_e=em.get_le_upper_bound(k_party_obj, i, j)
            min_e=em.get_le_lower_bound(k_party_obj, i, j)
            e_stats[str(i)+","+str(j)]={"max":max_e,"min":min_e}
    result=json.dumps(o)
    return result

def prepare_state_data_evolving(statev1,statev2,name):
    party_arr=[]
    steps=5
    dims=statev1.dims()
    k_party_dims=[ (1,[x]) for x in dims ]
    N=max(dims)
    k_party_obj=k_party(len(dims),N,k_party_dims,statev1)
    for i in range(steps):
        state_vector=custom_state_with_dims((i*statev1+(steps-i)*statev2/steps),dims)
        if state_vector.is_valid() == False: print ("Error: invalid state")
        #this normalizes the interpolated state
        k_party_obj_2=k_party(len(dims),N,k_party_dims,state_vector)
        party_arr.append(k_party_obj_2)
    state_obj=[{"re":x.real,"im":x.imag} for x in statev1]
    state_obj2=[{"re":x.real,"im":x.imag} for x in statev2]
    dims=statev1.dims()
    e_stats={}
    o={"state":state_obj,"state2":state_obj2,"name":name,"parties":len(dims),"dims":dims,
   "e_stats":e_stats,"is_changing":True,"steps":steps}    
    em = EntanglementMeasures(N, k_party_obj_2, 2)
    for i in range(len(dims)):
        for j in range(i):
            if i==j: 
                continue
            max_e=em.get_le_upper_bound_evolving(party_arr, i, j)
            min_e=em.get_le_lower_bound_evolving(party_arr, i, j)
            #max_e=[(x*1+(steps-x)*(2/3))/steps for x in range(steps)]
            #min_e=[(x*0+(steps-x)*(1/3))/steps for x in range(steps)]
            e_stats[str(i)+","+str(j)]={"max":max_e,"min":min_e}
    result=json.dumps(o)
    return result

def init_states():
    for name in named_states:
        print("processing " +name)
        data=named_states[name]
        if len(data)==2:
            state=custom_state_with_dims(data[1],data[0])
            states[name]=prepare_state_data(state,name)
        else:
            state1=custom_state_with_dims(data[1],data[0])
            state2=custom_state_with_dims(data[2],data[0])
            states[name]=prepare_state_data_evolving(state1,state2,name)
        
named_states={
    "ghz":( (2,2,2), [1,0,0,0,0,0,0,1] ),
    "w":  ( (2,2,2), [0,1,1,0,1,0,0,0]),
    "epr": ( (2,2,2), [1,1,0,0,0,0,1,1] ),
    "ghz4": ( (2,2,2,2), [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1] ),
    "322": ( (3,2,2), [1,1,0,0,0,0,1,1,0,0,0,0] ), #error!
    "ghz3":  ( (3,3,3),  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]),
    "changing":( (2,2,2), [1,0,0,0,0,0,0,1], [0,1,1,0,1,0,0,0]),
}

states={}

init_states()
state_name="ghz4"
user_state=states["ghz4"]



app = Flask(__name__,static_url_path='')

@app.route('/')
def index(): 
    return app.send_static_file('index.html')

@app.route('/favicon.ico')
def favicon(): 
    return app.send_static_file('favicon.ico')

@app.route('/d3.js')
def d3js(): 
    return app.send_static_file('d3.js')

@app.route('/<name>')
def index_state(name): 
    global state_name 
    global user_state
    if name in states: 
        state_name = name
        user_state=states[state_name]
        print(name, state_name)
    else:
        strs=name.split(",") #eg. each number is like 1+2j
        array=[complex(x) for x in strs]
        user_state=prepare_state_data(custom_state_from_qiskit(array),name)
        state_name=name
        states[name]=user_state
    #if state_name not in states: state_name="ghz"
        print(name, state_name,array)
    return app.send_static_file('index.html')

@app.route("/state.json")
def send_state():
    global state_name 
    global user_state
    print(state_name)
    return Response(user_state, mimetype='application/json')

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:3000/")

thread = threading.Thread(target=open_browser, args=())
thread.daemon = True  
thread.start() 
        

app.run(host='0.0.0.0', port=3000)


