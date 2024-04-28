from telethon.sync import events
from telethon import Button
from xmdb import user as XMUser
from xmdb import online_ip
from db import XM,Users,Data,Config,Codes
import qrcode,math,asyncio,os,flag,requests,jdatetime,random,datetime,string,re
from config import bot,ban,join,xmplus_address,sublink,Back,START,cget,number_format,my,admins
from xmplus import xmplus_api

def get_location(ip_address):
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    return response

def random_string(length):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0 B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def number_format(num):
    return "{:,}".format(num)

class StdClass:
    pass

def okey(code):
    if cget('sell') == '0':
        return
    res = Data.get_or_none(Data.code == code)
    if res is None:
        return
    config = Config.get_or_none()
    if config is None :
        return
    config.puser = int(cget('puser'))
    config.days = int(cget('days'))
    config.gigs = int(cget('gigs'))
    xco = Codes.get_or_none(Codes.uuser == res.cuser)
    if xco is not None:
        config = xco
    space = int(res.gig) * int(config.gigs)
    if res.user > 1:
        puser = (int(config.puser) * int(res.user)-int(config.puser)) - int(config.puser)
    else :
        puser = int(config.puser) * int(res.user)
    if res.days > 30:
        pday = (int(config.days) * int(res.days)) - (int(config.days) * 30)
    else :
        pday = 0
    price = space + puser + pday
    res.price = price
    res.save()
    return [
        [Button.inline('📊 حجم','space')],
        [Button.inline('➖',f'lowspace-{code}'),Button.inline(f'{res.gig} گیگ','space'),Button.inline('➕',f'upspace-{code}')],
        [Button.inline('🌐 تعداد اتصال همزمان','connections')],
        [Button.inline('➖',f'lowcon-{code}'),Button.inline(f'{res.user - 1 - 1 } کاربر','connections'),Button.inline('➕',f'upcon-{code}')],
        [Button.inline('⌛️ زمان سرویس','date')],
        [Button.inline('➖',f'lowday-{code}'),Button.inline(f'{res.days} روزه','date'),Button.inline('➕',f'upday-{code}')],
        [Button.inline(f'{number_format(price)} تومان','price'),Button.inline('💵 قیمت :','price')],
        [Button.inline('ساخت ⚙️',f'create-{code}')],
    ]

@bot.on(events.NewMessage(pattern='خرید سرویس 🛍',func=lambda e: e.is_private))
@ban
@join
async def newService(event):
    if cget('sell') == '0':
        return await event.reply('❌ درحال حاضر امکان ارائه سرویس جدید مقدر نمیباشد')
    code = random.randint(11111,99999)
    Data.create(code=code,cuser=event.sender_id)
    return await event.reply('🔐 کانفیـــــگ خودت رو بساز \n\n✅ جهت ساخت سرویس به صورت دلخواه\nمورد نیاز خودت ؛ می‌توانید از کیبورد های زیر جهت کم و زیاد کردن مشخصات سرویست استفاده کنی و خرید خودتون رو با مشخصات دلخواه خودت نهایی کنی:',buttons=okey(code))

