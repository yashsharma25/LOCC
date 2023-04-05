#run this and the next block only

import os
import sys
module_path = os.path.abspath(os.path.join('../locc'))
if module_path not in sys.path:
    sys.path.append(module_path)

# this block and the previous(if you can't include k_party otherwise) is the visualization server.py file
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
    dummy=False
    if "dummy" in name: dummy=True
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
            if dummy:
                max_e=2/3
                min_e=1/3
            else:
                max_e=em.get_le_upper_bound(k_party_obj, i, j)
                min_e=em.get_le_lower_bound(k_party_obj, i, j)
            e_stats[str(i)+","+str(j)]={"max":max_e,"min":min_e}
    result=json.dumps(o)
    return result

def prepare_state_data_evolving(statev1,statev2,name):
    dummy=False
    if "dummy" in name: dummy=True
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
            if dummy:
                max_e=[(x*1+(steps-x)*(2/3))/steps for x in range(steps)]
            else:
                max_e=em.get_le_upper_bound_evolving(party_arr, i, j)
            e_stats[str(i)+","+str(j)]={"max":max_e}
    for i in range(len(dims)):
        for j in range(i):
            if i==j: 
                continue
            if dummy:
                min_e=[(x*0+(steps-x)*(1/3))/steps for x in range(steps)]
            else:
                min_e=em.get_le_lower_bound_evolving(party_arr, i, j)
            e_stats[str(i)+","+str(j)]["min"]=min_e
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
    #"322": ( (3,2,2), [1,1,0,0,0,0,1,1,0,0,0,0] ), #error!
    #"ghz3":  ( (3,3,3),  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]),
    #"changing":( (2,2,2), [1,0,0,0,0,0,0,1], [0,1,1,0,1,0,0,0]),
}
default_state_name="ghz4"
aer_sim = qiskit.Aer.get_backend('aer_simulator')

def init_state(data):
    if len(data)==2:
        state=custom_state_with_dims(data[1],data[0])
        return state #{"state":state,"parties":len(data[0]),"dims":data[0],"is_changing":False}
    else:
        result=[]
        for i in range(1,len(data)):
            result.append(custom_state_with_dims(data[i],data[0]))
        return result 
    #{"state":result[0],"states":result,"parties":len(data[0]),"dims":data[0],"is_changing":True,"steps":len(data)-1}
    
def state2obj(state_vector):
    return [{"re":x.real,"im":x.imag} for x in state_vector]
def obj2state(obj):
    array=[x["re"]+j*x["im"] for x in obj]
    dims=[2 for i in range(int(math.log2(len(array))))]
    return custom_state_with_dims(array,dims)

cached_e_stats={}

class User_state:
    def __init__(self,state=None,states=None,name=None,qc=None):
        self.name=name
        self.state=state
        self.states=states # list of states
        
        if states is None and state is not None and isinstance(state[0],qiskit.quantum_info.Statevector): #detect state list
            self.states=state
            self.state=state[0]
        
        if qc is None and self.state is not None:
            self.num_qubits=len(self.state.dims())
            self.circuit=qiskit.QuantumCircuit(len(self.state.dims()),1) 
            # for now add a few gates for experimenting
            for i in range(self.num_qubits):
                self.circuit.rx(0.5,i)
            for i in range(self.num_qubits):
                self.circuit.ry(0.5,i)
            self.circuit.cx(0,1)
            self.circuit.crz(pi/2,0,1)
            self.circuit.crz(pi/2,1,2)
            self.circuit.measure(0,0)
            self.circuit.x(1).c_if(self.circuit.clbits[0].register, 1)
        else:
            self.circuit=qc
    def get_end_state(self):
        
        new_circuit=qiskit.QuantumCircuit(len(self.state.dims())) 
        new_circuit.initialize(self.state,self.circuit.qubits)
        new_circuit=new_circuit+self.circuit
        results=qiskit.quantum_info.Statevector(new_circuit)
        return results #note: use save state maybe?
    def get_circuit_states(self):
        new_circuit=qiskit.QuantumCircuit(len(self.state.dims()),1) 
        new_circuit.initialize(self.state,self.circuit.qubits)
        states=[]
        states.append(qiskit.quantum_info.Statevector(new_circuit))
        
        for gate in self.circuit.data:
            new_circuit.append(gate)
            states.append(qiskit.quantum_info.Statevector(new_circuit))
        return states
    
    def get_entanglement_stats(self):
        state_vector=self.state
        dims=self.state.dims()
        qubit_count=len(dims)
        k_party_dims=[ (1,[x]) for x in dims ]
        N=max(dims)
        k_party_obj=k_party(qubit_count,N,k_party_dims,state_vector)
        stats=[] #currently just the entanglement between each 1 qubit and everything else
        for i in range(qubit_count):
            A=[i]
            B=[x for x in range(i) ]+[x for x in range(i+1,qubit_count) ]
            stats.append(k_party_obj.bipartite_entropy(A,B))
        return  stats
    def get_entanglement_stats_old(self):
        state_vector=self.state
        text=json.dumps(state2obj(state_vector))
        if text in cached_e_stats:
            return cached_e_stats[text]
        dims=self.state.dims()
        qubit_count=len(dims)
        k_party_dims=[ (1,[x]) for x in dims ]
        N=max(dims)
        k_party_obj=k_party(qubit_count,N,k_party_dims,state_vector)
        em = EntanglementMeasures(N, k_party_obj, 2)
        e_stats={} 
        for i in range(qubit_count):
            for j in range(i):
                print(i,j)
                max_e=em.get_le_upper_bound(k_party_obj, i, j)
                min_e=em.get_le_lower_bound(k_party_obj, i, j)
                e_stats[str(i)+","+str(j)]={"max":max_e,"min":min_e}
        cached_e_stats[text]=e_stats
        return  e_stats
  
