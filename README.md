# Mars · Terrain Simulator

A 3D Mars exploration game for the **NASA International Space Apps Challenge** by Team Isabelinos Espaciales.

**Play:** open https://gustavoduqueo.github.io/isabelinosespaciales/ in Chrome. Nothing to install.

## Features
- Four real landing sites (Valles Marineris, Gale Crater, North Pole (Ice) and Olympus Mons), generated with the same algorithm and parameters as `a-marte.py`.
- A drivable rover with physics (gravity, jumping), tilt that follows the terrain, and solar power.
- Weather: clear, dust storm, sunset (blue, as on Mars) and night with Phobos and Deimos overhead.
- A network of underground tunnels 12 m below the surface, reached through an access shaft.
- Five science targets per site, each with a real fact from NASA missions.
- **Perseverance route mission:** retrace the path of the NASA Perseverance rover (Mars 2020) in Jezero Crater, drawn to scale (≈ 1:112) on every terrain. Visit the 5 waypoints in order. Each one shows its real coordinates and mission context:
  1. Landing zone · Octavia E. Butler Landing (18.4447° N, 77.4508° E), where the rover landed on February 18, 2021
  2. Delta Front · Three Forks (18.453° N, 77.408° E)
  3. Ancient riverbed · Fan Front (18.46° N, 77.38° E, approx.)
  4. Bright Angel formation (18.49° N, 77.34° E, approx.), where the rover found the Cheyava Falls rock in 2024
  5. Neretva Vallis (18.55° N, 77.20° E)

  The center of Jezero Crater (18.38° N, 77.58° E) is shown as a reference marker. Choose the mission on the start screen, in the pause menu, in the mission panel or with `M`. Links can open it directly with `?mission=route`.
- Bilingual: **Español** and **English**. Pick a language on the start screen, in the pause menu or with the `L` key. The choice is remembered, and links can force a language with `?lang=es` or `?lang=en`.

## Controls
| Key | Action |
|---|---|
| WASD / arrow keys | Drive the rover |
| SPACE | Jump |
| Mouse drag | Orbit the camera · Wheel: zoom |
| 1-4 / F1-F4 | Change terrain |
| C | Cycle weather |
| T | Underground tunnels · E: enter/exit at the shaft |
| R | Reset terrain |
| ESC | Pause |
| L | Switch language (Español / English) |
| M | Switch mission (science samples / Perseverance route) |

## Files
- `index.html`: the web game (Three.js, no install needed).
- `a-marte.py`: the original desktop prototype (Python + Ursina).