@bot.on(events.CallbackQuery(pattern=b'(upday|lowday|lowcon|lowspace|upcon|upspace)-(.*)'))
@ban
@join
async def plan(event):
    if cget('sell') == '0':
        return await event.answer('❌ درحال حاضر امکان ارائه سرویس جدید مقدر نمیباشد',alert=True)
    data = event.pattern_match.group(1).decode()
    code = event.pattern_match.group(2).decode()
    res = Data.get(Data.code==code)
    if data == 'upcon':
        res.user += 1
        if res.user > int(cget('max_user')):
            return await event.answer('❌ امکان ارائه بیشتر اتصال همزمان وجود ندارد !',alert=True)
    elif data == 'upspace':
        res.gig += 10
        if int(res.gig) > int(cget('max_gig')):
            return await event.answer(f'⚠️ حداقل حجم مجاز سرویس جهت ارتقا {cget("max_gig")} گیگ میباشد!',alert=True)
    elif data == 'lowcon':
        res.user -= 1
        if res.user == 1:
            return await event.answer('امکان کاهش نیست!',alert=True)
    elif data == 'lowspace':
        res.gig -= 10
        if res.gig < int(cget('min_gig')):
            return await event.answer(f'❌ امکان ارائه سرویس کمتر از {cget("min_gig")} گیگ نمیباشد !',alert=True)
    elif data == 'upday':
        res.days += 5
        if int(res.days) > int(cget('max_days')):
            return await event.answer(f'❌ امکان ارائه سرویس بیشتر از {cget("max_days")} روز وجود ندارد!',alert=True)
    elif data == 'lowday':
        res.days -= 5
        if res.days < 30:
            return await event.answer('امکان کاهش نیست!',alert=True)
    res.save()
    await event.edit(buttons=okey(code))
    
@bot.on(events.CallbackQuery(pattern=b'create-(.*)'))
@ban
@join
async def plan(event):
    if cget('sell') == '0':
        return await event.answer('❌ درحال حاضر امکان ارائه سرویس جدید مقدر نمیباشد',alert=True)
    code = event.pattern_match.group(1).decode()
    res = Data.get(Data.code==code)
    user = Users.get(Users.user_id == event.sender_id)
    if user.coin >= res.price:
        try :
            async with bot.conversation(event.sender_id,timeout = 300) as conv:
                pattern = r"^[A-Za-z0-9_-]*$"
                await conv.send_message('👤 لطفا یک نام کاربری برای سرویس خود ارسال کنید',buttons=Back)
                username = (await conv.get_response()).text
                if username in ('🔙','/start') : return
                while username is None:
                    await conv.send_message('‼️ لطفا یک متن ارسال کنید',buttons=Back)
                    username = (await conv.get_response()).text
                while len(username) > 11:
                    await conv.send_message('نام کاربری ارسالی باید کمتر از 10 کاراکتر باشد!',buttons=Back)
                    username = (await conv.get_response()).text
                while not re.match(pattern, username):
                    await conv.send_message('فقط حروف انگلیسی مجاز است!',buttons=Back)
                    username = (await conv.get_response()).text
            z = XM.get_or_none(XM.email == f'{username}.{event.sender_id}@gmail.com')
            if z is not None:
                return await event.reply('❌ شما یک سرویس با این نام کاربری دارید ، لطفا یک نام کاربری دیگر ارسال کنید',buttons=START)
        except asyncio.exceptions.TimeoutError:
            await event.reply('⚠️ مهلت به پایان رسید',Buttons=START)        
        f = await event.reply('♻️ درحال ساخت سرویس ...')
        await event.delete()
        user.coin -= int(res.price)
        user.save()
        username = f'{username}.{event.sender_id}'
        my.login()
        my.create_user(f'{username}@gmail.com',username)
        get = XMUser.get_or_none(XMUser.email == f'{username}@gmail.com')
        if get is not None:
            link = f'{sublink}{get.token}'
            XM.create(
                user = event.sender_id,
                email = f'{username}@gmail.com',
                uid = get.id,
                price = res.price,
                space = res.gig,
                day = res.days
            )
            img = qrcode.make(link)
            img.save(f"{get.token}.png")
            username = username.replace(f'.{event.sender_id}','')
            await bot.send_file(entity = event.sender_id,file = f"{get.token}.png",caption = f'✅ سرویس شما با موفقیت ساخته شد !\n\n👇 اطلاعات سرویس شما به شرح زیر میباشد :\n\n🔢 آیدی سرویس : `{get.id}`\n👤 کد اشتراک : `{username}`\n📊 حجم سرویس : `{res.gig}` گیگ\n🌐 تعداد اتصال همزمان : `{res.user - 1}` کاربر\n⏳ زمان سرویس : `{res.days}` روزه\n💰 قیمت سرویس : `{number_format(res.price)}` تومان\n\n📡 لینک اتصال : `{link}`',parse_mode='markdown',buttons=Button.inline('⁉️ راهنمای اتصال','apps')) # نویسنده : @sudohunter
            await event.reply('✅ به منوی اصلی بازگشتید :',buttons=START)
            os.unlink(f"{get.token}.png")
            my.edit_user(get.id,res.gig,res.user,res.days,event.sender_id)
            my.logout()
            mention = f'<a href="tg://user?id={event.sender_id}">{event.sender_id}</a>'
            await f.delete()
            txt = f'📌 کاربر {mention} سرویس جدید خریداری کرد !\n👇 مشخصات سرویس خریداری شده : \n🔢 آیدی سرویس : <code>{get.id}</code>\n👤 کد اشتراک : <code>{username}</code>\n📊 حجم سرویس : <code>{res.gig}</code> گیگ\n🌐 تعداد اتصال همزمان : <code>{res.user}</code> کاربر\n⏳ زمان سرویس : <code>{res.days}</code> روزه\n💰 قیمت سرویس : <code>{number_format(res.price)}</code> تومان\n'
            xco = Codes.get_or_none(Codes.uuser == event.sender_id)
            if xco is not None:
                txt += f'-----------\n🔰 کد نمایندگی کاربر : {xco.code}\nقیمت هر گیگ : {xco.gigs}\nقیمت هر روز : {xco.days}\nقیمت هر اتصال اضافه : {xco.puser}'
            for i in admins:
                await bot.send_message(int(i),str(txt),parse_mode='html')
        else:
            user.coin += int(res.price)
            user.save()
            await event.answer('❌ خطایی در ساخت سرویس پیش آمد!',alert=True)
    else :
        await event.answer('⚠️ موجودی شما کافی نیست!',alert=True)

