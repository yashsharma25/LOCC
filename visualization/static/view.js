import SvgBackground from "./svgbackground.js";
import {addKeyListener,addCheckbox,toNormalText} from "./util.js";
import {circuitPanel,settingsPanel,tooltip,showTooltip,hideTooltip} from "./ui.js";
import {nodeRadius,linkWidth,nodeStrength,linkStrength,minLinkStrength,linkDistance} from "./constants.js";

export default class View{
  constructor(svg,def){
    this.svg=svg;
    this.def=def;
    let that=this;

    let background=new SvgBackground(svg);//now the background colors are in a separate class






    let forceNode = d3.forceManyBody().strength((d)=>{
              let s=d.charge;if (isNaN(s))s=1;
              return -nodeStrength*s-1;
            });
    let forceLink = d3.forceLink([]).id((x) => x.id)
            .distance((d)=>{
              let d1=d.distance;if(isNaN(d1))d1=1;
              let r1=d.source.radius;if(isNaN(r1))r1=0;
              let r2=d.target.radius;if(isNaN(r2))r2=0;
              return d1*linkDistance+r1+r2;
            })
            .strength((d)=>{
              let s1=d.source.strength,s2=d.target.strength,s3=d.strength;
              if(isNaN(s1))s1=1;if(isNaN(s2))s2=1;if(isNaN(s3))s3=1;
              let result=s1*s2*s3*linkStrength+minLinkStrength;
              return result;});
this.forceLink=forceLink;



    function tick(data) {
      let def=that.def;
      let viewObj=that.viewObj;
      for(let relationName in def.relations){
        let relDef=def.relations[relationName];
        let svgs=relDef.svg;
        if(!svgs)continue;
        for(let type in svgs){
          svgs[type].selection
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);

          if(svgs[type].tick){
            svgs[type].tick(svgs[type].selection,viewObj);
          }
        }
      }
      for(let objectName in def.objects){
        let objDef=def.objects[objectName];
        let svgs=objDef.svg;
        if(!svgs)continue;
        for(let type in svgs){
          if(svgs[type].tick){
            svgs[type].tick(svgs[type].selection,viewObj);
          }
          let offsetX=0,offsetY=0;
          if(svgs[type].offset){
            offsetX=svgs[type].offset.x;
            offsetY=svgs[type].offset.y;
          }
          if(svgs[type].type===undefined||svgs[type].type=="circle"){
            svgs[type].selection
            .attr("cx", d => d.x+offsetX)
            .attr("cy", d => d.y+offsetY);
          }
          if(svgs[type].type=="text"){
            svgs[type].selection
            .attr("x", d => d.x+offsetX)
            .attr("y", d => d.y+offsetY);
          }
          if(svgs[type].type=="rect"){
            svgs[type].selection
            .attr("x", d => d.x+offsetX)
            .attr("y", d => d.y+offsetY);
          }
        }
      }
      //currently animation defs are stuff that help manage various animations of different lengths etc;

      for(let name in def.animations){
        let animDef=def.animations[name];
        if(animDef.paused===true){continue;}
        if(typeof animDef.paused=="function"&&animDef.paused()){continue;}
        let step=1;if(animDef.step!==undefined){if(typeof animDef.step =="function")step=animDef.step();else step=animDef.step;}
        if(animDef.bouncing&&animDef.reversed){animDef.value-=step;}
        else{animDef.value+=step;}
        let min=0,max=10;
        if(animDef.min!==undefined){if(typeof animDef.min =="function")min=animDef.min();else min=animDef.min;}
        if(animDef.max!==undefined){if(typeof animDef.max =="function")max=animDef.max();else max=animDef.max;}
        animDef.lastMax=max;animDef.lastMin=min;
        //min and max are both allowed reachable values; if at a step max is reached it will stay there; if it's exceeded, that step's value is set to min (or set to max and will start to bounce back next step if enabled); if you want to avoid a value just set the min or max above/below it
        if(animDef.value>=max){
          if(animDef.bouncing){animDef.reversed=true;animDef.value=max;}
          else{
            if(animDef.value>max)animDef.value=min;//if exactly at max, it stays there for one step
          }
        }
        if(animDef.value<=min){
          if(animDef.bouncing){animDef.reversed=false;animDef.value=min;}
          else{
            if(deanimDeff.value<min)animDef.value=min;//if exactly at min, it stays there for one step
          }
        }

        let newIntValue=Math.floor(animDef.value);//for use in array indices etc
        if(animDef.intValue!==undefined&&animDef.intValue!=newIntValue){

          if(animDef.intTick){
            animDef.intTick(newIntValue);
          }
        }
        animDef.intValue=newIntValue;
        if(animDef.tick){
          animDef.tick(time);
        }
      }

    }

