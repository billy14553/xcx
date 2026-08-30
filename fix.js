const fs = require('fs');
const h = fs.readFileSync('e:/ball/xcx games/level-devil-kids/index.html', 'utf8');
const p = fs.readFileSync('e:/ball/xcx games/level-devil-kids/make_game.py', 'utf8');
const old = '    if (player.onMoving !== null) {\n      const mp = movingPlatforms[player.onMoving];\n      const dx = mp.currentX - mpOldX[player.onMoving];\n      const dy = mp.currentY - mpOldY[player.onMoving];\n      player.x += dx;\n      player.y += dy;\n      if (dy !== 0 && collides(player, mp)) {\n        player.y = mp.currentY - player.h;\n        player.vy = 0;\n        player.onGround = true;\n      }\n      if (player.onMoving !== null && !collides(player, movingPlatforms[player.onMoving])) {\n        player.onMoving = null;\n        player.onGround = false;\n      }\n    }';
const nw = '    if (player.onMoving !== null) {\n      const mp = movingPlatforms[player.onMoving];\n      const dx = mp.currentX - mpOldX[player.onMoving];\n      const dy = mp.currentY - mpOldY[player.onMoving];\n      player.x += dx;\n      player.y += dy;\n      // Snap player to platform surface while riding it\n      if (player.y + player.h <= mp.currentY + 1) {\n        player.y = mp.currentY - player.h;\n        player.vy = 0;\n        player.onGround = true;\n      } else {\n        player.onMoving = null;\n        player.onGround = false;\n      }\n    }';
[h, p].forEach((c, i) => {
  const f = i === 0 ? 'index.html' : 'make_game.py';
  if (c.includes(old)) {
    fs.writeFileSync('e:/ball/xcx games/level-devil-kids/' + f, c.replace(old, nw));
    console.log('Fixed', f);
  } else {
    console.log('NOT found in', f);
    const j = c.indexOf('if (player.onMoving !== null)');
    console.log('Actual:', JSON.stringify(c.substring(j, j + 400)));
  }
});