@bot.on(events.NewMessage(pattern='سرویس تست 🎁',func=lambda e: e.is_private))
@ban
@join
async def plan(event):
    if cget('test') == '0':
        return await event.reply('❌ درحال حاضر امکان ارائه سرویس تست مقدر نمیباشد')
    if XM.select().where(XM.user == event.sender_id).where(XM.status == 'free').exists():
        return await event.reply('شما یک بار سرویس تست دریافت کرده اید!')
    f = await event.reply('♻️ درحال ساخت سرویس ...')
    username = 'Test'
    username = f'{username}.{event.sender_id}'
    my.login()
    my.create_user(f'{username}@gmail.com',username)
    get = XMUser.get_or_none(XMUser.email == f'{username}@gmail.com')
    if get is not None:
        link = f'{sublink}{get.token}'
        XM.create(
            user = event.sender_id,
            email = f'{username}@gmail.com',
            uid = get.id,
            price = 0,
            space = cget('test_gig'),
            day = cget('test_day'),
            status = 'free'
        )
        img = qrcode.make(link)
        img.save(f"{get.token}.png")
        username = username.replace(f'.{event.sender_id}','')
        await bot.send_file(entity = event.sender_id,file = f"{get.token}.png",caption = f'✅ سرویس تست شما با موفقیت ساخته شد !\n\n👇 اطلاعات سرویس شما به شرح زیر میباشد :\n\n🔢 آیدی سرویس : `{get.id}`\n👤 کد اشتراک : `{username}`\n📊 حجم سرویس : `{cget("test_gig")}` گیگ\n🌐 تعداد اتصال همزمان : `{cget("limit_test")}` کاربر\n⏳ زمان سرویس : `{cget("test_day")}` روزه\n\n📡 لینک اتصال : `{link}`',parse_mode='markdown',buttons=Button.url('Copy Link', f'streisand://import/{link}')) # نویسنده : @sudohunter
        await event.reply('✅ به منوی اصلی بازگشتید :',buttons=START)
        mention = f'<a href="tg://user?id={event.sender_id}">{event.sender_id}</a>'
        for i in admins:
            await bot.send_message(int(i),f'کاربر {mention} سرویس تست دریافت کرد!',parse_mode='html')
        os.unlink(f"{get.token}.png")
        my.edit_user(get.id,cget('test_gig'),cget('limit_test'),int(cget('test_day')),event.sender_id)
        my.logout()
        await f.delete()
    else:
        await event.answer('❌ خطایی در ساخت سرویس پیش آمد!',alert=True)

