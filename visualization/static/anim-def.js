//TODO: animations
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
