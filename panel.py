# نویسنده : @sudohunter
from telethon.sync import events
from telethon import Button
import telethon,asyncio,traceback,sys,os,asyncio,jdatetime,datetime,flag
from db import Users,XM,Config,Apps,send_all,Codes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import (
    bot,
    admins,
    panel,
    pback,
    convert_size,
    number_format,
    cget
)
from xmdb import user as XMUser
from xmdb import online_ip, servers

async def SendAll():
    send = send_all.get_or_none()
    info = await bot.get_me()
    if send is not None:
        user = Users.select()
        if send.type == 'SendToAll':
            for i in user.limit(send.limit).offset(send.xsends):
                try:
                    if i.user_id != int(info.id):
                        print(f'sended to : {i.user_id}')
                        await bot.send_message(int(i.user_id),str(send.text))
                        send.active += 1
                except (telethon.errors.rpcerrorlist.UserIsBlockedError,telethon.errors.rpcerrorlist.InputUserDeactivatedError):
                    pass
        elif send.type == 'ForToAll':
            for i in user.limit(send.limit).offset(send.xsends):
                try:
                    if i.user_id != int(info.id):
                        print(f'forwarded to : {i.user_id}')
                        t = await bot.forward_messages(int(i.user_id), int(send.message_id), int(send.user))
                        send.active += 1
                except (telethon.errors.rpcerrorlist.UserIsBlockedError,telethon.errors.rpcerrorlist.InputUserDeactivatedError):
                    pass
        send.xsends += int(send.limit)
        send.save()
        xxx = Users.select().count()
        if int(send.xsends) >= int(xxx):
            zzz = send
            send.delete_instance()
            return await bot.send_message(int(send.user),f'پروسه با موفقیت به اتمام رسید ☑️\n\n● زمان اتمام : {jdatetime.datetime.now().strftime("%H:%M")}\nتعداد ارسال های موفق : {zzz.active}',buttons=panel)

def rep(val):
    if val == '0':
        return '❌'
    else:
        return '✅'

def setting():
    return [
        [Button.inline(str(rep(cget('card-status'))),'power-card-status'),Button.inline('کارت به کارت','power-card-status')],
        [Button.inline(str(rep(cget('tron-status'))),'power-tron-status'),Button.inline('پرداخت با ترون','power-tron-status')],
        [Button.inline(str(rep(cget('tether-status'))),'power-tether-status'),Button.inline('پرداخت با تتر','power-tether-status')],
        [Button.inline(str(rep(cget('sell'))),'power-sell'),Button.inline('فروش سرویس','power-sell')],
        [Button.inline(str(rep(cget('test'))),'power-test'),Button.inline('سرویس تست','power-test')],
        [Button.inline(str(cget('min_gig')),'set-min_gig'),Button.inline('حداقل حجم سرویس :','set-min_gig')],
        [Button.inline(str(cget('max_gig')),'set-max_gig'),Button.inline('حداکثر حجم سرویس :','set-max_gig')],
        [Button.inline(str(cget('max_days')),'set-max_days'),Button.inline('حداکثر زمان سرویس :','set-max_days')],
        [Button.inline(str(cget('max_user')),'set-max_user'),Button.inline('حداکثر اتصالات سرویس :','set-max_user')],
        [Button.inline(str(cget('tron-min')),'set-tron-min'),Button.inline('حداقل پرداخت ترون :','set-tron-min')],
        [Button.inline(str(cget('test_gig')),'set-test_gig'),Button.inline('حجم سرویس تست:','set-test_gig')],
        [Button.inline(f'{cget("test_day")} روز','set-test_day'),Button.inline('مدت سرویس تست:','set-test_day')],
        [Button.inline(str(cget('limit_test')),'set-limit_test'),Button.inline('لیمیت ایپی : ','set-limit_test')],
        [Button.inline('تنظیم ولت ترون','set-tron-wallet'),Button.inline('تنظیم ولت تتر','set-tether-wallet')],
        [Button.inline('تنظیم آیدی پشتیبانی','set-support-id')]
    ]

