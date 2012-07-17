#- -encoding: utf8

import os
from autotemp import tempdir
from subprocess import Popen, PIPE, STDOUT

__all__ = ['generatesummary', 'walk']

def generatesummary(name, filename, depthlimit = 9999):
    if os.path.isdir(filename):
        return (name, _foldersummary(filename, depthlimit))
    else:
        return (name,) + _filesummary(filename, depthlimit)

def _filesummary(filename, depthlimit):
    if depthlimit > 0:
        table = {
            '.rar': lambda x:_archivesummary('rar',x,depthlimit),
            '.tar': lambda x:_archivesummary('tar',x,depthlimit),
            '.tar.gz': lambda x:_archivesummary('tar',x,depthlimit),
            '.tar.bz2': lambda x:_archivesummary('tar',x,depthlimit),
            '.zip': lambda x:_archivesummary('zip',x,depthlimit),
            '.txt': _textsummary,
        }
        for k in table:
            if filename.endswith(k):
                return table[k](filename)
    return (None, )

def walk(summary):
    if type(summary) is tuple:
        if summary and type(summary[0]) is str:
            yield summary[0]
            for e in walk(summary[1]):
                yield e
        else:
            for e in summary:
                for f in walk(e):
                    yield f
    elif type(summary) is str:
        yield summary

def _foldersummary(folder, depthlimit):
    if depthlimit > 0:
        #List files.
        files = os.listdir(folder)
        #Generate each summary of each file.
        return tuple([generatesummary(file, os.path.join(folder, file), depthlimit-1) for file in files])
    return None

