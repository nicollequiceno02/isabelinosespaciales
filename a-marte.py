# ============================================================
# REALISTIC MARS TERRAIN SIMULATION
# Engine: Ursina | Author: Interactive space simulation
# Controls: WASD move rover | Mouse orbit | F1-F4 terrains
#           C weather | T tunnels | R reset | ESC quit
# ============================================================

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

# ============================================================
# INITIALIZATION
# ============================================================
app = Ursina(title="Mars - 3D Terrain Simulator", borderless=False, fullscreen=False)
window.color = color.black
window.size = (1400, 800)

random.seed(42)

# ============================================================
# MAIN PROCEDURAL TERRAIN CLASS
# ============================================================
class TerrainGenerator:
    """Generates Martian terrain meshes with different parameters."""

    def __init__(self, name, size=80, height_scale=6, roughness=0.6,
                 color_base=color.rgb(150, 70, 40), crater_density=5,
                 has_ice=False, has_canyon=False, has_dunes=False):
        self.name = name
        self.size = size
        self.height_scale = height_scale
        self.roughness = roughness
        self.color_base = color_base
        self.crater_density = crater_density
        self.has_ice = has_ice
        self.has_canyon = has_canyon
        self.has_dunes = has_dunes
        self.heights = []
        self.entities = []

    def noise2d(self, x, y):
        """Simulates fractal noise for the terrain."""
        n = 0.0
        amp = 1.0
        freq = 0.06
        for _ in range(4):
            n += amp * math.sin(x * freq + math.cos(y * freq * 1.3))
            n += amp * math.cos(y * freq + math.sin(x * freq * 1.1))
            amp *= self.roughness
            freq *= 2.1
        return n

    def crater(self, cx, cy, radius, depth):
        """Applies a crater to the height map."""
        for ix in range(max(0, cx - radius), min(self.size, cx + radius)):
            for iy in range(max(0, cy - radius), min(self.size, cy + radius)):
                d = math.hypot(ix - cx, iy - cy)
                if d < radius:
                    factor = 1 - (d / radius) ** 2
                    self.heights[ix][iy] -= depth * factor

    def canyon(self):
        """Carves a central canyon."""
        mid = self.size // 2
        for ix in range(self.size):
            depth = 8 + 6 * math.sin(ix * 0.15)
            for iy in range(mid - 4, mid + 4):
                if 0 <= iy < self.size:
                    self.heights[ix][iy] -= depth

    def dunes(self):
        """Creates rolling dunes."""
        for ix in range(self.size):
            for iy in range(self.size):
                self.heights[ix][iy] += 3 * math.sin(ix * 0.25) * math.cos(iy * 0.2)

    def generate_mesh(self):
        """Builds the terrain as Ursina entities."""
        print(f"[+] Generating terrain: {self.name}")
        # Height map
        self.heights = [[0.0 for _ in range(self.size)] for _ in range(self.size)]
        for x in range(self.size):
            for y in range(self.size):
                h = self.noise2d(x, y) * self.height_scale
                self.heights[x][y] = h

        for _ in range(self.crater_density):
            cx = random.randint(6, self.size - 6)
            cy = random.randint(6, self.size - 6)
            r = random.randint(3, 7)
            self.crater(cx, cy, r, random.uniform(3, 6))

        if self.has_canyon:
            self.canyon()
        if self.has_dunes:
            self.dunes()

        # Create cubes (grid) -> voxel approximation
        step = 2
        for x in range(0, self.size - step, step):
            for y in range(0, self.size - step, step):
                h = self.heights[x][y]
                # Color variation by height and randomness
                t = (h + self.height_scale) / (2 * self.height_scale)
                t = max(0, min(1, t))
                r = int(self.color_base[0] * (0.6 + 0.5 * t) + random.randint(-8, 8))
                g = int(self.color_base[1] * (0.6 + 0.5 * t) + random.randint(-6, 6))
                b = int(self.color_base[2] * (0.6 + 0.5 * t) + random.randint(-6, 6))
                r = max(0, min(255, r)); g = max(0, min(255, g)); b = max(0, min(255, b))

                # Snow/frozen CO2 on high peaks
                if self.has_ice and h > self.height_scale * 0.55:
                    r, g, b = 220, 235, 250

                e = Entity(
                    model='cube',
                    color=color.rgb(r, g, b),
                    position=(x - self.size / 2, h, y - self.size / 2),
                    scale=(step, 1, step),
                    collider='box' if random.random() > 0.85 else None,
                    texture='white_cube'
                )
                self.entities.append(e)

    def destroy(self):
        for e in self.entities:
            destroy(e)
        self.entities.clear()


