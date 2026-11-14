// Exercise the production collection counter against completed quest records.
// This catches inventory-stack farming, locked milestones and cross-team leaks.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const callbacks={},logs=[],binding={key:'rank',quest_id:'reward',task_id:'task',kind:'bridge',target:'catalog_count',count:3,quest_ids:['a','b','c','d']};
const task={id:'task',max:1,button:true,getQuest:()=>({id:'reward'}),setEnableButton(v){this.button=v},setMaxProgress(n){this.max=n}};
function player(){
  const p={uuid:Math.random()+'',allowed:true,owned:999,completed:new Set(),progress:0};
  p.inventory={count:()=>p.owned};p.level={dimension:'minecraft:overworld'};
  p.team={canStartTasks:()=>p.allowed,isCompleted:x=>x===task?p.progress>=task.max:p.completed.has(x.id),addProgress:(x,n)=>p.progress=Math.min(x.max,p.progress+n)};
  return p;
}
let players=[];
const file={getID:x=>x,getTask:()=>task,getQuest:id=>({id})};
const classes={
 'dev.ftb.mods.ftbquests.quest.TeamData':{get:p=>p.team},
 'dev.ftb.mods.ftbquests.quest.ServerQuestFile':{INSTANCE:file},
 'net.minecraft.world.entity.monster.Monster':class {},
 'net.minecraft.server.level.ServerPlayer':class {},
 'net.minecraft.world.entity.npc.Villager':class {},
 'com.scout.symbiote.tracker.SymbioteTracker':{get:()=>({peek:()=>null})},
 'com.svs.tweak.kubejs.SvsDamageHelper':{},
 'net.darkhax.gamestages.GameStageHelper':{},
 'net.minecraftforge.registries.ForgeRegistries':{},
 'net.minecraft.resources.ResourceLocation':class {}
};
const ctx=vm.createContext({Java:{loadClass:n=>{if(!(n in classes))throw Error(n);return classes[n]}},
 global:{svsQuestV2Bindings:[binding],svsQuestV2Stages:[]},console:{info:()=>{},warn:s=>logs.push(s)},
 ServerEvents:{loaded:f=>callbacks.loaded=f,tick:f=>callbacks.tick=f},EntityEvents:{death:()=>{}}});
vm.runInContext(fs.readFileSync(path.join(__dirname,'../kubejs/server_scripts/svs_quests_bridge.js'),'utf8'),ctx);
function tick(){for(let i=0;i<40;i++)callbacks.tick({server:{getPlayers:()=>({size:()=>players.length,get:i=>players[i]})}})}
const p=player();players=[p];tick();assert.equal(p.progress,0,'999 owned copies must not count as distinct registrations');
p.completed.add('a');tick();assert.equal(p.progress,0);
p.owned=0;p.completed.add('b');tick();assert.equal(p.progress,0,'records persist after putting items away');
p.completed.add('c');p.allowed=false;tick();assert.equal(p.progress,0,'locked reward must wait for main-line gate');
p.allowed=true;tick();assert.equal(p.progress,3);assert.equal(task.button,false,'custom progress is never a checkmark button');
const other=player();players=[p,other];tick();assert.equal(other.progress,0,'another team cannot inherit collection count');
const mate=player();mate.team=p.team;players=[mate];tick();assert.equal(p.progress,3,'completed team ledger supports a teammate');
assert.deepEqual(logs,[]);console.log('PASS: distinct records, item removal, locked milestone, bounded reward, team isolation/sharing; production bridge, API doubles only');
