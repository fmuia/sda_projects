/* ==== fig: Colgate counterfactual schematic (S4) ==== */
(function(){
  const svg=document.getElementById('svgCounter'); if(!svg)return;
  function draw(){
    clr(svg); const c=COL();
    const D=DATA.counter, W=720, H=250, mL=52, mR=120, mT=26, mB=34;
    const n=D.actual.length, L=D.launch;
    const lo=Math.min(...D.cf, ...D.actual)-6, hi=Math.max(...D.actual)+6;
    const x=lin(0,n-1,mL,W-mR), y=lin(lo,hi,H-mB,mT);
    // axes
    svg.appendChild(el('line',{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:c.rule,'stroke-width':1}));
    svg.appendChild(el('line',{x1:mL,y1:mT,x2:mL,y2:H-mB,stroke:c.rule,'stroke-width':1}));
    svg.appendChild(el('text',{x:(mL+W-mR)/2,y:H-8,'text-anchor':'middle','font-size':11},'months around the launch'));
    svg.appendChild(el('text',{x:14,y:(mT+H-mB)/2,'font-size':11,transform:`rotate(-90 14 ${(mT+H-mB)/2})`,'text-anchor':'middle'},'category sales (index)'));
    [0,L,n-1].forEach(t=>svg.appendChild(el('text',{x:x(t),y:H-mB+14,'text-anchor':'middle','font-size':10},t-L)));
    // launch marker
    svg.appendChild(el('line',{x1:x(L),y1:mT,x2:x(L),y2:H-mB,stroke:c.faint,'stroke-width':1,'stroke-dasharray':'4 3'}));
    svg.appendChild(el('text',{x:x(L),y:mT-8,'text-anchor':'middle','font-size':10,fill:c.muted},'launch'));
    // gap shading (post-launch, between counterfactual and actual)
    let dTop='M', dBot='';
    for(let i=L;i<n;i++) dTop+=(i>L?'L':'')+x(i).toFixed(1)+' '+y(D.actual[i]).toFixed(1)+' ';
    for(let i=n-1;i>=L;i--) dBot+='L'+x(i).toFixed(1)+' '+y(D.cf[i]).toFixed(1)+' ';
    svg.appendChild(el('path',{d:dTop+dBot+'Z',fill:c.green,opacity:.16}));
    // counterfactual + actual lines
    svg.appendChild(el('path',{d:path(D.cf.map((v,i)=>[x(i),y(v)])),fill:'none',stroke:c.grey,'stroke-width':2,'stroke-dasharray':'6 4'}));
    svg.appendChild(el('path',{d:path(D.actual.map((v,i)=>[x(i),y(v)])),fill:'none',stroke:c.navy,'stroke-width':2.4}));
    // legend (line swatches, top-right band)
    const lx=W-mR+10;
    svg.appendChild(el('line',{x1:lx,y1:mT+8,x2:lx+22,y2:mT+8,stroke:c.navy,'stroke-width':2.4}));
    svg.appendChild(el('text',{x:lx+27,y:mT+11,'font-size':10},'actual'));
    svg.appendChild(el('line',{x1:lx,y1:mT+24,x2:lx+22,y2:mT+24,stroke:c.grey,'stroke-width':2,'stroke-dasharray':'6 4'}));
    svg.appendChild(el('text',{x:lx+27,y:mT+27,'font-size':10},'no launch'));
    svg.appendChild(el('rect',{x:lx,y:mT+34,width:22,height:9,fill:c.green,opacity:.3}));
    svg.appendChild(el('text',{x:lx+27,y:mT+42,'font-size':10},'incremental?'));
  }
  draw(); window.__redraw.push(draw);
})();

