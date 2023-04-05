import {addKeyListener,addCheckbox,toNormalText,getQuditValues} from "./util.js";
import dataDef from "./data-def.js";
import {codePanel,updateCode} from "./code-editor.js";

let body=d3.select("body");
let titleBar = body.append("div").style("position","absolute").style("top","0").style("left","70%").style("right","0")
.style("text-align","right").style("color","white").style("z-index",10);
export let titleText=titleBar.append("p");titleText.style("font-size","30px");



let basisBar = body.append("div").style("position","absolute").style("top","20%").style("width","100%")
.style("text-align","right").style("color","white").style("z-index",10);
export let basisText=basisBar.append("p");basisText.style("font-size","30px");

export let tooltip=body.append("div").style("position", "absolute").style("visibility", "hidden").style("color","white").style("z-index",10).
style("background-color", "rgba(70,100,155,0.6)").style("font-family","sans-serif").style("border-radius","5px").style("border","2px solid white").style("padding","5px").attr("class", "tooltip");
export let hideTooltipTimeout;
export function showTooltip(html,top,left){
  tooltip.html(html)
  .style("visibility", "visible")
  .style("top",top + "px")
  .style("left", left + "px");
  }
  export function hideTooltip (){

    function fadeout(){
      tooltip.transition()
      .duration(50)
      .style("visibility", "hidden");

    }
    if(hideTooltipTimeout){clearTimeout(hideTooltipTimeout);hideTooltipTimeout=null;}
    hideTooltipTimeout=setTimeout(fadeout,300);

  }


 export let settingsPanel=body.append("div").style("position","absolute").attr("class","panel").style("top","0").style("right","0").style("width","20%").style("height","100%").style("overflow-y","scroll").style("display","none");
settingsPanel.append("h3").style("text-align","center").style("z-index",10).text("Settings");
addKeyListener(body,"s",()=>{
  if(settingsPanel.style("display")=="none"){settingsPanel.style("display","block");}
  else{settingsPanel.style("display","none");}
});

export let circuitPanel=body.append("div").style("position","absolute").style("top","0%").style("left","30%").style("right","30%").attr("class","panel")
.style("font-family","monospace").style("white-space","pre").style("z-index",10).style("display","none");
addKeyListener(body,"c",()=>{
  if(circuitPanel.style("display")=="none"){circuitPanel.style("display","block");}
  else{circuitPanel.style("display","none");}
});
/*
export let qasmPanel=body.append("div").style("position","absolute").style("top","0%").style("left","30%").style("right","30%").attr("class","panel")
.style("font-family","monospace").style("white-space","pre").style("z-index",10).style("display","none");
addKeyListener(body,"q",()=>{
  if(qasmPanel.style("display")=="none"){qasmPanel.style("display","block");}
  else{qasmPanel.style("display","none");}
});
qasmPanel=body.append("div").style("position","absolute").style("top","0%").style("left","30%").style("right","30%").attr("class","panel")
.style("font-family","monospace").style("white-space","pre").style("z-index",10).style("display","none");
*/
export let toolsPanel=body.append("div").style("position","absolute").style("top","0").style("left","0").style("width","20%").style("height","100%").attr("class","panel").style("z-index",10).style("display","none");
addKeyListener(body,"t",()=>{
  if(toolsPanel.style("display")=="none"){toolsPanel.style("display","block");}
  else{toolsPanel.style("display","none");}
});

toolsPanel.append("h3").style("text-align","center").text("Tools");
let gatesArea=toolsPanel.append("div").style("border","1px solid grey").style("display","flex").style("flex-flow","row wrap").style("align-content","flex-start");



