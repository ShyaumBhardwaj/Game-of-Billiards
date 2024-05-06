import phylib
import os
import sqlite3
import math
################################################################################
# import constants from phylib to global varaibles
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER
BALL_RADIUS = phylib.PHYLIB_BALL_RADIUS
HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH
SIM_RATE = phylib.PHYLIB_SIM_RATE
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON
DRAG = phylib.PHYLIB_DRAG
MAX_TIME = phylib.PHYLIB_MAX_TIME
MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS
HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />"""
FOOTER = """</svg>\n"""
################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/
BALL_COLOURS = [
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",
    "MEDIUMPURPLE",
    "LIGHTSALMON",
    "LIGHTGREEN",
    "SANDYBROWN",
]

FRAME_RATE = 0.01
################################################################################
class Coordinate(phylib.phylib_coord):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass
################################################################################
class StillBall(phylib.phylib_object):
    """
    Python StillBall class.
    """

    def __init__(self, number, pos):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """
        phylib.phylib_object.__init__(self,
                                       phylib.PHYLIB_STILL_BALL,
                                       number,
                                       pos, None, None,
                                       0.0, 0.0)

        self.__class__ = StillBall

    def svg(self):
       
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, 28.5, BALL_COLOURS[self.obj.still_ball.number])
################################################################################
class RollingBall(phylib.phylib_object):
    """
    Rolling ball class.
    """

    def __init__(self, number, pos, vel, acc):
        """
        Constructor function.
        """
        phylib.phylib_object.__init__(self,
                                       phylib.PHYLIB_ROLLING_BALL,
                                       number,
                                       pos,
                                       vel,
                                       acc, 0.0, 0.0)

        self.__class__ = RollingBall

    def svg(self):
        
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, 28.5, BALL_COLOURS[self.obj.rolling_ball.number])
################################################################################
class Hole(phylib.phylib_object):
    """
    Hole class.
    """

    def __init__(self, pos):
        """
        Constructor function.
        """
        phylib.phylib_object.__init__(self,
                                       phylib.PHYLIB_HOLE,
                                       0,
                                       pos,
                                       None, None, 0.0, 0.0)

        self.__class__ = Hole

    def svg(self):
       
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (self.obj.hole.pos.x, self.obj.hole.pos.y, HOLE_RADIUS)
################################################################################
class HCushion(phylib.phylib_object):
    """
    Horizontal Cushion class.
    """

    def __init__(self, y):
        """
        Constructor function.
        """
        phylib.phylib_object.__init__(self,
                                       phylib.PHYLIB_HCUSHION,
                                       0,
                                       None,
                                       None, None, 0.0, y)
        self.__class__ = HCushion
        

    def svg(self):
       
       return """ <rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n""" %(self.obj.hcushion.y)
################################################################################
class VCushion(phylib.phylib_object):
    """
    Vertical Cushion class.
    """

    def __init__(self, x):
        """
        Constructor function.
        """
        phylib.phylib_object.__init__(self,
                                       phylib.PHYLIB_VCUSHION,
                                       0,
                                       None,
                                       None, None, x, 0.0)
        self.__class__ = VCushion
        

    def svg(self):
        
        return """ <rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n""" %(self.obj.vcushion.x)

################################################################################
    