    function drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0.2);
        event.subject.fx = null;
        event.subject.fy = null;
      }

      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }








    let simulation=d3.forceSimulation()
        .alphaTarget(0.2)
        .force("link", forceLink)
        .force("charge", forceNode)
        .force("center",  d3.forceCenter())
        .force("X",  d3.forceX())
        .force("Y",  d3.forceY())
        .on("tick", tick);
    this.simulation=simulation;

    let objectsMenu=settingsPanel.append("div");
    let relationsMenu=settingsPanel.append("div");
    for(let relationName in def.relations){


      let relDef=def.relations[relationName];
      let svgs=relDef.svg;
      if(!svgs)continue;
      //let container=relationsMenu.append("div");
      addCheckbox(relationsMenu,toNormalText(relationName),(value)=>{relDef.visible=value;updateView(viewObj);})(true);
      for(let type in svgs){ //lines are created before nodes so they appear behind nodes
        let elemType=svgs[type].type||"line";
        let g=svg.append("g")
        .attr("stroke-width",1)
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-linecap", "round");;
        g.attr("name",relationName+"-"+type);
        svgs[type].selection=g.selectAll(elemType);
        if(svgs[type].init){
          svgs[type].init(g);
        }
        if(svgs[type].style){
          for(let name in svgs[type].style){
            //set constant styles
            if (typeof svgs[type].style[name]!="function"){
              g.style(name,svgs[type].style[name]);
            }
          }
        }
        if(svgs[type].attr){
          for(let name in svgs[type].attr){
            //set constant attrs
            if (typeof svgs[type].attr[name]!="function"){
              g.attr(name,svgs[type].attr[name]);
            }
          }
        }
      }

    }
    for(let objectName in def.objects){
      let objDef=def.objects[objectName];
      let svgs=objDef.svg;
      if(!svgs)continue;
      addCheckbox(objectsMenu,toNormalText(objectName),(value)=>{objDef.visible=value;updateView(viewObj);})(true);
      for(let type in svgs){
        console.log(type);
        let elemType=svgs[type].type||"circle";
        let g=svg.append("g");g.attr("name",objectName+"-"+type);
        g.call(drag(simulation));
        g.on("mouseover", function mouseover(event, d){
          if(objDef.tooltip){
            d=event.target.__data__ ;//d isn't the datum since "this" is the svg
            tooltip.html(objDef.tooltip(d))
            showTooltip(objDef.tooltip(d),event.pageY,event.pageX)

          }
          if(objDef.onmouseover){
            objDef.onmouseover(event, d);
          }
        })
        .on("mouseout", function mouseout(){
          hideTooltip();
          if(objDef.tooltip){
            hideTooltip();
          }
        })
        .on("click", function click(event,d){
          console.log("svg clicked",event);
          d=event.target.__data__ ;//d isn't the datum since "this" is the svg
          console.log(objDef.onclick);
          if(objDef.onclick){
            objDef.onclick(d,event);
          }
        })
        .on("dblclick", function dblclick(event,d){
          console.log("svg dblclick",event);
          d=event.target.__data__ ;//d isn't the datum since "this" is the svg
          console.log(objDef.ondblclick);
          if(objDef.ondblclick){
            objDef.ondblclick(d,event);
          }
        })
        .on("scroll", function scroll(event,d){
          console.log("svg scrolled",event);
          d=event.target.__data__ ;//d isn't the datum since "this" is the svg
          if(objDef.onscroll){
            objDef.onscroll(d,event);
          }
        });
          svgs[type].selection=g.selectAll(elemType);
          if(svgs[type].init){
            svgs[type].init(g);
          }
          if(svgs[type].style){
            for(let name in svgs[type].style){
              //set constant styles
              if (typeof svgs[type].style[name]!="function"){
                g.style(name,svgs[type].style[name]);
              }
            }
          }
          if(svgs[type].attr){
            for(let name in svgs[type].attr){
              //set constant attrs
              if (typeof svgs[type].attr[name]!="function"){
                g.attr(name,svgs[type].attr[name]);
              }
            }
          }
      }
    }

  }
  set(inputData){
    console.log(inputData);
    this.data=inputData;
    //now this is responsible for creating the active view-and-force-objects
    let def=this.def;
    let graph={nodes:[],links:[]};
    let viewObj={objects:{},relations:{}};
    this.viewObj=viewObj;
    for(let name in def.objects){
      let objDef=def.objects[name];

      let data=inputData[name];

      let dataFunc=objDef.data;
      if(dataFunc!==undefined) data=dataFunc(inputData,viewObj);
      viewObj.objects[name]=data;
      if(objDef.visible===false)data=[];
      graph.nodes=graph.nodes.concat(data);
      let svgs=objDef.svg;
      if(!svgs)continue;
      for(let type in svgs){
        svgs[type].selection=svgs[type].selection.data(data,function(d){return d.id;}).join(svgs[type].type||"circle");
        if(svgs[type].update){svgs[type].update(svgs[type].selection,viewObj);}
        if(svgs[type].style){
          for(let name in svgs[type].style){
            //set constant styles
            if (typeof svgs[type].style[name]=="function"){
              svgs[type].selection.style(name,svgs[type].style[name]);
            }
          }
        }
        if(svgs[type].attr){
          for(let name in svgs[type].attr){
            //set constant attrs
            if (typeof svgs[type].attr[name]=="function"){
              svgs[type].selection.attr(name,svgs[type].attr[name]);
            }
          }
        }
      }
    }
    for(let name in def.relations){
      let relDef=def.relations[name];

      let data=inputData[name];



      //if the source/target node types are disabled, the link must be hidden too
      let sourceName=relDef.source;
      let targetName=relDef.target||relDef.source;
      let sourceDef=def.objects[sourceName],targetDef=def.objects[targetName];
      let dataFunc=relDef.data;
      if(dataFunc!==undefined) data=dataFunc(inputData,viewObj,viewObj.objects[sourceName],viewObj.objects[targetName]);
      viewObj.relations[name]=data;

      let sources=viewObj.objects[sourceName],targets=viewObj.objects[targetName];

      for(let d of data){
        d.relType=name;
        if(typeof d.source != "object")d.source=sources[d.source];
        if(typeof d.target != "object")d.target=targets[d.target];
      }

      if(relDef.visible===false||sourceDef.visible===false||targetDef.visible===false)data=[];
      graph.links=graph.links.concat(data);
      let svgs=relDef.svg;
      if(!svgs)continue;
      for(let type in svgs){
        svgs[type].selection=svgs[type].selection.data(data).join(svgs[type].type||"line");
        if(svgs[type].update){svgs[type].update(svgs[type].selection,viewObj);}
        if(svgs[type].style){
          for(let name in svgs[type].style){
            //set constant styles
            if (typeof svgs[type].style[name]=="function"){
              svgs[type].selection.style(name,svgs[type].style[name]);
            }
          }
        }
        if(svgs[type].attr){
          for(let name in svgs[type].attr){
            //set constant attrs
            if (typeof svgs[type].attr[name]=="function"){
              svgs[type].selection.attr(name,svgs[type].attr[name]);
            }
          }
        }

      }
    }
    console.log(graph);

    this.simulation.nodes(graph.nodes);
    this.forceLink.links(graph.links);

    this.simulation.restart();
  }
}