let gateList={
  x:{fullName:"X Gate",params:0,qubits:1},
  y:{fullName:"Y Gate",params:0,qubits:1},
  z:{fullName:"Z Gate",params:0,qubits:1},
  cx:{fullName:"Controlled X",params:0,qubits:2},
  cy:{fullName:"Controlled Y",params:0,qubits:2},
  cz:{fullName:"Controlled Z",params:0,qubits:2},
  rx:{fullName:"X rotation",params:1,qubits:1},
  ry:{fullName:"Y rotation",params:1,qubits:1},
  rz:{fullName:"Z rotation",params:1,qubits:1},

}
let gateTip = d3.select("body").append("div").style("position","absolute").style("background-color","rgba(200,200,255,0.5)").style("height","50px")
    .style("opacity", 0).style("margin","1px solid #aaf").style("padding","3px ")

let chosenGate=null;
export function getChosenGate(){return chosengate;}
for (let gateName in gateList){
  let gateDef=gateList[gateName];
  let gateTool=gatesArea.append("div").style("width","50px").style("height","50px").style("display","flex").style("margin","auto").style("border","1px solid darkgreen").style("background-color","rgba(200,200,200,0.8)").text(()=>gateName);
  gateTool.on("mouseover", function(event) {
  gateTip.style("opacity", 1)
     .text(gateDef.fullName)
     .style("left", (event.pageX-15) + "px")
     .style("top", (event.pageY-75) + "px")
  })
  .on("mouseout", function(event) {
    gateTip.style("opacity", 0)
  })
  gateTool.on("click",()=>{
    if(chosenGate==gateName){
      gateTool.style("border","1px solid darkgreen");
      chosenGate=null;
      console.log(gateName+" unchosen");
    }
    else{
      gateTool.style("border","1px solid red");
      chosenGate=gateName;
      console.log(gateName+" chosen");
    }

  })
}


export let worldlinePanel=body.append("div").style("position","absolute").attr("class","panel").style("bottom","0").style("left","20%").style("right","20%").style("height","10%").style("overflow-x","scroll").style("display","none");

let playbackBarContainer=worldlinePanel.append("div").style("width","90%").style("left","10%").style("margin","10px").style("height","5px").style("background-color","#888");
let playbackBar=playbackBarContainer.append("div").style("width","90%").style("left","0%").style("height","5px").style("background-color","#2b2").style("pointer-event","none");
playbackBarContainer.on("click",function(event,d){//get clicked position
  let rect=playbackBarContainer.node().getBoundingClientRect();
  let width=Math.max(Math.max(event.x,rect.width),0);
  let percent=Math.floor(100*(width)/rect.width)+"%";
  let value=(width)/rect.width;
  if(isNaN(value))return;//throw Error();

  playbackBar.style("width",percent);
});

let playbackButtonsArea=worldlinePanel.append("div").style("width","90%").style("left","10%").style("top","10%").style("display","flex").style("align-content","center");
let statesPlaying=false;
let playPauseButton=playbackButtonsArea.append("button").style("width","35px").style("height","25px").text("\u25b6").style("top","10%").on("click",()=>{
  if(dataDef.circuit_states.variation.paused==false){dataDef.circuit_states.variation.paused=true;playPauseButton.text("\u25b6");}
  else{dataDef.circuit_states.variation.paused=false;playPauseButton.text("\u23EF");}
});
let stepForwardButton=playbackButtonsArea.append("button").style("width","35px").style("height","25px").text(">").style("top","10%").on("click",()=>{
  dataDef.circuit_states.variation.value+=1;tick();

});
let stepBackwardButton=playbackButtonsArea.append("button").style("width","35px").style("height","25px").text("<").style("top","10%").on("click",()=>{
  dataDef.circuit_states.variation.paused-=1;tick();
});


addKeyListener(body,"w",()=>{
  if(worldlinePanel.style("display")=="none"){worldlinePanel.style("display","block");}
  else{worldlinePanel.style("display","none");}
});



export function setUI(data){
  circuitPanel.selectAll("p").data(data.circuit_text.split("\n")).join("p").text((d)=>d);
  //codePanel.selectAll("p").data(data.qasm.split("\n")).join("p").text((d)=>d);
  updateCode(data.qasm);
}