# ============================================================
# UNDERGROUND TUNNEL CLASS
# ============================================================
class UndergroundTunnel:
    """Explorable tunnel system beneath the terrain."""

    def __init__(self):
        self.entities = []

    def build(self, depth=-12):
        print("[+] Building underground tunnels...")
        # Main H-shaped tunnel
        segments = [
            (-30, depth, 0, 40, 2, 4),
            (0, depth, 0, 2, 2, 40),
            (30, depth, 0, 40, 2, 4),
            (0, depth, -18, 2, 2, 40),
        ]
        for seg in segments:
            x, y, z, sx, sy, sz = seg
            # Floor
            self.entities.append(Entity(
                model='cube', color=color.rgb(90, 45, 25),
                position=(x, y - 1.5, z), scale=(sx, 1, sz)
            ))
            # Ceiling
            self.entities.append(Entity(
                model='cube', color=color.rgb(70, 35, 20),
                position=(x, y + 1.5, z), scale=(sx, 1, sz)
            ))
            # Walls
            self.entities.append(Entity(
                model='cube', color=color.rgb(110, 55, 30),
                position=(x, y, z - sz / 2), scale=(sx, 2, 0.5)
            ))
            self.entities.append(Entity(
                model='cube', color=color.rgb(110, 55, 30),
                position=(x, y, z + sz / 2), scale=(sx, 2, 0.5)
            ))

        # Emergency lights
        for i in range(-30, 35, 15):
            self.entities.append(Entity(
                model='sphere', color=color.rgb(255, 180, 80),
                position=(i, depth + 1, 0), scale=0.6,
                emissive=color.rgb(255, 150, 50)
            ))
        # Entry point (ramp)
        self.entities.append(Entity(
            model='cube', color=color.rgb(60, 30, 15),
            position=(0, depth / 2 - 2, 22), scale=(6, 10, 6)
        ))

    def destroy(self):
        for e in self.entities:
            destroy(e)
        self.entities.clear()


