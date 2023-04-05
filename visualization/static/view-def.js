import {nodeRadius,linkWidth,nodeStrength} from "./constants.js";
export default {
  objects:{//node-like objects
    qubits:{
      data:(data,viewObj)=>{
        let nodes=[];
        for(let i=0;i<data.qubits.length;i++){
          let qubit=data.qubits[i];
          nodes.push( {id:i,dim:qubit.dim,index:i,party:i,charge:2});
        }
        return nodes;
      },
      svg:{
        node:{ // outline actually
          type:"circle",
          //if attr or style item is constant, it's applied on the group; if it's a function, it's used for the selection (per datum) avoiding the need of having tow rite separate init/update functions.
          attr:{
            "stroke-width":3,
            r:(d)=>(d.dim?Math.log2(d.dim):1)*nodeRadius
          },
          style:{
            stroke:'#def',

            //fill:"url(\"data:image/svg+xml,\");",
            //fill:'rgba(255,255,255,0.05)',
            fill:(d)=>("url(#qubit-fill"+d.index+")"),
            //fill:"none",
            filter:"drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4))"
          },
        },
        gradient:{
          type:"linearGradient",
          init:(g)=>{

          },
          update:(selection)=>{
            selection.attr("id",(d)=>"qubit-fill"+d.index);
            selection.append("stop").attr("stop-color","hsl(255, 90%, 70%)").attr("stop-opacity","1").attr("offset","0%");
            selection.append("stop").attr("stop-color","hsl(227, 90%, 70%)").attr("stop-opacity","1").attr("offset","100%");
          },
        },

        label:{
          type:"text",
          init:(g)=>{
            g.text(function(d) {
              return d&&d.id;
            })
            //.style('stroke', '#fff')
            .style('fill', '#fff')
            .style('font-size', '16px').style("pointer-events","none")
            .attr('x', 6)
            .attr('y', 3);
          },
          update:(selection)=>{
            selection.text(function(d) {
              return d.id;
            });
          },
          offset:{x:-3,y:3},
        },
      },
      tooltip:(d)=>{return "Qubit "+d.id;}
    },
    clbits:{
      data:(data,viewObj)=>{
        let nodes=[];
        for(let i=0;i<data.clbits.length;i++){
          let clbit=data.clbits[i];
          nodes.push( {id:i,index:i,name:clbit.register,register_index:clbit.register_index,charge:1.5});
        }
        return nodes;
      },
      svg:{
        node:{ // outline actually
          type:"circle",
          //if attr or style item is constant, it's applied on the group; if it's a function, it's used for the selection (per datum) avoiding the need of having tow rite separate init/update functions.
          attr:{
            "stroke-width":1,
            r:(d)=>0.5*nodeRadius
          },
          style:{
            stroke:'#def',
            fill:'rgba(255,255,255,0.05)',
            filter:" drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4))"
          },
        },
        outcome:{
          type:"circle",
          attr:{
            "stroke-width":2,
            r:(d)=>{
              //let result=viewObj.objects.possibilities[0].values[d.id];
              //if(result==0) return nodeRadius/2-2;
              //else return Math.log2(result)*nodeRadius });
              //return Math.log2(result)*nodeRadius
              return 0.5*nodeRadius;
             }
          },
          style:{
            stroke:'#def',
            fill:"rgba(140,205,255,0.8)",
            filter:"drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4))"
          },

          tick:(selection,viewObj)=>{
            /*
            selection
              .attr("r", (d)=>{
                let outcomeIndex=simDef.animations.qubit_outcomes.intValue;
                let outcome=viewObj.objects.possibilities[outcomeIndex];
                let result=outcome.values[d.id];
                //if(result==0) return nodeRadius/2-2;
                //else
                //
                return (Math.log2(result)+1)*nodeRadius });
              ;
              */
          }
        },
        label:{
          type:"text",
          init:(g)=>{
            g.text(function(d) {
              return d&&d.id;
            })
            //.style('stroke', '#fff')
            .style('fill', '#fff')
            .style('font-size', '16px').style("pointer-events","none")
            .attr('x', 6)
            .attr('y', 3);
          },
          update:(selection)=>{
            selection.text(function(d) {
              return d.id;
            });
          },
          offset:{x:-3,y:3},
        },
      },
      tooltip:(d)=>{return "Qubit "+d.id;}
    },
    qubit_system:{//central node for representing entanglement withteh rest of the system
      data:(data,viewObj)=>{
        return [{id:0,charge:0.1}];
      },
      visible:false,
      svg:{
        node:{ // outline actually
          type:"circle",
          init:(g)=>{
            g.attr("stroke-width", 1)
            .style('stroke', '#def')
            .style('fill', 'rgba(255,255,255,0.05)')
            .style("filter"," drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4))");
            ;
          },
          update:(selection)=>{
                selection
                .attr("r", (d)=>(0.1*nodeRadius));
          },
        },
      },
    },
    outcomes:{

      svg:{
        node:{ // outline actually
          type:"circle",
          init:(g)=>{
            g.attr("stroke-width", 0.1)
            .style('stroke', '#def')
            .style('fill', '#def')
            ;
          },
          update:(selection)=>{
                selection
                .attr("r", (d)=>{
                  if(d.prob>0){
                    return (d.prob*0.6+0.01)*nodeRadius;
                  }
                  else return 0;
                });
          },
        },

        label:{
          type:"text",
          init:(g)=>{
            g.text(function(d) {
              return d&&d.id;
            })
            //.style('stroke', '#fff')
            .style('fill', '#444')
            .style('font-size', '10px').style("pointer-events","none")
            .attr('x', 6)
            .attr('y', 3);
          },
          update:(selection)=>{
            selection.text(function(d) {
              return d.bits;
            }).attr("opacity", (d)=>(d.prob?d.prob*0.6+0.1:0)*nodeRadius);

          },
          offset:{x:-8,y:3},
        },
      }
    },
    possibilities:{

    },

    circuit_nodes_by_qubit:{

   },
   circuit_nodes:{

      svg:{
        node:{ // outline
          type:"circle",
          init:(g)=>{
            g
            .style('stroke', '#18f')
            .style("filter"," drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4))")
            .attr("stroke-width", 5)

            .style('fill', '#18f')

            ;
          },
          update:(selection)=>{
                selection.attr('r', '5');
          },
        },
      },
      onclick:function(d,event) {
        console.log("circuit node clicked",d);
        if(chosenGate==null)return;
        let gateDef=gateList[chosenGate];
        let qubits=[d.qubit];for(let i=1;i<gateDef.qubits;i++){qubits.push(0);}
        let newGate={name:chosenGate,qubits:[d.qubit],params:Array(gateDef.params).fill(0)}
        if (d.gate!=="END"){
          //append before the gate?
          view.viewObj.objects.gates.splice(d.gate,0,newGate);
        }
        else{
          view.viewObj.objects.gates.push(newGate);
        }
        console.log(  view.viewObj.objects.gates)
        set_data();
      },
      tooltip:(d)=>{return "Node of qubit"+d.qubit+" to gate "+d.gate;}
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
       svg:{
         rect:{ // outline
           type:"rect",
           init:(g)=>{
             g.attr("stroke-width", 3)
             .style('stroke', '#def')
             .style('fill', 'rgba(180,190,200,0.5)')

             ;
           },
           update:(selection)=>{
                 selection
                 .attr('width', (d)=>{return Math.max(d.name.length+d.params.length*5,3)*10;})
                 .attr('height', '25');
           },
           tick:(selection)=>{
             /*
             selection
                .style("opacity",(d)=>{
                  if(d.gate_index<=simDef.animations.circuit_states.intValue){
                    return 1;
                  }
                  else{
                    return 0.2;
                  }

                })
                .style("stroke",(d)=>{
                  if(d.gate_index<=simDef.animations.circuit_states.intValue){
                    return '#afe';
                  }
                  else{
                    return '#aef';
                  }

                });
                */
           }

         },
         label:{
           type:"text",
           init:(g)=>{
             g.text(function(d) {
               return d&&d.name;
             })
             //.style('stroke', '#fff')
             .style('fill', '#fff')
             .style('font-size', '16px').style("pointer-events","none")
             .attr('x', 3)
             .attr('y', 0);
           },
           update:(selection)=>{
             selection.text(function(d) {
               let text=d.name;
               if(d.params.length>0){text=text+" "+d.params.map((x)=>x.toString().substring(0,4)).join(" ");}
               return text;
             });
           },
           offset:{x:2,y:15},
         },
       },
       onclick:function(d,event) {
         //try changing the parameter
         console.log("gate clicked",d);
         if (d.params){d.params[0]+=0.5;}
         set_data();
       }
    },

  },
  relations:{
    //link-like objects
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
      svg:{
        outline:{
          init:(g)=>{g.attr("stroke-opacity", 0.9).attr("stroke", "#eee").style("filter"," drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4))");},
          update:(selection)=>{selection.attr("stroke-width",(d)=>1.05*linkWidth)}
        },
        max:{
          init:(g)=>{g.attr("stroke-opacity", 0.9).attr("stroke", "#adf")},
          update:(selection)=>{
            //if(stateData){
              /*if(stateData.is_changing){
                selection.attr("stroke-width",(d)=>d.max[timestep]*linkWidth)
              }
              else {
                selection.attr("stroke-width",(d)=>d.max*linkWidth)
              }*/
            //}
          },
        },
        min:{
          init:(g)=>{g.attr("stroke-opacity", 0.9).attr("stroke", "#35a")},
          update:(selection)=>{
            selection.attr("stroke-width",(d)=>{(stateData.is_changing)?(d.min[timestep]*linkWidth):(d.min*linkWidth)});
            //if(stateData&&(!stateData.is_changing)){
                //variant: synchronized animation with the same period for all
                /*
                function repeat() {
                  selection></
                  .attr("stroke-width",(d)=>d.min*linkWidth)
                  .transition()
                  .duration(linkAnimPeriod)
                  .attr("stroke-width",(d)=>d.max*linkWidth)
                  .transition()
                  .duration(linkAnimPeriod)
                  .attr("stroke-width",(d)=>d.min*linkWidth)
                  .on("end", repeat);
                }
                repeat();
                */
                //variant: each edge has its own period and offset, which are random
              /*  selection.each(function my(d,i){
                  let that=this;//need to be a named function to have this??
                  let period=minPeriod+addedPeriod*Math.random(),offset=period*Math.random();
                  function repeat() {

                    d3.select(that)
                    //.selectAll(".line")
                    .attr("stroke-width",(d)=>d.min*linkWidth)
                    .transition()
                    .duration(period)
                    .attr("stroke-width",(d)=>d.max*linkWidth)
                    .transition()
                    .duration(period)
                    .attr("stroke-width",(d)=>d.min*linkWidth)
                    .on("end", repeat);
                  }
                  setTimeout(repeat,offset);
                });
                */


          //  }
          },
        }

      }
    },
    qubit_system_entanglement:{
      source:"qubits",
      target:"qubit_system",

      svg:{
        outline:{
          init:(g)=>{g.attr("stroke-opacity", 0.9).attr("stroke", "#eee").style("filter"," drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4))");},
          update:(selection)=>{selection.attr("stroke-width",(d)=>d.entropy*0.1*linkWidth).attr("stroke-opacity", (d)=>d.entropy*0.5)}
        },
      }
    },
    outcome_similarity:{
      source:"outcomes",
      directed:false,

      svg:{
        outline:{
          init:(g)=>{
            g.attr("stroke-opacity", 0.2).attr("stroke", "#ddf")
          },
          update:(selection)=>{selection.attr("stroke-width",(d)=>0.05*linkWidth)}
        },
      }
    },
    qubit_outcome_association:{
      source:"qubits",
      target:"outcomes",
      directed:true,

      svg:{
        outline:{
          init:(g)=>{
            g.attr("stroke-opacity", 0.1).attr("stroke", "#ddd")
          },
          update:(selection)=>{selection.attr("stroke-width",(d)=>d.prob*0.05*linkWidth)},

        },
      }
    },
    circuit_node_gate_links:{
      source:"circuit_nodes",
      target:"gates",

      svg:{
        outline:{
          init:(g)=>{
            g.attr("stroke-opacity", 0.5).attr("stroke", "#33f")
          },
          update:(selection)=>{selection.attr("stroke-width",(d)=>0.05*linkWidth)}
        },
      }
    },
    /*
    circuit_node_links:{
      source:"circuit_nodes",
      target:"circuit_nodes",

      svg:{
        outline:{
          init:(g)=>{
            g.attr("stroke-opacity", 0.5).attr("stroke", "#f33")
          },
          update:(selection)=>{selection.attr("stroke-width",(d)=>0.05*linkWidth)}
        },
      }
    },
    */
    circuit_node_qubit_links:{
      source:"circuit_nodes",
      target:"qubits",

      svg:{
        outline:{
          init:(g)=>{
            g.attr("stroke-opacity", 0.5).attr("stroke", "#3f3")
          },
          update:(selection)=>{selection.attr("stroke-width",(d)=>0.05*linkWidth)}
        },
      }
    },
    circuit_node_clbit_links:{
      source:"circuit_nodes",
      target:"clbits",

      svg:{
        outline:{
          init:(g)=>{
            g.attr("stroke-opacity", 0.5).attr("stroke", "#3e8")
          },
          update:(selection)=>{selection.attr("stroke-width",(d)=>0.05*linkWidth)}
        },
      }
    },

  },
  animations:{
    circuit_states:{
      paused:true,
      value:0,
      intValue:0,
      max:(stateData,viewObj)=>{return stateData.circuit_states.length-1},
      step:0.0066,
      intTick:(index,stateData,viewObj)=>{
        let newState=stateData.circuit_states[index];
        let possibleStates=[];
        for(let [i,x] of newState.entries()){
          let values=getQuditValues(i,stateData.dims);
          let prob=Math.sqrt(x.re*x.re+x.im*x.im);
          let phase=Math.atan(x.im/x.re);
          if(prob<=0.00001)continue;
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
      }
    },
    qubit_outcomes:{
      paused:true,
      value:0,
      intValue:0,
      max:()=>{return viewObj.possibilities.length-1},
      step:0.02,
      intTick:(index)=>{
        let outcome=viewObj.possibilities[index];
        let possibleStates=[];
        for(let [i,x] of newState.entries()){
          let values=getQuditValues(i,stateData.dims);
          let prob=Math.sqrt(x.re*x.re+x.im*x.im);
          let phase=Math.atan(x.re/x.im);
          if(prob<=0.00001)continue;
          let obj={prob:prob,values:values,amplitude:x,phase:phase}
          possibleStates.push(obj);

          let text="";//data.name+" ";
          for(let [i,state] of possibleStates.entries()){
            text+=((i>0)?"+":"")+'<span style="'+"color:"+d3.hsl(state.phase*360/(2*Math.PI),1,0.7-state.prob*0.2).formatHsl() +'">'+complex2str(state.amplitude)+"</span> <b>|"+state.values.join("")+"\u3009</b> ";
          }
          titleText.html(text);
        }
      }
    }
  }


};
