// Reproducible procedural mesh for the native GitHub STL experiment.
// Run: node scripts/generate-3d-observatory.mjs
// Keeps the 3D object and its Markdown fence in sync.
import { writeFileSync, mkdirSync } from "node:fs";
const makeSculpture = function makeSculpture(){
 const triangles=[];
 const add=(a,b,c)=>triangles.push([a,b,c]);
 const vadd=(a,b)=>a.map((t,i)=>t+b[i]);
 const rot=(p,rx=0,ry=0,rz=0)=>{
   let [x,y,z]=p;
   let C=Math.cos(rx),S=Math.sin(rx);[y,z]=[y*C-z*S,y*S+z*C];
   C=Math.cos(ry);S=Math.sin(ry);[x,z]=[x*C+z*S,-x*S+z*C];
   C=Math.cos(rz);S=Math.sin(rz);[x,y]=[x*C-y*S,x*S+y*C];
   return [x,y,z];
 };
 const quad=(a,b,c,d)=>{add(a,b,c);add(a,c,d)};
 const box=(cx,cy,cz,sx,sy,sz)=>{
   const v=[];
   for(let j=0;j<2;j++)for(let k=0;k<2;k++)for(let i=0;i<2;i++)
     v.push([cx+(i-.5)*sx,cy+(k-.5)*sy,cz+(j-.5)*sz]);
   const sides=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]];
   sides.forEach(idx=>quad(...idx.map(i=>v[i])));
 };
 const torus=(R,r,nu,nv,c=[0,0,0],angles=[0,0,0])=>{
   const point=(i,j)=>{
     const u=2*Math.PI*i/nu, v=2*Math.PI*j/nv;
     return vadd(rot([(R+r*Math.cos(v))*Math.cos(u),(R+r*Math.cos(v))*Math.sin(u),r*Math.sin(v)],...angles),c);
   };
   for(let i=0;i<nu;i++)for(let j=0;j<nv;j++){
     let a=point(i,j),b=point(i+1,j),cc=point(i+1,j+1),d=point(i,j+1);
     quad(a,b,cc,d);
   }
 };
 const sphere=(R,nLon,nLat,c=[0,0,0])=>{
   const point=(theta,phi)=>vadd([R*Math.sin(phi)*Math.cos(theta),R*Math.sin(phi)*Math.sin(theta),R*Math.cos(phi)],c);
   for(let j=0;j<nLat;j++){
     const p0=Math.PI*j/nLat,p1=Math.PI*(j+1)/nLat;
     for(let i=0;i<nLon;i++){
       let a=point(2*Math.PI*i/nLon,p0),b=point(2*Math.PI*(i+1)/nLon,p0);
       let cc=point(2*Math.PI*(i+1)/nLon,p1),d=point(2*Math.PI*i/nLon,p1);
       if(j===0)add(a,cc,d);
       else if(j===nLat-1)add(a,b,d);
       else quad(a,b,cc,d);
     }
   }
 };
 const crystal=(x,y,z,s)=>{
   const v=[[x+s,y,z],[x-s,y,z],[x,y+s,z],[x,y-s,z],[x,y,z+s*1.6],[x,y,z-s*1.25]];
   for(const [a,b,c] of [[0,2,4],[2,1,4],[1,3,4],[3,0,4],[2,0,5],[1,2,5],[3,1,5],[0,3,5]])add(v[a],v[b],v[c]);
 };
 const letters={
   S:["01111","11000","10000","01110","00001","00011","11110"],
   A:["01110","10001","10001","11111","10001","10001","10001"],
   I:["11111","00100","00100","00100","00100","00100","11111"]
 };
 const glyph=(char,x0,y0,z0,u=.20)=>{
   const lines=letters[char];
   lines.forEach((row,j)=>[...row].forEach((p,i)=>{if(p==="1")box(x0+i*u,y0,z0+(6-j)*u,u*.81,u*.62,u*.81)}));
 };
 // The event horizon, a dense center surrounded by three tilted accretion bands.
 sphere(1.10,20,10,[0,0,.2]);
 torus(1.50,.13,32,6,[0,0,.2],[.10,.16,-.30]);
 torus(2.03,.075,32,5,[0,0,.2],[.26,-.16,.22]);
 torus(2.62,.055,32,4,[0,0,.2],[-.23,.18,-.08]);
 // A distinctive outer orbit, intentionally split into three smaller structures.
 for(let k=0;k<3;k++){
   const a=(2*Math.PI*k/3)+.25, rad=3.45;
   const x=rad*Math.cos(a), y=rad*Math.sin(a);
   crystal(x,y,.40+(k-1)*.15,.32);
   const a2=(2*Math.PI*(k+.38)/3);
   const x2=3.00*Math.cos(a2),y2=3.00*Math.sin(a2);
   box(x2,y2,-1.3,.23,.23,.85);
   crystal(x2,y2,-.66,.19);
 }
 // A deliberately physical wordmark: the geometry literally spells SAI,
 // yet nothing relies on textures, vertex color, web scripts, or external hosting.
 glyph("S",-1.80,-3.30,-2.20,.225);
 glyph("A",-.54,-3.30,-2.20,.225);
 glyph("I",.72,-3.30,-2.20,.225);
 const norm=(a,b,c)=>{
   const u=b.map((x,i)=>x-a[i]),v=c.map((x,i)=>x-a[i]);
   const p=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
   const d=Math.hypot(...p);
   return d<1e-10?[0,0,0]:p.map(x=>x/d);
 };
 const fmt=x=>Object.is(x,-0)?"0.000":x.toFixed(3);
 let out="solid sai_observatory\n";
 for(const [a,b,c] of triangles){
   const n=norm(a,b,c);
   out+=` facet normal ${n.map(fmt).join(" ")}\n  outer loop\n   vertex ${a.map(fmt).join(" ")}\n   vertex ${b.map(fmt).join(" ")}\n   vertex ${c.map(fmt).join(" ")}\n  endloop\n endfacet\n`;
 }
 out+="endsolid sai_observatory\n";
 return {out,triangleCount:triangles.length,byteCount:out.length};
};
const model = makeSculpture();
mkdirSync("models", {recursive:true});
mkdirSync("experiments", {recursive:true});
writeFileSync("models/sai-observatory.stl",model.out);
const intro = "# The SAI Observatory — native 3D inside GitHub\n\nThis is a **real, draggable 3D object rendered by GitHub itself**, not a video, screenshot, SVG, iframe, or JavaScript application.\n\nRotate it to explore a compact orbital sculpture: an event horizon with three accretion rings, three research satellites, and an extruded **SAI** wordmark.\n\nThe geometry is authored as a compact ASCII STL mesh and rendered by the native GitHub Markdown `stl` viewer. Try dragging the object to rotate it, scrolling to zoom, or switching the viewer to wireframe.\n\n> **Experiment, not the public profile.** This is a proof-of-concept for a truly three-dimensional profile. The project links, research notes, accessibility, and primary text still need a readable Markdown layer.\n\n```stl\n";
const closing = "```\n\n## What the 3D viewer proves\n\n- The geometry is truly three-dimensional and explorable without leaving GitHub.\n- STL has no embedded colors, textures, materials, click targets, or runtime animation. It's best for the **visual centerpieces** of a profile, not navigation or long text.\n- We could use multiple small STL viewers for projects, kernel diagrams, or research architectures, with short Markdown and hyperlinks between them.\n- GitHub's README itself has a 500 KiB truncation limit, so the complete profile needs careful triangle and byte budgets.\n\n[Open the same model in GitHub's standalone STL viewer](../models/sai-observatory.stl) · [Return to the existing profile](../README.md)\n\nGenerated for the native 3D profile experiment. No third-party scripts or model hosting are involved.\n";
writeFileSync("experiments/native-3d-observatory.md",intro+model.out+closing);
process.stdout.write(JSON.stringify({facets:model.triangleCount,bytes:model.byteCount})+"\n");
