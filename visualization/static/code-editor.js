import {addKeyListener,addCheckbox,toNormalText,getQuditValues} from "./util.js";
import dataDef from "./data-def.js";
import {set_qasm} from "./server-connection.js";
let body=d3.select("body");


export let codePanel=body.append("div").attr("id","code-editor").style("position","absolute").attr("class","panel").style("top","0%").style("bottom","0").style("left","30%").style("right","30%").attr("class","panel")
.style("font-family","monospace").style("white-space","pre").style("z-index",10).style("display","none").style("overflow-y","scroll").style("display","none");
addKeyListener(body,"q",()=>{
  if(codePanel.style("display")=="none"){
    console.log("displaying");
    codePanel.style("display","block");
  }
  else{
    console.log("hiding")
    codePanel.style("display","none");
  }
});

let codePanelContent=codePanel.append("div").style("position","relative").style("width","100%").style("height","80%");
let codePanelFeedback=codePanel.append("div").style("position","relative").style("width","100%").style("height","10%");
let  compileButton=codePanel.append("button").style("width","65px").style("height","25px").text("Compile").on("click",()=>{
  let textarea = codeTextarea.node();
  set_qasm(textarea.value);
});

  export let codeArea=codePanelContent.append("code").attr("class","language-javascript").style("position","absolute").style("width","100%").style("height","100%").style("overflow","scroll").style("box-sizing","border-box").style("padding","2px").style("background","rgba(200,225,255,0.1)")
  .style("border","1.6px solid transparent").style("white-space","pre-wrap");
 export let codeTextarea=codePanelContent.append("textarea").style("opacity","0.5").style("position","absolute").style("width","100%").style("height","100%").style("overflow","scroll")
 .style("white-space","pre-wrap").style("word-spacing","normal").style("word-break","normal").style("line-height","1.5").style("font-family",'Consolas,Monaco,"Andale Mono","Ubuntu Mono",monospace').style("font-size","1em")
 .style("color","rgba(0,0,0,0.2)").style("background","transparent").style("caret-color","darkgrey")
 .attr("spellcheck","false")
 .on("keydown",(ev)=>{ev.stopPropagation();});


export function updateCodeHighlight(){
  let code = codeArea.node();
  let textarea = codeTextarea.node();
  code.innerHTML = Prism.highlight(textarea.value, Prism.languages.javascript);
}
export function updateCode(str){
  console.log("code update received",str);
  let code = codeArea.node();
  let textarea = codeTextarea.node();
  textarea.value=str;
  code.innerHTML = Prism.highlight(textarea.value, Prism.languages.javascript);
}

codeTextarea.on("input",function() {
  console.log("input received");
  let code = codeArea.node();
  let textarea = codeTextarea.node();
    code.innerHTML = Prism.highlight(textarea.value, Prism.languages.javascript);
});
