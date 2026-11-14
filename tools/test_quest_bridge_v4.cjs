// Execute the production bridge callbacks with controlled API doubles.
// This checks event routing and negative cases; it is not a Minecraft runtime test.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
class Monster { constructor(type='minecraft:zombie') { this.type=type; } }
class Player {
  constructor() {
    this.uuid='tester'; this.rank='UNBONDED'; this.tokens=0; this.record=''; this.villagers=0; this.stages=new Set();
    this.level={ dimension:'minecraft:overworld', getEntitiesOfClass:()=>({size:()=>this.villagers}) };
    this.inventory={count:()=>this.tokens};
    this.team={allowed:false, progress:new Map(),
      canStartTasks:()=>this.team.allowed,
      isCompleted:t=>t.stageCheck ? !!this.team.finished : (this.team.progress.get(t.id)||0)>=t.max,
      addProgress:(t,n)=>this.team.progress.set(t.id, Math.min(t.max,(this.team.progress.get(t.id)||0)+n))};
  }
  getBoundingBox() { return {inflate:()=>({})}; }
  getPersistentData() { return {getString:()=>this.record}; }
}
const tasks=new Map(), warnings=[], callbacks={};
const bindings=[
  {key:'kill',task_id:'1',kind:'bridge',target:'hostile_kills',count:5},
  {key:'village',task_id:'2',kind:'bridge',target:'village',count:1},
  {key:'bond',task_id:'3',kind:'bridge',target:'bond',stage:'ATTACHED',count:1},
  {key:'bound',task_id:'4',kind:'bridge',target:'fireseed',count:1},
  {key:'ready',task_id:'5',kind:'bridge',target:'fireseed_ready',count:1},
  {key:'pending',task_id:'6',kind:'pending',target:'hostile_kills',count:1},
  {key:'milestone',task_id:'7',kind:'bridge',target:'milestone',count:1}
];
for (const b of bindings) tasks.set(b.task_id, {id:b.task_id,max:1,button:true,
  getQuest:()=>({}), setEnableButton(v){this.button=v;},setMaxProgress(v){this.max=v;}});
let player=new Player();
const file={getID:x=>x,getTask:x=>tasks.get(x),getQuest:()=>null};
const classes={
  'dev.ftb.mods.ftbquests.quest.TeamData':{get:p=>p.team},
  'dev.ftb.mods.ftbquests.quest.ServerQuestFile':{INSTANCE:file},
  'net.minecraft.world.entity.monster.Monster':Monster,
  'net.minecraft.server.level.ServerPlayer':Player,
  'net.minecraft.world.entity.npc.Villager':class {},
  'com.scout.symbiote.tracker.SymbioteTracker':{get:()=>({peek:()=>({stage:{name:()=>player.rank}})})},
  'com.svs.tweak.kubejs.SvsDamageHelper':{attackerOf:s=>s.attacker},
  'net.darkhax.gamestages.GameStageHelper':{hasStage:(p,s)=>p.stages.has(s),addStage:(p,s)=>p.stages.add(s)},
  'net.minecraftforge.registries.ForgeRegistries':{},
  'net.minecraft.resources.ResourceLocation':class {}
};
const ctx=vm.createContext({Java:{loadClass:n=>{if(!(n in classes)) throw Error(n); return classes[n];}},
  global:{svsQuestV2Bindings:bindings,svsQuestV2Stages:[],svsQuestV2Audit:{quests:['loaded'],items:[],entities:[]}},
  console:{info:()=>{},warn:s=>warnings.push(s)},
  ServerEvents:{loaded:f=>callbacks.loaded=f,tick:f=>callbacks.tick=f}, EntityEvents:{death:f=>callbacks.death=f}});
