import {addKeyListener,addCheckbox,toNormalText,getQuditValues,complex2str,getSimilarity} from "./util.js";
import {titleText} from "./ui.js";

export default {
  //data def doesn't really care aboutobjects or links, everything is like a database table with some attributes tha may reference others

  qubits:{
    data:(data)=>{
      let nodes=[];
      for(let i=0;i<data.qubits.length;i++){
        let qubit=data.qubits[i];
        nodes.push( {id:i,register:qubit.name,register_index:qubit.index,dim:data.dims[i],index:i});
      }
      return nodes;
    },
    label:function(d) {
      return d.id;
    },
  },
  clbits:{
    data:(data)=>{
      let nodes=[];
      for(let i=0;i<data.clbits.length;i++){
        let bit=data.clbits[i];
        nodes.push( {id:i,register:bit.name,register_index:bit.index,index:i});
      }
      return nodes;
    },
    label:function(d) {
      return d.id;
    },
  },
  states:{
    data:(data)=>{
      let nodes=[];
      if(!data.states)return [];
      for(let i=0;i<data.states.length;i++){
        nodes.push( {id:i,state:data.states[i]});
      }
      return nodes;
    },
    label:function(d) {
      return d.id;
    },
  },

  outcomes:{
    data:(data)=>{
      let nodes=[];
      for(let [i,x] of data.state.entries()){
        let values=getQuditValues(i,data.dims);
        let bits=values.join("");
        let prob=Math.sqrt(x.re*x.re+x.im*x.im);
        let phase=Math.atan(x.re/x.im);
        //if (prob<0.00001) continue;
        nodes.push( {id:i,state:i,values:values,index:i,prob:prob,amplitude:x,phase:phase,size:prob,charge:prob*5,strength:prob,bits:bits});
      }
      return nodes;
    },
    label:function(d) {
      return d.id;
    },

  },
  possibilities:{
    data:(data)=>{
      let possibleStates=[];
      for(let [i,x] of data.state.entries()){
        let values=getQuditValues(i,data.dims);
        let prob=Math.sqrt(x.re*x.re+x.im*x.im);
        let phase=Math.atan(x.re/x.im);
        if(prob<0.00001)continue;
        let obj={prob:prob,values:values,amplitude:x,phase:phase}
        possibleStates.push(obj);

        let text="";//data.name+" ";
        let likelyStates=Array.from(possibleStates).sort((a,b)=>{return a.prob<b.prob}).slice(0,Math.min(4,possibleStates.length));
        console.log(likelyStates);
        for(let [i,state] of likelyStates.entries()){
          state.phase=Math.atan(state.amplitude.re/state.amplitude.im);
          console.log(state.phase);
          text+=((i>0)?"+":"")+'<span style="'+"color:"+d3.hsl(state.phase*360/(2*Math.PI),1,0.7-state.prob*0.2).formatHsl() +'">'+complex2str(state.amplitude)+"</span> <b>|"+state.values.join("")+"\u3009</b> ";
        }
        titleText.html(text);




      }
      return possibleStates;
    }
  },

  circuit_nodes_by_qubit:{//actually now it has classical bits too
    data:(data,viewObj)=>{

    //update: now circuit nodes represent new or changed values/qubits that are inputs/outputs. and they connect to gates directly,so no connection between circuit nodes themselves.
     let gates=data.gates;let circuit_nodes=[];
     let qubit_nodes=[];
     let clbit_nodes=[];
     for(let i=0;i<data.qubits.length;i++){qubit_nodes.push([]);}
     for(let i=0;i<data.clbits.length;i++){clbit_nodes.push([]);}
     for(let [i,gate] of gates.entries()){
       for(let qubit of gate.qubits){
         if(qubit_nodes[qubit.index].length>0){
           let lastnode=qubit_nodes[qubit.index][qubit_nodes[qubit.index].length-1];
           lastnode.to_gate.push(i);
         }

         qubit_nodes[qubit.index].push({from_gate:i,to_gate:[],qubit:qubit,local_order:qubit_nodes[qubit.index].length,global_order:i});
       }
       for(let clbit of gate.clbits){
         if(clbit_nodes[clbit.index].length>0){
           let lastnode=clbit_nodes[clbit.index][clbit_nodes[clbit.index].length-1];
           lastnode.to_gate.push(i);
         }

         clbit_nodes[clbit.index].push({from_gate:i,to_gate:[],clbit:clbit,local_order:clbit_nodes[clbit.index].length,global_order:i});
       }
       if (gate.condition){
          let cond=gate.condition;//{"index":0,"name":x.name,"value":gate[0].condition[1]} ;
          let lastnode=clbit_nodes[cond.index][clbit_nodes[cond.index].length-1];
          lastnode.to_gate.push(i);

        }
     }


     return qubit_nodes.concat(clbit_nodes);
   },
 },
 circuit_nodes:{
    data:(data,viewObj)=>{
      return viewObj.circuit_nodes_by_qubit.flat();
    },
  },
  gates:{
    data:(data,viewObj)=>{
      //if data has no circuit defined, assume there is an initialization on qubits and measurements at the end?
      //gates and their related qubits need to be known before circuit_nodes can be initialized.
       let gates=[];
       if(data.gates){
         for(let [i,gate] of data.gates.entries()){gate.charge=0.001;gate.gate_index=i;}
         return data.gates;
       }
       let qubits=[];for(let i=0;i<data.num_qubits;i++){qubits.push(i);}
       //gates.push({type:"initialization",data:data.state,qubits:qubits});
       //or end-measuremnet can simply be the default state/outcome visualization instead,
       //and explicit measurement would be used for eg. LOCC protocols in the middle?
       for(let i=0;i<data.num_qubits;i++){
         //gates.push({type:"measurement",qubits:[i]});
       }
       return gates;
     },
  },

  qubit_entanglement:{
    source:"qubits",
    directed:false,
    visible:false,
    data:(data,viewObj)=>{
      let links=[];
      for(let key in data.e_stats){
        let st=key.split(",").map((x)=>parseInt(x.trim()));
        let value=data.e_stats[key];
        links.push({source:st[0],target:st[1],max:value.max,min:value.min,strength:0.5*(value.max+value.min)/2+0.5,distance:3});
        //note: d3 graph would want source and target to be node references
      }
      return links;
    },
  },
  qubit_system_entanglement:{
    source:"qubits",
    target:"qubit_system",
    data:(data,viewObj,qubits,qubit_system)=>{
      let links=[];
      for(let [i,qubit] of viewObj.qubits.entries()){
        links.push({source:i,target:0,entropy:data.entanglement_stats[i],strength:data.entanglement_stats[i]*0.01,distance:0.01+0.1*(1-data.entanglement_stats[i])});
      }
      return links;
    },
  },
  outcome_similarity:{
    source:"outcomes",
    directed:false,
    data:(data,viewObj)=>{

      let outcomes=viewObj.outcomes;
      let links=[];
      for(let i=0;i<outcomes.length;i++){
        for(let j=i+1;j<outcomes.length;j++){
          if(outcomes[i].prob==0||outcomes[j].prob==0){continue;}
          links.push({source:i,target:j,max:0.1,min:0,strength:getSimilarity(outcomes[i].values,outcomes[j].values)*0.05});

        }
      }
      return links;
    },

  },
  qubit_outcome_association:{
    source:"qubits",
    target:"outcomes",
    directed:true,
    data:(data,viewObj)=>{
      function getSalience(values,index){//how unique is the value in this index position
        let count=0;
        for(let i=0;i<values.length;i++){
          if(values[i]!=values[index]){count++;}
        }
        return count/values.length;
      }
      let qubits=viewObj.qubits,outcomes=viewObj.outcomes;
      let links=[];
      for(let i=0;i<qubits.length;i++){
        for(let j=0;j<outcomes.length;j++){
          //if(outcomes[j].prob>0){//outcomes[j].values[i]&&
            let salience=getSalience(outcomes[j],i);
            links.push({source:i,target:j,max:0.1,min:0,prob:outcomes[j].prob,salience:salience,distance:1+salience,strength:salience*outcomes[j].prob*0.001});
          //}


        }
      }
      return links;
    },
  },
  circuit_node_gate_links:{
    source:"circuit_nodes",
    target:"gates",
    data:(data,viewObj)=>{
      let circuit_nodes=viewObj.circuit_nodes;
      //just connect circuit nodes to their input/output gates;
      let links=[];
      for(let i=0;i<circuit_nodes.length;i++){
        //{from_gate:gate_index,to_gate:index, qubit:qubit,local_order:qubit_nodes[qubit].length,global_order:i}
        //if(circuit_nodes[i].gate=="END"){continue};
        links.push({source:i,target:circuit_nodes[i].from_gate,distance:0.01,strength:1});
        if(circuit_nodes[i].to_gate!==undefined){
          for(let gate of circuit_nodes[i].to_gate){
            links.push({source:i,target:gate,distance:0.01,strength:1});
          }
        }
      }
      return links;
    },

  },
  /*
  circuit_node_links:{
    source:"circuit_nodes",
    target:"circuit_nodes",
    data:(data,viewObj,circuit_nodes)=>{
      //connect adjacent nodes in the same qubit/clbit line
      let qubit_nodes=viewObj.circuit_nodes_by_qubit;
      let links=[];
      for(let [qubit,qubit_line] of qubit_nodes.entries()){
        for(let i=0;i<qubit_line.length-1;i++){
          links.push({source:qubit_line[i],target:qubit_line[i+1],qubit:qubit,distance:0.5});
          //this works because circuit_nodes contain teh same obejcts as qubit_nodes
        }
      }
      return links;
    },
  },
  */
  circuit_node_qubit_links:{
    source:"circuit_nodes",
    target:"qubits",
    data:(data,viewObj,circuit_nodes,qubits)=>{
      let links=[];
      let nodes_by_qubit=viewObj.circuit_nodes_by_qubit;
      for(let i=0;i<data.qubits.length;i++){
        //{gate:gate_index,qubit:qubit,local_order:qubit_nodes[qubit].length,global_order:i}
        links.push({source:nodes_by_qubit[i][0],target:i,distance:0.1});
      }
      return links;
    },
  },
  circuit_node_clbit_links:{
    source:"circuit_nodes",
    target:"clbits",
    data:(data,viewObj,circuit_nodes,clbits)=>{
      let links=[];
      let nodes_by_qubit=viewObj.circuit_nodes_by_qubit;
      for(let i=0;i<data.clbits.length;i++){
        //{gate:gate_index,qubit:qubit,local_order:qubit_nodes[qubit].length,global_order:i}
        links.push({source:nodes_by_qubit[data.qubits.length+i][0],target:i,distance:0.1});
      }


      return links;
    },
  },



  }
