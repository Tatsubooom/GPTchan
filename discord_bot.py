import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
import gpt_api
import voicevox_api
from mysql.connector import Error, pooling

#トークンの読み込み
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

#アクセス許可
intents = discord.Intents.default()
intents.message_content = True #テキストチャット
intents.voice_states = True #ボイスチャット
intents.members = True #メンバー変更

client = commands.Bot(command_prefix='!',intents=intents)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
voiceclient = None

#DBコネクションプールの作成
try:
    db_pool = pooling.MySQLConnectionPool(
        host = os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        pool_size = 5,
        pool_reset_session= True
    )
    print("DBプール作成完了")
except Error as e:
    print(f"DBプール作成エラー{e}")

#DB,テーブルの作成
db_conn = db_pool.get_connection()
try:   
    if db_conn.is_connected():
        db_cursor = db_conn.cursor()
        try:
            db_cursor.execute("CREATE DATABASE IF NOT EXISTS DCdatabase")
            db_cursor.execute("USE DCdatabase")
            create_table_query = """
                CREATE TABLE IF NOT EXISTS chat_logs(
                    user_id BIGINT NOT NULL,
                    user_name VARCHAR(255) NOT NULL,
                    channel_id BIGINT NOT NULL,
                    message TEXT,
                    reply TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            db_cursor.execute(create_table_query)
            print("DBテーブル作成完了")

        except Error as e:
            print(f"DB/テーブル作成エラー{e}")
        finally:
            db_cursor.close() 
finally:
    db_conn.close()

#起動処理
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


#会話生成
async def conversation(message):
    if message.content == None or len(message.content) <= 1:
        await message.channel.send("よんだ？")
        return
        
    async with message.channel.typing():
        current_conv = []
        personal_conv_text = ""
        current_conv,personal_conv_text = await get_conver(message.author.id,message.channel.id)
        current_conv.append({
                        "role" : "user",
                        "content" : f"[{message.author.display_name}] : {message.content}"
                    })

        output_text = gpt_api.createTextResponse(current_conv,personal_conv_text)
        if output_text:
            if voiceclient != None and voiceclient.is_connected():
                voicevox_api.createvoice(output_text)
                voiceclient.play(discord.FFmpegPCMAudio("output.wav"))

            await message.channel.send(output_text)
            await save_chat_log(message,output_text)

#会話ログDB受け取り
async def get_conver(user_id, channel_id):
    current_conv = []
    personal_conv_text = "【このユーザーに関する過去の記憶・情報】/n"
    conn = db_pool.get_connection()
    try:
        if conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            try:
                get_conv_query = """
                    SELECT user_id, user_name, message, reply
                    FROM DCdatabase.chat_logs 
                    WHERE channel_id = %s
                    ORDER BY created_at DESC
                    LIMIT 5
                """
                cursor.execute(get_conv_query,(channel_id,))
                rows = cursor.fetchall()
                rows.reverse()

                for row in rows:
                    name = row["user_name"]
                    text = row["message"]
                    rep = row["reply"]
                    current_conv.append({
                        "role" : "user",
                        "content" : f"[{name}] : {text}"
                    })
                    if rep:
                        current_conv.append({
                            "role" : "assistant",
                            "content" :rep
                        })
            
                get_personal_query = """
                    SELECT message, reply 
                    FROM DCdatabase.chat_logs 
                    WHERE user_id = %s AND reply IS NOT NULL
                    ORDER BY created_at DESC
                    LIMIT 2
                """
                cursor.execute(get_personal_query,(user_id,))
                rows = cursor.fetchall()
                rows.reverse()

                for row in rows:
                    text = row["message"]
                    rep = row["reply"]
                    personal_conv_text += f"- user: {text}\n- assistant: {rep}\n"

            except Error as e:
                print(f"ログ取得エラー: {e}")
            finally:
                cursor.close()
    finally:
        conn.close()

    return current_conv,personal_conv_text

async def save_chat_log(message,reply = None):
    conn = db_pool.get_connection()
    try:
        if conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            try:
                save_chat_query = """
                    INSERT INTO DCdatabase.chat_logs 
                    (user_id, user_name, channel_id, message, reply)
                    VALUES(%s,%s,%s,%s,%s)
                """
                cursor.execute(save_chat_query,(message.author.id,message.author.display_name,message.channel.id,message.content,reply))
                conn.commit()
            except Error as e:
                print(f"ログ取得エラー: {e}")
            finally:
                cursor.close()
    finally:
        conn.close()

#メンションでの会話
@client.event
async def on_message(message):
    if client.user in message.mentions and not message.mention_everyone:
        message.content = message.content.replace(f'<@{client.user.id}>','')
        await conversation(message)
    elif message.author != client.user:
        await save_chat_log(message)
    await client.process_commands(message)

#コマンドでの会話
@client.command()
async def talk(ctx):
    ctx.message.content = ctx.message.content.replace('!talk','')
    await conversation(ctx.message)

#ロール追加
@client.command()
async def roll(ctx):
    roll = ctx.message.content.replace('!roll','')
    roll = roll.replace('\n','').strip()

    if len(roll) > 30:
        await ctx.channel.send("ながすぎておぼえられないよ！")
        return
    
    if not roll:
        await ctx.channel.send("なにをおぼえてほしいの？")
        return

    file_path = 'SubRolls.txt'
    try:
        if os.path.exists(file_path):
            with open('SubRolls.txt', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                items = [s for s in content.split('\n') if s.strip()]
        else:
            items = []

        items.insert(0, roll)
        items = items[:10]

        with open(file_path,'w',encoding='utf-8') as f:
            f.write('\n'.join(items))    
    except Exception as e:
        await ctx.channel.send(f"えらーえらーえらー！: {e}")
        return

    await ctx.channel.send(roll + "！おぼえた！")

#ボイスチャンネル接続
@client.command()
async def vc(ctx):
    global voiceclient
    if ctx.author.voice == None:
        await ctx.channel.send("ボイスチャンネルにいないじゃん！")
        return
    
    voiceclient = await ctx.author.voice.channel.connect()
    await ctx.channel.send("きたよー")
    return

#ボイスチャンネル退出
@client.command()
async def leave(ctx):
    global voiceclient
    if voiceclient == None:
        await ctx.channel.send("ボイスチャンネルにはいないよー")
        return
    
    await voiceclient.disconnect()
    await ctx.channel.send("ばいばーい")
    voiceclient = None
    return

#ボイスチャンネルに誰もいなくなったら自動退出
@client.event
async def on_voice_state_update(member,before,after):
    global voiceclient
    if voiceclient == None: return
    if len(voiceclient.channel.members) <= 1:
        await voiceclient.disconnect()
        voiceclient = None

client.run(DISCORD_TOKEN,log_handler=handler)