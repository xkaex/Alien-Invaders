"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

# Kofi Efah(kae87) Reggie Ezeh(rce57)
# 12/4/2018
"""

from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen.
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of
    aliens.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.

    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _aliens: the 2d list of aliens in the wave [rectangular 2d list of Alien or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that
    you need to access in Invaders.  Only add the getters and setters that you need for
    Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may want to
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    ADDITIONAL ATTRIBUTES:
    _dir: The direction that the aliens are moving in [str, 'right' or 'left']
    _hold_fire: number of steps that the aliens take before firing. [int >= 0]
    _randomcol: generates a random number between 0 and the length of aliens
     in a column.[0 <= int <= len(self._aliens[0])-1]
    _steps_they_moved: keeps track of how many steps the aliens moved since they last fired.[int >= 0]
    _starting_left_column: A number to represent the leftmost column with atleast one alien in it.[int >= 0]
    _starting_right_column: A number to represent the rightmost column with atleast one alien in it.[int >=0]
    _total_score: Keeps track of the player's score.[int>=0]
    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getlife(self):
        """
        This getter returns the value of self._lives.
        """
        return self._lives

    def getscore(self):
        """
        Returns the attribute _total_score, the total score accrued.
        """
        return self._total_score

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self):
        """
        This is the main initializer for wave and initializes the attributes in
        wave
        """
        self._aliens=[]
        self.init_alien()

        self._ship = Ship(GAME_WIDTH/2,SHIP_BOTTOM,
        SHIP_WIDTH,SHIP_HEIGHT,source="ship.png")

        self._dline = GPath(points=[0,DEFENSE_LINE,
        GAME_WIDTH,DEFENSE_LINE],linewidth=2,linecolor="black")

        self._time = 0
        self._lives = SHIP_LIVES
        self._dir = 'right'
        self._bolts = []
        self._steps_they_moved =0  #reset to 0 in helper,
        self._hold_fire = random.randint(1,BOLT_RATE) # get a new in helper
        self._randomcol = random.randint(0,len(self._aliens[0])-1)
        self._starting_left_column = 0
        self._starting_right_column = len(self.transposed_alienlist())-1
        self._total_score = 0

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self,input,dt):
        """
        Animates the game objects.

        This method animates the aliens, Bolt, and ship objects.
        """
        self.shipmovement(input)
        self.init_Bolt(input)
        self.boltmovement()
        self.alienmovement(dt)
        self.shipcollide()
        self.aliencollide()
        self.leftmostcolumn(self._starting_left_column)
        self.rightmostcolumn(self._starting_right_column)
        self.alien_wins()
        self.player_wins()


    def obtain_vertical(self,rownum):
        """
        This helper function returns the y-coordinate of the aliens of a given row.
        """
        y_value = GAME_HEIGHT-(ALIEN_CEILING +\
         (ALIEN_HEIGHT+ALIEN_V_SEP)*(rownum))
        return y_value

    def init_alien(self):
        """
        This helper function defines the attribute _aliens for initialization in
        the __init__ method above.

        """
        total = ALIEN_ROWS
        for row in (range(ALIEN_ROWS)):
            each_row = []
            if row % ALIEN_ROWS==0:
                for t in range(ALIENS_IN_ROW):
                    each_alien = Alien((ALIEN_WIDTH+ALIEN_H_SEP)*(t+1),
                    GAME_HEIGHT-ALIEN_CEILING,ALIEN_WIDTH,ALIEN_HEIGHT,
                    ALIEN_IMAGES[0],5*total)
                    each_row.append(each_alien)
            if row % ALIEN_ROWS == 1:
                for t in range(ALIENS_IN_ROW):
                    each_alien = Alien((ALIEN_WIDTH+ALIEN_H_SEP)*(t+1),
                    self.obtain_vertical(row),ALIEN_WIDTH,ALIEN_HEIGHT,
                    ALIEN_IMAGES[0],5*total)
                    each_row.append(each_alien)
            elif row % ALIEN_ROWS==2 or row % ALIEN_ROWS==3:
                for t in range(ALIENS_IN_ROW):
                    each_alien = Alien((ALIEN_WIDTH+ALIEN_H_SEP)*(t+1),
                    self.obtain_vertical(row),ALIEN_WIDTH,ALIEN_HEIGHT,
                    ALIEN_IMAGES[1],5*total)
                    each_row.append(each_alien)
            elif row % ALIEN_ROWS==4:
                for t in range(ALIENS_IN_ROW):
                    each_alien = Alien((ALIEN_WIDTH+ALIEN_H_SEP)*(t+1),
                    self.obtain_vertical(row),ALIEN_WIDTH,ALIEN_HEIGHT,
                    ALIEN_IMAGES[2],5*total)
                    each_row.append(each_alien)
            total -= 1
            self._aliens.append(each_row)

        # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS

    def draw(self,view):
        """
        Draws game objects to the game view. This includes ships, aliens and bolts.
        """
        for x in self._aliens:
            for alien in x:
                if alien != None:
                    alien.draw(view)
        if self._ship is not None:
            self._ship.draw(view)
        self._dline.draw(view)
        for bolt in self._bolts:
            bolt.draw(view)

    def shipmovement(self,input):
        """
        This method controls the movement of the ship.

        A key press of 'left' or 'right' is detected and the x-coordinate of the
        ship is changes by +SHIP_MOVEMENT or -SHIP_MOVEMENT.
        """
        if input.is_key_down('right'):
            if self._ship.x + SHIP_WIDTH/2<=GAME_WIDTH:
                self._ship.x += SHIP_MOVEMENT

        if input.is_key_down('left'):
            if self._ship.x - SHIP_WIDTH/2 >= 0:
                self._ship.x -= SHIP_MOVEMENT

    def moveright(self,dt):
        """
        This method controls alien movement in the positive x direction.

        The aliens in each row are looped over and their x-coordinates are
        increased by ALIEN_H_WALK.
        """
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.x += ALIEN_H_WALK

    def movedown(self,dt):
        """
        This method controls downward alien movement.

        Like the above method, the aliens in each row are looped over, but the
        y-coordinate changes by -ALIEN_V_WALK.
        """
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.y -= ALIEN_V_WALK

    def moveleft(self,dt):
        """
        This method controls alien movement in the negative x direction.

        The aliens in the row are looped over, but their x-coordinates change by
        -ALIEN_H_WALK.
        """
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    alien.x -= ALIEN_H_WALK

    def leftmostcolumn(self, left):
        """
        Returns: An alien in the leftmost column where there is atleast one alien.
        """
        amount_dead = 0
        if self.player_wins():
            return None
        for alien in self.transposed_alienlist()[self._starting_left_column]:
            if alien == None:
                amount_dead += 1
        if amount_dead != len(self.transposed_alienlist()\
        [self._starting_left_column]):
            for alien in self.transposed_alienlist()[left]:
                if alien != None:
                    return alien
        else:
            self._starting_left_column += 1
            return self.leftmostcolumn(left)

    def rightmostcolumn(self,right):
        """
        Returns: An alien in the rightmost column where there is atleast one alien.
        """
        amount_dead = 0
        accum = False
        if self.player_wins():
            return None
        for alien in self.transposed_alienlist()[self._starting_right_column]:
            if alien == None:
                amount_dead += 1
        if amount_dead != len(self.transposed_alienlist()[self._starting_right_column]):
            for alien in self.transposed_alienlist()\
            [right]:
                if alien != None:
                    return alien
        else:
            self._starting_right_column -= 1
            return self.rightmostcolumn(right)

    def alienmovement(self,dt):
        """
        This method controls alien movement.

        if _dir attribute is 'right' and the rightmost column is nearest to the
        right edge of the window, the aliens move down. This process is repeated
        to account for movement in the left direction.
        """
        b = self._aliens[0]
        rightalien = b[len(b)-1]
        leftalien = b[0]

        if self._time > ALIEN_SPEED:
            if self._dir == 'right':
                if GAME_WIDTH-self.rightmostcolumn(self._starting_right_column).x < \
                (ALIEN_H_SEP+ ALIEN_WIDTH/2):
                    self.movedown(dt)
                    self._dir = 'left'
                else:
                    self.moveright(dt)

            elif self._dir == 'left':
                if 0-self.leftmostcolumn(self._starting_left_column).x >  \
                -1*(ALIEN_H_SEP + ALIEN_WIDTH/2):
                    self.movedown(dt)

                    self._dir = 'right'
                else:
                    self.moveleft(dt)

            self._steps_they_moved+=1  # increments each time the aliens move
            self._time=0

        else:
            self._time+= dt

    def boltmovement(self):
        """
        """
        for bolt in self._bolts:
            if bolt._is_player_bolt == True:
                if bolt.y - BOLT_HEIGHT/2 < GAME_HEIGHT: # if bolt is still in the game screen
                    bolt.y += bolt.getvelocity()
                else:
                    self._bolts.remove(bolt)

            else:    #if it is an alien bolt
                if bolt.y + BOLT_HEIGHT/2 > 0:
                    bolt.y += bolt.getvelocity() * -1
                else:
                    self._bolts.remove(bolt)

    def init_Bolt(self,input):
        """
        This helper function defines the _bolts attribute for initialization in
        the __init__ method above.
        """
        total=0

        if input.is_key_down('up'):   #It's a players bolt
            if len (self._bolts)>0:    # when player fires check to see if there are bolts in the LIST
                for bolt in self._bolts: # if there are bolts in the list check each bolt to see if it belongs to the player or not
                    if bolt._is_player_bolt == True:
                        total+=1    # if it does belong to the palyer, add 1 to the accumulator
            if total <=0: # if there is already a player bolt in the list dont create (fire) another bolt
                self._bolts.append(Bolt(self._ship.x,self._ship.y+
                (SHIP_HEIGHT/2),BOLT_WIDTH,BOLT_HEIGHT,'blue',True))

        if self._steps_they_moved == self._hold_fire:
            self._steps_they_moved=0
            self._bolts.append(Bolt(self.whofires().x,
            self.whofires().y-ALIEN_HEIGHT/2-BOLT_HEIGHT/2,
            BOLT_WIDTH,BOLT_HEIGHT,'red',False))
            self._hold_fire = random.randint(1,BOLT_RATE)
            self._randomcol = random.randint(0,len(self._aliens[0])-1) # get a new column to fire from

    def transposed_alienlist(self):
        """
        Returns a copy of a transposed alien list.
        """
        rows = len(self._aliens)
        cols = len(self._aliens[0])
        rows_to_cols = []
        for x in list(range(cols)):
            row = []
            for y in list(range(rows)):
                row.append(self._aliens[y][x])
            rows_to_cols.append(row)
        return rows_to_cols

    def whofires(self):
            """
            This method checks which alien will fire a bolt.
            """
            total = 0
            for i in self.transposed_alienlist()[self._randomcol]:
                if i == None:
                    total += 1
            if total == len(self.transposed_alienlist()[self._randomcol]): # if the column has no aliens at all
                self._randomcol = random.randint(0,len(self._aliens[0])-1) # get a new index and..
                return self.whofires()      # this calls the function again to try with an new index

            else:
                not_none=0
                for a in range(len(self.transposed_alienlist()[self._randomcol])):  # finds the last alien in the column
                     if self.transposed_alienlist()[self._randomcol][a] != None:
                         not_none = a
                     else:
                         not_none = not_none

                return self._aliens[not_none][self._randomcol] #return the y positon of the alien that fires

    def shipcollide(self):
        """
        This method detects if a bolt collides with the player ship.
        """
        for bolt in self._bolts:
            if bolt._is_player_bolt == False: # if bolt is from alien
                if self._ship != None: # Check is ship is None.
                    if self._ship.collides(bolt) == True: #if bolt hits the ship
                        self._ship = None     #Remove ship
                        self._bolts.remove(bolt)      #Remove bolt from list
                        self._lives -= 1

    def verify_ship_collide(self):
        """
        Returns: True if the ship has been hit.
        """
        if self._ship == None:
            return True

    def aliencollide(self):
        """
        This method detects if a player bolt hits an alien.

        The bolt is tested to see if it is a player bolt.
        """
        for bolt in self._bolts:
            if bolt._is_player_bolt == True:
                for row in self._aliens:
                    for alien in row:
                        if alien != None:
                            if alien.collides(bolt) == True: # if bolt hits alien.
                                dead_alien_row = self._aliens.index(row)
                                dead_alien_column = row.index(alien) #find the alien that died.
                                self._aliens[dead_alien_row][dead_alien_column] = None # remove dead alien
                                self._bolts.remove(bolt)
                                self._total_score += alien._worth


    def revive(self):
        """
        Creates a new ship object if the player has remaining lives.
        """
        self._ship = Ship(GAME_WIDTH/2,SHIP_BOTTOM,
        SHIP_WIDTH,SHIP_HEIGHT,source="ship.png")


    def alien_wins(self):
        """
        Returns True if any alien passes the defense line.
        """
        for row in self._aliens:
            for alien in row:
                if alien != None:
                    if alien.y - ALIEN_HEIGHT/2 < DEFENSE_LINE + self._dline.linewidth/2:
                        return True


    def player_wins(self):
        """
        Returns True if all aliens are destroyed.
        """
        total_alien_positions = 0
        aliens_dead = 0
        for i in self._aliens:
            for alien in i:
                total_alien_positions += 1 # This checks to see the total number of positions in the alien list

        for row in self._aliens:
            for alien in row:
                if alien == None:
                    aliens_dead +=1 #Checks to see how many aliens are dead

        if aliens_dead == total_alien_positions:
            return True
        else:
            return False







    # HELPER METHODS FOR COLLISION DETECTION