@bot.on(events.CallbackQuery(func=lambda e: e.is_private))
async def query(event):
    data = event.data.decode()
    if data == 'SendToAll':
        if event.sender_id not in admins:
            return
        if send_all.get_or_none() is not None:
            return await event.reply('**⚠️ : یک پروسه در حال اجرا دارید !\n❗️: جهت لغو کردن آن از /cancel استفاده کنید.**')
        try :
            async with bot.conversation(event.sender_id) as conv:
                await (await event.reply('.', buttons=Button.clear())).delete()
                sent = await conv.send_message('✏️ : با استفاده از این بخش می توانید یک پیام را به همه ی کاربران فعال ربات ارسال نمایید!\n\nپیام خود را #ارسال نمایید.', buttons=pback)
                message = await conv.get_response()
                if message.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                sent = await conv.send_message('✅ : لطفا تعداد کاربری که قصد دارید این پیام در هر 30 ثانیه برای آن ها ارسال شود را ارسال کنید.', buttons=pback)
                count = await conv.get_response()
                if count.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not count.raw_text.isnumeric():
                    sent = await conv.send_message(f'**⚠️ :  مقدار ارسالی فقط باید عدد باشد**', buttons=pback)
                    count = await conv.get_response()
                while int(count.raw_text) <= 99 or int(count.raw_text) >= 501:
                    sent = await conv.send_message('**⚠️ عدد وارد شده باید بیشتر از 100 و کمتر از 500 باشد !**',buttons=pback)
                    count = await conv.get_response()
                send_all.create(
                    text = message.text,
                    user = event.sender_id,
                    message_id = message.id,
                    limit = int(count.raw_text),
                    type = 'SendToAll',
                )
                proc = int(Users.select().count()) / int(count.raw_text)
                if proc >= 1:
                    await event.reply(f'✅ : پروسه ارسال پیام همگانی با موفقیت ارسال شد !\n\n⏰ زمان تقریبی اتمام پروسه : {round(proc)} دقیقه',buttons=panel)
                return await SendAll()
        except asyncio.exceptions.TimeoutError:
            await sent.delete()
            return await event.reply('فرصت به پایان رسید',buttons=panel)
        except:
            pass
    elif data == 'ForToAll':
        if event.sender_id not in admins:
            return
        if send_all.get_or_none() is not None:
            return await event.reply('**⚠️ : یک پروسه در حال اجرا دارید !\n❗️: جهت لغو کردن آن از /cancel استفاده کنید.**')
        try :
            async with bot.conversation(event.sender_id) as conv:
                await (await event.reply('.', buttons=Button.clear())).delete()
                sent = await conv.send_message('✏️ : با استفاده از این بخش می توانید یک پیام را به همه ی کاربران فعال ربات فوروارد نمایید!\n\nپیام خود را #فوروارد نمایید.', buttons=pback)
                message = await conv.get_response()
                if message.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                sent = await conv.send_message('✅ : لطفا تعداد کاربری که قصد دارید این پیام در هر 30 ثانیه برای آن ها ارسال شود را ارسال کنید.', buttons=pback)
                count = await conv.get_response()
                if count.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not count.raw_text.isnumeric():
                    sent = await conv.send_message(f'**⚠️ :  مقدار ارسالی فقط باید عدد باشد**', buttons=pback)
                    count = await conv.get_response()
                while int(count.raw_text) <= 99 or int(count.raw_text) >= 501:
                    sent = await conv.send_message('**⚠️ عدد وارد شده باید بیشتر از 100 و کمتر از 500 باشد !**',buttons=pback)
                    count = await conv.get_response()
                x = send_all.create(
                    user = event.sender_id,
                    message_id = message.id,
                    limit = int(count.raw_text),
                    type = 'ForToAll',
                )
                proc = int(Users.select().count()) / int(count.raw_text)
                if proc >= 1:
                    await event.reply(f'✅ : پروسه ارسال پیام همگانی با موفقیت ارسال شد !\n\n⏰ زمان تقریبی اتمام پروسه : {round(proc)} دقیقه',buttons=panel)
                return await SendAll()
        except asyncio.exceptions.TimeoutError:
            await sent.delete()
            return await event.reply('فرصت به پایان رسید',buttons=panel)
        except Exception as e:
            r  = traceback.format_exc()
            await event.reply(str(r))
    elif data == 'SendUser':
        try:
            async with bot.conversation(event.sender_id) as conv:
                await (await event.reply('.', buttons=Button.clear())).delete()
                sent = await conv.send_message('🆔 ایدی عددی کاربر مورد نظر را ارسال کنید', buttons=pback)
                userid = await conv.get_response()
                while not userid.raw_text.isnumeric():
                    sent = await conv.send_message('‼️ ایدی را به صورت عدد ارسال کنید', buttons=pback)
                    userid = await conv.get_response()
                if Users.get_or_none(Users.user_id == userid.raw_text) is None:
                    return await event.reply('❌ کاربری با این ایدی عددی عضو ربات نیست!', buttons=panel)
                sent = await conv.send_message('پیام خود را ارسال کنید', buttons=pback)
                pm = await conv.get_response()
                try:
                    await bot.send_message(int(userid.raw_text), pm)
                except Exception as e:
                    pass
                return await event.reply('پیام شما ارسال شد', buttons=panel)
        except asyncio.exceptions.TimeoutError:
            await sent.delete()
            return await event.reply('⚠️ فرصت به پایان رسید\n❗️در صورتی که نیاز به فرصت بیشتری دارید، مراحل را مجدد طی کنید', buttons=panel)
        except telethon.errors.common.AlreadyInConversationError as a:
            pass


