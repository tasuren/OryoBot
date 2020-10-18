# -*- coding: utf-8 -*-
# Oryo Bot
# Code by tasuren

from discord.ext import commands
from discord.ext import tasks

import discord


from datetime import timedelta

import psutil
import rtutil
import json
import os


mode = 0


print(f'-Now loading...\n|MODE:{mode}')


# データ読み込み
with open("data.json",mode="r") as f:
    data = json.load(f)

color = [0x7d5ad1,0xff2931,0x93c1c0]

# Jishaku
team_id = [756801990889046017,634763612535390209]
class MyBot(commands.Bot):
    async def is_owner(self, user: discord.User):
        if user.id in team_id:
            return True
        return await super().is_owner(user)


pr = data["data"]["pr"][mode]


# 初期設定
intents = discord.Intents.all()
bot = MyBot(command_prefix=pr,intents=intents)
bot.load_extension("jishaku")
bot.remove_command("help")



# 行ゲット
def get_line(content,line):
    return content.splitlines()[line-1]


# エラーメッセージ用
def error(smode,title,desc,footer=None,ccolor=color[1]):
    if smode == "error":
        emoji = "<:error:765533830299123753>"
    elif smode == "none":
        emoji = "<:none:765535237702549514>"
        ccolor = color[2]
    embed = discord.Embed(
        title=f"{emoji}  {title}",
        description=desc,
        color=ccolor
    )
    if footer is not None:
        embed.set_footer(text=footer)
    return embed


# エラー時
@bot.event
async def on_command_error(ctx,error):
  try:
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send(embed=error("none","Unknown","そのコマンドはありません。"))
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send(embed=error("none","Unknown","引数がたりません。"))
    else:
        await ctx.send(embed=error("error","内部エラー","すみませんが、OryoBot内でエラーが発生しました。\nもしこのエラーが治らない場合は[サポートサーバー](https://discord.gg/ZffyWb8)で報告してください。"))
  except:
    print(f"エラーが発生：{error}")
    await ctx.send(embed=error("error","エラー","すみませんが、OryoBot内でエラーが発生しました。\nコマンド、引数をしっかりと入力しているかご確認ください。\nもしこのエラーが治らない場合は[サポートサーバー](https://discord.gg/ZffyWb8)で報告してください。"))


# 起動時
@bot.event
async def on_ready():
    activity = discord.Activity(
        name=f"{pr}help | {len(bot.guilds)}server", type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)
    print("|Conected\n|Started bot")


# tasuren
@bot.command()
async def tasuren(ctx):
    await ctx.send("BOT開発者が仕込んだ隠しメッセージ!")


# 招待リンク
@bot.command()
async def invite(ctx):
    await ctx.send(
        embed=discord.Embed(
            title="このBOTの招待リンク",
            description=f'{data["data"]["link"][mode]}'
            )
        )


# HELP コマンド
@bot.command()
async def help(ctx,arg=None):
    print(f"-Help\n|<Author>{ctx.author}")
    if arg is None:
        # ノーマル
        embed = discord.Embed(
            title="Oryo Bot HELP",
            description=f"**`{pr}help 見たい機能の名前`**  で機能の詳細を見ることができます。",
            color=color[0])
        with open("help/1.txt","r",encoding="utf-8_sig") as f:
            cont = f.read()
        name = get_line(cont,1)
        value = cont.replace(get_line(cont,1),"",1)
        embed.add_field(
            name=name,
            value=value)
        await ctx.send(embed=embed)
    else:
        # 機能詳細
        if (os.path.exists(f"help/{arg}.txt")):
            with open(f"help/{arg}.txt",encoding="utf-8_sig") as f:
                cont = f.read()
            name = get_line(cont,1)
            value = cont.replace(get_line(cont,1),"",1)
            embed = discord.Embed(
                title=name,
                description=value,
                color=color[0])
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=error("none","Unknown",f"`{arg}`の名前の詳細が見つかりませんでした。"))


