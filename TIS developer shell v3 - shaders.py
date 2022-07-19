'''
Tesla in Space Developer - Cam, Player, asteroids, gameview
By Casey R
Last modified 7/16/2022
Testing glsl shader
'''
import arcade
import arcade.gui
import math
from arcade.experimental.shadertoy import Shadertoy

SPRITE_SCALING_TILES = 0.5
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_ASTROID = 0.7
PLASMA_SCALING = 0.5
VIEWPORT_MARGIN_Y = 350
VIEWPORT_MARGIN_X = 450
CAMERA_SPEED = 0.8
# Size of screen to show, in pixels
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
SCREEN_TITLE = "TIS dveloper v3"
PLAYER_MASS = 1
PLAYER_FRICTION = 0.6
ASTEROID_MASS = 1
ASTEROID_FRICTION = 0.6
PLAYER_MOVE_FORCE = 200
BULLET_FORCE_1 = 1000
PLAYER_IMAGE = ":resources:/images/Tesla in Space/TIS_P1.png"
ASTEROID_IMAGE_1 = ":resources:/images/space_shooter/meteorGrey_big1.png"
GLOW_BALL_SHADER = ":resources:/shaders/shadertoy/glow_ball.glsl"


class GlowBall(arcade.Sprite):
    def __init__(self, scale=1.0,center_x=0,center_y=0,angle=0,shadertoy=None, glowcolor=(0,0,0), radius=5):
        super().__init__(scale=scale,center_x=center_x,center_y=center_y,angle=angle)
        self.shadertoy = shadertoy
        self.glowcolor = glowcolor
        self.scale = scale
        self.center_x = center_x
        self.center_y = center_y
        self.angle = angle
        self.radius = radius
        self.texture = arcade.make_circle_texture(radius * 2, glowcolor)
        self._points = self.texture.hit_box_points

    def draw(self):
        self.shadertoy.program['color'] = arcade.get_three_float_color(self.glowcolor)
        #self.shadertoy.render()

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.world_mouse_x = 0
        self.world_mouse_y = 0
        self.click_x = 0
        self.click_y = 0
        self.view_left = 0
        self.view_bottom = 0
        self.dt = 0
        self.glowball_shadertoy = Shadertoy.create_from_file(self.window.get_size(), GLOW_BALL_SHADER)
        self.camera_sprites = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.physics_engine = None
    
    def setup(self):
        self.player_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.glow_bullet_list = arcade.SpriteList()
        self.player = arcade.Sprite(PLAYER_IMAGE, SPRITE_SCALING_PLAYER)
        self.player.center_x = 0
        self.player.center_y = 0
        self.player_list.append(self.player)

        self.asteroid_sprite = arcade.Sprite(ASTEROID_IMAGE_1, SPRITE_SCALING_ASTROID)
        self.asteroid_sprite.center_x = 200
        self.asteroid_sprite.center_y = 200
        self.asteroid_list.append(self.asteroid_sprite)
        self.physics_engine = arcade.PymunkPhysicsEngine(gravity=(0,0))
        self.physics_engine.add_sprite(self.player,
                                mass = PLAYER_MASS,
                                friction = PLAYER_FRICTION,
                                damping = 0.5,
                                collision_type='player')
        self.physics_engine.add_sprite(self.asteroid_sprite,
                                mass = ASTEROID_MASS,
                                friction = ASTEROID_FRICTION,
                                damping = 0.5,
                                collision_type='default')
        self.view_left = 0
        self.view_bottom = 0
        self.scroll_screen() 
        self.camera_sprites.update()
    
    def player_static_collision(self,player,static_list):
            arcade.check_for_collision_with_list(player, static_list) 
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.click_x = x + self.view_left
        self.click_y = y + self.view_bottom
        if button == 1:
            self.fire_bullet()   

    def fire_bullet(self):           
        angle = math.radians(self.player.angle) + math.pi/2
        player_size = max(self.player.width, self.player.height) / 2
        bullet_size = max(self.player.width, self.player.height) / 2
        radius_start = player_size + bullet_size        
        bullet_x,bullet_y = self.polar_to_cart(radius_start,angle,[self.player.center_x,self.player.center_y])
        bullet = GlowBall(shadertoy=self.glowball_shadertoy,
                            glowcolor= (250,250,250),
                            radius=5,
                            scale=PLASMA_SCALING,
                            center_x=bullet_x,
                            center_y=bullet_y,
                            angle=math.degrees(angle) - 90)
        self.glow_bullet_list.append(bullet)
        angle = math.pi/2
        bullet_force_x = BULLET_FORCE_1 * math.cos(angle)
        bullet_force_y = BULLET_FORCE_1 * math.sin(angle)
        self.physics_engine.add_sprite(bullet,
                                mass=0.05,
                                damping=1,
                                friction=0.01,
                                moment_of_intertia=100000,
                                elasticity=0.9)
        self.physics_engine.apply_force(bullet, (bullet_force_x,bullet_force_y)) 

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.S:
            self.down_pressed = True
        if key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True
    
    def on_key_release(self, key, modifiers):
        ''' Called when the user releases a key. '''
        if key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.S:
            self.down_pressed = False
        if key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False
    
    def scroll_screen(self):
        # Scroll left
        left_boundary = self.view_left + VIEWPORT_MARGIN_X
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
        
        # Scroll right
        right_boundary = self.view_left + self.window.width - VIEWPORT_MARGIN_X
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary

        # Scroll up
        top_boundary = self.view_bottom + self.window.height - VIEWPORT_MARGIN_Y
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary

        # Scroll down
        bottom_boundary = self.view_bottom + VIEWPORT_MARGIN_Y
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom
        
        self.camera_position = self.view_left, self.view_bottom
        self.camera_sprites.move_to(self.camera_position, CAMERA_SPEED)
     
    def on_mouse_motion(self, x, y, dx, dy):
        # Getting mouse to match world position
        self.mouse_x = x 
        self.mouse_y = y 
        self.world_mouse_x = x + self.view_left
        self.world_mouse_y = y + self.view_bottom
     
    def on_update(self, delta_time):
        if self.up_pressed and not self.down_pressed:
            self.thrust_force = (0,PLAYER_MOVE_FORCE)
            self.physics_engine.apply_force(self.player, self.thrust_force)
        elif self.down_pressed and not self.up_pressed:
            self.thrust_force = (0,-PLAYER_MOVE_FORCE)
            self.physics_engine.apply_force(self.player, self.thrust_force)
        else:
            self.thrust_force = (0,0)
        if self.left_pressed and not self.right_pressed:
            force = (-PLAYER_MOVE_FORCE/2,0)
            self.physics_engine.apply_force_point(self.player, force, (0,60))
            force = (PLAYER_MOVE_FORCE/2,0)
            self.physics_engine.apply_force_point(self.player, force, (0,-60))        
            #self.player.change_angle = 3
        elif self.right_pressed and not self.left_pressed:
            force = (PLAYER_MOVE_FORCE/2,0)
            self.physics_engine.apply_force_point(self.player, force, (0,60))
            force = (-PLAYER_MOVE_FORCE/2,0)
            self.physics_engine.apply_force_point(self.player, force, (0,-60))
        self.player_static_collision(self.player,self.asteroid_list)
        #self.player_static_collision(self.player,self.static_list)
        self.physics_engine.step()  
        self.scroll_screen() 
    
    def on_draw(self):     
        self.clear() 
        self.camera_sprites.use()

        self.player.draw()
        self.asteroid_list.draw()
        self.glowball_shadertoy.program['pos'] = (self.player.position[0]-self.camera_sprites.position[0],
                                        self.player.position[1]-self.camera_sprites.position[1])
        self.glowball_shadertoy.render()
        self.glow_bullet_list.draw()
        self.camera_gui.use()
        # drawing mouse aimer
        arcade.draw_circle_outline(center_x = self.mouse_x, center_y = self.mouse_y, 
                        radius = 7, color = arcade.color.GREEN, border_width = 2)  
        self.developer_feedback(self.player,self.window.size[0]/2 -100,self.window.size[1]-50,False)
    
    def developer_feedback(self,sprite,x_position,y_position,margin_bool):
        pymunk_px = self.physics_engine.get_physics_object(sprite).body.position[0]
        pymunk_py = self.physics_engine.get_physics_object(sprite).body.position[1]
        pymunk_pa = self.physics_engine.get_physics_object(sprite).body.angle
        pymunk_angV = self.physics_engine.get_physics_object(sprite).body.angular_velocity  
        pymunk_V = self.physics_engine.get_physics_object(sprite).body.velocity
        pymunk_F = self.physics_engine.get_physics_object(sprite).body.force # seems to be always zero? why?
        F_calc_x = (1/32)*(0.5* PLAYER_MASS * pymunk_V[0]**2)/(pymunk_V[0]*self.dt + 1e-9)
        F_calc_y = (1/32)*(0.5* PLAYER_MASS * pymunk_V[1]**2)/(pymunk_V[1]*self.dt + 1e-9) 
        #F_calc_x = self.player.mass * self.player.velocity[0]/(self.dt + 1e-9)
        #F_calc_y = self.player.mass * self.player.velocity[1]/(self.dt + 1e-9)         
        pymunk_T = self.physics_engine.get_physics_object(sprite).body.torque
        # net angular momentum/ angular velocity http://www.pymunk.org/en/latest/pymunk.html?highlight=moment#pymunk.Body.moment
        pymunk_mom = self.physics_engine.get_physics_object(sprite).body.moment
        # this is the same as self.player.center_x and y and self.player.angle
        px_py_pa = f"Px, Py, Angle: ({pymunk_px:5.1f}, {pymunk_py:5.1f}), {math.degrees(pymunk_pa):5.1f}"
        arcade.draw_text(px_py_pa, x_position, y_position, arcade.color.WHITE, 14)
        V_angV = f"V, angular V: ({pymunk_V[0]:5.1f},{pymunk_V[1]:5.1f}),{pymunk_angV:5.1f}"
        arcade.draw_text(V_angV, x_position, y_position-20, arcade.color.WHITE, 14)
        '''F_T_mom = f"Force, Torque, moment: ({F_calc_x:5.1f},{F_calc_y:5.1f}), {pymunk_T:5.1f}, {pymunk_mom:5.1f}"
        arcade.draw_text(F_T_mom, x_position, y_position-40, arcade.color.WHITE, 14)'''
        mouse_text = f"mouse pos/click: ({self.mouse_x:5.1f},{self.mouse_y:5.1f}),({self.click_x:5.1f},{self.click_y:5.1f})"
        arcade.draw_text(mouse_text, 10, self.window.size[1]-65, arcade.color.WHITE, 14)
        world_mouse = f"world mouse: ({self.world_mouse_x:5.1f},{self.world_mouse_y:5.1f})"
        arcade.draw_text(world_mouse, 10, self.window.size[1]-45, arcade.color.WHITE, 14)
        if margin_bool:
            # for checking the margin of the camera
            left_boundary = VIEWPORT_MARGIN_X
            right_boundary = SCREEN_WIDTH - VIEWPORT_MARGIN_X
            top_boundary = SCREEN_HEIGHT - VIEWPORT_MARGIN_Y
            bottom_boundary = VIEWPORT_MARGIN_Y
            arcade.draw_lrtb_rectangle_outline(left_boundary, right_boundary, top_boundary, bottom_boundary,
                                            arcade.color.RED, 2) 
    
    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)
        self.camera_sprites.resize(width, height)
        self.camera_gui.resize(width, height)
        self.glowball_shadertoy.resize((width, height))
    
    def polar_to_cart(self, magnitude, angle, center):
        '''returns x and y''' 
        x = magnitude  * math.cos(angle) + center[0]
        y = magnitude  * math.sin(angle) + center[1]
        return x, y

    def cart_to_polar(self,start,end):
        '''returns r and angle'''
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        r = math.sqrt(dx**2 + dy**2) 
        angle = math.atan2(dy,dx) 
        return r,angle 

class GameWindow(arcade.Window):
    """
    Main application class.
    """
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        game_view = GameView()
        game_view.setup()
        self.show_view(game_view)

    def on_resize(self, width, height):
        """ This method is automatically called when the window is resized. """
        super().on_resize(width, height)
    
    def on_draw(self):
        pass

def main():
    """ Main function """
    # The font name needs to match the name given in the properties of the .ttf files 
    GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()
