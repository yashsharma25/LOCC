


export function addKeyListener(elem,key,keydownfunc,keyupfunc,preventDefault){
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
export function addCheckbox(parentElem,text,func){
    if (parentElem instanceof d3.selection ==false){parentElem=d3.select(parentElem);}

		let s=parentElem.append("div");
		let label=s.append("p").text(text);
		let checkbox=s.append("input").attr("type","checkbox");
		let checkboxElem=checkbox.node();
		checkbox.on("input",()=>func(checkboxElem.checked));
		let onUpdate=function(value){checkboxElem.checked=value;};
		return onUpdate;//call when the value is changed outside
	}






export function getQuditValues(index,dims){
  let result=[];
  for(let d of dims){

    result.unshift(index%d);
    index=Math.floor(index/d);
  }
  return result;
}

export function getSimilarity(values1,values2){
  let a=0;
  for(let i=0;i<values1.length;i++){
    if(values1[i]==values2[i]){a++;}
  }
  return a/values1.length;
}
const floatFormatter = d3.format(".2f");
export function complex2str(x){
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
export function toNormalText(str){//un-Camel case
	str=String(str);
	return str.replace(/([a-z])([A-Z/]+)/g, '$1 $2').replace("_"," ").replace(/^./, function(str){ return str.toUpperCase(); });
}
