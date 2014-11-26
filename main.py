import pygame, spritesheet, os.path, math, random
from pygame.locals import *

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0.5
started = True

# Image class that helps working with images
# TODO: Check if it's needed!
class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
        self.center = center
        self.size = size
        self.radius = radius
        self.lifespan = lifespan if lifespan else float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

# helper function for loading images
# define the current path
main_dir = os.path.split(os.path.abspath(__file__))[0]
def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'art', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert_alpha()
	
def load_sound(file):
    file = os.path.join(main_dir, 'audio', file)
    sound = pygame.mixer.Sound(file)
    return sound

# helper functions for transformation, leave for now, we'll see if they're needed
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)
	
def rot_center(image, angle):
	"""rotate an image while keeping its center and size"""
	orig_rect = image.get_rect()
	rot_image = pygame.transform.rotate(image, angle)
	rot_rect = orig_rect.copy()
	rot_rect.center = rot_image.get_rect().center
	rot_image = rot_image.subsurface(rot_rect).copy()
	return rot_image

# Ship class

class Ship:
	def __init__(self, pos, vel, angle, image, info):
		self.pos = [pos[0],pos[1]]
		self.vel = [vel[0],vel[1]]
		self.thrust = False
		self.angle = angle
		self.angle_vel = 0
		self.images = image
		self.image = self.images[0]
		self.image_width = self.image.get_width()
		self.image_height = self.image.get_height()
		self.original = self.image
		self.image_center = info.get_center()
		self.image_size = info.get_size()
		self.radius = info.get_radius()
		self.rect = self.image.get_rect()
        
	def get_position(self):
		return self.pos
    
	def get_radius(self):
		return self.radius
    
	def turn(self, direction):
		self.angle_vel = direction
        
	def move(self, thrust):
		self.thrust = thrust
		if self.thrust:
			ship_thrust_sound.play(-1)
		else:
			ship_thrust_sound.stop()
			
	def shoot(self):
		global missile_group       
		base_missle_speed = 6
		forward = angle_to_vector(math.radians(self.angle))
		vel = [0, 0]
		vel[0] = self.vel[0] + forward[0] * base_missle_speed
		vel[1] = self.vel[1] + -forward[1] * base_missle_speed

		pos = [0, 0]
		# TODO: think about why the radius has to be increased by this magic number
		pos[0] = self.pos[0] + (self.radius + 5 + self.image_width / 2 * forward[0])
		pos[1] = self.pos[1] + (self.radius + 5 + self.image_height / 2 * -forward[1])

		a_missile = Sprite(pos, vel, 0, 0, missile_image, missile_info, missile_sound)
		missile_group.add(a_missile)
        
	def draw(self,screen):
		if self.thrust:
			self.original = self.images[1]
		else:
			self.original = self.images[0]
		
		screen.blit(self.image, self.pos)

	def update(self):
		self.pos[0] += self.vel[0]
		self.pos[1] += self.vel[1]
		
		# Friction update
		c = 0.015
		self.vel[0] *= (1 - c)
		self.vel[1] *= (1 - c)
        
        # Screen wrapping
		if self.pos[1] + self.image_height <= self.radius: #or self.pos[1] >= HEIGHT:
			self.pos[1] = self.pos[1] % HEIGHT + self.image_height
		if self.pos[1] >= HEIGHT:
			self.pos[1] = self.pos[1] % HEIGHT - self.image_height
                  
		if self.pos[0] + self.image_width <= 0: # or self.pos[0] >= WIDTH:
			self.pos[0] = self.pos[0] % WIDTH + self.image_width
		if self.pos[0] >= WIDTH:
			self.pos[0] = self.pos[0] % WIDTH - self.image_width

        # Thrusting forward      
		forward = angle_to_vector(math.radians(self.angle))
		if self.thrust:
			self.vel[0] += forward[0] * 0.1
			self.vel[1] += -forward[1] * 0.1
		self.angle += self.angle_vel
		self.image = rot_center(self.original, self.angle)
		