@bot.on(events.NewMessage(from_users=admins,func=lambda e: e.is_private))
async def admin(event):
    text = event.text
    if text in ('/panel','panel','پنل','برگشت'):
        try:
            conv = bot.conversation(event.sender_id)
            await conv.cancel_all()
        except:
            pass
        return await event.reply('به پنل مدیریت خوش آمدید :',buttons=panel)
    elif text == '📊 آمار ربات':
        u = Users.select()
        pay = 0
        sercx = XM.select()
        for i in sercx:
            pay += int(i.price )
        service = sercx.count()
        t = datetime.datetime.now()
        connections = online_ip.select().where(online_ip.datetime > (int(t.timestamp()) - 60))
        allusers = XMUser.select()
        date = datetime.datetime.now()
        m = date - datetime.timedelta(days = 30)
        w = date - datetime.timedelta(days = 7)
        todayu = allusers.where(XMUser.reg_date.year == date.year).where(XMUser.reg_date.month == date.month).where(XMUser.reg_date.day == date.day)
        week = allusers.where(XMUser.reg_date >= w)
        month = allusers.where(XMUser.reg_date >= m)
        ser = servers.select()
        await event.reply(f'👤 تعداد کاربران : `{number_format(u.count())}`\n💰 کل فروش ربات : `{number_format(pay)}`\n🌐 تعداد سرویس های فروخته شده : `{number_format(service)}`\n\n📡 تعداد کاربران آنلاین : `{connections.count()}`\n🕹 تعداد کل یوزر های پنل : `{allusers.count()}`\n📈 تعداد یوزر های ربات : `{XM.select().count()}`\n\n⏰ کاربران اضافه شده امروز : `{todayu.count()}`\n📅 تعداد کاربران یک هفته گذشته : `{week.count()}`\n🕰 تعداد کاربران یک ماه گذشته : `{month.count()}`\n\n📌 تعداد سرور ها : `{ser.count()}`\n✅ تعداد سرور های فعال : `{ser.where(servers.heartbeat > date.timestamp() - 300).count()}`')
    elif text == '🔗 وضعیت اتصالات':
        t = datetime.datetime.now()
        connections = online_ip.select().where(online_ip.datetime > (int(t.timestamp()) - 60))
        lists = []
        if connections.exists():
            for i in connections:
                lists.append(i.serverid)
            txt = ''
            d = []
            for n in lists:
                if n not in d:
                    d.append(n)
                    ser = servers.get(servers.id == n)
                    txt += f'{flag.flag(ser.country)} {ser.name} : {lists.count(n)} کاربر\n'
            await event.reply(str(txt))
        else :
            await event.reply('هیچ اتصالی وجود ندارد!')

    elif text == '📩 ارسال پیام':
        key = [[Button.inline('پیام همگانی','SendToAll'),Button.inline('پیام به کاربر','SendUser'),Button.inline('فوروارد همگانی','ForToAll')]]
        return await event.reply('لطفا یک گزینه را انتخاب کنید :',buttons=key)
    elif text == '➕ افزودن راهنمای اتصال':
        try :
            async with bot.conversation(event.chat.id) as conv:
                sent = await conv.send_message('🏷 نام آموزش را ارسال کنید', buttons=pback)
                name = await conv.get_response()
                if name.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not name.text:
                    sent = await conv.send_message('یک متن ارسال کنید', buttons=pback)
                    name = await conv.get_response()
                sent = await conv.send_message('🌐 لینک اموزش را ارسال کنید', buttons=pback)
                link = await conv.get_response()
                if link.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not link.text:
                    sent = await conv.send_message('لینک ارسال کنید !', buttons=pback)
                    link = await conv.get_response()
            Apps.create(name = name.text,link = link.text)
            await event.reply('✅ آموزش مورد نظر با موفقیت اضافه شد!',buttons=panel)
        except asyncio.exceptions.TimeoutError:
            await sent.delete()
            return await event.reply('وقت تمام شد', buttons=panel)
        except telethon.errors.common.AlreadyInConversationError as a:
            pass
    elif text == '❌ حذف راهنمای اتصال':
        try :
            async with bot.conversation(event.chat.id) as conv:
                sent = await conv.send_message('👈 نام راهنمایی که قصد پاک کردن آن را دارید ارسال کنید ', buttons=pback)
                name = await conv.get_response()
                if name.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not name.text:
                    sent = await conv.send_message('یک متن ارسال کنید', buttons=pback)
                    name = await conv.get_response()
                info = Apps.get_or_none(Apps.name == name.text)
                if info is None:
                    return await event.reply('‼️ این راهنما وجود ندارد',buttons=panel)
                info.delete_instance()
            await event.reply('✅ راهنمای مورد نظر با موفقیت حذف شد!',buttons=panel)
        except asyncio.exceptions.TimeoutError:
            await sent.delete()
            return await event.reply('وقت تمام شد', buttons=panel)
        except telethon.errors.common.AlreadyInConversationError as a:
            pass
    elif text == '🎁 ساخت کد نمایندگی':
        try :
            async with bot.conversation(event.chat.id) as conv:
                sent = await conv.send_message('👈 کد را ارسال کنید', buttons=pback)
                code = await conv.get_response()
                if code.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not code.text:
                    sent = await conv.send_message('یک متن ارسال کنید', buttons=pback)
                    code = await conv.get_response()
                xx = Codes.get_or_none(Codes.code == code.text)
                if xx is not None:
                    return await event.reply('‼️ این کد وجود دارد',buttons=panel)
                sent = await conv.send_message('👈 آیدی عددی کاربر را ارسال کنید', buttons=pback)
                uid = await conv.get_response()
                if uid.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not uid.raw_text.isnumeric():
                    sent = await conv.send_message('‼️ مقدار خواسته شده را به صورت عدد ارسال کنید', buttons=pback)
                    uid = await conv.get_response()
                user = Users.get_or_none(Users.user_id == uid.raw_text)
                if user is None:
                    return await event.reply('کاربر در ربات عضو نیست !',buttons=panel)
                sent = await conv.send_message('👈 قیمت هر گیگ را ارسال کنید', buttons=pback)
                gigs = await conv.get_response()
                if gigs.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not gigs.raw_text.isnumeric():
                    sent = await conv.send_message('‼️ مقدار خواسته شده را به صورت عدد ارسال کنید', buttons=pback)
                    gigs = await conv.get_response()
                sent = await conv.send_message('👈 قیمت هر اتصال اضافه رو ارسال کنید', buttons=pback)
                puser = await conv.get_response()
                if puser.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not puser.raw_text.isnumeric():
                    sent = await conv.send_message('‼️ مقدار خواسته شده را به صورت عدد ارسال کنید', buttons=pback)
                    puser = await conv.get_response()
                sent = await conv.send_message('👈 قیمت هر روز اضافه را ارسال کنید', buttons=pback)
                days = await conv.get_response()
                if days.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not days.raw_text.isnumeric():
                    sent = await conv.send_message('‼️ مقدار خواسته شده را به صورت عدد ارسال کنید', buttons=pback)
                    days = await conv.get_response()
            Codes.create(
                xuser = uid.raw_text,
                code = code.text,
                puser = puser.raw_text,
                days = days.raw_text,
                gigs = gigs.raw_text
            )
            await event.reply('✅ کد مورد نظر با موفقیت ایجاد شد!',buttons=panel)
        except asyncio.exceptions.TimeoutError:
            await sent.delete()
            return await event.reply('وقت تمام شد', buttons=panel)
        except telethon.errors.common.AlreadyInConversationError as a:
            pass
    elif text == '🗑 حذف کد':
        try :
            async with bot.conversation(event.chat.id) as conv:
                sent = await conv.send_message('👈 کد را ارسال کنید', buttons=pback)
                code = await conv.get_response()
                if code.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not code.text:
                    sent = await conv.send_message('یک متن ارسال کنید', buttons=pback)
                    code = await conv.get_response()
                xx = Codes.get_or_none(Codes.code == code.text)
                if xx is None:
                    return await event.reply('‼️ این کد وجود ندارد',buttons=panel)
                xx.delete_instance()
            await event.reply('✅ کد مورد نظر با موفقیت حذف شد!',buttons=panel)
        except asyncio.exceptions.TimeoutError:
            await sent.delete()
            return await event.reply('وقت تمام شد', buttons=panel)
        except telethon.errors.common.AlreadyInConversationError as a:
            pass
    elif text == '💰 تغییر تعرفه ها':
        config = Config.get_or_none()
        if config is None:
            return
        config.puser = int(cget('puser'))
        config.days = int(cget('days'))
        config.gigs = int(cget('gigs'))
        return await event.reply('👇 لیست تعرفه های ربات به شرح زیر است :\nجهت تغییر هر کدام بر روی ان کلیک کنید',buttons=[
            [Button.inline(f'{number_format(config.gigs)} تومان','chprice-gigs'),Button.inline('قیمت هر گیگ :','chprice-gigs')],
            [Button.inline(f'{number_format(config.days)} تومان','chprice-days'),Button.inline('هر روز اضافه :','chprice-days')],
            [Button.inline(f'{number_format(config.puser)} تومان','chprice-puser'),Button.inline('هر اتصال اضافه :','chprice-puser')]
        ])
    elif text == '👤 مدیریت کاربر':
        try :
            async with bot.conversation(event.chat.id) as conv:
                sent = await conv.send_message(f'🆔 ایدی عددی کاربر مورد نظر را ارسال کنید', buttons=pback)
                uid = await conv.get_response()
                if uid.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not uid.raw_text.isnumeric():
                    sent = await conv.send_message(f'‼️ ایدی را به صورت عدد ارسال کنید', buttons=pback)
                    uid = await conv.get_response()
            user = Users.get_or_none(Users.user_id == uid.raw_text)
            if user is None :
                return await event.reply('❌ کاربری با این ایدی عددی در دیتابیس موجود نیست',buttons=panel)
            pays = 0
            secx = XM.select().where(XM.user == uid.raw_text)
            for i in secx:
                pays += int(i.price)
            mention = f"<a href='tg://user?id={user.user_id}'>{user.user_id}</a>"
            if user.ban:
                ban = 'مسدود'
            else :
                ban = 'ازاد'
            key = [
                [Button.inline(str(ban),f'ban-{user.user_id}'),Button.inline('🏷 وضعیت حساب :',f'ban-{user.user_id}')],
                [Button.inline('♻️ سرویس ها',f'allservice-{user.user_id}')],
                [Button.inline('افزایش موجودی',f'upcoin-{user.user_id}'),Button.inline('کاهش موجودی',f'downcoin-{user.user_id}')],
                ]
            await event.reply(f'👤 اطلاعات حساب شخص {mention}\n\n💰 موجودی حساب : <code>{user.coin}</code> تومان\n💳 کل مبلغ خرید ها : <code>{pays}</code> تومان\n🌐 تعداد سرویس ها : <code>{secx.count()}</code>\n🕰 تاریخ عضویت در ربات : <code>{user.joinDate}</code>',buttons=key,parse_mode='html')
            return await event.reply('پنل مدیریت :',buttons=panel)
        except asyncio.exceptions.TimeoutError:
            await sent.delete()
            return await event.reply('وقت تمام شد', buttons=panel)
        except telethon.errors.common.AlreadyInConversationError as a:
            pass
    elif text == '⚙️ تنظیمات':
        await event.reply('👇 به منوی تنظیمات ربات خوش آمدید ، با کلیک بر روی نام هر گزینه میتوانید آن را مدیریت کنید یا مقدار آن را تغییر دهید',buttons=setting())

