#! /usr/bin/env python3

import os
from compare import main

output = []

for filename1 in os.listdir('pgnsplit/set1'):
    for filename2 in os.listdir('pgnsplit/set2'):
        output.append((filename1, filename2, main(f'pgnsplit/set1/{filename1}', f'pgnsplit/set2/{filename2}', 10, 100)))
print(output)

#pgn1, pgn2, depth, desired games
#main(library[0], library[1], 10, 100)

#[('pachamama.pgn', 'andrewrun.pgn', 5.524305895004758), ('pachamama.pgn', 'erindreki.pgn', 0.183917639881066), ('pachamama.pgn', 'Kobylka.pgn', 0.0), ('schnappi.pgn', 'andrewrun.pgn', 0.695844198824029), ('schnappi.pgn', 'erindreki.pgn', 1.5224649479305619), ('schnappi.pgn', 'Kobylka.pgn', 0.44984428137772947), ('nefantii.pgn', 'andrewrun.pgn', 0.7626273737385536), ('nefantii.pgn', 'erindreki.pgn', 0.15343216631864126), ('nefantii.pgn', 'Kobylka.pgn', 0.39137070508011784)]
