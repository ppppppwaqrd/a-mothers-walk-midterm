extends Node
## Player-facing copy. Thai is the default voice; English follows the same jokes.

signal language_changed

var lang: String = "th"

const TEXTS := {
	"th": {
		"menu_title": "กล่องข้าวน้อย",
		"menu_sub": "A Mother's Walk",
		"menu_new": "เริ่มเรื่องใหม่",
		"menu_continue": "เดินต่อจากเดิม",
		"menu_options": "ตั้งค่า",
		"menu_credits": "ผู้จัดทำ",
		"menu_quit": "ปิดสมุด",
		"opt_title": "ตั้งค่า",
		"opt_music": "เพลง",
		"opt_music_on": "เปิดเพลง",
		"opt_sfx": "เสียง",
		"opt_sfx_on": "เปิดเสียง",
		"opt_screen": "หน้าจอ",
		"opt_fullscreen": "เต็มจอ",
		"opt_lang": "ภาษา",
		"opt_back": "กลับ",
		"pause_title": "พักก่อนนะ",
		"pause_resume": "เดินต่อ",
		"pause_retry": "เดินช่วงนี้ใหม่",
		"pause_menu": "กลับหน้าปก",
		"hud_hp": "แม่",
		"hud_patience": "ไอ้ทอง",
		"hud_god": "โหมดซน",
		"toast_god": "โหมดซนอยู่ — กด F10 ถ้าจะเลิก",
		"toast_save": "จำหน้านี้ไว้แล้ว",
		"toast_villager": "ช่วยเขาแล้ว ไอ้ทองใจเย็นลงหน่อย",
		"toast_checkpoint": "ศาลนี้จำแม่ไว้แล้ว",
		"toast_bamboo": "กำแพงไผ่เลื่อนออกแล้ว",
		"toast_bridge": "สะพานยื่นมาแล้ว ข้ามได้",
		"toast_canal": "สะพานข้ามคูมาแล้ว",
		"toast_mini_win": "ศาลพยักหน้า ได้หินอีกสามก้อน ไอ้ทองหิวช้าลง",
		"toast_mini_lose": "สิ่งศักดิ์ไม่พอใจ... ไอ้ทองโมโหขึ้นมา!",
		"help": "ช่วย!",
		"chapter": "บทที่ %s",
		"level_skip": "แตะจอ หรือกดปุ่มอะไรก็ได้ ค่อยพลิกต่อ",
		"level_hint": "เก็บกระติบให้ครบแปดใบนะ อย่าให้ลูกหิวจนทนไม่ไหว",
		"lv1_title": "ออกจากหมู่บ้าน",
		"lv1_verse": "ฟ้ายังไม่สว่างดี แม่ก็ออกจากบ้านแล้ว\nกล่องข้าวยังอุ่นอยู่เลย",
		"lv2_title": "ป่าไผ่",
		"lv2_verse": "ป่าไผ่กรอบแกรบไปตามลม\nแดดสายส่องมาเป็นทาง",
		"lv3_title": "ทางขรุขระ",
		"lv3_verse": "เที่ยงแล้ว ดินลูกรังร้อนเท้า\nทางนี้สูงบ้างต่ำบ้าง อย่าพลาดขา",
		"lv4_title": "ทุ่งนากลางทาง",
		"lv4_verse": "ทุ่งนาเหลืองยาวตา\nกลิ่นข้าวในกล่องยังไม่จาง",
		"lv5_title": "คูน้ำกลางคืน",
		"lv5_verse": "มืดแล้ว คูน้ำดำสนิท\nอีกนิดก็ถึงลูก",
		"lv6_title": "ส่งกล่องให้อ้ายทอง",
		"lv6_verse": "แสงวันใกล้หมด\nกล่องนี้ต้องถึงมือไอ้ทองให้ได้",
		"shrine_crow_scare": "ศาลท้าวแฮก",
		"shrine_buffalo_herd": "ศาลพระภูมิ",
		"shrine_rice_guard": "ศาลพระแม่โพสพ",
		"mini_start": "เอาสิ",
		"mini_space": "หรือกด Space ก็ได้",
		"mini_mother": "แม่",
		"mini_crow_deity": "ท้าวแฮก ผู้เฝ้านา",
		"mini_crow_title": "ไล่อีกาออกจากนา",
		"mini_crow_story": "ท้าวแฮกขอดูหน่อย แม่ไล่นกกาทันมั้ย\nไล่พ้นทุ่ง ไอ้ทองจะหิวช้าลง\nไล่ไม่ทัน... ศาลจะเร่งท้องลูกให้ร้องดังขึ้น",
		"mini_crow_how": "A กับ D เดิน   J ปาหินขึ้นไปโดนอีกา   หินมีจำกัดนะ",
		"mini_crow_hard": "รอบนี้อีกาเยอะขึ้น เวลาก็สั้นลงด้วย",
		"mini_crow_play": "A / D เดิน    J ปาหินไล่อีกา",
		"mini_crow_ammo": "A / D เดิน    J ปาหิน    หิน x%d",
		"mini_crow_win": "ไล่ทันแล้ว ท้าวแฮกพยักหน้า",
		"mini_crow_lose": "ไล่ไม่ทัน... สิ่งศักดิ์ทำให้ไอ้ทองโมโห!!",
		"mini_buf_deity": "พระภูมิเจ้าที่",
		"mini_buf_title": "ขวางควายไว้ก่อน",
		"mini_buf_story": "พระภูมิขอให้แม่ขวางควาย อย่าให้ชนชาวบ้าน\nขวางไว้จนครบเวลา ไอ้ทองจะรอได้ต่อ\nถ้าควายพุ่งเข้าไป ศาลจะไม่ปล่อยผ่านง่าย ๆ",
		"mini_buf_how": "เดินทั่วลาน ยืนขวางทางควาย อย่าให้ชนชาวบ้านจนหมดเวลา",
		"mini_buf_play": "เดินขวางควาย อย่าให้ชนชาวบ้าน",
		"mini_buf_win": "ควายไม่ชนใคร พระภูมิพอใจ",
		"mini_buf_lose": "ขวางไม่ไหว... สิ่งศักดิ์ทำให้ไอ้ทองโมโห!!",
		"mini_rice_deity": "พระแม่โพสพ",
		"mini_rice_title": "เฝ้าข้าวตาก",
		"mini_rice_story": "พระแม่โพสพขอให้แม่ไล่ไก่ ไม่ให้คุ้ยข้าวตาก\nเฝ้าจนครบเวลา ไอ้ทองจะหิวช้าลง\nข้าวเละ ศาลจะเร่งท้องลูกทันที",
		"mini_rice_how": "A กับ D เดินชนไก่ ให้มันถอยออกจากเสื่อข้าว",
		"mini_rice_play": "A / D เดินชนไก่ให้ถอย",
		"mini_rice_win": "ข้าวรอด พระแม่โพสพยิ้ม",
		"mini_rice_lose": "ปกป้อง...ไม่สำเร็จ! สิ่งศักดิ์ทำให้ไอ้ทองโมโห!!",
		"over_hunger_title": "ไอ้ทองรอไม่ไหว",
		"over_hunger_line": "แม่ยังไปไม่ถึง\nท้องลูกว่างเปล่าก่อนแม่จะถึง",
		"over_fall_title": "ข้าวหล่นกลางทาง",
		"over_fall_line": "แม่ล้มก่อนถึงลูก\nแต่พลิกหน้ากลับมาเดินใหม่ได้นะ",
		"win_good_title": "ถึงมือแล้ว",
		"win_good_line": "กล่องยังอุ่นอยู่ดี\nแม่วางลงข้างลูก แค่นี้ก็พอแล้ว",
		"win_ok_title": "ถึงแล้ว… แต่ข้าวน้อยไป",
		"win_ok_line": "เดินมาไกลขนาดนี้ แต่กระติบไม่ครบ\nไอ้ทองยังทำหน้าหิวอยู่",
		"kratib_count": "กระติบ %d จาก %d",
		"over_retry": "เดินใหม่จากศาลล่าสุด",
		"over_menu": "กลับหน้าปก",
		"win_retry": "เริ่มเรื่องใหม่",
		"win_menu": "ปิดสมุด",
		"credit_title": "ผู้จัดทำ",
		"credit_group": "กลุ่มที่ 4  —  ปัญญาประดิษฐ์ ตอนที่ 1",
		"credit_course": "วิชา Computer Game Development\nวิทยาลัยการคอมพิวเตอร์ มหาวิทยาลัยขอนแก่น",
		"credit_craft": "ภาพ กระเบื้อง เพลง และเสียง\nทำขึ้นสำหรับเรื่องนี้โดยเฉพาะ",
		"credit_colophon": "กล่องข้าวน้อย  ·  A Mother's Walk",
		"story_folio": "แผ่น %d จาก %d",
		"story_next": "พลิกต่อ",
		"story_begin": "ออกเดิน",
		"story_prev": "หน้าก่อน",
		"story_skip": "ข้ามไปเดินเลย",
		"s1_ch": "กล่องข้าวน้อย",
		"s1_title": "กาลครั้งหนึ่ง",
		"s1_body": "แม่หุงข้าวเหนียวใส่กล่องใบน้อย\nจะเอาไปให้ลูกชาย ไอ้ทอง ที่รออยู่ปลายทาง\n\nท้องมันว่างเปล่า\nไม่มีใครคอยได้ทั้งวันหรอก",
		"s2_ch": "ทางที่ต้องเดิน",
		"s2_title": "จากบ้านถึงมือลูก",
		"s2_body": "ออกจากบ้าน ผ่านป่าไผ่ ทางขรุขระ ทุ่งนา\nแล้วก็คูน้ำตอนกลางคืน กว่าจะถึงมือไอ้ทอง\n\nหนามมี หอกมี สัตว์ป่ามี\nบางที่หินขวางทาง กระโดดอย่างเดียวไม่รอด",
		"s3_ch": "จะจบยังไง",
		"s3_title": "อย่าให้ลูกหิวเกินไป",
		"s3_body": "ส่งกล่องให้ถึงก่อนไอ้ทองหิวจนทนไม่ไหว\nแถบน้ำตาลนั่นลดเรื่อย ๆ หมดแล้วเรื่องจบ\n\nเก็บกระติบให้ครบแปดใบทั้งเรื่อง ลูกจะยิ้มได้\nเก็บไม่ครบ ก็ถึงได้ แต่ข้าวยังไม่พอ",
		"s4_ch": "เดินยังไง",
		"s4_title": "เท้ากับมือ",
		"s4_body": "A หรือ ลูกศรซ้าย — เดินซ้าย\nD หรือ ลูกศรขวา — เดินขวา\nSpace หรือ W — กระโดด\nJ — ปาหิน  (หินมีจำกัด ต้องเก็บเติม)\nEsc หรือ P — พักก่อน\n\nถ้าเล่นบนจอสัมผัส ปุ่มอยู่มุมล่าง",
		"s5_ch": "มุมบนกระดาษ",
		"s5_title": "ดูแถวนี้นะ",
		"s5_body": "หัวใจคือชีวิต หมดดวงนึง ตื่นที่ศาลเขียว\nหมดทุกดวง เรื่องจบ\n\nแถบเขียว คือแรงแม่\nแถบน้ำตาล คือความอดทนของไอ้ทอง\nตัวเลขกระติบ คือข้าวที่เก็บได้   หิน คือก้อนที่ปาได้",
		"s6_ch": "ของบนทาง",
		"s6_title": "ระวังขา",
		"s6_body": "งู หมูป่า ควาย นกกา — ปาหินได้ ควายกับหมูทนกว่า\nหนาม หอกไผ่ ลูกตุ้ม ใบมีด — อย่าไปเหยียบ\nตกคูน้ำแล้วจบ\n\nหินลูกรังดันทับสวิตช์ กำแพงหรือสะพานถึงจะเปิด\nศาลเขียวจำทางไว้  ศาลเทวดาขอให้ช่วยงานนิดหน่อย\nช่วยทัน ไอ้ทองหิวช้าลง   ช่วยไม่ทัน ลูกโมโหเร็วขึ้น",
	},
	"en": {
		"menu_title": "A Mother's Walk",
		"menu_sub": "กล่องข้าวน้อย",
		"menu_new": "Start a new story",
		"menu_continue": "Pick up where you left off",
		"menu_options": "Settings",
		"menu_credits": "Credits",
		"menu_quit": "Close the book",
		"opt_title": "Settings",
		"opt_music": "Music",
		"opt_music_on": "Music on",
		"opt_sfx": "Sounds",
		"opt_sfx_on": "Sounds on",
		"opt_screen": "Screen",
		"opt_fullscreen": "Fullscreen",
		"opt_lang": "Language",
		"opt_back": "Back",
		"pause_title": "Hold up",
		"pause_resume": "Keep going",
		"pause_retry": "Walk this stretch again",
		"pause_menu": "Back to the cover",
		"hud_hp": "Mae",
		"hud_patience": "Ai Tong",
		"hud_god": "Silly mode",
		"toast_god": "Silly mode on — F10 to drop it",
		"toast_save": "Got this page marked",
		"toast_villager": "You helped. Ai Tong can wait a bit.",
		"toast_checkpoint": "This shrine remembers you",
		"toast_bamboo": "The bamboo wall slid aside",
		"toast_bridge": "The plank's out. Cross it.",
		"toast_canal": "Bridge over the canal. Go on.",
		"toast_mini_win": "The shrine nods. Three more stones. Ai Tong eases up.",
		"toast_mini_lose": "The shrine's cross... Ai Tong's furious!",
		"help": "Help!",
		"chapter": "Chapter %s",
		"level_skip": "Tap or press a key to turn the page",
		"level_hint": "Grab eight baskets. Don't let the boy starve waiting.",
		"lv1_title": "Leaving the village",
		"lv1_verse": "Sky's still grey and she's already out the gate\nThe rice box is still warm",
		"lv2_title": "Bamboo woods",
		"lv2_verse": "Bamboo clicking in the wind\nLate-morning sun laying out a path",
		"lv3_title": "The rough road",
		"lv3_verse": "Noon on laterite. Hot on the feet\nUp, down — watch your step",
		"lv4_title": "The rice fields",
		"lv4_verse": "Gold paddies as far as you can see\nThe box still smells like lunch",
		"lv5_title": "Night canal",
		"lv5_verse": "Dark water. Almost there\nOne more push",
		"lv6_title": "Hand him the box",
		"lv6_verse": "Last light of the day\nThis box has to reach Ai Tong",
		"shrine_crow_scare": "Thao Haek's shrine",
		"shrine_buffalo_herd": "The land spirit's shrine",
		"shrine_rice_guard": "Mae Phosop's shrine",
		"mini_start": "Alright",
		"mini_space": "Or just hit Space",
		"mini_mother": "Mae",
		"mini_crow_deity": "Thao Haek, watcher of the fields",
		"mini_crow_title": "Chase the crows off the paddy",
		"mini_crow_story": "Thao Haek wants to see if you can clear the crows\nDo it and Ai Tong stays calmer\nMiss it... and the shrine winds up his hunger",
		"mini_crow_how": "A / D to move    J to throw stones up at the crows    stones are limited",
		"mini_crow_hard": "More crows this time, and less clock",
		"mini_crow_play": "A / D move    J throw",
		"mini_crow_ammo": "A / D move    J throw    stones x%d",
		"mini_crow_win": "Crows gone. Thao Haek nods.",
		"mini_crow_lose": "Couldn't keep the field... the shrine's made Ai Tong furious!!",
		"mini_buf_deity": "The land spirit",
		"mini_buf_title": "Keep the buffalo off the yard",
		"mini_buf_story": "Stand in the way. Don't let a buffalo hit anyone\nHold the line till time's up\nIf one gets through, the shrine won't be kind",
		"mini_buf_how": "Walk the yard. Block the buffalo. Nobody gets hit.",
		"mini_buf_play": "Block the buffalo. Don't let them hit anyone.",
		"mini_buf_win": "Nobody got hit. The spirit's pleased.",
		"mini_buf_lose": "Couldn't hold them... the shrine's made Ai Tong furious!!",
		"mini_rice_deity": "Mae Phosop",
		"mini_rice_title": "Guard the drying rice",
		"mini_rice_story": "Keep the chickens off the mats\nHold them back till time's up\nIf they wreck the rice, the shrine speeds up his hunger",
		"mini_rice_how": "A / D bump the chickens off the rice mats",
		"mini_rice_play": "A / D bump chickens back",
		"mini_rice_win": "Rice is safe. Mae Phosop smiles.",
		"mini_rice_lose": "Couldn't protect it... the shrine's made Ai Tong furious!!",
		"over_hunger_title": "Ai Tong couldn't wait",
		"over_hunger_line": "She didn't make it\nThe boy was too hungry to hold on",
		"over_fall_title": "Rice in the dirt",
		"over_fall_line": "She went down before she reached him\nYou can turn the page and walk it again",
		"win_good_title": "It reached him",
		"win_good_line": "The box is still warm\nShe sits down. That's enough.",
		"win_ok_title": "She got there… the rice didn't",
		"win_ok_line": "Long walk. Not enough baskets\nAi Tong's still looking hungry",
		"kratib_count": "Baskets %d of %d",
		"over_retry": "From the last shrine",
		"over_menu": "Back to the cover",
		"win_retry": "Start the story over",
		"win_menu": "Close the book",
		"credit_title": "Credits",
		"credit_group": "Group 4  —  AI, section 1",
		"credit_course": "Computer Game Development\nCollege of Computing, Khon Kaen University",
		"credit_craft": "Art, tiles, music, and sounds\nmade for this story",
		"credit_colophon": "กล่องข้าวน้อย  ·  A Mother's Walk",
		"story_folio": "Page %d of %d",
		"story_next": "Turn",
		"story_begin": "Start walking",
		"story_prev": "Back",
		"story_skip": "Skip to the walk",
		"s1_ch": "A Mother's Walk",
		"s1_title": "Once",
		"s1_body": "A mother packs sticky rice in a little box\nand sets out for her boy, Ai Tong, waiting at the far end\n\nHis stomach's empty.\nNobody can wait all day.",
		"s2_ch": "The road",
		"s2_title": "From home to his hands",
		"s2_body": "Village, bamboo, a rough track, the fields\nthen the canal at night, before the box hits his hands\n\nThorns, spears, animals\nSome spots a rock's in the way. Jumping won't cut it.",
		"s3_ch": "How it ends",
		"s3_title": "Don't let him starve waiting",
		"s3_body": "Get the box there before Ai Tong's bar runs out\nThat brown bar never stops. Empty means the story's over\n\nEight baskets the whole way and he smiles\nFewer than that, you arrive, but he's still hungry",
		"s4_ch": "How to walk",
		"s4_title": "Hands and feet",
		"s4_body": "A or Left — walk left\nD or Right — walk right\nSpace or W — jump\nJ — throw a stone  (limited; pick more up)\nEsc or P — pause\n\nOn a phone, use the buttons in the corner",
		"s5_ch": "The paper up top",
		"s5_title": "Watch this row",
		"s5_body": "Hearts are lives. Lose one, you wake at the green shrine\nLose them all, that's it\n\nGreen bar is Mae\nBrown bar is Ai Tong's patience\nThe basket count is rice  ·  stones are what you throw",
		"s6_ch": "What's on the path",
		"s6_title": "Watch your feet",
		"s6_body": "Snakes, boars, buffalo, crows — stones work. Boars and buffalo take more\nThorns, spears, pendulums, blades — don't step on them\nThe canal kills you\n\nShove laterite onto a switch to open a wall or a bridge\nGreen shrine saves  ·  spirit shrine asks a favour\nDo it in time, he waits  ·  fail it, he gets hungrier faster",
	},
}