@bot.on(events.CallbackQuery(pattern='power-(.*)'))
async def coin(event):
    if event.sender_id not in admins:
        return
    data = event.pattern_match.group(1).decode()
    c = Config.get(Config.key == data)
    if c.value == '0':
        c.value = '1'
    else:
        c.value = '0'
    c.save()
    await event.edit(buttons=setting())


@bot.on(events.CallbackQuery(pattern='(upcoin|downcoin)-(.*)'))
async def coin(event):
    if event.sender_id not in admins:
        return
    Type = event.pattern_match.group(1).decode()
    user = event.pattern_match.group(2).decode()
    user = Users.get_or_none(Users.user_id == user)
    if user is None:
        return await event.answer('❌ کاربر وجود ندارد',alert=True)
    else :
        try :
            async with bot.conversation(event.chat.id) as conv:
                if Type == 'upcoin':
                    msg = '➕ مقدار موجودی که قصد دارید به حساب کاربر اضافه شود را ارسال کنید'
                    umsg = 'مبلغ {x} تومان توسط مدیریت به حساب شما اضافه شد!'
                else :
                    msg = '➖ مقدار موجودی که قصد دارید از حساب کاربر کم شود را ارسال کنید'
                    umsg = 'مبلغ {x} تومان توسط مدیریت ربات از حساب شما کسر شد!'
                sent = await conv.send_message(str(msg), buttons=Button.text('برگشت',resize=True))
                coin = await conv.get_response()
                if coin.text in ('/panel','panel','پنل','برگشت','/start'):
                    return
                while not coin.raw_text.isnumeric():
                    sent = await conv.send_message(f'‼️ مبلغ را به صورت عدد ارسال کنید', buttons=Button.text('برگشت',resize=True))
                    coin = await conv.get_response()
                if Type == 'upcoin':
                    user.coin += int(coin.text)
                else :
                    user.coin -= int(coin.text)
                user.save()
                await bot.send_message(int(user.user_id),umsg.format(x = number_format(int(coin.text))))
                return await event.reply('✅ عملیات مورد نظر با موفقیت انجام شد',buttons=panel)
        except asyncio.exceptions.TimeoutError:
            await sent.delete()
            return await event.reply('وقت تمام شد', buttons=panel)
        except telethon.errors.common.AlreadyInConversationError as a:
            pass
        except Exception as e:
            s = traceback.format_exc()
            await event.reply(str(s))