@bot.on(events.NewMessage(pattern='سرویس های من ⚙️',func=lambda e: e.is_private))
@ban
@join
async def myServices(event):
    xmus = XM.select().where(XM.user == event.sender_id).where(XM.status == None)
    if not xmus.exists():
        return await event.reply("⭕️ لیست سفارش ها شما خالی می باشد. لطفا یک پلن جدید خریداری کنید.")
    key = []
    key.append([Button.inline('🔎 جستجو در سرویس ها','search')])
    key.append([Button.inline('🏷️ کد اشتراک','code'),Button.inline('📉 حجم مانده','space'),Button.inline('⏳ زمان مانده','expire')])
    for i in xmus.limit(10):
        i = XMUser.get_or_none(XMUser.email == i.email)
        if i is None:
            continue
        rem = i.transfer_enable - i.total_data_used
        if rem < 1 :
            rem = i.transfer_enable - i.transfer_enable
        t = datetime.datetime.now()
        expire = datetime.date(i.expire_in.year,i.expire_in.month,i.expire_in.day) - datetime.date(t.year,t.month,t.day)
        edays = expire.days
        if edays < 1 :
            edays = 0
        remsize = convert_size(rem)
        si = int(round(float(remsize.split(' ')[0])))
        emoji = '🟢'
        if si < si/4 or edays < 15:
            emoji = '🟠'
        if si < 5 or edays < 5:
            emoji = '🔴'
        if edays == 0 or si == 0:
            emoji = '🚫'
        da = i.username.replace(f'.{event.sender_id}','')
        key.append([Button.inline(f'{emoji} {da}',f'manage-{i.id}'),Button.inline(str(remsize),f'manage-{i.id}'),Button.inline(f'{edays} روز',f'manage-{i.id}')])
    if xmus.count() > 10:
        key.append([Button.inline('➡️ صفحه بعد', f'next 0')])
    await event.reply(f'📊 لیست سرویس ها شما: \n\n⤵️ کاربرعزیز، شما با استفاده از دکمه های زیر میتونید آمار اشتراک هایی که تهیه کردید را مشاهده کنید، جهت مشاهده و یا مدیریت انها روی کد اشتراک انها کلیک کنید:',buttons = key)

