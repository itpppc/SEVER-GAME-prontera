# Custom NPC scripts

Put rAthena NPC scripts here as `*.txt`. `scripts/apply-config.sh` copies them to
`rathena/npc/custom/sever/` and loads each one through an `npc:` line in `conf/import/map_conf.txt`.
After changing a script: run `scripts/apply-config.sh`, then `@reloadscript` in game (or restart map-server).

rAthena already ships ready-made service NPCs in `rathena/npc/custom/` (warper.txt, healer.txt,
jobmaster.txt, resetnpc.txt, ...). To enable one without copying it, add a line such as
`npc: npc/custom/warper.txt` to `config/import/map_conf.txt`.