/* ==== fig: ROAS inversion + lift-test repair (S6) ==== */
(function(){
  const svg=document.getElementById('svgRoas'); if(!svg)return;
  const cb=document.getElementById('roasCal'), rd=document.getElementById('roasRead');
  function draw(){
    clr(svg); const c=COL();
    const W=720, H=172, mB=28, mT=20;
    const R=DATA.roas, cal=cb&&cb.checked;
    // left panel: the baseline model's claim (ordering only; the post prints no baseline ROAS values)
    svg.appendChild(el('text',{x:180,y:mT,'text-anchor':'middle','font-size':12,'font-weight':'700',fill:c.navy},'uncalibrated model: the ranking'));
    svg.appendChild(el('rect',{x:60,y:48,width:240,height:32,rx:8,fill:'none',stroke:c.red,'stroke-width':1.6}));
    svg.appendChild(el('text',{x:180,y:69,'text-anchor':'middle','font-size':13,fill:c.red,'font-weight':'700'},'x1 ranked above x2'));
    svg.appendChild(el('text',{x:180,y:100,'text-anchor':'middle','font-size':11,fill:c.muted},'no experiment in the model'));
    svg.appendChild(el('text',{x:180,y:117,'text-anchor':'middle','font-size':11,fill:c.muted},'the direct opposite of the truth'));
    // right panel: true ROAS bars, revealed by calibration
    svg.appendChild(el('text',{x:530,y:mT,'text-anchor':'middle','font-size':12,'font-weight':'700',fill:c.navy},
      cal?'calibrated with the lift tests: the truth':'planted truth (check the box)'));
    const y=lin(0,190,H-mB,mT+18), bx=[440,600], names=['x1','x2'], vals=[R.x1,R.x2];
    svg.appendChild(el('line',{x1:410,y1:H-mB,x2:690,y2:H-mB,stroke:c.rule}));
    names.forEach((nm,i)=>{
      const bh=(H-mB)-y(vals[i]);
      if(cal){
        svg.appendChild(el('rect',{x:bx[i],y:y(vals[i]),width:56,height:bh,rx:4,fill:i?c.green:c.blue,opacity:.85}));
        svg.appendChild(el('text',{x:bx[i]+28,y:y(vals[i])-6,'text-anchor':'middle','font-size':12,'font-weight':'700',fill:c.ink},vals[i].toFixed(2)));
      } else {
        svg.appendChild(el('rect',{x:bx[i],y:y(vals[i]),width:56,height:bh,rx:4,fill:'none',stroke:c.faint,'stroke-dasharray':'4 3'}));
        svg.appendChild(el('text',{x:bx[i]+28,y:y(vals[i])-6,'text-anchor':'middle','font-size':12,fill:c.faint},'?'));
      }
      svg.appendChild(el('text',{x:bx[i]+28,y:H-mB+16,'text-anchor':'middle','font-size':11},nm+' ROAS'));
    });
    if(rd) rd.textContent = cal ? 'ranking corrected: x2 nearly twice x1' : 'the model has only observational spend';
  }
  if(cb)cb.addEventListener('change',draw);
  draw(); window.__redraw.push(draw);
})();

/* ==== fig: the MMM / experiment / synthetic-control loop (S7) ==== */
(function(){
  const svg=document.getElementById('svgLoop'); if(!svg)return;
  function draw(){
    clr(svg); const c=COL();
    const nodes=[
      {x:170,y:52,w:150,label:'MMM',sub:'always-on model'},
      {x:88,y:212,w:150,label:'Geo experiment',sub:'episodic truth'},
      {x:252,y:212,w:150,label:'Synthetic control',sub:'reads it out'},
    ];
    function box(n,col){
      svg.appendChild(el('rect',{x:n.x-n.w/2,y:n.y-26,width:n.w,height:52,rx:10,fill:'none',stroke:col,'stroke-width':2}));
      svg.appendChild(el('text',{x:n.x,y:n.y-5,'text-anchor':'middle','font-size':13,'font-weight':'700',fill:c.navy},n.label));
      svg.appendChild(el('text',{x:n.x,y:n.y+13,'text-anchor':'middle','font-size':10,fill:c.muted},n.sub));
    }
    box(nodes[0],c.blue); box(nodes[1],c.orange); box(nodes[2],c.green);
    function arrow(x1,y1,x2,y2){
      svg.appendChild(el('line',{x1,y1,x2,y2,stroke:c.faint,'stroke-width':1.6}));
      const a=Math.atan2(y2-y1,x2-x1);
      svg.appendChild(el('path',{d:`M${x2} ${y2} L${x2-9*Math.cos(a-0.4)} ${y2-9*Math.sin(a-0.4)} L${x2-9*Math.cos(a+0.4)} ${y2-9*Math.sin(a+0.4)} Z`,fill:c.faint}));
    }
    arrow(128,80,100,182);  // MMM -> experiment (asks)
    arrow(120,182,148,80);  // experiment -> MMM (calibrates)
    arrow(166,224,176,224); // experiment -> SC
    svg.appendChild(el('text',{x:56,y:132,'font-size':10,fill:c.muted},'asks for'));
    svg.appendChild(el('text',{x:56,y:144,'font-size':10,fill:c.muted},'ground truth'));
    svg.appendChild(el('text',{x:152,y:132,'font-size':10,fill:c.muted},'calibrates'));
    svg.appendChild(el('text',{x:152,y:144,'font-size':10,fill:c.muted},'(priors, lift tests)'));
    svg.appendChild(el('text',{x:170,y:262,'text-anchor':'middle','font-size':10,fill:c.muted},'nb06 · this morning: Ch 9 · this closing act: all three'));
  }
  draw(); window.__redraw.push(draw);
})();