commonchar = '，的。　了不一是我“”他她这你在有人来着个？么…上说就到那子看！道也好要下没地大出心然会去得过里可想还小自们时为后起都什：头天身以手对只眼中能样开知己事笑而很回点话面声之真情意如和前生气女无又多现见让儿家些发走已被才把怎再经脸啊但—吗所口吧给老当觉间问却定两住明动从打听边用太方于「」成将正感白轻像进几、做跟力神死直向门本王光色皇此最长水年次别外因放实果呢男快三公候爱应难种十便相冷何安.刚其同风高行该法全望叫离西分美等更?主张微紧少清作找花吃东接带重宫完亲关算姐日连理先转音-二第似与娘今黑比哥体原思喜竟怕信总处满容落龙红惊!名若受车变位月早表乎国房机深突四底衣许坐并入常内爷双步解静虽往孩马嘴欢哪反目越学命认拿电伤谁失空倒刻青楚平错怪远飞,火半夜般千忙服指记随由妈站告拉任云始山干加路痛文金绝非易阳晚强南淡言流语至结终答怀场影近办星世且急慢视万物妃低睛请活林雪立帮久沉字夫息血切害阿件根师奇丝脚灵敢抱苏温朝管传摇整提部片句著性"即度通睡者父李忍依书古新香暗柔它脑苦玉哈五眉跑莫使留阵宝必杀母工石谢海保木合楼停司顾*量未背角冲兴每照条钱乱室送交疑诉旁细居床百穿识寒准特待代呼陈亮收夏蓝断喝掉尽极醒装八酒确友周题热令抬露妹冰w章消够求及玩呵泪愿念城1精跳墨系梦包唇单显缓怒乐院异赶或响客教备尔曾续兰顿象您医数初战计复颜狠呀决萧；鬼恶希爸幸紫利继晓忽饭形唐伸推闪线耳婚差哭弟叶贵抓台破n帝君江雨肯忘丽福礼足拍牙隐味巴迷况注皮吸除报担姑救哦速叹段嘛默啦简药士故渐化吓界佛则制势靠功‘份恐另（刘护约）宇’恨持病顺七众朋摸华眸军止激卫黄退剑尸扬秘殿烈换墓偷既嗯追程压密六呆杨甚围官2模松首调珠弄料坏轩桌烦格击修禁刀斯论毫丫翻瞪掌疼需画期刺屋兄块胸警散宁取毒承仿毕否握吻罗武0伙凡试魔各板逃裁阴~招弱引态猛雅举麻欣肩熟烟副懂股摆端店团休置假遇咬闻飘严．写愣透查钟叔九考慕兵暖仍迟府喊陪挑左沙洞皱达俊袋狂顶费品买`齐野示脱业草骨魂元寻证布岁险杯欲藏领谈旧唯存究堂胡s羽毛选洪银树雷辰弯案颤观按永闭独负术封威软惜婆层盖抽坚窗员族排t4凝哼傻臣瞬探i改较景瞧班震盯茶亦习硬幽凌恩米昨斗图具舒讨甜运蒙游守肉德胖讲义状惑释支贝奴洛奶灯群座☆察挂镜铁亚厉孙=餐素腰扶p睁挥舞朕b侍式致右展蛋欧偏绪爹园凤巧类奈责充凉厅议抹尖累闷洗辈巨悦闹罪＊午抖3戏属局英撞腿慌仅荣派节(墙助环养诺器)菜集碰秦质民娇辛务赵商混造·吐o伦残某号索虚校纸骂;食拥鼻冒临翼介须趣乖土劲智绿尚浩球资危余&纪妳盘秋魅套春梅挺称扯历歌队敬弃怜北替搞玄丢额争躲建宣朵e短臂烧超忧躺免圣忆熙恋适良怨尊汗抚碎迹杂疯妖折珊吴糊晃伶妻划穆耶董犹稍迎付据猜傲设克专丁嫁番枪拜村浅愤印侧喂卖聊贺架陆移童骗贴漂厌昏级帅颗狼沈彻概扑傅擦借鱼误波悄秀5猪6境触零射市联苍托9弹束氏逼产咱胆》志汉嘿勾《艾罢暴柳腾韩凶圈遍舍琳纯仙控奔吼御曲律徐滚避权枫庄妙材邪妇梁爬虎厚圆笔含滴眨莲拒肚洋拳宋扎抢狗桃升略浓孤善菲怔羞蓉伊演祖娜薇晨泽投荡畔防晕惨悲宛盛薛貌犯际哀奋锦吟稳价私晶挣值鲜痕浑壁净浮配粉r晴吹蜜努区佳纷l杰街惯虑宠扫仔歉扭参掩讶烁滑恼川敌垂雾悉哲唤竹隔y困彩谓宗败僵缠择喃陷剩闲牛眯牌夕g采敏匆跪尘杜耐呜薄浪映仪型欺灰焰京敲镇漫河附琪练赏尹监兽挡胜抗治攻归漠烨椅导亡迅凭醉曦灭伯姓狐乔哎户普谷缘规膀涌郁卷媚广惹幻仇棺悔池堆富嘉优森娃慰距递纤珍湖测婢拖酸唉油牵遗尾悠湘幕诚赫允埋璃烂踪缩基阻萱芒盗锁网预田汤姨脖懒聚痴剧补吞愈迫伴肤耀翔舌芷俩绕c甩源磨裂横冬康席朗施瞳碧宜寂喘豫_恭庭梯脆焦夺爆咳勇维8搭组甘碗鸡屈艳尼遥徒偶粗恢蛇颊S袖职扔执胤孔姿屁兮豪聪委笨7标臭忠钻咒蝶湿x统踏插轮隆共仰倾瓶揉洁社晋戴虫扰饰纳拼暂塞厨甲尤拾嘻豆骑宽牢鼓铃袭财绍项载帐惧M读巫验码凯史捏陌辉染占吵瑶娶脏★船课陵政启营阮咖喔穴估夹饿靖鹰废齿颖呃限潮塔澈摩岳啡妾降莉范琴郭郎趁扮效佩仁a旋泡吉梨符爽姬馆柜撑赞哇萝蓠祸舟莹逐秒脉祈旦－咪丈丹季登摔祥抵m瑞昊互咐缺遭劳炎霜搬h恒婉浴茫尝腹斜戒溜针箱丰後阶喷词庆劝纹曼拔唱挤壮卓诡铜乌搂芯撇玲芳凑咽享卡猫贼嬷拨挖瞻霸庞昌炼训输鸟箭欠液葬苗泉旭彼冥郑毁谋藤研:泛撒嗓纵葛朱涩肃鸣瘦盒汪廷沁谅冢赖炸潇姊堪尬扇伏荷鞋耸井尴央授库侠佑拦盈亏酷赛票锋殷燃淑昂宴赌陶艺嫔咕毅煜裙积科捂砸诱轰涵勉延跌燕技窝抛辆逸缝吩脾糟绵霞嘲跃恍辞泄愕孝雄促驾瓜胁皆掏固抑涂灿泰企筑洒娟纠帘皓芸～踩操麦锐列丑骆寝刑铺孕昭妮阁罕愧枝融岂嫌氛宿翟稀货〓怡赤帆躯惠瞒嫩衫肌闯泣纱扣盼捉嫂诸倩疲哑供─诗罚乃征糕捧获煞黎裤怖铭熊述丧饶荒滋润澜踢慎伟弥奸录仓柯撕健谨措麼径忌劫倍俏笼泥炫率逗乡潜凛喉咧悟颇博询彦蹙誓省慧蒲趴妆肖伍乾夸典罩牧蹲峰悬雕A披例姚晰坦啪覆谎旅霆侯妍芙魄袍诧漆织辜咯抿催屏讽柴检损※奉绑末途蕾款勤F遮歪邵腕颈俞叮辣嫣蛮莞韵搜俗饮玛瞄尉嘟佣赐渴漓碍巾亭奖创鸿佟胳郡茹愁眠＂痒谦衡签O昧斥烫判烛版增祝批薰狱育截霍疾饱串莳仲绳寸刷摊卧湾贞婷樱瞥桑繁啾予凄州狸络啥慈链妥玫沾策膊逛岛奕访晌键祭裹详婴耍刹羊萍贪韦岚坠挽廊桐筋屑辱讯岸筒孟爵柱匙胎卑沿勒岩赢莱砰麽咦P奥磊夭於/鲁鄙幅翠割掀鹏眶哄赚编俯醋躁梳肆嚷蛊添寞卿迈献叛玻棒矩绣裸耻怯订捡麟穷拽暧裘盟啧减衬澡沫愉妒苒窜猎啸拐茉淋邀宅瓣沐蠢跨鬟揪倪趟协胃溢卦评旨鼎贱扁哟歹黛盆殊懿宸腐幼梓召钢樨冠寺钥掐婕疚尺契呈堵煮擎坟吕膛耗裡劈熠瑟鼠菱驶括锅瞎墅崇域馨灾肥骷髅坑噢腔枕叠畅恰裴砍篇漏C驳谣冯敛斩阑筱愚奏魏爪倏鹤灌侵寿姻冤吊绷灼惶矮兔旗淳崩膝销宾崔玥妲T频骄歇雀為哗绽苡乘咚棋菊丸瑰振揽拂裳塌呐捕租桥逢骇瞅缕涨N腻掠赔挨描蓦贤莎仗妄俱羡龄仆I袁黯轿艰唔K毓驰蔓u拧鞭瑜姜葵凰辩济疏窃翘媳刃丞糖冻逝嗦厢贾戈违泼吁B肠铲审疗熬拢益竖崖陛拭勃钰丛匕档匹陡腥构戚舅茵碌掘伪睿症汁弓逆娅倚畏曹嚣返偿渊咙挪×惩蹦申膳枯憋嫉揭肿蕴霉绫浸柄寄d筷枚噬摄患匪憾彤厂牲溪培睨粥兆搁吱伺佐污骚沟澹惫诅婶县庙烤f恬颠翅拆购禀洲弘津棍壶瞟舔漾阔媒嘱甫序玟刮娿绮媛隙桶桂禛弦琼懊帕汽撤耿溺叨驱镶琉榻植嘶嘀稚沦栋惚阅盾狈汇芝萨』狡剪攀『D砖蹭J芦孽辕坛虐栈叉吾茜贯均棉磁炉灏衷斑瓦朦骏哽鉴棠搅翩册寡瓷邦苑摘拎噜呻杆胧澄骥宏棵诊熏播狄悍玺躬寓钉肢寰镖脂睫矛填沧潘扩倦昶农飚昼帽誉溃葫伐卒函汹诈飙嗤X磕析巷盏挠劣辨龟恳堡窒渺妨奢械慨夷亿牺乳涟魁兼埃港炽绩珀涉喽泊倔讪擅豹阎翎萤罐卜梵彷囊蒂篷骤炮猴哆峻渗狭翌肺迪噗鸢乏栏歆胞枉剥核^荻悸瘫账沸宰籍兜薙嘎噷粒厮壳淫敞撼巡叙戳虹滞翰钧址绯栽jR芽珩耽Y页―Q鸭捷坡雁淌邻尧霎辅棘襟循禹焕聂寨稿邃撩涛噩E篮邑嘘呕燥嗽谱琢赋削蹄踹熄障朴饼革V璇眩忿蔡顽楞谜萼犀嬉垣粘毯皙觑援矿疤筹嚎蜡犬眷弧诀伞嗡垃圾绘遵酥冉扳诞侦嗳励庸债溅押贫硕抄【捶呛哧竣】郝兀栗啰恕烬斤驻玮昆携侃岗珑狮胀窘焚渔揍吭乍币衍凳嗅屹扒睹搓窄捣拱暇梭竭捞窥渡僧簪蓄妤遂垫迁宙薪碑狞咆碟哮雩梧蚁竞乙炀哨柏蝉蛛叩脊坤嗔拓俐督勺藉彬窟搐遣蜂L杏倘煎蝴廖岭桀逞蒋怦衅幺喵侣氓储羲缸裕塑桩乞囚璨胯旺H逮咸绸喧敷厕涯嬛蔽疆啤淹赴寅琦哩钏瑀潭搀絮膜邹绞粮炙匠贡剔#泳靳轨蔑楠珞兢炒晒衰澌崎啃迭敭叽焱腮冽傍v昵杖缚驿框酬霖嚼鹅茂闺踱祷浇坊焉偎霏讳茅党沌扛咋搏肝垮喻毋雍狰儒苹瘩挫疙侄颓褪鸦瞠喇讥淼孜滩椁悴惕黏骸憔唬鞠辽淮揣侮姆卸陋豁沮蔷逊跺妓舰蓬鹿呸泓嵌巳暮镯芬栖郊勋'