# ============================================================
# EXPLORER ROVER CLASS
# ============================================================
class Rover(Entity):
    """WASD-controlled rover with a third-person camera."""

    def __init__(self):
        super().__init__(
            model='cube',
            color=color.rgb(220, 220, 230),
            scale=(1.2, 0.6, 1.6),
            position=(0, 2, -10)
        )
        self.speed = 8
        self.jump_power = 5
        self.velocity_y = 0
        self.gravity = -20
        self.is_grounded = False

        # Visual details
        self.body = Entity(parent=self, model='cube', scale=(0.9, 0.4, 1.2),
                           color=color.rgb(180, 180, 200), position=(0, 0.4, 0))
        # Solar panels
        self.panel = Entity(parent=self, model='cube', scale=(1.4, 0.05, 1.0),
                            color=color.rgb(40, 60, 150), position=(0, 0.7, 0))
        # Camera/antenna
        self.antenna = Entity(parent=self, model='cylinder', scale=(0.05, 0.8, 0.05),
                              color=color.gray, position=(0.3, 1.0, 0.4))
        self.light_cam = Entity(parent=self, model='sphere', scale=0.15,
                                color=color.yellow, position=(0.3, 1.4, 0.4),
                                emissive=color.yellow)
        # Wheels
        for (dx, dz) in [(-0.6, 0.6), (0.6, 0.6), (-0.6, -0.6), (0.6, -0.6)]:
            Entity(parent=self, model='cube',
                   color=color.rgb(40, 40, 40),
                   position=(dx, -0.3, dz), scale=(0.3, 0.4, 0.4))

        # Headlight
        self.headlight = PointLight(parent=self, color=color.rgb(255, 240, 200),
                                    position=(0, 0.8, 1.0))

    def update(self):
        # Movement
        move = Vec3(
            (held_keys['d'] - held_keys['a']),
            0,
            (held_keys['w'] - held_keys['s'])
        )
        # Orient relative to the camera
        if camera:
            yaw = camera.rotation_y
            forward = Vec3(math.sin(math.radians(yaw)), 0, math.cos(math.radians(yaw)))
            right = Vec3(math.cos(math.radians(yaw)), 0, -math.sin(math.radians(yaw)))
            direction = forward * (held_keys['w'] - held_keys['s']) + right * (held_keys['d'] - held_keys['a'])
            if direction.length() > 0:
                direction = direction.normalized()
                self.position += direction * self.speed * time.dt
                self.rotation_y = math.degrees(math.atan2(direction.x, direction.z))

        # Jump and gravity
        if held_keys['space'] and self.is_grounded:
            self.velocity_y = self.jump_power
            self.is_grounded = False
        self.velocity_y += self.gravity * time.dt
        self.y += self.velocity_y * time.dt

        # Simple raycast to the ground
        hit = raycast(self.world_position + Vec3(0, 0.5, 0), Vec3(0, -1, 0),
                      distance=3, ignore=[self])
        if hit.hit and self.y - hit.world_point.y < 1.2:
            self.y = hit.world_point.y + 1.0
            self.velocity_y = 0
            self.is_grounded = True


# ============================================================
# WEATHER MANAGER
# ============================================================
class WeatherManager:
    """Controls lighting, fog and sky."""

    PRESETS = {
        'clear': {
            'sky': color.rgb(210, 170, 140),
            'light': color.rgb(255, 220, 190),
            'fog': color.rgb(220, 180, 150),
            'fog_density': 0.008,
            'ambient': 0.7
        },
        'storm': {
            'sky': color.rgb(140, 90, 60),
            'light': color.rgb(180, 120, 80),
            'fog': color.rgb(160, 100, 60),
            'fog_density': 0.045,
            'ambient': 0.35
        },
        'sunset': {
            'sky': color.rgb(200, 110, 70),
            'light': color.rgb(255, 140, 90),
            'fog': color.rgb(210, 120, 90),
            'fog_density': 0.020,
            'ambient': 0.5
        },
        'night': {
            'sky': color.rgb(20, 20, 45),
            'light': color.rgb(90, 110, 160),
            'fog': color.rgb(15, 15, 35),
            'fog_density': 0.030,
            'ambient': 0.15
        },
    }

    def __init__(self, sun):
        self.sun = sun
        self.current = 'clear'
        self.apply('clear')

    def apply(self, preset_name):
        p = self.PRESETS[preset_name]
        window.color = p['sky']
        self.sun.color = p['light']
        scene.fog_color = p['fog']
        scene.fog_density = p['fog_density']
        ambient_light.color = color.rgba(*p['light'][:3], int(255 * p['ambient']))
        self.current = preset_name
        print(f"[☁] Weather: {preset_name}")

    def next(self):
        keys = list(self.PRESETS.keys())
        idx = keys.index(self.current)
        self.apply(keys[(idx + 1) % len(keys)])


# ============================================================
# CUSTOM ORBIT CAMERA
# ============================================================
class OrbitCamera(Entity):
    """Camera that orbits around the rover."""

    def __init__(self, target):
        super().__init__()
        self.target = target
        self.distance = 18
        self.yaw = 0
        self.pitch = 25
        self.smooth = 6

    def update(self):
        # Mouse to orbit
        if mouse.right:
            self.yaw += mouse.velocity[0] * 400
            self.pitch -= mouse.velocity[1] * 300
        self.pitch = max(-20, min(80, self.pitch))

        # Zoom
        self.distance -= mouse.velocity[1] * 300 * time.dt
        self.distance -= mouse.velocity[0] * 300 * time.dt
        self.distance = max(6, min(50, self.distance))

        # Orbit position
        rad_y = math.radians(self.yaw)
        rad_p = math.radians(self.pitch)
        offset = Vec3(
            math.sin(rad_y) * math.cos(rad_p),
            math.sin(rad_p),
            math.cos(rad_y) * math.cos(rad_p)
        ) * self.distance

        target_pos = self.target.world_position + Vec3(0, 2, 0)
        desired = target_pos + offset

        camera.world_position = lerp(camera.world_position, desired, time.dt * self.smooth)
        camera.look_at(target_pos)