@bot.on(
    events.CallbackQuery(
        pattern=b'(next|prev) (.*)'
    )
)
async def show(event):
    try:
        Type = event.pattern_match.group(1).decode()
        offset = event.pattern_match.group(2).decode()
        key = []
        key.append([Button.inline('🔎 جستجو در سرویس ها','search')])
        key.append([Button.inline('🏷️ کد اشتراک','code'),Button.inline('📉 حجم مانده','space'),Button.inline('⏳ زمان مانده','expire')])
        if Type == 'next':
            offset = int(offset) + 10
        elif Type == 'prev' : 
            offset = int(offset) - 10
        xmus = XM.select().where(XM.user == event.sender_id).where(XM.status == None)
        for i in xmus.limit(10).offset(offset):
            i = XMUser.get_or_none(XMUser.email == i.email)
            if i is None:
                continue
            rem = i.transfer_enable - i.total_data_used
            if rem < 1 :
                rem = i.transfer_enable - i.transfer_enable
            t = datetime.datetime.now()
            expire = datetime.date(i.expire_in.year,i.expire_in.month,i.expire_in.day) - datetime.date(t.year,t.month,t.day)
            edays = expire.days
            if edays < 1 :
                edays = 0
            remsize = convert_size(rem)
            si = int(round(float(remsize.split(' ')[0])))
            emoji = '🟢'
            if si < si/4 or edays < 15:
                emoji = '🟠'
            if si < 5 or edays < 5:
                emoji = '🔴'
            if edays == 0 or si == 0:
                emoji = '🚫'
            da = i.username.replace(f'.{event.sender_id}','')
            key.append([Button.inline(f'{emoji} {da}',f'manage-{i.id}'),Button.inline(str(remsize),f'manage-{i.id}'),Button.inline(f'{edays} روز',f'manage-{i.id}')])
        if Type == 'next':
            if xmus.count() > int(offset) + 10:
                key.append([Button.inline('⬅️ صفحه قبل', f'prev {offset}'), Button.inline('➡️ صفحه بعد', f'next {offset}')])
            else:
                if offset < 1:
                    key.append([Button.inline('➡️ صفحه بعد', f'next 0')])
                else :
                    key.append([Button.inline('⬅️ صفحه قبل', f'prev {offset}')])
        else :
            if offset < 1:
                key.append([Button.inline('➡️ صفحه بعد', f'next 0')])
            else :
                key.append([Button.inline('⬅️ صفحه قبل', f'prev {offset}'), Button.inline('➡️ صفحه بعد', f'next {offset}')])
        return await event.edit(buttons=key)
    except Exception as e:
        pass

@bot.on(events.CallbackQuery(pattern=b'search'))
async def search(event):
    try:
        async with bot.conversation(event.chat.id, timeout=300) as conv:
            sent = await conv.send_message('🔐 لطفا کد اشتراک سرویس خود را جهت جستجو در بین سرویس ها ارسال کنید', buttons=Back)
            code = await conv.get_response()
            while not code.text:
                sent = await conv.send_message('❌ فقط متن ارسال کنید', buttons=Back)
                code = await conv.get_response()
            username = f'{code.raw_text}.{event.sender_id}'
            get = XMUser.get_or_none(XMUser.username == username)
            if get is None : 
                await event.reply('سرویسی با این کد اشتراک وجود ندارد!',buttons=START)
            else :
                await event.reply('✅ سرویس مورد نظر شما با موفقیت پیدا شد ! جهت مدیریت سرویس از دکمه ی زیر استفاده کنید 👇',buttons=Button.inline('مدیریت سرویس',f'manage-{get.id}'))
                return await event.reply('منوی اصلی : ',buttons=START)
    except asyncio.exceptions.TimeoutError:
        await sent.delete()
        return await event.reply('❌ مهلت ارسال پیام به کاربر به اتمام رسید', buttons=START)

