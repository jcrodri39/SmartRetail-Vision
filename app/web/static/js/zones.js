const c=document.getElementById('zoneCanvas'),x=c.getContext('2d');let pts=[];
function draw(){x.clearRect(0,0,c.width,c.height);x.fillStyle='#111c29';x.fillRect(0,0,c.width,c.height);if(!pts.length)return;x.strokeStyle='#31d6a0';x.fillStyle='#31d6a0';x.lineWidth=3;x.beginPath();x.moveTo(...pts[0]);pts.slice(1).forEach(p=>x.lineTo(...p));if(pts.length>=3)x.closePath();x.stroke();pts.forEach(p=>{x.beginPath();x.arc(p[0],p[1],5,0,7);x.fill()})}
c.onclick=e=>{const r=c.getBoundingClientRect();pts.push([Math.round((e.clientX-r.left)*c.width/r.width),Math.round((e.clientY-r.top)*c.height/r.height)]);draw()}
function resetPoly(){pts=[];draw()} function savePoly(){if(pts.length<3){alert('Se requieren al menos 3 puntos');return false}coords.value=JSON.stringify(pts);return true}draw();