# ============================================================
# TERRAIN DEFINITIONS
# ============================================================
TERRAIN_PRESETS = {
    '1': ('Valles Marineris', dict(
        size=80, height_scale=7, roughness=0.55,
        color_base=color.rgb(160, 80, 50), crater_density=8,
        has_canyon=True
    )),
    '2': ('Gale Crater', dict(
        size=80, height_scale=5, roughness=0.7,
        color_base=color.rgb(140, 65, 40), crater_density=15,
        has_dunes=False
    )),
    '3': ('North Pole (Ice)', dict(
        size=80, height_scale=4, roughness=0.4,
        color_base=color.rgb(180, 170, 160), crater_density=6,
        has_ice=True, has_dunes=True
    )),
    '4': ('Olympus Mons', dict(
        size=80, height_scale=14, roughness=0.65,
        color_base=color.rgb(120, 60, 35), crater_density=10,
        has_ice=True
    )),
}

# ============================================================
# GLOBAL STATE
# ============================================================
state = {
    'current_terrain': None,
    'current_key': '1',
    'tunnels': None,
    'show_tunnels': False,
}

# ============================================================
# WORLD CONSTRUCTION
# ============================================================
# Directional sun
sun = DirectionalLight(
    color=color.rgb(255, 220, 190),
    rotation=(55, -30, 0),
    shadows=True
)
sun.look_at(Vec3(0, -1, 0))
ambient_light = AmbientLight(color=color.rgba(180, 160, 140, 180))

weather = WeatherManager(sun)

# Rover
rover = Rover()

# Orbit camera (replaces the default)
camera.parent = None
camera.position = (0, 20, -25)
camera.rotation = (25, 0, 0)
orbit = OrbitCamera(rover)


# ============================================================
# CONTROL FUNCTIONS
# ============================================================
def load_terrain(key):
    """Loads the terrain for the given key."""
    # Clear the previous one
    if state['current_terrain']:
        state['current_terrain'].destroy()
    if state['tunnels']:
        state['tunnels'].destroy()
        state['tunnels'] = None

    name, params = TERRAIN_PRESETS[key]
    terrain = TerrainGenerator(name, **params)
    terrain.generate_mesh()
    state['current_terrain'] = terrain
    state['current_key'] = key
    state['show_tunnels'] = False

    # Reposition rover
    rover.position = (0, 4, -12)
    rover.velocity_y = 0

    ui_terrain_label.text = f"📍 Terrain: {name}"
    print(f"[✓] Terrain loaded: {name}")


def toggle_tunnels():
    """Toggles the underground tunnels on/off."""
    if not state['show_tunnels']:
        if not state['tunnels']:
            state['tunnels'] = UndergroundTunnel()
            state['tunnels'].build(depth=-12)
        else:
            for e in state['tunnels'].entities:
                e.enabled = True
        state['show_tunnels'] = True
        ui_info_label.text = "🕳 Tunnels ENABLED - Drive the rover down (depth -12)"
    else:
        for e in state['tunnels'].entities:
            e.enabled = False
        state['show_tunnels'] = False
        ui_info_label.text = "🕳 Tunnels disabled"


def reset_world():
    load_terrain(state['current_key'])
    print("[↺] World reset")


# ============================================================
# USER INTERFACE (UI)
# ============================================================
ui_panel = Entity(
    parent=camera.ui,
    model='quad',
    color=color.rgba(0, 0, 0, 120),
    scale=(0.55, 0.28),
    position=(-0.70, 0.80),
    z=1
)