class Table(phylib.phylib_table):
    """
    Pool table class.
    """

    def __init__(self):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__(self)
        self.current = -1

    def __iadd__(self, other):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object(other)
        return self

    def __iter__(self):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        self.current = -1
        return self

    def __next__(self):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1  # increment the index to the next object
        if self.current < MAX_OBJECTS:  # check if there are no more objects
            return self[self.current]  # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1  # reset the index counter
        raise StopIteration  # raise StopIteration to tell for loop to stop

    def __getitem__(self, index):
        """
        This method adds item retrieval support using square brackets [ ] .
        It calls get_object (see phylib.i) to retrieve a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object(index)
        if result == None:
            return None
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion
        return result

    def __str__(self):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = ""  # create empty string
        result += "time = %6.1f;\n" % self.time  # append time
        for i, obj in enumerate(self):  # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i, obj)  # append object description
        return result  # return the string

    def segment(self):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment(self)
        if result:
            result.__class__ = Table
            result.current = -1
        return result

    def svg(self):
       
        svg_string = HEADER
        for obj in self:
            if obj is not None:  
                svg_string += obj.svg()
        svg_string += FOOTER
        return svg_string
    
    
    
    def roll( self, t ):
        new = Table();
        for ball in self:
            if isinstance( ball, RollingBall ):
                # create4 a new ball with the same number as the old ball
                new_ball = RollingBall( ball.obj.rolling_ball.number,
                                        Coordinate(0,0),
                                        Coordinate(0,0),
                                        Coordinate(0,0) );
                # compute where it rolls to
                phylib.phylib_roll( new_ball, ball, t );
                # add ball to table
                new += new_ball;
            if isinstance( ball, StillBall ):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall( ball.obj.still_ball.number,
                                    Coordinate( ball.obj.still_ball.pos.x,
                                                ball.obj.still_ball.pos.y ) );
                # add ball to table
                new += new_ball;
                # return table
                return new;

    def cueBall(self):
        for obj in self:
            if isinstance(obj, StillBall) and obj.obj.still_ball.number == 0:
                return obj
            if isinstance(obj, RollingBall) and obj.obj.still_ball.number == 0:
                return obj
            
    def deepcopy_table(original_table):
        new_table = Table()

        for obj in original_table:
            if isinstance(obj, RollingBall):
                new_ball = RollingBall(
                    obj.obj.rolling_ball.number,
                    Coordinate(obj.obj.rolling_ball.pos.x, obj.obj.rolling_ball.pos.y),
                    Coordinate(obj.obj.rolling_ball.vel.x, obj.obj.rolling_ball.vel.y),
                    Coordinate(obj.obj.rolling_ball.acc.x, obj.obj.rolling_ball.acc.y)
                )
                new_table += new_ball

            elif isinstance(obj, StillBall):
                new_ball = StillBall(
                    obj.obj.still_ball.number,
                    Coordinate(obj.obj.still_ball.pos.x, obj.obj.still_ball.pos.y)
                )
                new_table += new_ball

        new_table.time = original_table.time

        return new_table
    
    def num_balls(self):
        count=0;
        for obj in self:
            if isinstance(obj, StillBall):
                count=count+1;
            elif isinstance(obj, RollingBall):
                count=count+1;
        return count

    def get_table_balls(self):
        """
        Get all balls (still and rolling) currently on the table.
        Returns:
            set: A set containing all balls on the table.
        """
        table_balls = set()
        for obj in self:
            if isinstance(obj, StillBall) or isinstance(obj, RollingBall):
                table_balls.add(obj)
        return table_balls
class Database:
    def __init__(self, reset=False):
        # Database file path
        db_file_path = "phylib.db"

        # Check if reset is True, delete the database file
        if reset and os.path.exists(db_file_path):
            os.remove(db_file_path)

        # Connect to the database
        self.conn = sqlite3.connect(db_file_path)

        self.db_conn = self.conn

        cursor = self.conn.cursor()


    def createDB( self ):
        cursor = self.conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Ball (
            BALLID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            BALLNO INTEGER NOT NULL,
            XPOS FLOAT NOT NULL,
            YPOS FLOAT NOT NULL,
            XVEL FLOAT,
            YVEL FLOAT
        );
    ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TTable (
                TABLEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                TIME FLOAT NOT NULL
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS BallTable (
                BALLID INTEGER NOT NULL,
                TABLEID INTEGER NOT NULL,
                FOREIGN KEY (BALLID) REFERENCES Ball,
                FOREIGN KEY (TABLEID) REFERENCES TTable
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Shot (
                SHOTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                PLAYERID INTEGER NOT NULL,
                GAMEID INTEGER NOT NULL,
                FOREIGN KEY (PLAYERID) REFERENCES Player,
                FOREIGN KEY (GAMEID) REFERENCES Game
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TableShot (
                SHOTID INTEGER NOT NULL,
                TABLEID INTEGER NOT NULL,
                FOREIGN KEY (TABLEID) REFERENCES TTable,
                FOREIGN KEY (SHOTID) REFERENCES Shot
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Game (
                GAMEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                GAMENAME VARCHAR(64) NOT NULL
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Player (
                PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                GAMEID INTEGER NOT NULL,
                PLAYERNAME VARCHAR(64) NOT NULL,
                FOREIGN KEY (GAMEID) REFERENCES Game
            );
        ''')

       

        cursor.close()
        self.conn.commit()




    def readTable(self, tableID):
        # Check if the TABLEID exists in the BallTable
        cursor = self.conn.cursor()

        # Create a new Table
        table = Table()

        try:
            # Retrieve data from the Ball and TTable tables using a JOIN clause
            cursor.execute("""
                SELECT B.BALLNO, B.XPOS, B.YPOS, B.XVEL, B.YVEL, T.TIME
                FROM Ball B
                JOIN BallTable BT ON B.BALLID = BT.BALLID
                JOIN TTable T ON BT.TABLEID = T.TABLEID
                WHERE T.TABLEID = ?
            """, (tableID + 1,))

            rows = cursor.fetchall()

            if not rows:
                return None

            for row in rows:
                ballNo, xPos, yPos, xVel, yVel, time = row
                position = Coordinate(xPos, yPos)
                velocity = Coordinate(float(xVel), float(yVel)) if xVel is not None and yVel is not None else None

                acc_x = 0.0  # Initialize acc_x outside the if-else block
                acc_y = 0.0  # Initialize acc_y outside the if-else block

                if xVel is not None and yVel is not None:
                    speedrb = math.sqrt(xVel ** 2 + yVel ** 2)
                    if speedrb > VEL_EPSILON:
                        acc_x = -xVel / speedrb * DRAG
                        acc_y = -yVel / speedrb * DRAG

                    acc = Coordinate(acc_x, acc_y)
                    ball = RollingBall(ballNo, position, velocity, acc)
                else:
                    ball = StillBall(ballNo,position)

                table += ball
                table.time = time
            return table

        except Exception as e:
            print(f"Error reading table: {e}")

        finally:
            cursor.close()
            self.conn.commit()

        return None

    def writeTable(self, table):
        
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO TTable (TIME) VALUES (?)", (table.time,))

        # Get the autoincremented TABLEID value minus 1
        tableID = cursor.lastrowid - 1

        for obj in table:
            if isinstance(obj, RollingBall):
                # If the object is a RollingBall, insert its information into the Ball table
                cursor.execute("""
                    INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL)
                    VALUES (?, ?, ?, ?, ?)
                """, (obj.obj.rolling_ball.number, obj.obj.rolling_ball.pos.x, obj.obj.rolling_ball.pos.y,
                        obj.obj.rolling_ball.vel.x, obj.obj.rolling_ball.vel.y))

                
                ballID = cursor.lastrowid

                # Insert the BALLID and TABLEID into the BallTable table
                cursor.execute("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)", (ballID, tableID + 1))

            elif isinstance(obj, StillBall):
                # If the object is a StillBall, insert its information into the Ball table
                cursor.execute("""
                    INSERT INTO Ball (BALLNO, XPOS, YPOS)
                    VALUES (?, ?, ?)
                """, (obj.obj.still_ball.number, obj.obj.still_ball.pos.x, obj.obj.still_ball.pos.y))

                
                ballID = cursor.lastrowid

                # Insert the BALLID and TABLEID 
                cursor.execute("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)", (ballID, tableID+1))

       
        self.conn.commit()

       
        cursor.close()

        return tableID



    
    def close(self):
    # Commit changes to the database
        self.conn.commit()

    # Close the database conn
        self.conn.close()
   
    def getLastGameID(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(GAMEID) FROM Game")
        last_game_id = cursor.fetchone()[0]
        cursor.close()
        self.conn.commit()
        return last_game_id
    
    def getLastTableID(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(TABLEID) FROM TTable")
        last_table_id = cursor.fetchone()[0]
        cursor.close()
        self.conn.commit()
        return last_table_id


    

    
    def getGame(self, gameID):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT G.GAMENAME
            FROM Game G
            WHERE G.GAMEID = ?
        """, (gameID,))
        game_name = cursor.fetchone()
        cursor.close()
        self.conn.commit()

        if game_name:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT P.PLAYERNAME
                FROM Player P
                WHERE P.GAMEID = ?
            """, (gameID,))
            player_names = cursor.fetchall()
            cursor.close()

            if len(player_names) == 2:
                return {
                    "gameID": gameID,
                    "gameName": game_name[0],
                    "player1Name": player_names[0][0],
                    "player2Name": player_names[1][0]
                }
            else:
                return None  # Game should have exactly two players
        else:
            return None  # Game not found

    def setGame(self, gameName, player1Name, player2Name):
        cursor = self.conn.cursor()
        try:
            # Insert gamename and ID into Game Table
            cursor.execute('''
                INSERT INTO Game (GAMENAME) VALUES (?)
            ''', (gameName,))

            gameID = self.getGameID(gameName)

            # Insert player1Name 
            cursor.execute('''
                INSERT INTO Player (PLAYERNAME, GAMEID) VALUES (?, ?);
            ''', (player1Name, gameID,))
            player1ID = self.getPlayerID(player1Name)

            # Insert player2Name 
            cursor.execute('''
                INSERT INTO Player (PLAYERNAME, GAMEID) VALUES (?, ?);
            ''', (player2Name, gameID,))
            player2ID = self.getPlayerID(player2Name)

            # Commit the changes 
            self.conn.commit()

        except sqlite3.Error as e:
            print(f"Error setting up the game: {e}")
            raise

        finally:
            cursor.close()

    def getPlayerID(self,playerName):
        cursor = self.conn.cursor()

        cursor.execute("SELECT PLAYERID FROM Player WHERE PLAYERNAME = ?", (playerName,))
        playerID = cursor.fetchone()

        cursor.close()
        self.conn.commit()

        return playerID[0] if playerID else None
    
    def newShot(self, playerID, gameID):
        cursor = self.conn.cursor()

        try:
            # Add a new entry to the Shot table
            cursor.execute("INSERT INTO Shot (PLAYERID, GAMEID) VALUES (?, ?)", (playerID, gameID))

            # Get the autoincremented SHOTID value
            shotID = cursor.lastrowid

            return shotID

        except Exception as e:
            print(f"Error creating new shot: {e}")

        finally:
            cursor.close()
            self.conn.commit()

        return None
    

    def getGameID(self, gameName):
        try:
            # Implement logic to retrieve the gameID based on the gameName from your database
            query = "SELECT GameID FROM Game WHERE GameName = ?"
            result = self.conn.execute(query, (gameName,)).fetchone()

            if result:
                return result[0]  # Assuming the first column is the gameID in the result
            else:
                print(f"Game '{gameName}' not found.")
                return None
        except Exception as e:
            print(f"Error retrieving GameID for '{gameName}': {str(e)}")
            return None



class Game:
    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):
        database = Database()
        self.database = database
        database.createDB()
        if gameID is not None:
            # Constructor version (i) with gameID provided
            if any(arg is not None for arg in [gameName, player1Name, player2Name]):
                raise TypeError("Invalid combination of arguments for constructor version (i)")

            # Fetch details from the Database using the helper method
            game_data = database.getGame(gameID)
            if game_data is None:
                raise ValueError("Game with specified gameID not found in the database")

            self.gameID = game_data["gameID"]
            self.gameName = game_data["gameName"]
            self.player1Name = game_data["player1Name"]
            self.player2Name = game_data["player2Name"]
            

        else:
            # Constructor version (ii) with gameID=None
            if not all(arg is not None and isinstance(arg, str) for arg in [gameName, player1Name, player2Name]):
                raise TypeError("Invalid combination of arguments for constructor version (ii)")

            # Add new rows to Game and Player tables using the helper method
            database.setGame(gameName, player1Name, player2Name)

            # Fetch newly added gameID from the Database
            self.gameID = database.getLastGameID()
            self.gameName = gameName
            self.player1Name = player1Name
            self.player2Name = player2Name
            




    def shoot(self, gameName, playerName, table, xvel, yvel):
        # Get the playerID from the playerName using the Database class helper method
        
        playerID = self.database.getPlayerID(playerName)
        
        if playerID is None:
            print(f"Player '{playerName}' not found.")
            return None

        # Create a new entry in the Shot table and get the shotID

        gameID = self.database.getGameID(gameName)

        if gameID is None:
            print(f"Game '{gameName}' not found.")
            return None
        

        shotID = self.database.newShot(playerID, gameID)

        if shotID is None:
            print("Error creating new shot.")
            return None
        

        # Get the cue ball from the table using the Table class helper method
        cue_ball = table.cueBall()
        
        if cue_ball is None:
            print("Cue ball not found on the table.")
            return None

        # Store the current position of the cue ball
        xpos = cue_ball.obj.still_ball.pos.x
        ypos = cue_ball.obj.still_ball.pos.y

        # Set the type attribute of the cue ball to PHYLIB_ROLLING_BALL
        cue_ball.type = phylib.PHYLIB_ROLLING_BALL

        # Set the attributes of the cue ball
        cue_ball.obj.rolling_ball.pos.x = xpos
        cue_ball.obj.rolling_ball.pos.y = ypos
        cue_ball.obj.rolling_ball.vel.x = xvel
        cue_ball.obj.rolling_ball.vel.y = yvel
        speed_rb = 0
        # Recalculate the acceleration parameters
        speed_rb = math.sqrt(xvel ** 2 + yvel ** 2)

        # Compute acceleration with drag
        if speed_rb > VEL_EPSILON:
            accx = (-xvel/ speed_rb) * DRAG
            accy = (-yvel / speed_rb) * DRAG
        else:
            accx = 0.0
            accy = 0.0
            
        cue_ball.obj.rolling_ball.acc.x = accx
        cue_ball.obj.rolling_ball.acc.y = accy


        
        
        # Set the number of the cue ball to 0
        cue_ball.obj.rolling_ball.number = 0

        
        

        # print(table)
        while table is not None:
            # Call the segment method to simulate physics for the next time step
            tt = Table.deepcopy_table(table)
            segment_start_time = table.time
            # print("Before segment call - table:", table)
            table = table.segment()

            

            if table is None:
                break 
            # Calculate the length of the segment in seconds
            segment_length = round((table.time - segment_start_time) / FRAME_RATE)

            # Display the start and end times for the current segment
            # print(f"Segment Start Time: {segment_start_time}, Segment End Time: {table.time}")

            # Loop over the integers representing frames
            for frame_number in range(segment_length):
                # Calculate the time for the current frame
                current_frame_time = segment_start_time + (frame_number * FRAME_RATE)

                # Create a new Table object for the next frame
                frame_table = Table()

                # Iterate over all objects in the original table
                for obj in tt:  # Use the initial_table for iteration
                    if isinstance(obj, RollingBall):
                        # Create a new RollingBall with the same attributes
                        new_ball = RollingBall(
                            obj.obj.rolling_ball.number,
                            Coordinate(obj.obj.rolling_ball.pos.x, obj.obj.rolling_ball.pos.y),
                            Coordinate(obj.obj.rolling_ball.vel.x, obj.obj.rolling_ball.vel.y),
                            Coordinate(obj.obj.rolling_ball.acc.x, obj.obj.rolling_ball.acc.y)
                        )
                        # Call phylib_roll to compute the new position
                        phylib.phylib_roll(new_ball, obj, frame_number* FRAME_RATE)
                        # Add the new ball to the frame table
                        frame_table += new_ball

                    elif isinstance(obj, StillBall):
                        # Create a new StillBall with the same attributes
                        new_ball = StillBall(
                            obj.obj.still_ball.number,
                            Coordinate(obj.obj.still_ball.pos.x, obj.obj.still_ball.pos.y)
                        )
                        # Add the new ball to the frame table
                        frame_table += new_ball

                # Set the time of the frame table to the current frame time
                frame_table.time = current_frame_time

                # Save the frame table to the database using writeTable
                table_id = self.database.writeTable(frame_table)

                # Record the table in the TableShot table
                self.database.conn.execute(
                    "INSERT INTO TableShot (SHOTID, TABLEID) VALUES (?, ?)",
                    (shotID, table_id)
                )
               
            # Update the segment start time for the next iteration
            segment_start_time = table.time
            table_id = self.database.writeTable(table)
            self.database.conn.execute(
                "INSERT INTO TableShot (SHOTID, TABLEID) VALUES (?, ?)",
                (shotID, table_id))


        self.database.close()

        # Return the shotID
        return shotID
    