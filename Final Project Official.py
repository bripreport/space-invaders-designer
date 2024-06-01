from dataclasses import dataclass
from designer import *
from random import randint

SPACESHIP_SPEED = 10
ALIEN_SPEED = 3
LASER_SPEED = 10
ALIENS_APPEAR = 100
NUM_LIVES = 5
SPACING = 80
SCORE = 0
background_image("https://img.itch.zone/aW1nLzgwMjIzMDUucG5n/315x250%23c/jj28MR.png")

@dataclass
class World:
    ''' Dataclass representing the game world state '''
    
    spaceship: DesignerObject
    spaceship_speed:int
    aliens: list[DesignerObject]
    alien_speed: int
    aliens_appear: int
    laser_beams: list[DesignerObject]
    explosions: list[DesignerObject]
    lives: int
    score: int
    left_pressed : bool
    right_pressed: bool
    lives_counter: DesignerObject
    score_counter: DesignerObject
    level_up_indicator: DesignerObject
    game_over_screen: DesignerObject

     
def create_world() -> World:
    """
    Creates and initializes a new game world.

    Returns:
    World: The initialized game world.
    """
    return World(create_spaceship(),SPACESHIP_SPEED,
                 [], ALIEN_SPEED,ALIENS_APPEAR,[],[],
                 NUM_LIVES,SCORE,
                 False,False,
                 text("white", "Lives: ",20,x=get_width()//2+330,y=get_height()-50),
                 text("white", "Score: ",30,x=100,y=50),
                 text("white", "Level Up At 500",15,x=100,y=20),
                 text("red", "GAME OVER", 70, x=get_width() // 2, y=((get_height() // 2)-100)))

def create_spaceship() -> DesignerObject:
    """
    Creates and initializes the player's spaceship.

    Returns:
    DesignerObject: The player's spaceship.
    """
    spaceship = image("https://www.lexaloffle.com/bbs/files/30811/x-wing.png")
    grow(spaceship,0.15)
    spaceship.y = get_height() * 0.8
    spaceship.flip_x = True
    return spaceship

def create_alien()-> DesignerObject:
    """
    Creates and initializes an alien.

    Returns:
    DesignerObject: The created alien.
    """
    alien = image("https://media.moddb.com/images/games/1/69/68735/GameLogo.png")
    grow(alien, 0.09)
    return alien

def create_laser(world: World):
    """
    Creates and initializes a laser beam shot by the spaceship.

    Args:
    world (World): The game world.
    """
    laser = rectangle("yellow", 5, 20)
    laser.x = world.spaceship.x
    laser.y = world.spaceship.y - laser.height
    world.laser_beams.append(laser)
    
def powerup_double_lasers(world:World):
    """
    Powers up the spaceship by adding two laser beams.

    Args:
    world (World): The game world.
    """
    laser1 = rectangle("red", 5, 20)
    laser1.x = world.spaceship.x + 40
    laser1.y = world.spaceship.y - laser1.height
    world.laser_beams.append(laser1)
    
    if world.score >= 1000:
        laser2 = rectangle("orange", 5, 20)
        laser2.x = world.spaceship.x - 40
        laser2.y = world.spaceship.y - laser2.height
        world.laser_beams.append(laser2)


def create_explosion(world: World, x: int, y: int, url:str, scale:int):
    """
    Creates and initializes an explosion animation.

    Args:
    world (World): The game world.
    x (int): X-coordinate of the explosion.
    y (int): Y-coordinate of the explosion.
    url (str): URL of the explosion image.
    scale (int): Scale factor for the explosion.
    """
    explosion = image(url)
    grow(explosion, scale)
    explosion.x = x
    explosion.y = y
    show(explosion)
    world.explosions.append(explosion)
    
def update_explosions(world:World):
    """
    Updates the explosion animations, gradually reducing their alpha values.

    Args:
    world (World): The game world.
    """
    kept_explosions = []
    for explosion in world.explosions:
        alpha_value = explosion['alpha']
        if alpha_value > 0:
            explosion['alpha'] = max(alpha_value - 0.05,0)
            kept_explosions.append(explosion)
        else:
            destroy(explosion)
    world.explosions = kept_explosions

def make_alien_groups(world:World):
    """
    Generates groups of aliens to appear on the screen using border measurements.
    Arranges alien components in a random formation during each wave.

    Args:
    world (World): The game world.
    """
    if world.aliens_appear <= 0: #when spawn delay becomes zero
        num_of_aliens = randint(10,20) #sets up random groups of aliens to spawn 
        
        for i in range(num_of_aliens):            
            alien = create_alien()
            alien.x = randint(100,get_width()-alien.width-100)
            # ^aliens can't spawn outside window by choosing int between 10 and (window width - alien's width - 10 units from left/right of window) to keep alien away from the edges
            
            alien.y = -i * (-alien.height + SPACING)
            # ^ -i, current alien positioned above window, * a int that spaces out each alien with respect to the height of the object
                        
            world.aliens.append(alien)
            world.aliens_appear = ALIENS_APPEAR + 200
        
    else:
        world.aliens_appear -= 1 #after group of aliens spawn, counts down ALIENS_APPEAR variable to zero and next group of aliens spawns

def collision(obj1: DesignerObject, obj2: DesignerObject) -> bool: #global function that can be called for any two colliding objects
    """
    Checks for collision between two objects.

    Args:
    obj1 (DesignerObject): The first object.
    obj2 (DesignerObject): The second object.

    Returns:
    bool: True if collision occurs, False otherwise.
    """
    
    if (
        obj1.x < obj2.x + obj2.width and
        obj1.x + obj1.width > obj2.x and
        obj1.y < obj2.y + obj2.height and
        obj1.y + obj1.height > obj2.y
    ):
        return True
    return False


def move_spaceship(world:World):
    """
    Moves the spaceship based on user input.

    Args:
    world (World): The game world.
    """
    if world.left_pressed:
        head_left(world)
        world.spaceship.x -= world.spaceship_speed
        
    if world.right_pressed:
        head_right(world)
        world.spaceship.x += world.spaceship_speed
    
def wrap_spaceship(world: World):
    """
    Wraps the spaceship around the screen when it goes beyond the window boundaries.

    Args:
    world (World): The game world.
    """
    if world.spaceship.x > get_width():
        world.spaceship.x = 0
    elif world.spaceship.x < 0:
        world.spaceship.x = get_width()   
 
def move_aliens(world:World):
    """
    Moves the aliens downwards at a fixed speed and wraps them to the top of the screen
    when they go out of vertical bounds.

    Args:
    world (World): The game world.
    """
    for alien in world.aliens:
        alien.y += world.alien_speed
        if alien.y > get_height():
            alien.y = -alien.height
            
def move_lasers(world:World):
    """
    Moves the laser beams upward and removes off-screen lasers.

    Args:
    world (World): The game world.
    """
    kept = []
    for laser in world.laser_beams:
        laser.y -= LASER_SPEED
        if laser.y + laser.height > 0:
            kept.append(laser)
        else:
            destroy(laser)
    world.laser_beams = kept

def check_player_enemy_collision(world: World):
    destroyed_aliens = []  # List to store aliens that need to be removed
    """
    Checks for collisions between the player's spaceship and aliens.
    Triggers an explosion, desroying both alien and player objects then updates to the lives counter -1 life. 

    Args:
    world (World): The game world.
    """

    for alien in world.aliens:
        if collision(world.spaceship, alien):
            create_explosion(world, alien.x, alien.y,"https://cdn.yurishwedoff.com/88990744658.png",0.15)
            alpha_value = world.spaceship['alpha']
            if alpha_value > 0:
                world.spaceship['alpha'] = max(alpha_value - 0.01,0)
            reset_spaceship(world)
            world.lives -= 1
            update_lives(world)
            destroyed_aliens.append(alien)  # Mark alien for removal
            world.collision_detected = True
            break

    world.aliens = filter_from(world.aliens, destroyed_aliens)
    world.collision_detected = False
    

def check_laser_collision(world:World):
    """
    Checks for collisions between laser beams and aliens.
    The alien and laser objects get destroyed and score updates +10 whenever a collision occurs

    Args:
    world (World): The game world.
    """
    destroyed_lasers = []
    destroyed_aliens = []
    
    for laser in world.laser_beams:
        for alien in world.aliens:
            if collision(laser, alien):
                create_explosion(world, alien.x, alien.y,"https://cdn.yurishwedoff.com/88990744658.png",0.07)
                destroyed_lasers.append(laser)
                destroyed_aliens.append(alien)
                world.score += 10
                
    world.laser_beams = filter_from(world.laser_beams, destroyed_lasers)
    world.aliens = filter_from(world.aliens, destroyed_aliens)
                
                
def filter_from(old_list: list[DesignerObject], elements_to_not_keep: list[DesignerObject]) -> list[DesignerObject]:
    """
    Filters out specified elements from a list.

    Args:
    old_list (list[DesignerObject]): The original list.
    elements_to_not_keep (list[DesignerObject]): List of elements to be filtered out.

    Returns:
    list[DesignerObject]: The filtered list.
    """
    new_values = []
    for item in old_list:
        if item not in elements_to_not_keep:
            new_values.append(item)
        else:
            destroy(item)
    return new_values            
                
def shoot_lasers(world:World, key:str):
    """
    Initiates laser shot when the spacebar is pressed.

    Args:
    world (World): The game world.
    key (str): The key pressed by the user.
    """
    if key == "space":
        create_laser(world)
        if world.score >= 500:
            world.level_up_indicator.text = "Level Up At 1000"
            powerup_double_lasers(world)
                

def reset_spaceship(world: World):
    """
    Resets the position of the player's spaceship to the center of the screen.

    Args:
    world (World): The game world.
    """
    world.spaceship.x = get_width() // 2 # resets spaceship to the middle of screen
    world.spaceship.y = get_height() * 0.8


def head_left(world: World):
    """
    Sets the spaceship speed for left movement.

    Args:
    world (World): The game world.
    """
    world.spaceship_speed = SPACESHIP_SPEED
    
def head_right(world: World):
    """
    Sets the spaceship speed for right movement.

    Args:
    world (World): The game world.
    """
    world.spaceship_speed = SPACESHIP_SPEED
    
def navigate_spaceship(world: World, key: str):
    """
    Handles navigation of the spaceship based on user input.

    Args:
    world (World): The game world.
    key (str): The key pressed.
    """
    
    if key == "left":
        world.left_pressed = True
        if world.right_pressed:
            head_right(world)
            
    if key == "right":
        world.right_pressed = True
        if world.left_pressed:
            head_left(world)
        
def release_key(world: World, key: str):
    """
    Handles key release events for spaceship navigation.
    Controls spaceship behavior when both left and right keys are held down with boolean flags

    Args:
    world (World): The game world.
    key (str): The key released.
    """
    if key == "left":
        world.left_pressed = False
        if world.right_pressed:
            head_right(world)
            
    if key == "right":
        world.right_pressed = False
        if world.left_pressed:        
            head_left(world)
            
def update_lives(world: World):
    """
    Updates the displayed lives counter.

    Args:
    world (World): The game world.
    """
    world.lives_counter.text = "Lives: " + str(world.lives)
    
def no_lives(world: World) -> bool:
    """
    Checks if the player has no remaining lives.

    Args:
    world (World): The game world.

    Returns:
    bool: True if no lives remaining, False otherwise.
    """
    hide(world.game_over_screen)
    no_more_lives_left = False
    if world.lives == 0:
        no_more_lives_left = True
        show(world.game_over_screen)
    return no_more_lives_left

def game_over_screen(world: World):
    """
    Hides all unwanted game objects and displays the game over screen.
    Shows final player stats

    Args:
    world (World): The game world.

    Returns:
    DesignerObject: The game over screen.
    """
    if no_lives(world):
        set_window_color("black")
        hide(world.level_up_indicator)
        hide(world.lives_counter)
        hide(world.spaceship)
        
        for alien in world.aliens:
            hide(alien)
        for laser in world.laser_beams:
            hide(laser)

        for explosion in world.explosions:
            hide(explosion)

        show(world.game_over_screen)
        update_score_counter(world)
        world.score_counter.x = get_width() // 2 
        world.score_counter.y = get_height() * 0.5
        world.score_counter.text = "FINAL SCORE: " + str(world.score)

        return world.game_over_screen
    
    
    hide(world.game_over_screen)
    
def update_score_counter(world: World):
    """
    Updates the displayed score counter.

    Args:
    world (World): The game world.
    """
    world.score_counter.text = "SCORE: " + str(world.score)    


'''Event Handlers controlling game state and user input'''
when('starting', create_world)
when('updating', move_spaceship)
when('updating', wrap_spaceship)
when('updating', make_alien_groups)
when('updating', move_aliens)
when('typing', shoot_lasers)
when('updating', move_lasers)
when('updating', check_laser_collision)
when('updating', check_player_enemy_collision)
when('updating', update_explosions)
when('updating', update_lives,)
when('updating', update_score_counter)
when('typing', navigate_spaceship)
when('done typing', release_key)
when(no_lives ,game_over_screen,pause)

start()
