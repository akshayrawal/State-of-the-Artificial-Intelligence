import pygame
import time
import math
from NeuralNetwork import *
from GeneticAlgorithm import *
from Level import *

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARKSLATEBLUE = (72,61,139)
DEEPSKYBLUE = (0,191,255)
PALEGREEN = (152,251,152)
ROSYBROWN = (188,143,143)
PALEVIOLET = (219,112,147)
YELLOW = (255,255,0)


class Player(pygame.sprite.Sprite):
    """ This class represents the bar at the bottom that the player
        controls. """
 
    # -- Methods
    def __init__(self, playerID, color, screen, AI = True):
        """ Constructor function """
 
        # Call the parent's constructor
        super().__init__()
 
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.width = 40
        self.height = 60

        genomeInputs = 3
        genomeOutputs = genomeInputs
        self.brain = Genome()
        
        self.enemy = None
        
        vision = genomeInputs #the input array fed into the neuralNet  <- does this come from look?
        decision = genomeOutputs #the out put of the NN 
        #vision = []
        # decision = []

        # self.framesAlive = 0

        # self.runningFitness
        # self.totalFitnessCalculations
        # self.avgFitness

        self.maxHealth = 40
        self.health = 40
        self.color = color 
        self.playerID = playerID

        self.sword = None
        self.isAI = AI
        self.isAttacking = False

        self.direction = "none"
        self.moveLeftEvent = pygame.event.Event(pygame.USEREVENT, action = "moveLeft", id = playerID)
        self.moveRightEvent = pygame.event.Event(pygame.USEREVENT, action = "moveRight", id = playerID)
        self.jumpEvent = pygame.event.Event(pygame.USEREVENT, action = "jump", id = playerID)
        self.stopEvent = pygame.event.Event(pygame.USEREVENT, action = "stop", id = playerID)
        self.killEvent = pygame.event.Event(pygame.USEREVENT, action = "kill", id = playerID)
        self.attackEvent = pygame.event.Event(pygame.USEREVENT, action = "attack", id = playerID)

        self.damage = pygame.event.Event(pygame.USEREVENT, action = "damage", id= playerID)
        self.sideJumpCount = 0
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(color)

        # So our player can modify the overall screen
        self.screen = screen
 
        # Set a referance to the image rect.
        self.rect = self.image.get_rect()

        #coordinate point
        self.player_coord = (self.rect.x, self.rect.y)

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0
 
        # List of sprites we can bump against
        self.level = None

    def setEnemy(self, enemy):
        self.enemy = enemy

    #once neural net is established, send in the output nodes
    #as parameters
    def think(self, vision):
        """
        Converts output of neural net into events
        that generate actions for the specific player
        in the main driver class
        """
        max = 0
        maxIndex = 0
        #get the output of the neural network
        decision = brain.feedForward(vision)
        for i in decision:
            if (decision[i] > max):
                max = decision[i]
                maxIndex = i
        
        if (self.rect.x < vision[0] and self.rect.x + self.width > vision[0]) and (self.rect.y < vision[1] and self.rect.y + self.height > vision[1]):
            # print("Player ", self.playerID, " has ", self.health)
            pygame.event.post(self.damage)

        if self.rect.x > vision[0]:
            pygame.event.post(self.moveRightEvent)
        elif self.rect.x < vision[0]:
            pygame.event.post(self.moveLeftEvent)
        elif self.distanceToPoint(point) < 100:
            pygame.event.post(self.jumpEvent)
        #add to next statement when debugged:
        else:
            pygame.event.post(self.stopEvent)
            
    
    def calculateFitness(self):
      progressToGoal = self.distanceToPoint((800,500), False, RED, "X") / 500
      timeAlive = self.framesAlive / 60
      health = self.health / self.maxHealth
      fitness = timeAlive - progressToGoal + health
      self.runningFitness += fitness
      self.totalFitnessCalculations += 1
      return fitness
    
    def determineAvgFitness(self):
      return self.runningFitness / self.totalFtinessCalculations

    def look(self, otherPlayers, gameWidth):
        temp = 0
        min = 10000
        minIndex = -1
        counter = 0
        for i in otherPlayers: 
            counter = counter + 1
            poscalc = i.posX + i.w / 2 - (self.posX - gameWidth / 2)
            if(poscalc < min and poscalc > 0):
                min = poscalc
                minIndex = counter
        vision[1] = minIndex ##This is the distance between the players
        vision[2] = otherPlayer.direction ##We might have to fix this <---- direction other player is facing
        vision[0] = 1.0/(min/10.0) # <----What does this calculate?
        return vision #<--- this wasn't returned inthe dino run c version         

    def updateHealth(self):
        healthBarLength = (self.health/self.maxHealth) * self.width
        if self.health <= 0:
            # pygame.draw.line(self.screen, RED, (self.rect.x, self.rect.y - 10), (self.rect.x + self.width, self.rect.y - 10), 4)
            # self.displayDeath()
            pygame.event.post(self.killEvent)
        else:
            if self.health/self.maxHealth > .8:
                pygame.draw.line(self.screen, GREEN, (self.rect.x, self.rect.y - 10), (self.rect.x + healthBarLength, self.rect.y - 10), 4)
            elif self.health/self.maxHealth > .5:
                pygame.draw.line(self.screen, PALEGREEN, (self.rect.x, self.rect.y - 10), (self.rect.x + healthBarLength, self.rect.y - 10), 4)
            elif self.health/self.maxHealth > .2:
                healthBarLength = (self.health/self.maxHealth) * self.width
                pygame.draw.line(self.screen, YELLOW, (self.rect.x, self.rect.y - 10), (self.rect.x + healthBarLength, self.rect.y - 10), 4)
            else: 
                pygame.draw.line(self.screen, RED, (self.rect.x, self.rect.y - 10), (self.rect.x + healthBarLength, self.rect.y - 10), 4)

    
    def distanceToPoint(self, point, drawFlag = False, color = WHITE, axis = "BOTH"):
        x_goal = point[0]
        y_goal = point[1]

        player_pos = (self.rect.x + (self.width/2), self.rect.y + (self.height/2))
        x_player = player_pos[0]
        y_player = player_pos[1]

        x_distance = abs(x_goal - x_player)
        y_distance = abs(y_goal - y_player)

        if axis == "BOTH":
            total_distance = x_distance*x_distance + y_distance*y_distance
            total_distance = math.sqrt(total_distance)
            total_distance = int(total_distance)
        if axis == "X":
            total_distance = x_distance
        if axis == "Y":
            total_distance = y_distance

        if drawFlag == True:
            font = pygame.font.SysFont('tahoma', 15, False, False)
            # HIT TEXT
            distanceText = font.render(str(total_distance), True, WHITE)
            x_mid = x_player
            y_mid = y_player
            if x_player <= x_goal:
                x_mid += x_distance/2
            else:
                x_mid -= x_distance/2
            if y_player <= y_goal:
                y_mid += y_distance/2
            else:
                y_mid -= y_distance/2

            if axis =="X":
                pygame.draw.line(self.screen, color, player_pos, (x_goal, y_player), 1)
                midPoint = (x_mid, y_player)
            else:
                pygame.draw.line(self.screen, self.color, player_pos, point, 1)
                midPoint = (x_mid, y_mid)
            self.screen.blit(distanceText, midPoint)

        return total_distance
    

    def update(self):
        #update neural network
        mouse_pos = pygame.mouse.get_pos()
        
        #helps determine fitness
        # self.framesAlive += 1

        enemyPos = (self.enemy.rect.x, self.enemy.rect.y)
        #pass outputs to think
        if self.isAI:
            self.think(enemyPos)

        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x

        if self.isAttacking == True:
            print("Player: ", self.playerID, " is looking ", self.direction)
            if self.direction == "left":
                self.sword.rect.x = self.rect.x - 50
                self.sword.rect.y = self.rect.y + 30
            elif self.direction == "right":
                self.sword.rect.x = self.rect.x + self.width + 50
                self.sword.rect.y = self.rect.y + 30
            else:
                self.sword.rect.x = self.rect.x + self.width/2
                self.sword.rect.y = self.rect.y -30
            self.level.attack_list.remove(self.sword)
            self.sword = None
            self.isAttacking = False      

        # hit_box_list = pygame.sprite.spritecollide(self, self.level.danger_list, False)
        # See if we hit anything
        attack_hit_list = pygame.sprite.spritecollide(self, self.level.attack_list, False)
        if len(attack_hit_list) > 0:
            pygame.event.post(self.damage)          
        
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
 
        # Move up/down
        self.rect.y += self.change_y
        # If the player gets near the right side, shift the world left (-x)
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
 
        # If the player gets near the left side, shift the world right (+x)
        if self.rect.left < 0:
            self.rect.left = 0
 
        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        
        if len(block_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.sideJumpCount = 0
        
        for block in block_hit_list:
 
            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
            # Stop our vertical movement
            self.change_y = 0
 
    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .45
 
        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height
 
    def jump(self):
        """ Called when user hits 'jump' button. """
 
        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down
        # 1 when working with a platform moving down.
        self.rect.y += 4
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 4

        if (self.rect.left == 0 or self.rect.right == SCREEN_WIDTH) and self.sideJumpCount == 0:
                self.change_y = -10
                self.sideJumpCount = 1
 
        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
                self.change_y = -10

        
 
    # Player-controlled movement:
    def boost(self):
        """Fires a look vector"""
        if self.direction == "left":
            self.change_x -= 10
        elif self.direction == "right":
            self.change_x += 10
        
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -4 
 
    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 4
 
    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.direction = "none"
        self.change_x = 0

    def executeAction(self, action):
        if action == 0:
            self.go_left()
        elif action == 1:
            self.go_right()
        elif action == 2:
            self.jump()
        elif action == 3:
            self.stop()
