

export default class SvgBackground{
  constructor(svg){
    if (svg instanceof d3.selection==false){svg=d3.select(svg)}
    let svgDefs = svg.select('defs');
    if (svgDefs.node()==null){
      svgDefs = svg.append('defs');
    }

    this.gradient=svgDefs.append("linearGradient").attr("gradientTransform","rotate(226, 0.5, 0.5)").attr("x1","50%").attr("y1","0%").attr("x2","50%").attr("y2","100%").attr("id","ffflux-gradient");

    this.feColor1=this.gradient.append("stop").attr("stop-color","hsl(179, 90%, 82%)").attr("stop-opacity","1").attr("offset","0%");
    this.feColor2=this.gradient.append("stop").attr("stop-color","hsl(227, 90%, 75%)").attr("stop-opacity","1").attr("offset","100%");

    this.filter=svgDefs.append("filter").attr("x","-20%").attr("y","-20%").attr("filterUnits","objectBoundingBox")
                                        .attr("primitiveUnits","userSpaceOnUse").attr("color-interpolation-filters","sRGB");
    this.turbulence= this.filter.append("feTurbulence").attr("type","fractalNoise").attr("baseFrequency","0.006 0.004").attr("numOctaves","1")  .attr("seed","2").attr("stitchTiles","stitch").attr("x","0%").attr("y","0%").attr("width","100%")
    .attr("height","100%");
    this.feGaussianBlur=this.filter.append("feGaussianBlur").attr("stdDeviation","13 80").attr("in","turbulence").attr("edgeMode","duplicate")  .attr("result","blur").attr("x","0%").attr("y","0%").attr("width","100%").attr("height","100%");
    this.filter.append("feBlend").attr("mode","hard-light").attr("in","SourceGraphic").attr("in2","blur")  .attr("result","blend").attr("x","0%").attr("y","0%").attr("width","100%").attr("height","100%");

    this.backgroundRect=svg.append("rect").attr("width","100%").attr("height","100%").attr("x","-50%").attr("y","-50%").attr("fill","url(#ffflux-gradient)").attr("filter","url(#ffflux-filter)");

    this.animate();
    this.animate2();

  }
  animate(repeat=false){
    let randomHue1=Math.floor(Math.random()*30)+150;
    let randomHue2=Math.floor(Math.random()*50)+160;
    let randomDuration=Math.floor(Math.random()*5000)+3000;

    this.feColor1
    .transition()
    .duration(randomDuration)
    .attr("stop-color","hsl("+randomHue1+", 80%, 90%)")
    .transition()
    .duration(randomDuration)
    .attr("stop-color","hsl("+randomHue2+", 80%, 82%)")
    .on("end", ()=>{if(repeat){this.animate(true);}} );


  }
  animate2(repeat=false) {
    let randomHue3=Math.floor(Math.random()*30)+180;
    let randomHue4=Math.floor(Math.random()*50)+200;
    let randomDuration=Math.floor(Math.random()*5000)+3000;

    this.feColor2
    .transition()
    .duration(randomDuration)
    .attr("stop-color","hsl("+randomHue3+", 80%, 85%)")
    .transition()
    .duration(randomDuration)
    .attr("stop-color","hsl("+randomHue4+", 80%, 80%)")
    .on("end", ()=>{if(repeat){this.animate2(true);}} );

  }


}