class Sprite:
	def __init__(self, pos, vel, ang, ang_vel, image, info, sound=None):
		self.pos = [pos[0],pos[1]]
		self.vel = [vel[0],vel[1]]
		self.angle = ang
		self.angle_vel = ang_vel
		self.image = image
		self.original = self.image
		self.image_width = self.image.get_width()
		self.image_height = self.image.get_height()
		self.image_center = info.get_center()
		self.image_size = info.get_size()
		self.radius = info.get_radius()
		self.lifespan = info.get_lifespan()
		self.animated = info.get_animated()
		self.age = 0
		if sound:
			sound.stop()
			sound.play()
            
	def get_position(self):
		return self.pos
    
	def get_radius(self):
		return self.radius
    
	def collide(self, other_object):
		distance = dist(self.pos, other_object.get_position())

		if distance > self.radius + other_object.get_radius():
			return False
		elif distance < self.radius + other_object.get_radius():
			return True
   
	def draw(self, screen):
		screen.blit(self.image, self.pos)
		#pass
    #    if self.animated:
    #        explosion_index = self.age % 24
    #        canvas.draw_image(self.image, [self.image_center[0] + explosion_index * self.image_size[0], self.image_center[1]], self.image_size, self.pos, self.image_size, self.angle)
    #    else:
    #        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
    
	def update(self):
		self.pos[0] += self.vel[0]
		self.pos[1] += self.vel[1]
		self.age += 1
		
        # Screen wrapping
		if self.pos[1] + self.image_height <= self.radius:
			self.pos[1] = self.pos[1] % HEIGHT + self.image_height
		if self.pos[1] >= HEIGHT:
			self.pos[1] = self.pos[1] % HEIGHT - self.image_height
                  
		if self.pos[0] + self.image_width <= 0:
			self.pos[0] = self.pos[0] % WIDTH + self.image_width
		if self.pos[0] >= WIDTH:
			self.pos[0] = self.pos[0] % WIDTH - self.image_width
            
		self.angle += self.angle_vel
		self.image = rot_center(self.original, self.angle)
        # check lifespan
		if self.age < self.lifespan:
			return False
		else:
			return True
	
def process_sprite_group(group, screen):
	for elem in set(group):
		elem.draw(screen)
		is_old = elem.update()
		if is_old:
			group.remove(elem)
			
def score_to_range():
	global score
	if score < 10:
		return 1
	elif score >= 10 and score < 20:
		return 2
	elif score >= 20:
		return 4
	else:
		return 5

# timer handler that spawns a rock    
def rock_spawner():
	global rock_group, started, my_ship, score
	rang = score_to_range()
	if len(rock_group) < 11 and started:
		vel = [0, 0]
		vel[0] = random.randrange(-(rang), rang + 1)
		vel[1] = random.randrange(-(rang), rang + 1)
		x = random.randrange(0, 800)
		y = random.randrange(0, 600) 

		ang = (random.randrange(-5, 11))
      
		a_rock = Sprite([x, y], vel, 0, ang, asteroid_image, asteroid_info)
		distance = dist(my_ship.get_position(), a_rock.get_position())
		if distance > 100:
			rock_group.add(a_rock)
			
def main():
	# Init pygame
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption('Rice Rocks')
	
	# Load the graphics
	ship_info = ImageInfo([45, 45], [90, 90], 35)
	ship_sheet = spritesheet.spritesheet('art/double_ship.png')
	ship_images = ship_sheet.images_at(((0, 0, 90, 90),(90, 0, 90,90)), colorkey=(255, 255, 255))
	
	global asteroid_info
	asteroid_info = ImageInfo([45, 45], [90, 90], 40)
	global asteroid_image
	asteroid_image = load_image('asteroid_blue.png')
	
	global missile_info 
	missile_info = ImageInfo([5,5], [10, 10], 3, 50)
	global missile_image
	missile_image = load_image('shot2.png')
	

	# Load the sounds
	# Make em global first though
	global ship_thrust_sound, missile_sound
	soundtrack = load_sound('music.ogg')
	missile_sound = load_sound('shoot.wav')
	ship_thrust_sound = load_sound('thrust.wav')
	ship_thrust_sound.set_volume(0.05)
	explosion_sound = load_sound('explode.wav')
	
	# Init the ship and other objects
	global my_ship
	my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_images, ship_info)
	global rock_group, missile_group
	rock_group = set([])
	missile_group = set([])
	# Load the background
	background = load_image('nebula_blue.f2014.png')

	pygame.display.flip()
	
	# Init game objects
	clock = pygame.time.Clock()
	pygame.time.set_timer(USEREVENT+1, 1000)
	# Game loop
	while 1:
		clock.tick(60)
		# Event listener
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			if event.type == USEREVENT+1:
				rock_spawner()
			# Register key handlers
			if event.type == KEYDOWN and event.key == K_RIGHT:
				my_ship.turn(-5)
			if event.type == KEYDOWN and event.key == K_LEFT:
				my_ship.turn(5)
			if event.type == KEYDOWN and event.key == K_UP:
				my_ship.move(True)
			if event.type == KEYUP and event.key == K_UP:
				my_ship.move(False)
			if event.type == KEYUP and event.key == K_RIGHT:
				my_ship.turn(0)
			if event.type == KEYUP and event.key == K_LEFT:
				my_ship.turn(0)
			if event.type == KEYUP and event.key == K_ESCAPE:
				return
			if event.type == KEYUP and event.key == K_SPACE:
				my_ship.shoot()
		# Update everything
		my_ship.update()
		
		# Draw everything
		screen.blit(background, (0,0))
		my_ship.draw(screen)
		process_sprite_group(missile_group, screen)
		process_sprite_group(rock_group, screen)
		pygame.display.flip()
print ("If you can see this, then PyGame was succesfully imported")


if __name__ == '__main__': main()
