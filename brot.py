import discord
import yaml
import brut


###Load config
try:
    with open('conf.yaml') as file:
        conf = yaml.safe_load(file)
except Exception as e:
    print(e)
    exit()

try:
    token = conf['credentials']['token']
except Exception as e:
    print(e)
    exit()

bruv_list = [
'bruv',
'brut',
'brunt',
'bruck',
'bruc',
'bruk',
'brub',
'brug',
'bruh',
'bruy',
'bruf',
'bruph',
'brud',
'brun',
'brum',
'brup'
]




client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return


    #Brut Scores

    if  message.content.lower() == '!globalbrutscore':
        await brut.GetTopBrutHighScores(message)
        return
    
    if message.content.lower() == '!channelbrutscore':
        await brut.GetChannelBrutHighScores(message)
        return
    
    if message.content.lower() == '!serverbrutscore':
        await brut.GetServerBrutHighScores(message)
        return
    
    if message.content.lower() == '!mybrutscore':
        await brut.GetUserBrutScore(message)
        return

    #Check for brutlist match
    for bruv in bruv_list:
        if bruv in message.content.lower():
            #check for a close match, maybe some punctuation at the end
            if len(message.content) <= (len(bruv) +4 ):
                matched_string = bruv
            else: 
                matched_string = 'miss'
            #Send message and log
            await brut.Brut(message, matched_string)
            return




client.run(token)