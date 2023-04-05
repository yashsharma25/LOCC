

export default class State{
  constructor(view,def){
    this.view=view;
    this.def=def;
  }
  set(inputData){
    console.log(inputData);
    //dims:qudit dims,parties:parties(currently one qudit per party),state:state vector
    this.inputData=inputData;
    let def=this.def;

    //note: this func should prepare all data objects, including non-visible ones like possibilities

    let dataObj={};
    window.dataObj=dataObj;
    console.log(dataObj);

    //data defs don't have object/relation split, rather, they are like database tables where each kind of object can refeence others with arbitrary numbers of attributes
    for(let name in def){
      let objDef=def[name];
      let dataFunc=objDef.data;
      let data=dataFunc(inputData,dataObj);
      //for(let d of data){d.objType=name;}//this is only useful for views
      dataObj[name]=data;
    }
      //todo: define references; soruce/target ids should be handled by view instead.
      /*
      
      */


    this.view.set(dataObj);
  }
}
