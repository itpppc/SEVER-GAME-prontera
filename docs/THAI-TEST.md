# Thai text in the game: experiment

Goal: see whether Thai can be shown in the game without a new client. Nothing here changes the installer.

How the game decides: the client picks a font and a character set from `<langtype>` in `data/clientinfo.xml`
(0 = Korean, 1 = English, 5 = Thai). The text itself comes from the server as bytes in Thai code page 874.
So two things are needed together: a Thai langtype on the PC, and Thai text saved as cp874 on the server.

## 1. Server (EC2): load the Thai test NPC

    cd ~/SEVER-GAME-prontera && git pull && scripts/apply-config.sh && sudo systemctl restart rathena

This adds the NPC "Thai Test" at prontera 149,189 (next to the Sage of Ayodhya). Its text is in `custom/npc/thai_test.txt`, saved as cp874.

## 2. One PC (the owner's): set the Thai langtype

In PowerShell (game folder C:\Gravity\Ragnarok):

    foreach ($n in 'clientinfo.xml','sclientinfo.xml') { $f = "C:\Gravity\Ragnarok\data\$n"; (Get-Content $f) -replace '<langtype>0</langtype>','<langtype>5</langtype>' | Set-Content $f -Encoding ASCII }

Start the game from the Prontera icon, log in, talk to "Thai Test".

## 3. Undo

    foreach ($n in 'clientinfo.xml','sclientinfo.xml') { $f = "C:\Gravity\Ragnarok\data\$n"; (Get-Content $f) -replace '<langtype>5</langtype>','<langtype>0</langtype>' | Set-Content $f -Encoding ASCII }

## What the result means

- Thai letters with tone marks look right: Thai works. Next step is translating our NPCs and items.
- Boxes or strange letters: this client cannot show Thai with a langtype change alone. Next options are Thai font files or a Thai client translation, a bigger project.
- The game fails to start or the login screen changes: undo step 3 and report what happened.

Not tested on a real PC yet. The value 5 for Thai comes from the clientinfo documentation and is not confirmed with this client.