# ユーザー取得
@bot.command()
async def user(ctx,uid):
    print(f"-user\n|<Author>{ctx.author}")
    try:
        user = await bot.fetch_user(int(uid))
    except:
        user = None
    if user is not None:
        s = ""
        if user.bot:
            s = "`BOT`"
        embed = discord.Embed(title=f"{user} {s}",color=color[0])
        time = user.created_at+timedelta(hours=9)
        embed.add_field(name="アイコンURL",value=user.avatar_url_as(format="png"),inline=False)
        embed.add_field(name="タグ",value=user.discriminator)
        embed.add_field(name="ID",value=user.id)
        embed.set_footer(text=f"Discord参加日：{time.strftime('%Y-%m-%d')}")
        embed.set_thumbnail(url=user.avatar_url_as(format="png"))
        await ctx.send(embed=embed)
    else:
        await ctx.send(embed=error("none","Unknown",f"`{uid}`のIDのユーザーが見つかりませんでした。"))


# GBAN 追加、削除コマンド
@bot.command()
async def gban(ctx,mode,uid,reason):
    if mode == "add":
        if ctx.author.id in [756801990889046017,756801990889046017,634763612535390209]:
            try:
                user = await bot.fetch_user(int(uid))
            except:
                user = None
            if user is not None:
                if data["gban"].get(uid) is None:
                    async with ctx.typing():
                        pic = ""
                        if ctx.message.attachments != []:
                            for at in ctx.message.attachments:
                                pic = pic + f"[証拠画像]({at.url})" + "\n"
                        if pic != "":
                            reason = reason + "\n" + pic
                        data["gban"][uid] = reason
                        await rtutil.jwrite("data.json",data)
                        embed = discord.Embed(
                            title=f"GBANリストにユーザーが追加されました。",
                            description=f"追加ユーザー：{user} ({user.id})",
                            color=color[1])
                        embed.add_field(name="理由",value=data["gban"][uid])
                        embed.set_thumbnail(url=user.avatar_url_as(format="png"))
                        for tg in bot.guilds:
                            if user in tg.members:
                                await tg.ban(user,reason=f"<ORYO-GBAN>{data['gban'][uid]}")
                            tc = [i for i in tg.text_channels if "oryo-gban" in i.name]
                            if tc:
                                await tc[0].send(embed=embed)
                    await ctx.send(f"`{uid}`のユーザーをGBANに追加しました。")
                else:
                    await ctx.send(embed=error("error","Unknown",f"`{uid}`のIDのユーザーは既に追加されています。"))
            else:
                await ctx.send(embed=error("none","Unknown",f"`{uid}`のIDのユーザーが見つかりませんでした。"))
        else:
            try:
                user = await bot.fetch_user(int(uid))
            except:
                user = None
            if user is not None:
                pic = ""
                if ctx.message.attachments != []:
                    for at in ctx.message.attachments:
                        pic = pic + f"[画像リンク]({at.url})" + "\n"
                channel = bot.get_channel(764655684041965609)
                if channel is None:
                    channel = bot.get_channel(762149088400900139)
                embed = discord.Embed(
                    title=f"GBANの申請が来ました。",
                    color=color[1])
                embed.add_field(
                    name="実行者",
                    value=f"{ctx.author}\n({ctx.author.id}")
                embed.add_field(
                    name="対象者",
                    value=f"{user}\n({user.id})")
                if pic != "":
                    embed.add_field(
                        name="証拠画像URL",
                        value=pic)
                embed.add_field(
                    name="理由",
                    value=reason,
                    inline=True)
                await channel.send(embed=embed)
                await ctx.send("GBANを申請しました。")
            else:
                await ctx.send(embed=error("none","Unknown",f"`{uid}`のIDのユーザーが見つかりませんでした。"))
    elif mode == "rm":
        if ctx.author.id in [756801990889046017,756801990889046017,634763612535390209]:
            if data["gban"].get(uid) is not None:
                del data["gban"][uid]
                await rtutil.jwrite("data.json",data)
                await ctx.send(f"`{uid}`のユーザーをGBANから削除しました。")
            else:
                await ctx.send(embed=error("none","Unknown",f"`{uid}`のユーザーはまだ追加されていません。"))
        else:
            await ctx.send(embed=error("error","権限エラー",f"GBAN削除を実行できるのはBotオーナー,開発者だけです。"))


