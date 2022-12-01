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



#GHZ state
def ghz_state_from_qiskit():
    circuit = qiskit.QuantumCircuit(3)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(0, 2)
    #circuit.draw("text")
    results=qiskit.quantum_info.Statevector(circuit)
    return results

#W state
def w_state_from_qiskit():
    a=np.sqrt(1/3)
    v=[0,a,a,0,a,0,0,0]
    return qiskit.quantum_info.Statevector(v)

#EPR pair state
def epr_state_from_qiskit():
    a=np.sqrt(1/4)
    v=[a,a,0,0,0,0,a,a]
    return qiskit.quantum_info.Statevector(v)

#custom state
def custom_state_from_qiskit(vec):
    s=0
    for x in vec: s=s+abs(x)*abs(x)#complex x
    a=np.sqrt(s)
    v=[x/a for x in vec]
    return qiskit.quantum_info.Statevector(v)

#custom state
def custom_state_with_dims(vec,dims):
    s=0
    for x in vec: s=s+abs(x)*abs(x)#complex x
    a=np.sqrt(s)
    v=[x/a for x in vec]
    return qiskit.quantum_info.Statevector(v,dims)

#qutrit state
def qutrit_state_from_qiskit():
    return custom_state_with_dims([1,1,0,0,0,0,1,1,0,0,0,0],(3,2,2))

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
    circuit.draw("text")
    results=qiskit.quantum_info.Statevector(circuit)
    return results
    
def test_state_data():
    circuit = qiskit.QuantumCircuit(5)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(0, 2)
    circuit.cx(0, 3)
    circuit.cx(0, 4)
    state_vector=qiskit.quantum_info.Statevector(circuit)
    
    state_obj=[{"re":x.real,"im":x.imag} for x in state_vector]
    dims=state_vector.dims()
    e_stats={}
    o={"state":state_obj,"name":"test","parties":len(dims),"dims":dims,
   "e_stats":e_stats}
    #em = EntanglementMeasures(2, tri_party, 2)
    for i in range(len(dims)):
        for j in range(i):
            if i==j: 
                continue
            #max_e=em.get_le_upper_bound(tri_party, i, j)
            #min_e=em.get_le_lower_bound(tri_party, i, j)
            max_e=2.0/3
            min_e=1.0/3
            e_stats[str(i)+","+str(j)]={"max":max_e,"min":min_e}
    result=json.dumps(o)
    return result

def qutrit_test_state_data():
    vec=[1,1,0,0,0,1,0,1,0,1,1,0]
    dims=(3,2,2)
    s=0
    for x in vec: s=s+abs(x)*abs(x)#complex x
    a=np.sqrt(s)
    v=[x/a for x in vec]
    state_vector=qiskit.quantum_info.Statevector(v,dims)
    state_obj=[{"re":x.real,"im":x.imag} for x in state_vector]
    #state_obj=[{"re":x,"im":0} for x in v]
    #dims=state_vector.dims()
    e_stats={}
    o={"state":state_obj,"name":"qutrits","parties":len(dims),"dims":dims,
   "e_stats":e_stats}
    #em = EntanglementMeasures(2, tri_party, 2)
    for i in range(len(dims)):
        for j in range(i):
            if i==j: 
                continue
            #max_e=em.get_le_upper_bound(tri_party, i, j)
            #min_e=em.get_le_lower_bound(tri_party, i, j)
            max_e=2.0/3
            min_e=1.0/3
            e_stats[str(i)+","+str(j)]={"max":max_e,"min":min_e}
    result=json.dumps(o)
    return result


def prepare_state_data(state_vector,name):
    tri_party=k_party(3,2,[(1,[2]),(1,[2]),(1,[2])],state_vector)
    state_obj=[{"re":x.real,"im":x.imag} for x in state_vector]
    dims=state_vector.dims()
    e_stats={}
    o={"state":state_obj,"name":name,"parties":len(dims),"dims":dims,
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

def prepare_state_data_evolving(statev1,statev2,name):
    #get_le_upper_bound_evolving(self, arr, partyA, partyB)
    #interpolate vectors: 
    party_arr=[]
    steps=5
    tri_party=k_party(3,2,[(1,[2]),(1,[2]),(1,[2])],statev1)
    for i in range(steps):
        state_vector=custom_state_from_qiskit((i*statev1+(steps-i)*statev2)/steps)
        if state_vector.is_valid() == False: print ("Error: invalid state")
        #this normalizes the interpolated state
        tri_party2=k_party(3,2,[(1,[2]),(1,[2]),(1,[2])],state_vector)
        party_arr.append(tri_party2)
    
    
    state_obj=[{"re":x.real,"im":x.imag} for x in statev1]
    state_obj2=[{"re":x.real,"im":x.imag} for x in statev2]
    dims=statev1.dims()
    e_stats={}
    o={"state":state_obj,"state2":state_obj2,"name":name,"parties":len(dims),"dims":dims,
   "e_stats":e_stats,"is_changing":True,"steps":steps}
    em = EntanglementMeasures(2, tri_party, 2)
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

def prepare_state_data2(q_state,name="untitled"):
    
    state_obj=[{"re":x.real,"im":x.imag} for x in state_vector]
    dims=state_vector.dims()
    parties=k_party(len(dims),2,[(1,[2]),(1,[2]),(1,[2])],state_vector)
    e_stats={}
    o={"state":state_obj,"name":name,"parties":len(dims),"dims":dims,
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


states={
        "ghz":prepare_state_data(ghz_state_from_qiskit(),"ghz"),
        "w":prepare_state_data(w_state_from_qiskit(),"w"),
        "epr":prepare_state_data(epr_state_from_qiskit(),"epr"),
        #"000":prepare_state_data(custom_state_from_qiskit([1,0,0,0,0,0,0,0]),"000"),
        #"graph":prepare_state_data(graph_state_from_qiskit(graph),"graph"),
        #"test":test_state_data(),
        "changing":prepare_state_data_evolving(ghz_state_from_qiskit(),w_state_from_qiskit(),"changing"),
    
        #"qutrits":prepare_state_data(qutrit_state_from_qiskit(),"qutrits"), 
        #the above gives an error now
        "qutrits":qutrit_test_state_data(),
    
    }
user_state=states["changing"]

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


