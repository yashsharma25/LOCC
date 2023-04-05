//animations here are abstract processes that may be defined on data and change the data for display (eg. current state), or defined on the view and only change the visual objects

export default class Animation{

  constrcutor(def){
    this.def=def;
    this.tick=0;
  }
  tick(){
    this.tick+=1;
    let def=this.def;
    if(def.paused===true){continue;}
    if(typeof def.paused=="function"&&def.paused()){continue;}
    let step=1;if(def.step!==undefined){if(typeof def.step =="function")step=def.step();else step=def.step;}
    if(def.bouncing&&def.reversed){def.value-=step;}
    else{def.value+=step;}
    let min=0,max=10;
    if(def.min!==undefined){if(typeof def.min =="function")min=def.min();else min=def.min;}
    if(def.max!==undefined){if(typeof def.max =="function")max=def.max();else max=def.max;}
    def.lastMax=max;def.lastMin=min;
    //min and max are both allowed reachable values; if at a step max is reached it will stay there; if it's exceeded, that step's value is set to min (or set to max and will start to bounce back next step if enabled); if you want to avoid a value just set the min or max above/below it
    if(def.value>=max){
      if(def.bouncing){def.reversed=true;def.value=max;}
      else{
        if(def.value>max)def.value=min;//if exactly at max, it stays there for one step
      }
    }
    if(def.value<=min){
      if(def.bouncing){def.reversed=false;def.value=min;}
      else{
        if(def.value<min)def.value=min;//if exactly at min, it stays there for one step
      }
    }

    let newIntValue=Math.floor(def.value);//for use in array indices etc
    if(def.intValue!==undefined&&def.intValue!=newIntValue){

      if(def.intTick){
        def.intTick(newIntValue);
      }
    }
    def.intValue=newIntValue;
    if(def.tick){
      def.tick(time);
    }
  }

}