# run this for the server. restart only this if you don't need to change the prepared states.
# if you see RuntimeError: The Werkzeug web server is not designed to run in production, 
# do  pip install eventlet gevent
# for now there's a new bug in dnspython, so if you have an error like 
# module 'dns.rdtypes' has no attribute 'ANY', do pip install dnspython==2.2.1

from math import pi
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import mimetypes



app = Flask(__name__,static_url_path='')
#app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

user_states={}


#what states do we cache now?
#init state only when teh ser connects? And then only compute statistics when requested?

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
def index_name(name): 
    possibletype=mimetypes.guess_type(name)
    if possibletype[0] is None:
        #possibly a state selection
        return app.send_static_file('index.html') # state selection now handled by socket.io
    else:
        return app.send_static_file(name)






    
#socket stuff

#now on connect it doesn't just send teh data, but waits for teh client to choose a named or custom state

@socketio.on('connect')
def test_connect(sid):
    print("sid",sid)
    
@socketio.on('set_state')
def set_state(data):
    #print('connected', sid)
    #print (request)
    #print(request.url)
    sid=request.sid
    print("sid2",sid)
    #print("data",data)
    name=data["name"]
    
    user_state=User_state()
    
    if name=="": name=default_state_name
    #todo get name
    state_data=named_states[name]
    if name in named_states: 
        user_state=User_state(name=name,state=init_state(named_states[name]))
        print("state name",name)
    else:
        strs=name.split(",") #eg. each number is like 1+2j
        array=[complex(x) for x in strs]
        dims=[2 for i in range(int(math.log2(len(array))))]
        user_state=User_state(name="custom",state=prepare_state_data(custom_state_with_dims(array,dims)))
        print(name, array)
    user_states[sid]=user_state #set to the named state based on the user URL
    #emit('after connect',  {'data':'hello!'})
    send_data(sid,None)

    
@socketio.on('get_data')
def send_data(sid,input_data):
    #state_vector,name
    user_state=user_states[sid]
    state_vector=user_state.state
    dims=state_vector.dims()
    obj={"name":user_state.name,"state":state2obj(user_state.state),"dims":dims,"num_qubits":len(dims)}
    if user_state.states is not None:
        statesobj=[]
        obj["states"]=statesobj
        for state in user_state.states: 
            statesobj.append(state2obj(state))
    
    if user_state.circuit==None:
        pass
        #circuit.initialize(state_vector,circuit.qubits) 
        # add the start state on evaluation only? because it can change
    else:
        circuit=user_state.circuit
        qubits=[]
        for qubit in circuit.qubits:
            qubits.append({"name":qubit.register.name,
                          "index":qubit.index
                         })
        obj["qubits"]=qubits
        clbits=[]
        for clbit in circuit.clbits:
            clbits.append({"name":clbit.register.name,
                          "index":clbit.index
                         })
        obj["clbits"]=clbits
        
        gates=[]
        #print(circuit.draw("text"))
        for gate in circuit.data:
            cond=None
            if  gate[0].condition!= None: 
                if hasattr(gate[0].condition[0],"register"): # a clbit
                    x=gate[0].condition[0] #the bit
                    cond = {"index":x.index,"name":x.register.name,"value":gate[0].condition[1]} 
                else: #a register
                    x=gate[0].condition[0] #the bit
                    cond = {"index":0,"name":x.name,"value":gate[0].condition[1]} 
            gates.append({"name":gate[0].name,
                          "qubits":[{"index":x.index,"name":x.register.name} for x in gate[1]],
                          "clbits":[{"index":x.index,"name":x.register.name} for x in gate[2]],
                          "params":gate[0].params,
                          "condition":cond
                         })
        obj["gates"]=gates
    # and the end state (if there's a circuit and unmeasured qubits)
    obj["circuit_text"]=str(circuit.draw("text")) 
    obj["circuit_latex"]=circuit.draw("latex_source")
    #end_state=user_state.get_end_state()
    #obj["end_state"]=state2obj(end_state)
    
    #circuit_states=user_state.get_circuit_states()
    #obj["circuit_states"]=[state2obj(state) for state in circuit_states]
    
    obj["entanglement_stats"]=user_state.get_entanglement_stats()
    obj["e_stats"]=user_state.get_entanglement_stats_old()
    
    obj["qasm"]=circuit.qasm()
    
    result=json.dumps(obj)
    print(result)
    socketio.emit('data',  obj )
    
@socketio.on('set_data')
def set_data(data):
    #state_vector,name
    print("setting data")
    sid=request.sid
    user_state=user_states[sid]
    #can set name state, states and/or circuit separately
    if "name" in data:
        user_state.name=data["name"];
    if "state" in data:
        state=obj2state(data["state"])
        user_state.state=state
    if "circuit" in data:
        new_circuit=qiskit.QuantumCircuit(len(user_state.state.dims())) 
        for gate in data["circuit"]:
            gateargs=gate["params"]+gate["qubits"]
            getattr(new_circuit,gate["name"])(*gateargs)
        user_state.circuit=new_circuit
    if "qasm" in data:
        try:
            new_circuit = qiskit.QuantumCircuit.from_qasm_str(data["qasm"])
        except e:
            print("Failed to parse qasm")
            return
        else:
            user_state.circuit=new_circuit
        
    #update state - todo: update only what's changed
    send_data(sid,None)
        
@socketio.on('*')
def catch_all(event, sid, data):
    print(event)






def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:3000/")

thread = threading.Thread(target=open_browser, args=())
thread.daemon = True  
thread.start() 
        
#if __name__ == '__main__':
#app.run(host='0.0.0.0', port=3000)
socketio.run(app,host='0.0.0.0', port=3000)


















