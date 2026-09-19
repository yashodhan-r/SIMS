import pygame
import numpy as np
import random
import arcade

# Configuration

WIDTH = 800
HEIGHT = 800

BOWL_CENTER = np.array([WIDTH / 2, HEIGHT / 2], dtype=float)
BOWL_RADIUS = 300

# Start with 1 ball, then 2. Many at once is the bonus.
NUM_PARTICLES = 50
PARTICLE_RADIUS = 5
PARTICLE_SPEED = 150.0

# Pixels per second squared, not m/s^2. Note that +y points DOWN on screen.
GRAVITY = 900

# How much speed survives a bounce. 1.0 loses nothing, below 1.0 is weaker.
WALL_RESTITUTION = 1.0
RESTITUTION = 1.0

FPS = 60

positions = []
velocities = []

for i in range(NUM_PARTICLES):

    # A random spot inside the bowl, with the whole ball fitting.
    angle = random.uniform(0, 2 * np.pi)
    distance = random.uniform(0, BOWL_RADIUS - PARTICLE_RADIUS)

    positions.append(BOWL_CENTER + distance * np.array([
        np.cos(angle),
        np.sin(angle)
    ]))

    # A random direction, at roughly PARTICLE_SPEED.
    # Swap for np.array([0.0, 0.0]) to drop the ball from rest.
    angle = random.uniform(0, 2 * np.pi)

    velocities.append(PARTICLE_SPEED * np.array([
        np.cos(angle),
        np.sin(angle)
    ]))

# Pygame setup
#pygame.mixer.init()
#pygame.mixer.music.load('sound_final.mp3')
sound = arcade.load_sound("sound_final.mp3")
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Simulation")

clock = pygame.time.Clock()

running = True

# Main loop

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # Seconds since the last frame. This is your timestep.
    dt = clock.tick(FPS) / 1000.0

    ###########################################################################
    # TODO: Make every ball fall, and bounce it off the wall of the bowl.     #
    #                                                                         #
    # Two things happen here, in an order that matters.                       #
    #                                                                         #
    # First, it falls. Gravity is an acceleration, so ask yourself what it    #
    # changes directly: the position, or the velocity? And once that has      #
    # changed, what does the ball's new position depend on?                   #
    #                                                                         #
    # Second, it has to stay in the bowl. Work out how you would even         #
    # tell that it has escaped, given that you know where the centre of       #
    # the bowl is, how wide the bowl is, and how wide the ball is.            #
    # Careful: the ball is drawn with a radius of its own, so its edge        #
    # reaches the wall before its centre would.                               #
    #                                                                         #
    # Once you know it has escaped, two things need fixing. Where should      #
    # the ball actually be, and what should its velocity become? For the      #
    # velocity, only the part heading into the wall should change. The        #
    # part sliding along the wall carries on untouched. WALL_RESTITUTION      #
    # decides how much of the incoming speed comes back out.                  #
    ###########################################################################
    
    # CODE STARTS HERE.

    for i in range(NUM_PARTICLES):
        velocities[i][1] += GRAVITY * dt # i decides ball number and 1 decides y velocity. 0 is x 
        positions[i] += velocities[i] * dt # here, positions[i] pulls out np.array([x,y]) for ith ball and adds velocity to it. velocity is called as [i]. so it also comes our as [x,y]. 

    for i in range(NUM_PARTICLES):
        # Check if the ball is outside the bowl
        direction_to_center = positions[i] - BOWL_CENTER
        distance_to_center = np.linalg.norm(direction_to_center)#computes the length of the vector from the ball to the center of the bowl
        if distance_to_center + PARTICLE_RADIUS > BOWL_RADIUS:
            direction_to_center /= distance_to_center #unit direction vector
            #arcade.play_sound(sound)
            
            # Reflect the velocity along the normal direction
            velocity_normal_component = np.dot(velocities[i], direction_to_center)
            velocities[i] -= (1 + WALL_RESTITUTION) * velocity_normal_component * direction_to_center
            
            # Move the ball back to the edge of the bowl
            positions[i] = BOWL_CENTER + direction_to_center * (BOWL_RADIUS - PARTICLE_RADIUS)
    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################

    ###########################################################################
    # TODO: Make the balls bounce off each other.                             #
    #                                                                         #
    # Start with the condition. Given two balls, what has to be true          #
    # about where they are for them to be touching? Every ball has the        #
    # same radius, which makes this simpler than it sounds.                   #
    #                                                                         #
    # Then the response. A collision changes velocities, not positions.       #
    # Which direction does the change act along, and how would you get        #
    # that direction from the two positions you have? Only the motion         #
    # along that direction matters, the rest is unaffected.                   #
    #                                                                         #
    # One trap worth thinking about: two balls that are overlapping but       #
    # already moving apart should be left alone. If you bounce them again     #
    # they will get stuck together. How would you tell "approaching"          #
    # from "separating"?                                                      #
    #                                                                         #
    # Finally, this has to happen for every pair of balls, not just one.      #
    ###########################################################################

    # CODE STARTS HERE.

    for i in range(NUM_PARTICLES):
        for j in range(i+1, NUM_PARTICLES):
            direction = positions[i] - positions[j]
            distance = np.linalg.norm(direction)
            if distance < 2*PARTICLE_RADIUS:
                direction /= distance
                relative_velocity = velocities[i] - velocities[j]
                if np.dot(relative_velocity, direction) < 0:
                    overlap = 2*PARTICLE_RADIUS - distance
                    positions[i] += direction * (overlap / 2)
                    positions[j] -= direction * (overlap / 2)

                    velocities[i] -= (1+RESTITUTION)/2 * np.dot(relative_velocity, direction)*direction
                    velocities[j] += (1+RESTITUTION)/2 * np.dot(relative_velocity, direction)*direction
                    #arcade.play_sound(sound)



    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################

    # Render

    screen.fill((20, 20, 25))

    pygame.draw.circle(
        screen,
        (180, 180, 180),
        BOWL_CENTER.astype(int),
        BOWL_RADIUS,
        width=3
    )

    for position in positions:
        pygame.draw.circle(screen,(255,0,0),position.astype(int),PARTICLE_RADIUS)

    pygame.display.flip()

pygame.quit()