def _textsummary(path):
    result = ''
    with open(path,'rb') as f:
        r = f.read(100)
    encoding = guessencoding(r)
    result = str(r, encoding, 'ignore')
    return (result, )

def guessencoding(text):
    maxcommon = 0
    result = 'utf8'
    for encoding in 'utf8','gbk','utf16','utf32','big5':
        a = str(text, encoding, 'ignore')
        commoncount = 0
        for e in a:
            if e in commonchar:
                commoncount += 1
        if maxcommon < commoncount:
            maxcommon = commoncount
            result = encoding
    return result

def _archivesummary(archivetype, filename, depthlimit):
    if depthlimit > 0:
        with tempdir('histo-') as temp:
            error = None
            try:
                _extractarchive(archivetype, filename, temp)
            except _extracterror as e:
                error = repr(e)
                print('warning:', repr(e))
            return _foldersummary(temp,depthlimit), (archivetype, error)
    return (None,)

def _extractarchive(type, filename, target):
    p7zcommand = ['7z', 'x', filename, '-o', target]
    rarcommand = ['rar', 'x', filename, '-p-', target+'/']
    tarcommand = ['tar', '-xf', filename, '-C', target]
    zipcommand = ['unzip', '-P', '123456', filename, '-d', target]
    winrarcommand = ['winrar', '-ibck', '-p-', 'x', filename, target+'/']
    linuxcommand = {'rar': rarcommand,
                   'tar': tarcommand,
                   'zip': zipcommand}
    wincommand = {'rar': winrarcommand,
                  'tar': winrarcommand,
                  'zip': winrarcommand}
    command = {'win32': wincommand, 'linux2': linuxcommand}
    command = command[os.sys.platform]
    command = command[type]
    rarmessage = {1: 'warning',
                  2: 'fatal error',
                  3: 'CRC fail',
                  4: 'locked archive',
                  5: 'write file error',
                  6: 'open file error',
                  7: 'user error',
                  8: 'not enough memory',
                  9: 'create file error',
                  10: 'no input file',
                  255: 'user abort'}
    tarmessage = {1: 'error occurs',
                  2: 'no input file'}
    zipmessage = {1: 'warning',
                  2: 'generic format error',
                  3: 'severe format error',
                  4: 'not enough memory at startup',
                  5: 'fail read password',
                  6: 'not enough memory during disk decompression',
                  7: 'not enough memory during in-memory decompression',
                  9: 'no input file',
                  10: 'invalid option',
                  11: 'no input file because no matching files found',
                  80: 'aborted',
                  81: 'unsupport compression method',
                  82: 'bad password'}
    linuxmessage = {'rar': rarmessage,
                   'tar': tarmessage,
                   'zip': zipmessage}
    winmessage = {'rar': rarmessage,
                  'tar': rarmessage,
                  'zip': rarmessage}
    message = {'win32': winmessage, 'linux2': linuxmessage}
    message = message[os.sys.platform]
    proc = Popen(command, stdin = None, stderr = STDOUT, stdout = PIPE)
    while True:
        try:
            proc.communicate()
        except ValueError:
            break
    exitcode = proc.wait()
    if exitcode:
        message = message[type]
        if exitcode in message.keys():
            message = message[exitcode]
        else:
            message = 'unknown exitcode {}'.format(exitcode)
        raise _extracterror(message)

class _extracterror(OSError):
    def __repr__(self):
        return 'extracterror({})'.format(repr(self.args[0]))