@bot.on(events.CallbackQuery(pattern=b'(manage|changelink|tamdid|yes)-(.*)'))
@ban
@join
async def plan(event):
    data = event.pattern_match.group(1).decode()
    code = event.pattern_match.group(2).decode()
    xmus = XMUser.get_or_none(XMUser.id == code)
    XMD = XM.get_or_none(XM.uid == code)
    if XMD.status == 'nowshow': return
    if data in ('tamdid','yes') and XMD.status == 'free':
        return await event.answer('❌ به دلیل رایگان بودن سرویس شما نمی توانید از این بخش استفاده کنید جهت فعال شدن بخش های مختلف ابتدا سرویسی خریداری کنید',alert=True)
    if data == 'changelink':
        await event.answer('♻️ کمی صبر کنید ...')
        await event.delete()
        panel = xmplus_api(xmplus_address,f'{XMD.email}','1mmd@@@M')
        panel.login()
        panel.change()
        panel.logout()
        return await event.reply('✅ لینک اتصال و uuid سرویس شما با موفقیت تغییر یافت ! جهت مشاهده اطلاعات سرویس بر روی دکمه زیر کلیک کنید 👇',buttons=Button.inline('مشاهده اطلاعات',f'manage-{code}'))
    t = datetime.datetime.now()
    if xmus is None or XMD is None:
        return await event.answer('❌ خطایی در دریافت اطلاعات پیش آمد',alert=True)
    await event.delete()
    if data == 'tamdid':
        if XMD.status == 'notshow': return
        return await event.reply(f'‼️ توجه داشته باشید با انجام این عملیات تمامی حجم و زمان باقی مانده فعلی سرویس شما صفر میشود \n👇در صورت تایید روی گزینه "✅ تایید" کلیک کنید\n\n💰 هزینه تمدید سرویس : {number_format(XMD.price)}',buttons=[
            [Button.inline('✅ تایید',f'yes-{code}'),Button.inline('❌ لغو','cancel')]
        ])
    elif data == 'yes':
        if XMD.status == 'notshow': return
        user = Users.get(Users.user_id == event.sender_id)
        if user.coin > XMD.price:
            xmus.u = 0
            xmus.d = 0
            xmus.total_data_used = 0
            xmus.used = 0
            xmus.save()
            user.coin -= XMD.price
            user.save()
            my.login()
            if XMD.day is None:
                XMD.day = 30
            my.edit_user(XMD.uid,XMD.space,xmus.iplimit,XMD.day,event.sender_id)
            my.logout()
            await event.reply('✅ سرویس شما با موفقیت تمدید شد!',buttons=Button.inline('مدیریت سرویس',f'manage-{xmus.id}'))
            for i in admins:
                await bot.send_message(int(i),f'‼️ کاربر <a href="tg://user?id={event.sender_id}">{event.sender_id}</a> یک سرویس به مبلغ {XMD.price} تومان تمدید کرد\nآیدی سرویس : {XMD.uid}',parse_mode='html')
        else:
            await event.reply('موجودی شما کافی نیست!')
        return
    rem = xmus.transfer_enable - xmus.total_data_used
    if rem < 1 :
        rem = 0
    link = f'{sublink}{xmus.token}'
    img = qrcode.make(link)
    img.save(f"{xmus.token}.png")
    txt = f"👇 اطلاعات سرویس شما به شرح زیر میباشد :\n\n🔰 کل مصرف : `{convert_size(xmus.total_data_used)}`\n🆙 اپلود : `{convert_size(xmus.u)}`\n♻️ دانلود : `{convert_size(xmus.d)}`\n🆓 حجم باقی مانده : `{convert_size(rem)}`\n\n🌐 لینک سابسکریپشن : `{link}`"
    key = [
        [Button.inline('🔗 دریافت لینک',f'getlink-{code}'),Button.inline('📊 مشخصات سرویس',f'getinfo-{code}')],
        [Button.inline('🔏 وضعیت اتصالات',f'connections-{code}'),Button.inline('🧬 حجم اضافه',f'adddata-{code}')],
        [Button.inline('🔄 تمدید سرویس',f'tamdid-{code}'),Button.inline('➕ کاربر اضافه',f'newuser-{code}')],
        [Button.inline('تغییر لینک و ریست uuid 〽️',f'changelink-{code}'),Button.inline('❌ حذف اشتراک',f'deleteuser-{code}')]
    ]
    await bot.send_file(entity = event.sender_id,file = f'{xmus.token}.png', caption = str(txt),parse_mode='markdown',buttons=key)
    os.unlink(f'{xmus.token}.png')