ui_title = Text(
    parent=camera.ui,
    text="MARS · TERRAIN SIMULATOR",
    position=(-0.98, 0.92),
    scale=1.2,
    color=color.rgb(255, 200, 150),
    origin=(-0.5, 0.5)
)

ui_terrain_label = Text(
    parent=camera.ui,
    text="📍 Terrain: -",
    position=(-0.98, 0.87),
    scale=1.0,
    color=color.rgb(255, 255, 255),
    origin=(-0.5, 0.5)
)

ui_info_label = Text(
    parent=camera.ui,
    text="",
    position=(-0.98, 0.83),
    scale=0.85,
    color=color.rgb(200, 255, 200),
    origin=(-0.5, 0.5)
)

ui_controls = Text(
    parent=camera.ui,
    text=(
        "WASD: move rover  |  SPACE: jump  |  Right mouse: orbit\n"
        "1-4: terrains  |  T: tunnels  |  C: weather  |  R: reset  |  ESC: quit"
    ),
    position=(-0.98, 0.76),
    scale=0.75,
    color=color.rgb(220, 220, 255),
    origin=(-0.5, 0.5)
)

# Weather buttons
weather_buttons = []
weather_keys = list(WeatherManager.PRESETS.keys())
for i, wk in enumerate(weather_keys):
    btn = Button(
        parent=camera.ui,
        text=wk.capitalize(),
        scale=(0.09, 0.035),
        position=(0.75 - i * 0.10, 0.92),
        color=color.rgba(80, 60, 40, 200),
        highlight_color=color.rgba(140, 100, 70, 220),
        on_click=Func(weather.apply, wk)
    )
    weather_buttons.append(btn)

# Terrain buttons
terrain_buttons = []
for i, tk in enumerate(TERRAIN_PRESETS.keys()):
    name = TERRAIN_PRESETS[tk][0]
    btn = Button(
        parent=camera.ui,
        text=f"F{tk}: {name}",
        scale=(0.18, 0.035),
        position=(0.75 - i * 0.20, 0.87),
        color=color.rgba(100, 50, 30, 200),
        highlight_color=color.rgba(160, 80, 50, 220),
        on_click=Func(load_terrain, tk)
    )
    terrain_buttons.append(btn)

# Tunnels button
tunnel_btn = Button(
    parent=camera.ui,
    text="🕳 Tunnels [T]",
    scale=(0.14, 0.04),
    position=(0.80, 0.80),
    color=color.rgba(60, 40, 20, 220),
    highlight_color=color.rgba(120, 80, 40, 240),
    on_click=toggle_tunnels
)

# Reset button
reset_btn = Button(
    parent=camera.ui,
    text="↺ Reset [R]",
    scale=(0.10, 0.04),
    position=(0.80, 0.75),
    color=color.rgba(60, 20, 20, 220),
    highlight_color=color.rgba(120, 40, 40, 240),
    on_click=reset_world
)


# ============================================================
# INPUT
# ============================================================
def input(key):
    if key == 'escape':
        application.quit()
    elif key in ('1', '2', '3', '4'):
        load_terrain(key)
    elif key == 't':
        toggle_tunnels()
    elif key == 'c':
        weather.next()
    elif key == 'r':
        reset_world()
    elif key == 'f1':
        load_terrain('1')
    elif key == 'f2':
        load_terrain('2')
    elif key == 'f3':
        load_terrain('3')
    elif key == 'f4':
        load_terrain('4')


# ============================================================
# START
# ============================================================
load_terrain('1')
print("\n" + "=" * 60)
print("  MARS TERRAIN SIMULATOR - STARTED")
print("=" * 60)
print("  Controls:")
print("    WASD     -> Move rover")
print("    SPACE    -> Jump")
print("    RMouse   -> Orbit camera")
print("    1-4/F1-4 -> Change terrain")
print("    T        -> Underground tunnels")
print("    C        -> Cycle weather")
print("    R        -> Reset")
print("    ESC      -> Quit")
print("=" * 60 + "\n")

app.run()