vm.runInContext(fs.readFileSync(path.join(root,'kubejs/server_scripts/svs_quests_bridge.js'),'utf8'),ctx);
callbacks.loaded({});
assert.equal(tasks.get('1').max,1, 'empty FTB graph must not cache a completed audit');
file.getQuest=()=>({});
callbacks.loaded({});
assert.equal(tasks.get('1').max,5, 'configure server counter before player login');
function tick(players=[player]){ for(let i=0;i<40;i++) callbacks.tick({server:{getPlayers:()=>({size:()=>players.length,get:i=>players[i]})}}); }
function progress(id){return player.team.progress.get(id)||0;}
function death(entity,attacker){callbacks.death({entity,source:{attacker}});}
// Closed dependency, then wrong lethal source, non-monster, and exactly five new kills.
death(new Monster(),player); assert.equal(progress('1'),0);
tick(); assert.equal(progress('7'),0,'closed milestone dependencies must not complete');
player.team.allowed=true;
death(new Monster(),null); death({type:'minecraft:cow'},player); death(new Monster(),{});
assert.equal(progress('1'),0);
for(let i=0;i<4;i++) death(new Monster(),player);
assert.equal(progress('1'),4); death(new Monster(),player); assert.equal(progress('1'),5);
death(new Monster(),player); assert.equal(progress('1'),5);
assert.equal(progress('6'),0, 'pending never advances');
tick(); assert.equal(progress('2'),0); assert.equal(progress('3'),0); assert.equal(progress('4'),0);
assert.equal(progress('7'),1,'aggregate milestone completes only with open dependencies');
player.villagers=2; tick(); assert.equal(progress('2'),0);
player.villagers=3; player.level.dimension='minecraft:the_nether'; tick(); assert.equal(progress('2'),0);
player.level.dimension={location:()=> 'minecraft:overworld'}; tick(); assert.equal(progress('2'),1);
player.tokens=1; tick(); assert.equal(progress('5'),1); assert.equal(progress('4'),0,'holding does not equal bound');
player.tokens=0; player.record='malformed'; tick(); assert.equal(progress('4'),0);
player.record='Tester123|100'; tick(); assert.equal(progress('4'),1);
// A fresh team with a binding made before opening the task must not need a second token.
player=new Player(); player.team.allowed=true; player.record='Tester123|100'; tick();
assert.equal(progress('5'),1); assert.equal(progress('4'),1);
player.rank='DOMINANT'; tick(); assert.equal(progress('3'),1,'higher stage recognized');
for(const t of tasks.values()) assert.equal(t.button,false,'custom tasks cannot click through');
assert.equal(tasks.get('1').max,5);
// Verify this bridge always uses the fatal attacker's team, and stage sync uses
// the current team quest record for each player (including a late joiner).
const owner=new Player(), peer=new Player(), stranger=new Player();
owner.uuid='owner'; peer.uuid='peer'; stranger.uuid='stranger';
owner.team.allowed=true; peer.team.allowed=true; stranger.team.allowed=true;
death(new Monster(),owner);
assert.equal(owner.team.progress.get('1'),1);
assert.equal(peer.team.progress.get('1')||0,0,'different team must not receive kill credit');
peer.team=owner.team;
death(new Monster(),peer);
assert.equal(owner.team.progress.get('1'),2,'same team accumulates both players kills');
assert.equal(stranger.team.progress.get('1')||0,0);
ctx.global.svsQuestV2Stages=[{quest_id:'graduation',stage:'svs_stage1_prologue'}];
file.getQuest=id=>({stageCheck:id==='graduation'});
tick([owner,peer,stranger]);
assert.equal(owner.stages.size,0,'unfinished team must not get stage');
owner.team.finished=true;
tick([owner,stranger]);
assert(owner.stages.has('svs_stage1_prologue'));
assert.equal(peer.stages.size,0,'offline/absent member is not silently mutated');
tick([owner,peer,stranger]);
assert(peer.stages.has('svs_stage1_prologue'),'late joiner catches up from team completion');
assert.equal(stranger.stages.size,0,'different team must not inherit stage');
assert.deepEqual(warnings,[]);
console.log('PASS: production callbacks, dependency gates, lethal-source exclusions, counter bounds, village dimensions, holding/binding, early binding, fusion rank, pending lock, team isolation/sharing and late-join stage sync; API doubles only');
