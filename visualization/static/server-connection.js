import {circuitPanel,setUI } from "./ui.js";

export let socket = io();
socket.on('connect', function() {
    socket.emit('set_state', {name:window.location.pathname.substring(1)});
  });

  socket.on("*",function(event,data) {
      console.log(event);
      console.log(data);
  });

  export function set_circuit(){
    let obj={},circuit=[];

    let gates=viewObj.objects.gates;
    for(let gate of gates){
      circuit.push(gate);
    }
    obj.circuit=circuit;

    socket.emit('set_data', obj);
  }

  export function set_qasm(str){
    let obj={},circuit=[];

    let qasm=str;

    obj.qasm=qasm;

    socket.emit('set_data', obj);
  }
