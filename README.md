The GoFamiliar is an attempt to create the fundamental analysis tools for an expert system for go playing, that is a system to help players choose moves and potentially learn. The contention is that a computer-aided but Go knowledgeable human can out-perform the computer Go player alone, and possibly high ranking players.

The eventual aim is to include these analysis tools in a set of display and interaction tools for one or more players and computers to play a hydra style game. See Advanced or Freestyle Chess.

There are two principal inputs: a library of professional games and a Monte Carlo go simulator.

# Use of the professional game library:
The planned use of the pro game library is as an aid to opening play in a Go game being played. This is accomplished by searching the library for games with the same or similar moves so far, and giving an indication of the places where pros played next via a heatmap or similar board overlay.

_(Note Aug 4, 2015 - Given the relative simplicity of using the pro games, it is the first idea I aim to implement)_

# Use of the Monte Carlo simulator:
The planned use of the Monte Carlo simulator is to "siphon off" the random games used in its calculation, save them, and use them in various ways. As these are random games, the intermediate game states may not be very useful, but the final game states should offer the same usefulness as they do for the MC computer players.

A collection of relevant positions (_i.e._ matching the current state of the game) could be used to create percentage chance of groups dying, or point acquisition (same thing in chinese counting). An application could be that areas with close to 50%/50% B and W are "hot areas to play". As games get completed in simulation, percentages could actively update. As the game advances, non-relevant simulation games get filtered, also actively updating the percentages.

The real interactive power comes from the human player(s) being able to seed the MC simulator with likely moves and being able to test the change or percentage chances around the board with various 'test' moves'.

More ambitious to my mind is trying to use the MC simulator to find tesujis, or use it as an end game move comparator.