const STORY_ART := [
	"res://Assets/Generated/Story/cover_menu.png",
	"res://Assets/Generated/Story/page_01.png",
	"res://Assets/Generated/Story/page_06.png",
	"res://Assets/Generated/Story/page_02.png",
	"res://Assets/Generated/Story/page_03.png",
	"res://Assets/Generated/Story/page_05.png",
]


func t(key: String) -> String:
	var table: Dictionary = TEXTS.get(lang, TEXTS["th"])
	if table.has(key):
		return str(table[key])
	return str(TEXTS["th"].get(key, key))


func tf(key: String, values: Array) -> String:
	return t(key) % values


func set_lang(code: String, persist: bool = true) -> void:
	if code != "en":
		code = "th"
	var changed := lang != code
	lang = code
	if changed:
		language_changed.emit()
	if persist and changed:
		GameManager.save_option()


func chapter_label(number: int) -> String:
	if lang == "en":
		return t("chapter") % str(number)
	var thai: Array[String] = ["", "๑", "๒", "๓", "๔", "๕", "๖"]
	var n: String = str(number)
	if number >= 0 and number < thai.size():
		n = thai[number]
	return t("chapter") % n


func story_pages() -> Array:
	var keys := [
		["s1_ch", "s1_title", "s1_body"],
		["s2_ch", "s2_title", "s2_body"],
		["s3_ch", "s3_title", "s3_body"],
		["s4_ch", "s4_title", "s4_body"],
		["s5_ch", "s5_title", "s5_body"],
		["s6_ch", "s6_title", "s6_body"],
	]
	var pages: Array = []
	for i in keys.size():
		pages.append({
			"chapter": t(keys[i][0]),
			"title": t(keys[i][1]),
			"body": t(keys[i][2]),
			"art": STORY_ART[i],
		})
	return pages


func mini_prefix(game_id: String) -> String:
	match game_id:
		"buffalo_herd":
			return "mini_buf"
		"rice_guard":
			return "mini_rice"
		_:
			return "mini_crow"
