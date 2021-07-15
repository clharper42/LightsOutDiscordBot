from discord.ext import commands
import discord
import random
from PIL import Image
import os
from discord_slash import SlashCommand

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.remove_command('help')

slash = SlashCommand(bot, sync_commands=True)

#https://discord-py-slash-command.readthedocs.io/en/latest/quickstart.html

class Circle:
    def __init__(self,fill,empty):
        self.state = False #off
        self._neighbors = []
        self.fill = fill
        self.empty = empty
    @property
    def neighbors(self):
        return self._neighbors
    @property
    def image(self):
        if self.state:
            return self.fill
        else:
            return self.empty 
    def addNeighbors(self,cir):
        self._neighbors.append(cir)
        
    def changeState(self):
        if self.state:
            self.state = False
        else:
            self.state = True
    def changeStateNeightbors(self):
        self.changeState()
        for neigh in self._neighbors:
            neigh.changeState()

#keep track of clicks
goalclicks = 0
totalclicks = 0

#make matrix
allcircles = []
grid_image = Image.new("RGB", (500, 500))
fill_image = Image.open("fill.png")
empty_image = Image.open("empty.png")
#board is 5 by 5
for i in range(26):
    allcircles.append(Circle(fill_image,empty_image))
matrix = []
numinmatrix = 0
innerrow = [] # 5 in row, 5 by 5
for i in range(len(allcircles)):
    if i - 5 >= 0: #top
        allcircles[i].addNeighbors(allcircles[i-5])
    
    if i - 1 >= 0 and (i % 5 != 0): #left
        allcircles[i].addNeighbors(allcircles[i-1])
        
    if i + 1 < len(allcircles) and i != 4 and i != 9 and i != 14 and i != 19: #right
        allcircles[i].addNeighbors(allcircles[i+1])
        
    if i + 5 < len(allcircles): #bottom
        allcircles[i].addNeighbors(allcircles[i+5])
        
    if numinmatrix != 4:
        innerrow.append(allcircles[i])
        numinmatrix += 1
    else:
        innerrow.append(allcircles[i])
        matrix.append(innerrow)
        numinmatrix = 0
        innerrow = []

@slash.slash(name="setboard",
             description="setup/reset board",
             guild_ids = [*Channel IDs Here*])
async def setboard(ctx):
  numclicks = random.randint(5,13)
  global goalclicks
  global totalclicks
  goalclicks = numclicks
  totalclicks = 0
  ranindexs = []
  lastnum = -1
  for i in range(numclicks):
      num = -1
      while True:
          num = random.randint(0,24)
          if num != lastnum:
              lastnum = num
              break
      ranindexs.append(num)
  for index in ranindexs:
    allcircles[index].changeStateNeightbors()
  await displayboard(ctx,True)
  

async def displayboard(channel,calboard):
  if calboard:
    for i in range(len(matrix)):
      for l in range(len(matrix[i])):
          grid_image.paste(matrix[i][l].image, (l*100,i*100))
  grid_image.save("grid_image.png")
  file = discord.File("grid_image.png")
  global goalclicks
  global totalclicks
  embed=discord.Embed(title="Clicks", color=0x1e00ff)
  embed.add_field(name="Goal:", value=str(goalclicks))
  embed.add_field(name="Total:", value=str(totalclicks))
  await channel.send(embed=embed,file=file)

@slash.slash(name="getboard",
             description="get current board",
             guild_ids = [841686118609190942])
async def getboard(ctx):
  await displayboard(ctx,False)
  


@slash.slash(name="pushbutton",
             description="given coordinates turn on/off button and neighbors",
             guild_ids = [*Channel IDs Here*])
async def pushbutton(ctx,row,col):
  try:
    rowind = int(row)
    colind = int(col)
    matrix[rowind-1][colind-1].changeStateNeightbors()
    global totalclicks
    totalclicks += 1
    await displayboard(ctx,True)
  except:
    await ctx.send("bad input")
  


bot.run(os.getenv('TOKEN'))