@bot.on(events.CallbackQuery(pattern='chprice-(.*)'))
async def chprice(event):
    if event.sender_id not in admins:
        return
    data = event.pattern_match.group(1).decode()
    config = Config.get_or_none(Config.key == data)
    try :
        async with bot.conversation(event.chat.id) as conv:
            sent = await conv.send_message('👈 قیمت جدید را به عدد ارسال کنید', buttons=Button.text('برگشت',resize=True))
            price = await conv.get_response()
            if price.text in ('/panel','panel','پنل','برگشت','/start'):
                return
            while not price.raw_text.isnumeric():
                sent = await conv.send_message(f'‼️ قیمت را به صورت عدد ارسال کنید', buttons=Button.text('برگشت',resize=True))
                price = await conv.get_response()
        config.delete_instance()
        Config.create(
            key = data,
            value = int(price.raw_text)
        )
        return await event.reply('✅ عملیات مورد نظر با موفقیت انجام شد',buttons=panel)
    except asyncio.exceptions.TimeoutError:
        await sent.delete()
        return await event.reply('وقت تمام شد', buttons=panel)
    except telethon.errors.common.AlreadyInConversationError:
        pass
    except Exception as e:
        s = traceback.format_exc()
        await event.reply(str(s))

@bot.on(events.CallbackQuery(pattern='ban-(.*)'))
async def ban(event):
    if event.sender_id not in admins:
        return
    user = event.pattern_match.group(1).decode()
    user = Users.get_or_none(Users.user_id == user)
    if user is None:
        return await event.answer('❌ کاربر وجود ندارد',alert=True)
    else :
        if user.ban:
            x = False
        else :
            x = True
        user.ban = x
        user.save()
        if user.ban:
            ban = 'مسدود'
        else :
            ban = 'ازاد'
        key = [
            [Button.inline(str(ban),f'ban-{user.user_id}'),Button.inline('🏷 وضعیت حساب :',f'ban-{user.user_id}')],
            [Button.inline('♻️ سرویس ها',f'allservice-{user.user_id}')],
            [Button.inline('افزایش موجودی',f'upcoin-{user.user_id}'),Button.inline('کاهش موجودی',f'downcoin-{user.user_id}')],
        ]
        return await event.edit(buttons=key)