/* ==== fig: break the counterfactual yourself (probe slide) ==== */
(function(){
  const svg=document.getElementById('svgBreak'); if(!svg)return;
  const on=document.getElementById('brkOn'), tr=document.getElementById('brkT');
  const tv=document.getElementById('brkTv'), rd=document.getElementById('brkRead');
  function draw(){
    clr(svg); const c=COL();
    const D=DATA.counter, n=D.actual.length, L=D.launch;
    const active=on&&on.checked, t2=tr?+tr.value:10;
    if(tr)tr.disabled=!active;
    if(tv)tv.textContent=(t2-L>=0?'+':'')+(t2-L);
    // world: base = D.cf; first launch lift = D.actual - D.cf; second launch = same ramp shape
    const lift2=i=>(active&&i>=t2)?11*(1-Math.exp(-(i-t2)/2.5)):0;
    const y=[],cfTrue=[];
    for(let i=0;i<n;i++){cfTrue.push(D.cf[i]+lift2(i));y.push(D.actual[i]+lift2(i));}
    // the analyst's counterfactual: trend + seasonality fit on the observed pre-period.
    // In the clean world this model is EXACT (the schematic base is linear + sin(i/2.2)),
    // so measured/true reads 100% until the second launch contaminates the fit window.
    const feats=i=>[1,i,Math.sin(i/2.2)];
    const M=[[0,0,0],[0,0,0],[0,0,0]],v=[0,0,0];
    for(let i=0;i<L;i++){const f=feats(i);
      for(let r=0;r<3;r++){v[r]+=f[r]*y[i];for(let s=0;s<3;s++)M[r][s]+=f[r]*f[s];}}
    for(let r=0;r<3;r++){                       // Gaussian elimination, 3x3
      let p=r;for(let s=r+1;s<3;s++)if(Math.abs(M[s][r])>Math.abs(M[p][r]))p=s;
      [M[r],M[p]]=[M[p],M[r]];[v[r],v[p]]=[v[p],v[r]];
      for(let s=r+1;s<3;s++){const f=M[s][r]/M[r][r];
        for(let k=r;k<3;k++)M[s][k]-=f*M[r][k]; v[s]-=f*v[r];}}
    const co=[0,0,0];
    for(let r=2;r>=0;r--){let acc=v[r];for(let k=r+1;k<3;k++)acc-=M[r][k]*co[k];co[r]=acc/M[r][r];}
    const cfHat=[]; for(let i=0;i<n;i++){const f=feats(i);cfHat.push(co[0]*f[0]+co[1]*f[1]+co[2]*f[2]);}
    // measured vs true lift over the post-period
    let g=0,t=0; for(let i=L;i<n;i++){g+=y[i]-cfHat[i];t+=D.actual[i]-D.cf[i];}
    const share=Math.round(100*g/t);
    // scales
    const W=720,H=200,mL=52,mR=118,mT=20,mB=30;
    const lo=Math.min(...cfHat,...y,...cfTrue)-5, hi=Math.max(...y,...cfHat)+5;
    const x=lin(0,n-1,mL,W-mR), yy=lin(lo,hi,H-mB,mT);
    svg.appendChild(el('line',{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:c.rule}));
    [0,L,n-1].forEach(k=>svg.appendChild(el('text',{x:x(k),y:H-mB+14,'text-anchor':'middle','font-size':10},k-L)));
    svg.appendChild(el('text',{x:(mL+W-mR)/2,y:H-4,'text-anchor':'middle','font-size':10},'months around the launch'));
    svg.appendChild(el('line',{x1:x(L),y1:mT,x2:x(L),y2:H-mB,stroke:c.faint,'stroke-dasharray':'4 3'}));
    svg.appendChild(el('text',{x:x(L),y:mT-6,'text-anchor':'middle','font-size':10,fill:c.muted},'launch'));
    if(active){
      svg.appendChild(el('line',{x1:x(t2),y1:mT,x2:x(t2),y2:H-mB,stroke:c.orange,'stroke-dasharray':'4 3'}));
      svg.appendChild(el('text',{x:x(t2),y:mT-6,'text-anchor':'middle','font-size':10,fill:c.orange},'2nd launch'));
    }
    svg.appendChild(el('path',{d:path(cfTrue.map((v,i)=>[x(i),yy(v)])),fill:'none',stroke:c.grey,'stroke-width':2,'stroke-dasharray':'6 4'}));
    svg.appendChild(el('path',{d:path(cfHat.map((v,i)=>[x(i),yy(v)])),fill:'none',stroke:c.red,'stroke-width':2,'stroke-dasharray':'2 3'}));
    svg.appendChild(el('path',{d:path(y.map((v,i)=>[x(i),yy(v)])),fill:'none',stroke:c.navy,'stroke-width':2.4}));
    // legend
    const lx=W-mR+8;
    [['observed',c.navy,null],['true no-launch',c.grey,'6 4'],['model projection',c.red,'2 3']].forEach((r,i)=>{
      const attrs={x1:lx,y1:mT+8+i*15,x2:lx+20,y2:mT+8+i*15,stroke:r[1],'stroke-width':2};
      if(r[2])attrs['stroke-dasharray']=r[2];
      svg.appendChild(el('line',attrs));
      svg.appendChild(el('text',{x:lx+25,y:mT+11+i*15,'font-size':9},r[0]));
    });
    if(rd){rd.textContent='measured / true lift: '+share+'%';
      rd.style.fontWeight='800';
      rd.style.color=Math.abs(share-100)<=5?c.green:(Math.abs(share-100)<=20?c.orange:c.red);}
  }
  if(on)on.addEventListener('change',draw);
  if(tr)tr.addEventListener('input',draw);
  draw(); window.__redraw.push(draw);
})();
