import discord
import sqlite3


async def Brut(message,matched_string):
    #Message back if it's mostly a loney brut
    if matched_string != 'miss':
        await message.channel.send(f'{matched_string}\n{matched_string}\n{matched_string}')
    
    #Log brut regardless
    await LogBrut(message)

def GetSqlObj():
    try:
        con = sqlite3.connect('brot.db')
        cur = con.cursor()
    except Exception as e:
        print(e)
        return
    return con,cur

async def LogBrut(message):    
    
    con,cur = GetSqlObj()

    user_id = message.author.id
    user_name = message.author.name.replace('\'','')
    channel_id = message.channel.id
    channel_name = message.channel.name.replace('\'','')
    guild_id = message.guild.id
    guild_name = message.guild.name.replace('\'','')


    ##############################
    #Check if user exists already#
    ##############################
    user_score_query = f'''
    Select
    brutScore
    FROM Brut

    Where
    UserID = '{user_id}' and
    ChannelID = '{channel_id}' and
    GuildID = '{guild_id}'
    '''

    current_score = cur.execute(user_score_query).fetchone()
    if current_score is None:
        create_user_statment = f'''
        Insert Into Brut
        (UserID, UserName, ChannelID, ChannelName,GuildID,GuildName,brutScore)
        Values
        ('{user_id}','{user_name}','{channel_id}','{channel_name}','{guild_id}','{guild_name}',1)        
        ''' 

        try:
            cur.execute(create_user_statment)
            con.commit()
            print(f'Created user {user_name}:{user_id}')
        except Exception as e:
            print(e)
    else:

    #################
    #Update Existing#
    #################
    
        new_score = current_score[0]+1
        
        update_score_statment = f'''
        Update brut
        Set  brutScore = {new_score}

        Where
        UserID = '{user_id}' and
        ChannelID = '{channel_id}' and
        GuildID = '{guild_id}'
        '''
        cur.execute(update_score_statment)
        con.commit()






async def GetChannelBrutHighScores(message):
    con, cur = GetSqlObj()

    sql_query = f'''
    Select
    brutScore,
    UserName    
    From brut

    where ChannelID = '{message.channel.id}'

    Order by brutScore Desc

    Limit 10        
    '''

    scores = cur.execute(sql_query).fetchall()    

    response_string = f'```brut Leaderboard for channel {message.channel.name}\n'
    formatted_table = FormatTable(('Score','UserName'),scores)
    response_string = response_string + formatted_table + '```'

    await message.channel.send(response_string)
    
async def GetUserBrutScore(message):

    con,cur = GetSqlObj()

    sql_query_channel = f'''
    Select
    'CurrentChannel' as responsetype,
    brutScore
    from brut

    Where
    UserID = '{message.author.id}' and
    ChannelID = '{message.channel.id}'
    '''
    
    sql_query_server = f'''
    Select
    'CurrentServer' as responsetype,
    Sum(brutScore)
    from brut

    Where
    UserId = '{message.author.id}'and
    GuildID = '{message.guild.id}'
    '''

    sql_query_total = f'''
    Select
    'Total' as responsetype,
    Sum(brutScore)
    From brut

    Where
    UserId = '{message.author.id}'
    '''

    cur_channel_score = cur.execute(sql_query_channel).fetchone()    
    cur_server_score = cur.execute(sql_query_server).fetchone()
    cur_total_score = cur.execute(sql_query_total).fetchone()

    scores= ((cur_channel_score),(cur_server_score),(cur_total_score))


    response_string = f'```{message.author.name} brut Stats\n'+ FormatTable(('Type','Score'),scores) + '```'
    #formatted_table = FormatTable(('Type','Score'),scores)
    await message.channel.send(response_string)

async def GetTopBrutHighScores(message):
    con, cur = GetSqlObj()

    sql_query = f'''
    Select
    UserName,
    Sum(BrutScore)
    From brut

    Group By UserName
    Order By Sum(BrutScore) Desc
    Limit 10
    '''
       
    scores = cur.execute(sql_query).fetchall()
    response_string = f'```Global brut Leaderboard\n'+ FormatTable(('Type','Score'),scores) + '```'
    await message.channel.send(response_string)

async def GetServerBrutHighScores(message):
    con,cur = GetSqlObj()

    sql_query = f'''
    Select
    UserName,
    Sum(brutScore)
    From brut

    Where
    GuildID = '{message.guild.id}'
    
    Group By UserName
    Order By Sum(brutScore) Desc
    Limit 10
    '''

    scores = cur.execute(sql_query).fetchall()
    response_string = f'```{message.guild.name} brut Leaderboard\n'+ FormatTable(('Type','Score'),scores) + '```'
    await message.channel.send(response_string)


def FormatTable(headers, scores):
    #I built this because when I tried out of the box libraries I had formatting issues.  After I wrote this I realized Discord is not monospace.
    #Adding ``` at the front and back of the message signifies a "block" message which is monospace

    col_width = 20

    #Build the header string    
    header_string = ''
    for header in headers:
        #Conctact the new header onto the string
        header_string = header_string + header
        #Add required whitespace
        i=0
        while i < col_width - len(header):
            header_string = header_string + ' '
            i += 1
    #Add new line
    header_string = header_string + '\n'


    #Build score string
    score_string = ''

    for score in scores:
        x = 0
        while x < len(headers):
            score_string = score_string + str(score[x])
            #Add whitespace
            i=0
            while i < col_width - len(str(score[x])):
                score_string = score_string + ' '
                i += 1
            x += 1
        score_string = score_string + '\n'
    message_string = header_string+score_string
    return message_string