@bot.on(events.CallbackQuery(pattern='allservice-(.*)'))
async def allservice(event):
    if event.sender_id not in admins:
        return
    user = event.pattern_match.group(1).decode()
    user = Users.get_or_none(Users.user_id == user)
    if user is None:
        return await event.answer('❌ کاربر وجود ندارد',alert=True)
    services = XMUser.select().where(XMUser.telegram_id == user.user_id)
    if services.count() == 0:
        return await event.answer('این کاربر سرویسی ندارد!',alert=True)
    key = []
    key.append([Button.inline('کد سرویس','code')])
    for i in services:
        key.append([Button.inline(str(i.username.replace(f'.{event.sender_id}','')),f'show-{i.id}')])
    await event.edit('👇 لیست سرویس های کاربر به شرح زیر میباشد :',buttons=key)


@bot.on(events.CallbackQuery(pattern='show-(.*)'))
async def allservice(event):
    if event.sender_id not in admins:
        return
    code = event.pattern_match.group(1).decode()
    serv = XMUser.get_or_none(XMUser.id == code)
    if serv is None:
        return await event.answer('❌ سرویسی با این کد وجود ندارد',alert = True)
    expire = serv.expire_in
    create = serv.reg_date
    space = convert_size(serv.transfer_enable)
    total = convert_size(serv.u + serv.d)
    status = 'فعال'
    if serv.status == 0:
        status = 'غیرفعال'
    else :
        status = 'فعال'
    if datetime.datetime.now() > serv.expire_in:
        status = 'غیرفعال (اتمام مهلت استفاده)'
    rem = serv.transfer_enable - serv.total_data_used
    if rem < 1 :
        rem = serv.transfer_enable - serv.transfer_enable
    if int(round(float(convert_size(rem).split(' ')[0]))) < 1:
        status = 'غیرفعال (اتمام حجم)'
    await event.answer(f'تاریخ ساخت : {create}\nتاریخ انقضا : {expire}\nکل حجم : {space}\nحجم مصرف شده : {total}\nحجم باقی مانده : {convert_size(rem)}\nوضعیت سرویس : {status}\nمحدودیت اتصال : {serv.iplimit}',alert=True)

