 const fs = require('fs');
 const path = require('path');
 const dir = 'e:\\ball\\xcx games\\level-devil-kids';
 
 // Read the Python script and extract the HTML content
 const py = fs.readFileSync(path.join(dir, 'make_game.py'), 'utf8');
 const start = py.indexOf("html = r'''");
 const end = py.indexOf("'''", start + 15);
 let content = py.substring(start + 11, end);
 
 // Fix the moving platform follower bug:
 // The current code applies BOTH dx and dy from the platform delta to the player.
 // But the vertical collision response already positions the player correctly
 // relative to the platform's CURRENT position. Adding dy pushes the player off.
 // Fix: only apply dx (horizontal follower), not dy.
 content = content.replace(
   /player\.x \+= dx;\s*\n\s*player\.y \+= dy;/,
   'player.x += dx;'
 );
 
 fs.writeFileSync(path.join(dir, 'index.html'), content, 'utf8');
 console.log('Written', content.length, 'bytes');
 console.log('Fix applied: removed dy from moving platform follower');
