scoreboard objectives add __world_init dummy
execute unless score .init __world_init matches 1 run function init:do_init