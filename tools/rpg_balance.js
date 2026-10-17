// Balance check for website/rpg: node tools/rpg_balance.js [auto|mash]
require(require("path").join(__dirname, "../website/rpg/engine.js"));
const { Battle, STAGE_1 } = globalThis.LankaRPG;
let wins=0, stars=[0,0,0,0], rounds=0, N=2000, mode=process.argv[2]||'auto';
for (let i=0;i<N;i++){
  const b=new Battle(STAGE_1,{seed:i+1}); b.nextWave();
  let guard=0;
  while(!b.over && guard++<500){
    if (b.waveCleared()) { b.nextWave(); continue; }
    const u=b.nextActor(); const bt=b.beginTurn(u); if(bt.skip) continue;
    if(u.side==='enemy') b.enemyAct(u);
    else { let c;
      if(mode==='mash'){ c={skill:u.skills[0].id,target:b.alive(b.enemies)[0].uid}; }
      else c=b.autoChoice(u);
      b.useSkill(u,c.skill,c.target); }
    if(!b.over && b.waveCleared() && b.hasMoreWaves()) b.nextWave();
  }
  if(b.over==='win'){wins++;rounds+=b.round;} stars[b.stars()]++;
}
console.log(mode,'win%',(wins/N*100).toFixed(1),'avgRounds',(rounds/Math.max(wins,1)).toFixed(1),'stars0-3',stars);
