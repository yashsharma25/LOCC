



class SimUI{
  constructor(sim){
    var gui;
    let dashboardSelection=selectE("dashboard");
    let dashboardContent=getE("dashboard-content");
    let dashboardButtonsArea=getE("dashboard-header-buttons");
    let dashboardTabs=d3.selectAll("#dashboard-content>div");
    let dashboardHeader=getE("dashboard-header");
    let dashboardVisualizationMenu=getE("visualization-menu");
    let proxy;
    //function initUI(){
    //init dashboard

  	d3.select("#dashboard-menu-area").selectAll("div").data(dashboardTabs.nodes()).enter().append("div").attr("class","tab-title").text((d)=>toNormalText(d.id)).on("click",(d)=>{
  		dashboardTabs.style("display",function(){return (this==d)?"block":"none";});
  	});
  	dashboardTabs.style("display",function(d,i){return (i==0)?"block":"none";});

  	window.addEventListener("keyup", ev=>{
  		if ( ev.key==="`" ) {
  			if(dashboardSelection.style("display")=="none"){dashboardSelection.style("display","");}
  			else{dashboardSelection.style("display","none");}
  		}
  	});

    let stats=sim.stats;
    //stats.dom.style.position="absolute";stats.dom.style.top="";stats.dom.style.bottom="5px";stats.dom.style.left="5px";
    //stats.dom.style.display="none";

    stats.showPanel(0);// 0: fps, 1: ms, 2: mb, 3+: custom
    getE("overview-menu").appendChild(stats.dom);
    stats.dom.style.position="relative";stats.dom.style.right="0";

  	//some buttons in the header

  	let root=new Extract();
  	proxy=root.initRoot(sim,schema,getE("simulation-menu"));
    this.proxy=proxy;

  	gui = new dat.GUI({autoPlace:false});
  	document.getElementById("style-menu").appendChild(gui.domElement);
  	gui.domElement.style.zIndex=4;
  	controlsUI.backgroundColor=0xeeeeee;
  	sim.canvas.style.backgroundColor=("#"+controlsUI.backgroundColor.toString(16).padStart(6,"0"));
  	gui.addColor(controlsUI,"backgroundColor").onChange((value)=>{
  		console.log("#"+value.toString(16).padStart(6,"0"));
  		sim.canvas.style.backgroundColor=("#"+value.toString(16).padStart(6,"0"));
  	});
  	gui.add(controlsUI,"switch style");

  }
}