@bot.on(events.CallbackQuery(pattern=b'(deleteuser|getlink|getinfo|connections|newuser|adddata)-(.*)'))
@ban
@join
async def get(event):
    data = event.pattern_match.group(1).decode()
    code = event.pattern_match.group(2).decode()
    xmus = XMUser.get_or_none(XMUser.id == code)
    XMD = XM.get_or_none(XM.uid == code)
    if XMD.status == 'notshow': return
    if data not in ('getlink','getinfo','connections') and XMD.status == 'free':
        return await event.answer('❌ به دلیل رایگان بودن سرویس شما نمی توانید از این بخش استفاده کنید جهت فعال شدن بخش های مختلف ابتدا سرویسی خریداری کنید',alert=True)
    t = datetime.datetime.now()
    connections = online_ip.select().where(online_ip.userid == code).where(online_ip.datetime > (int(t.timestamp()) - 60))
    user = Users.get(Users.user_id == event.sender_id)
    if xmus is None:
        return await event.answer('❌ خطایی در دریافت اطلاعات پیش آمد',alert=True)
    status = 'فعال'
    if xmus.status == 0:
        status = 'غیرفعال'
    else :
        status = 'فعال'
    if datetime.datetime.now() > xmus.expire_in:
        status = 'غیرفعال (اتمام مهلت استفاده)'
    rem = xmus.transfer_enable - xmus.total_data_used
    if rem < 1 :
        rem = 0
    if int(round(float(convert_size(rem).split(' ')[0]))) < 1:
        status = 'غیرفعال (اتمام حجم)'
    key = [
        [Button.inline('🔗 دریافت لینک',f'getlink-{code}'),Button.inline('📊 مشخصات سرویس',f'getinfo-{code}')],
        [Button.inline('🔏 وضعیت اتصالات',f'connections-{code}'),Button.inline('🧬 حجم اضافه',f'adddata-{code}')],
        [Button.inline('🔄 تمدید سرویس',f'tamdid-{code}'),Button.inline('➕ کاربر اضافه',f'newuser-{code}')],
        [Button.inline('تغییر لینک و ریست uuid 〽️',f'changelink-{code}'),Button.inline('❌ حذف سرویس',f'deleteuser-{code}')]
    ]
    if data == 'getinfo':
        await event.reply(f"🔢 آیدی سرویس : `{xmus.id}`\n👤 کد اشتراک : `{xmus.username.replace(f'.{event.sender_id}','')}`\n💡 تعداد اتصالات : `{xmus.iplimit -1} / {connections.count()}`\n\n⚙️ تاریخ ساخت : `{str(jdatetime.date.fromgregorian (day = xmus.reg_date.day, month = xmus.reg_date.month, year = xmus.reg_date.year))}`\n⏳ تاریخ انقضا : `{str(jdatetime.date.fromgregorian (day = xmus.expire_in.day, month = xmus.expire_in.month, year = xmus.expire_in.year))}`\n📊 حجم سرویس : `{convert_size(xmus.transfer_enable)}`\n🏷 وضعیت سرویس : {status}\n📲 تعداد اتصال همزمان : `{xmus.iplimit - 1}` کاربر\n\n📡 uuid : `{xmus.uuid}`\n🌐 token : `{xmus.token}`")
    elif data == 'connections':
        if connections.count() == 0:
            return await event.answer('هیچ اتصالی وجود ندارد!')
        d = 1
        for i in connections: 
            res = get_location(i.ip)
            await event.edit(f'تعداد اتصالات : {connections.count()}\n\n{d} : \n نام سرور : {i.servername}\nip : {i.ip}\nزمان : {datetime.datetime.fromtimestamp(i.datetime)}\nlocation : {res["country_name"]} {flag.flag(res["country_code"])}/ {res["city"]}\n',buttons=key)
            d += 1
    elif data == 'getlink':
        link = f'{sublink}{xmus.token}'
        await event.reply(f'🌐 لینک سابسکریپشن : `{link}`')
    elif data == 'newuser':
        config = StdClass
        config.puser = int(cget('puser'))
        config.days = int(cget('days'))
        config.gigs = int(cget('gigs'))
        xco = Codes.get_or_none(Codes.uuser == event.sender_id)
        if xco is not None:
            config = xco
        try :
            async with bot.conversation(event.sender_id,timeout = 300) as conv:
                await conv.send_message(f'👤 لطفا تعداد کاربری که قصد دارید به این سرویس اضافه شود را ارسال کنید :\n\n💰 هزینه هر کاربر اضافه : {number_format(int(config.puser))}',buttons=Back)
                res = await conv.get_response()
                if res.text == '🔙' : return
                while not res.raw_text.isnumeric():
                    await conv.send_message('‼️ لطفا تعداد را به صورت عدد ارسال کنید',buttons=Back)
                    res = await conv.get_response()
            res = int(res.raw_text)
            if user.coin > res * config.puser:
                xmus.iplimit += res
                xmus.save()
                user.coin -= res * config.puser
                user.save()
                XMD.price += res * config.puser
                XMD.day += res
                XMD.save()
                await event.reply(f'✅ تعداد {res} اتصال اضافه به سرویس شما اضافه شد',buttons=START)
            else :
                await event.reply(f'❌ موجودی حساب شما جهت انجام این کار کافی نیست !',buttons=START)
        except asyncio.exceptions.TimeoutError:
            await event.reply('⚠️ مهلت زمان انجام عملیات به پایان رسید ! چنانچه قصد ادامه دارید مراحل را دوباره طی کنید.',buttons=START)
    elif data == 'adddata':
        try :
            config = StdClass
            config.puser = int(cget('puser'))
            config.days = int(cget('days'))
            config.gigs = int(cget('gigs'))
            xco = Codes.get_or_none(Codes.uuser == event.sender_id)
            if xco is not None:
                config = xco
            async with bot.conversation(event.sender_id,timeout = 300) as conv:
                await conv.send_message(f'👤 لطفا مقدار حجمی که قصد دارید به این سرویس اضافه شود را ارسال کنید :\n\n💰 هزینه هر گیگ اضافه : {number_format(int(config.gigs))}',buttons=Back)
                res = await conv.get_response()
                if res.text == '🔙' : return
                while not res.raw_text.isnumeric():
                    await conv.send_message('‼️ لطفا تعداد را به صورت عدد ارسال کنید',buttons=Back)
                    res = await conv.get_response()
            res = int(res.raw_text)
            if user.coin > res * config.gigs:
                xmus.transfer_enable += res * (1024**3)
                xmus.save()
                user.coin -= res * config.gigs
                user.save()
                XMD.price += res * config.gigs
                XMD.space += res
                XMD.save()
                await event.reply(f'✅ مقدار {res} گیگ به سرویس شما اضافه شد',buttons=START)
            else :
                await event.reply(f'❌ موجودی حساب شما جهت انجام این کار کافی نیست !',buttons=START)
        except asyncio.exceptions.TimeoutError:
            await event.reply('⚠️ مهلت زمان انجام عملیات به پایان رسید ! چنانچه قصد ادامه دارید مراحل را دوباره طی کنید.',buttons=START)
    elif data == 'deleteuser':
        try:
            async with bot.conversation(event.sender_id,timeout = 300) as conv:
                await conv.send_message(f"آیا از حذف کردن اشتراک {xmus.username.replace(f'.{event.sender_id}','')} مطمئن هستید؟\n\nبا انجام این کار هیچ مبلغی به حساب شما باز نمیگردد!",buttons=[[Button.text('بله',resize=True,single_use=True),Button.text('خیر')]])
                res = (await conv.get_response()).text
                if res == '🔙' : return    
                while res not in ('بله','خیر'):
                    res = (await conv.get_response()).text
                if res == 'بله':
                    await event.reply(f"اشتراک {xmus.username.replace(f'.{event.sender_id}','')} با موفقیت حذف گردید.",buttons=START)
                    XMD.status = 'nowshow'
                    XMD.save()
                    my.login()
                    my.delete_user(xmus.uid)
                    my.logout()
                elif res == 'خیر':
                    await event.reply('به منوی اصلی برگشتید :',buttons= START)
                    return await myServices(event)
        except asyncio.exceptions.TimeoutError:
            await event.reply('⚠️ مهلت زمان انجام عملیات به پایان رسید ! چنانچه قصد ادامه دارید مراحل را دوباره طی کنید.',buttons=START)