@bot.on(events.CallbackQuery(pattern='set-(.*)'))
async def set(event):
    if event.sender_id not in admins:
        return
    data = event.pattern_match.group(1).decode()
    config = Config.get_or_none(Config.key == data)
    try :
        async with bot.conversation(event.chat.id) as conv:
            sent = await conv.send_message('👈 مقدار جدید را وارد کنید', buttons=Button.text('برگشت',resize=True))
            res = await conv.get_response()
            if res.text in ('/panel','panel','پنل','برگشت','/start'):
                return
            if data not in ('support-id','tether-wallet','tron-wallet','test_gig'):
                while not res.raw_text.isnumeric():
                    sent = await conv.send_message(f'‼️ مقدار را به صورت عدد ارسال کنید', buttons=Button.text('برگشت',resize=True))
                    res = await conv.get_response()
        config.delete_instance()
        Config.create(
            key = data,
            value = res.raw_text
        )
        return await event.reply('✅ عملیات مورد نظر با موفقیت انجام شد',buttons=panel)
    except asyncio.exceptions.TimeoutError:
        await sent.delete()
        return await event.reply('وقت تمام شد', buttons=panel)
    except telethon.errors.common.AlreadyInConversationError:
        pass

@bot.on(events.NewMessage(pattern='[\/\.]reload',from_users =admins))
async def Reload(event):
    await event.reply('Reloaded Successfully')
    python = sys.executable
    os.execl(python, python, *sys.argv)

scheduler = AsyncIOScheduler(timezone="Asia/Tehran")
scheduler.add_job(SendAll, trigger="interval",seconds=30)
scheduler.start()    