var schema={
	elem:"div.simulation",//shorthand that can specify the class and id of elements
	style:"display:flex;flex-flow:row;box-sizing: border-box;",

	numDimensions:{
		elem:"p",customParent:getE("overview-menu"),text:(value)=>"dimensions: "+value,
	},
	status:{
		elem:"p",style:"margin-left:13px;",customParent:getE("dashboard-status-bar"),
		text:(value)=>"status: "+value,
		listen:true,
	},
	running:{elem:"button",customParent:getE("dashboard-header-buttons"),
		text:(value)=>(value?"Pause":"Resume"),
		onclick:function(o){
			if(o.value){sim.running=false;}
			else{sim.running=true;}
		},
		listen:true,
	},
	reset:{
		elem:"button",customParent:getE("dashboard-header-buttons"),
		text:"Reset",
		onclick:function(o){
			sim.reset();
		}
	},
  resetPrograms:{
		elem:"button",customParent:getE("dashboard-header-buttons"),
		text:"Reset Programs",
		onclick:function(o){
			sim.resetPrograms();
		}
	},
  formulas:{
    elem:"div.sim-objects",customParent:getE("formula-menu"),style:"overflow-y: scroll;flex-grow: 1;",label:"Formulas",
    addChild:{
			func:function(obj){
				let data=this.__obj.__parent.__proxy.addFormula(obj.name);
				return {value:data,key:this.__obj.value.indexOf(data)};
			},
			properties:["name"],
		},
    entries:{

			elem:"div.sim-formula",style:"display:flex;flex-flow:wrap;padding:5px;border-top:1px rgba(200,230,255,0.4) solid;",
			removeItem:{
				func:function(){
					let result=this.__obj.__parent.__parent.value.removeObject(this.__obj.value.name);
					return result;
				},
				rearrange:true,
			},
			name:{
				elem:"p",text:(value)=>"Name: "+value,
			},
			desc:{
				elem:"p",text:(value)=>"description: "+value,
			},
      body:{
        elem:"div",
      },
    },
  },
	objects:{

		elem:"div.sim-objects",customParent:getE("data-menu"),style:"overflow-y: scroll;flex-grow: 1;",label:"Objects",
		addChild:{

			func:function(obj){
				let data=this.__obj.__parent.__proxy.addObject(obj.name);
				return {value:data,key:this.__obj.value.indexOf(data)};
			},
			properties:["name"],
		},

		entries:{

			elem:"div.sim-object",style:"display:flex;flex-flow:wrap;padding:5px;border-top:1px rgba(200,230,255,0.4) solid;",
			removeItem:{
				func:function(){
					let result=this.__obj.__parent.__parent.value.removeObject(this.__obj.value.name);
					return result;
				},
				rearrange:true,
			},
			name:{
				elem:"p",text:(value)=>"Object: "+value,
			},
			size:{
				elem:"p",text:(value)=>"size: "+value,
			},
			attributes:{
				elem:"div",style:"margin-left:1em;width: 100%;box-sizing:border-box;",label:"Attributes",
				addChild:{
					func:function(obj){
						let data=this.__obj.__parent.value.addAttribute(obj.name,parseInt(obj.dimensions));
						return {value:data,key:this.__obj.value.indexOf(data)};
					},
					properties:["name","dimensions"],
				},
				entries:{
					elem:"div",style:"display:flex;flex-flow:wrap;padding:5px;position:relative;",
					removeItem:{
						func:function(){
							let result=this.__obj.__parent.__parent.value.removeAttribute(this.__obj.value.name);
							return result;
						},
						rearrange:true,
					},
					name:{
						elem:"p",text:(value)=>"Attribute: "+value,
					},
					dims:{
						elem:"p",text:(value)=>"dimensions: "+value,
					},
					retrieveData:{
						elem:"button",
						text:"Inspect",
						onclick:function(o){
							//let varname=this.__obj.__parent.name.value;let objname=this.__obj.__parent.__parent.__parent.name.value;
							//let result=this.__obj.value.call(this.__obj.__parent.value);//should function values be bound to the original owner??
              let result=o.value.call(o.parentValue);
							alert(result.join(",").substring(0,1000)+"...");
							console.log(result);

						}
					},
					originalData:{//show the function if the type is a function
						elem:"textinput",style:"width:100%;",text:function(v){
							if(typeof v=="object")return JSON.stringify(v);
							return v.toString();
						},
						oninput:function(o){
							let object=o.parentValue;
							try{
								let newValue=eval("("+o.elemValue+")");
								object.setData(newValue);
							}
							catch(e){
								return true;
							}

						},
					},

				}
			},
			uniforms:{
				elem:"div",style:"margin-left:1em;width: 100%;box-sizing:border-box;",label:"Uniforms",
				addChild:{
					func:function(obj){
						let data=this.__obj.__parent.value.addUniform(obj.name,obj.type);
						return {value:data,key:this.__obj.value.indexOf(data)};
					},
					properties:["name","type"],
				},
				entries:{
					elem:"div",style:"display:flex;flex-flow:wrap;padding:5px;position:relative;",
					removeItem:{
						func:function(){
							let result=this.__obj.__parent.__parent.value.removeUniform(this.__obj.value.name);
							return result;
						},
						rearrange:true,
					},
					name:{
						elem:"p",text:(value)=>"Name: "+value,
					},
					type:{
						elem:"p",text:(value)=>"type: "+value,
					},
					originalData:{//show the function if the type is a function
						elem:"textinput",style:"width:100%;",text:function(v){
							if(typeof v=="object")return JSON.stringify(v);
							return v.toString();
						},
						oninput:function(o){
							let object=o.parentValue;
							try{
								let newValue=eval("("+o.elemValue+")");
								object.setData(newValue);
							}
							catch(e){
								return true;
							}

						},
					},

				}
			},
		}
	},
	uniforms:{
		elem:"div.sim-uniforms",style:"overflow-y: scroll;width:20%;flex-grow: 1;",label:"Uniforms",
		addChild:{
			func:function(obj){
				let data=this.__obj.__parent.value.addUniform(obj.name,obj.type);
				return {value:data,key:this.__obj.value.indexOf(data)};
			},
			properties:["name","type"],
		},
		entries:{
			elem:"div",style:"display:flex;flex-flow:wrap;padding:5px;position:relative;",
			removeItem:{
				func:function(){
					let result=this.__obj.__parent.__parent.value.removeUniform(this.__obj.value.name);
					return result;
				},
				rearrange:true,
			},
			name:{
				elem:"p",text:(value)=>"Name: "+value,
			},
			type:{
				elem:"p",text:(value)=>"type: "+value,
			},
			originalData:{//show the function if the type is a function
				elem:"textinput",style:"width:100%;",text:function(v){
					if(typeof v=="object")return JSON.stringify(v);
					return v.toString();
				},
				oninput:function(o){
					let object=o.parentValue;
					try{
						let newValue=eval("("+o.elemValue+")");
						object.setData(newValue);
					}
					catch(e){
						return true;
					}

				},
			},

		}
	},

	programs:{

		elem:"div.sim-programs",customParent:getE("programs-menu"),style:"overflow-y: scroll;flex-grow: 1;",label:"Programs",
		addChild:{
			func:function(obj){

				let data;let simObjects=this.__obj.__parent.value.objects;
				if(obj.type=="TF"&&(obj.object in simObjects)){
					data=this.__obj.__parent.value.addTFProgram(simObjects[obj.object]);
				}
				else if(obj.type=="RTT"&&(obj.object in simObjects)&&(obj.outputObject in simObjects)&&(obj.outputAttribute in simObjects[obj.outputObject].attributes)){
					data=this.__obj.__parent.value.addRTTProgram(simObjects[obj.object],simObjects[obj.outputObject].attributes[obj.outputAttribute]);
				}
				else return false;//cannot add
				this.__obj.__parent.value.reset();
				return {value:data,key:this.__obj.value.indexOf(data)};
			},
			properties:["type","object","outputObject","outputAttribute"],
		},
		entries:{
      debug:true,
			elem:"div.sim-program",style:"display:flex;flex-flow:wrap;padding:5px;position:relative;border-top:1px rgba(200,230,255,0.4) solid;",
			removeItem:{
				func:function(){
					let sim=this.__obj.__parent.__parent.value;
					let result=sim.removeProgram(this.__obj.value);
					sim.reset();

					return result;
				},
				rearrange:true,
			},
			type:{
				elem:"p",text:(value)=>value+" program",
			},
			sourceObject:{
				elem:"p",text:(value)=>"of object: "+value.name,
			},
			targetAttribute:{
				elem:"p",text:(value)=>", output to: "+value.name,
			},
			targetAttributeOwner:{
				elem:"p",text:(value)=>"of object: "+value.name,
			},
			instances:{
				elem:"textinput",text:(value)=>(value?value:"(no instances)"),
				oninput:function(o){
					let program=o.parentValue;
					if(parseInt(o.newValue))
					program.instances=parseInt(o.elemValue);
				},
			},
			blendingName:{
				elem:"textinput",style:"max-width:600px;", label:"blending",text:(value)=>(value?value:"(none)"),
				oninput:function(o){
					let program=o.parentValue;
					program.setBlending(o.elemValue);
				},
			},
      isBreakpoint:{
        elem:"checkbox",label:"breakpoint",oninput:function(o){
					let program=o.parentValue;
					program.isBreakpoint=o.elemValue;//this.checked;
				},
      },
      disabled:{
        elem:"checkbox",label:"disabled",oninput:function(o){
					let program=o.parentValue;
					program.disabled=o.elemValue;
				},
      },
			code:{
				elem:"textarea.code",style:"width:100%;max-width:600px;",text:(value)=>(value?value:"enter code here"),
				oninput:function(o){
					let program=o.parentValue;program.code=o.elemValue;//this.value
				},
			},
			vscode:{
				elem:"textarea.code",style:"width:100%;max-width:600px;",text:(value)=>(value?value:"enter vertex shader code here"),
				oninput:function(o){
					let program=o.parentValue;program.vscode=o.elemValue;//this.value;
				},
			},
			fscode:{
				elem:"textarea.code",style:"width:100%;max-width:600px;",text:(value)=>(value?value:"enter vertex shader code here"),
				oninput:function(o){
					let program=o.parentValue;program.fscode=o.elemValue;
				},
			}
		}

	},
	visualization:{
		elem:"div.visualization",style:"display:flex;flex-flow:row;box-sizing: border-box;",customParent:getE("visualization-menu"),
		objects:{
			elem:"div.viz-objects",style:"overflow-y: scroll;flex-grow: 1;",label:"Visual objects",
      addChild:{
  			func:function(obj){
  				let data;let viz=this.__obj.__parent.value;
  				try{
            data=this.__obj.__parent.value.addObject(obj.object);
          }
          catch(e){
            console.log(e);return false;//cannot add
          }
  				this.__obj.__parent.__parent.value.reset();
  				return {value:data,key:this.__obj.value.indexOf(data)};
  			},
  			properties:["object"],
  		},
			entries:{
				elem:"div.viz-object",style:"display:flex;flex-flow:wrap;padding:5px;",
        removeItem:{
  				func:function(){
  					let result=this.__obj.__parent.__parent.value.removeObject(this.__obj.value.name);
  					return result;
  				},
  				rearrange:true,
  			},
				originalObject:{
					elem:"p",text:(value)=>"Original object: "+value.name,
				},
				visible:{
					elem:"checkbox",update:true,oninput:true,
				},
			},
		},
	},

};



function switchStyle(bright){
 var el1 = getE('style-light'),el2 = getE('style-dark');
  if(el1.disabled){
	  el1.disabled = false;
	el2.disabled = true;
  }
  else{
	  el1.disabled = true;
	el2.disabled = false;
  }
}
var controlsUI={"switch style":switchStyle};


function getString(obj){
	if(typeof obj=="function")return obj.toString();
	return JSON.stringify(obj);
}

function toNormalText(str){//un-Camel case
	str=String(str);
	return str.replace(/(?=[a-z])([A-Z/]+)/g, ' $1').replace("_"," ").replace("-"," ").replace(/^./, function(str){ return str.toUpperCase(); });
}
//UI helpers

function addButton(parentElem,text,func,rightclickfunc){
	let s=d3.select(parentElem).append("button").text(text);
	let buttonElem=s.node();
	s.on("click",()=>func());
	if(rightclickfunc){
		if(typeof rightclickfunc=="function")s.on("contextmenu",(d)=>{d3.event.stopPropagation();d3.event.preventDefault();rightclickfunc(d);});
		else s.on("contextmenu",(d)=>{d3.event.stopPropagation();d3.event.preventDefault();func(true);});
	}
	return s;
}