# メンバーが入った時
@bot.event
async def on_member_join(member):
    # GBANリストにいるか
    channel = None
    for channel in member.guild.text_channels:
        if "oryo-gban" in channel.name:
            break
    if data["gban"].get(str(member.id)) is not None:
        await member.guild.ban(member,reason=f"<ORYO-GBAN>{data['gban'][str(member.id)]}")
        embed = discord.Embed(
            title=f"GBAN実行のお知らせ",
            description=f"{member}をGBANリストに登録されているためBANしました。",
            color=color[1])
        embed.add_field(name="理由",value=data["gban"][str(member.id)])
        embed.set_thumbnail(url=member.avatar_url_as(format="png"))
        if channel:
            await channel.send(embed=embed)


# デバッグ用
@bot.group()
async def debug(ctx):
    if not ctx.author.id in team_id:
        await ctx.send(embed=error("none","権限エラー","このコマンドはOryoBotの開発者のみ有効です。"))
        return
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="OryoBot",
            description="Running on Glitch (Linux)",
            color=color[0]
        )
        if mode == 1:
            mode_s = "Not Canary"
        elif mode == 0:
            mode_s = "Canary"
        else:
            mode_s = "Unknown"
        embed.add_field(name="MODE",value=mode_s)
        embed.add_field(name="Memory",value=f"{psutil.virtual_memory().percent}%")
        embed.add_field(name="CPU",value=f"{psutil.cpu_percent(interval=1)}%")
        embed.add_field(name="Disk",value=f"{psutil.disk_usage('/').percent}%")
        await ctx.send(embed=embed)


@debug.command()
async def reboot(ctx):
    if not ctx.author.id in team_id:
        await ctx.send(embed=error("none","権限エラー","このコマンドはOryoBotの開発者のみ有効です。"))
        return
    activity = discord.Activity(
        name="再起動中。。。", type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)
    await ctx.send("再起動します。")
    await bot.logout()


# メッセージが来たとき
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    # BOTはreturn
    if message.author.bot:
        return

    return

    ### グローバルチャット ###
    # 1.tsuna-globalというのがチャンネルにあるか 2.あったらすべてのサーバーでtsuna-globalのチャンネルを探す
    # 3.ウェブフックがない場合作り送信する
    # tg - サーバー    tc - サーバーのチャンネル
    if "tsuna-global" in message.channel.name:
        print(f"-Global Chat\n|<Author>{message.author}\n|<Guild> {message.guild.name}")
        for tg in bot.guilds:
            for tc in tg.text_channels:
                if "tsuna-global" in tc.name and tc.id != message.channel.id:
                    # 画像あったら画像送信
                    pic = ""
                    if message.attachments != []:
                        for at in message.attachments:
                            pic = pic + at.url + "\n"
                    # ウェブフックを探す
                    ch_webhooks = await tc.webhooks()
                    webhook = discord.utils.get(ch_webhooks, name="tuna-global-webhook")
                    # ウェブフックがなかったら作る
                    if webhook is None:
                        webhook = await tc.create_webhook(name="tuna-global-webhook")
                    # ウェブフックを送信
                    await webhook.send(
                        content=f"{message.content}\n{pic}",
                        username=f"{message.author} ({message.author.id}) From:{message.guild.name}",
                        avatar_url=message.author.avatar_url_as(format="png"))


print("|Conecting...")

if mode == 1:
    bot.run("")
else:
    bot.run("")
