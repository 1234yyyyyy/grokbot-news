(function(){var bs=document.querySelectorAll('#f button[data-k]'),ps=document.querySelectorAll('#f button[data-p]'),cs=document.querySelectorAll('.c'),cnt=document.getElementById('cnt'),q=document.getElementById('q'),em=document.getElementById('em'),cat='',typ='';
function run(){var ts=q.value.trim().toLowerCase().split(/\s+/).filter(Boolean),n=0;
cs.forEach(function(c){var k=c.querySelector('.k').textContent,t=(c.querySelector('.t').textContent+' '+c.href).toLowerCase();var ok=(!cat||k.indexOf(cat+' ')>=0)&&(!typ||k.indexOf(typ+' ')>=0)&&ts.every(function(w){return t.indexOf(w)>=0});c.classList.toggle('h',!ok);if(ok)n++});
cnt.textContent=n+' 則';em.style.display=n?'none':'block';}
bs.forEach(function(b){b.addEventListener('click',function(){bs.forEach(function(x){x.classList.remove('on')});b.classList.add('on');cat=b.dataset.k;run();});});
ps.forEach(function(b){b.addEventListener('click',function(){ps.forEach(function(x){x.classList.remove('on')});b.classList.add('on');typ=b.dataset.p;run();});});
q.addEventListener('input',run);document.getElementById('qc').addEventListener('click',function(){q.value='';run();q.focus();});})();(function(){var K='gb_notimp',st={};try{st=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
var btn=document.getElementById('nib');
function save(){localStorage.setItem(K,JSON.stringify(st));var n=Object.keys(st).length;btn.textContent='送出不重要清單（'+n+'）';btn.style.display=n?'block':'none';}
document.querySelectorAll('.c').forEach(function(c){var cb=c.querySelector('.nic'),l=c.querySelector('.ni'),h=c.href;
 if(st[h]){cb.checked=true;c.classList.add('ni-on')}
 l.addEventListener('click',function(ev){ev.preventDefault();ev.stopPropagation();cb.checked=!cb.checked;
  if(cb.checked){st[h]={t:c.querySelector('.n').textContent.replace(/^\d+\.\s*/,'').replace(/可參考$/,'').replace(/^不重要/,''),k:c.dataset.cat||''}}else delete st[h];
  c.classList.toggle('ni-on',cb.checked);save();});});
btn.addEventListener('click',function(){var d=new Date(Date.now()+8*36e5).toISOString().slice(0,10),ks=Object.keys(st),lines=[],cut=0;
 for(var i=0;i<ks.length;i++){var ln='- ['+st[ks[i]].k+'] '+st[ks[i]].t+' | '+ks[i];if(encodeURIComponent(lines.join('\n')+ln).length>6000){cut=ks.length-i;break}lines.push(ln)}
 var body='以下項目不重要，之後雷同內容請排除：\n\n'+lines.join('\n')+(cut?'\n\n（另有 '+cut+' 則因網址長度限制未列入，請送出後再按一次）':'');
 window.open('https://github.com/1234yyyyyy/grokbot-news/issues/new?labels=not-important&title='+encodeURIComponent('不重要回饋 '+d)+'&body='+encodeURIComponent(body),'_blank');
 if(confirm('送出後要清除這些勾選嗎？（已列入的才會清除）')){for(var j=0;j<lines.length;j++)delete st[ks[j]];document.querySelectorAll('.c').forEach(function(c){if(!st[c.href]){c.classList.remove('ni-on');c.querySelector('.nic').checked=false}});save();}});
save();})();
