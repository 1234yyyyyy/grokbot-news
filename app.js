(function(){var bs=document.querySelectorAll('#f button[data-k]'),ps=document.querySelectorAll('#f button[data-p]'),cs=document.querySelectorAll('.c'),cnt=document.getElementById('cnt'),q=document.getElementById('q'),em=document.getElementById('em'),cat='',typ='';
function run(){var ts=q.value.trim().toLowerCase().split(/\s+/).filter(Boolean),n=0;
cs.forEach(function(c){var k=c.querySelector('.k').textContent,t=(c.querySelector('.t').textContent+' '+c.href).toLowerCase();var ok=(!cat||k.indexOf(cat+' ')>=0)&&(!typ||k.indexOf(typ+' ')>=0)&&ts.every(function(w){return t.indexOf(w)>=0});c.classList.toggle('h',!ok);if(ok)n++});
cnt.textContent=n+' 則';em.style.display=n?'none':'block';}
bs.forEach(function(b){b.addEventListener('click',function(){bs.forEach(function(x){x.classList.remove('on')});b.classList.add('on');cat=b.dataset.k;run();});});
ps.forEach(function(b){b.addEventListener('click',function(){ps.forEach(function(x){x.classList.remove('on')});b.classList.add('on');typ=b.dataset.p;run();});});
q.addEventListener('input',run);document.getElementById('qc').addEventListener('click',function(){q.value='';run();q.focus();});})();