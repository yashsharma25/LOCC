import {circuitPanel,setUI } from "./ui.js";
import SvgBackground from "./svgbackground.js";
import View from "./view.js";
import State from "./data.js";
import dataDef from "./data-def.js";
import viewDef from "./view-def.js";
import {socket} from "./server-connection.js";

socket.on('data', function(data) {
  console.log(data);
  setUI(data);
  state.set(data);
});


  let width=1536,height=728;
  d3.select("body").style("width", "100%").style("height", "100%").style("position", "absolute").style("margin", "0").style("padding", "0");
  let svgContainer=d3.select("body").append("div").style("width", "100%").style("height", "100%").style("position", "absolute").style("margin", "0").style("padding", "0");
  let svg =svgContainer.append("svg")
  .style("position", "absolute").attr("viewBox", [-width / 2, -height / 2, width/2 , height/2])
          //.attr("width", "100%")
          //.attr("height", "100%")

          //.attr("style", "max-height: 100%; width: auto; height: intrinsic;")
          //.attr("preserveAspectRatio","xMidYMid meet");
  window.addEventListener("resize", resizeCanvas, false);
  function resizeCanvas() {
    let container=svgContainer.node();
    width=container.clientWidth;
    height=container.clientHeight;
    svg.attr("width", width)
      .attr("height", height)
      .attr("viewBox", [-width / 2, -height / 2, width, height])
  }
  setTimeout(resizeCanvas,10);



let stateData;let viewObj;


    let nodeRadius=20;
    let linkWidth=48;
    let nodeStrength=120;
    let linkDistance=100,linkStrength=1,minLinkStrength=0.01;
    let linkAnimPeriod=2000,minPeriod=1000,addedPeriod=1000;
    let timestep=0,time=0,maxtimestep=100;

let num_qubits=0;

let view=new View(svg,viewDef);
let state=new State(view,dataDef);





function addKeyListener(elem,key,keydownfunc,keyupfunc,preventDefault){
  if (elem instanceof d3.selection){elem=elem.node();}
		elem.addEventListener("keydown", ev=>{
			if((ev.keyCode===key)||(ev.key===key)){
				if(preventDefault)ev.preventDefault();
				if(keydownfunc)keydownfunc(ev);
			}
		});
		elem.addEventListener("keyup", ev=>{
			if((ev.keyCode===key)||(ev.key===key)){
				if(preventDefault)ev.preventDefault();
				if(keyupfunc)keyupfunc(ev);
			}
		});
	}
function addCheckbox(parentElem,text,func){
    if (parentElem instanceof d3.selection ==false){parentElem=d3.select(parentElem);}

		let s=parentElem.append("div");
		let label=s.append("p").text(text);
		let checkbox=s.append("input").attr("type","checkbox");
		let checkboxElem=checkbox.node();
		checkbox.on("input",()=>func(checkboxElem.checked));
		let onUpdate=function(value){checkboxElem.checked=value;};
		return onUpdate;//call when the value is changed outside
	}






function getQuditValues(index,dims){
  let result=[];
  for(let d of dims){

    result.unshift(index%d);
    index=Math.floor(index/d);
  }
  return result;
}

function getSimilarity(values1,values2){
  let a=0;
  for(let i=0;i<values1.length;i++){
    if(values1[i]==values2[i]){a++;}
  }
  return a/values1.length;
}
const floatFormatter = d3.format(".2f");
function complex2str(x){
  let re=floatFormatter(x.re),im=floatFormatter(x.im);
  if(x.re!=0)
  {
    if(x.im!=0){
      if(x.im<0&&im[0]=="−"){
        return "("+re+""+im+"i)";
      }
      else{return "("+re+"+"+im+"i)";}
    }
    else {return ""+re;}
  }
  else{
    if(x.im!=0){return im+"i";}
    else {return "0";}
  }
}
function toNormalText(str){//un-Camel case
	str=String(str);
	return str.replace(/([a-z])([A-Z/]+)/g, '$1 $2').replace("_"," ").replace(/^./, function(str){ return str.toUpperCase(); });
}
