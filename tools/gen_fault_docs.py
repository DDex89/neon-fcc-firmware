#!/usr/bin/env python3
"""Generate the fault code reference (docs/en|ru/fault_codes.md) from the
fault descriptors at $D4E3 in each ROM image.

Descriptor layout (8 bytes, index*8 + $D4E3):
  +0 fault index            +1 maturing count (1 = at once)
  +2 flash code (BCD)       +3 flags
  +4 bit mask, +5 byte offset into the fault bitmap at $0135
  +6..7 OBD-II code in BCD (0000 = none)
Flags: bit7 enabled, bit6 emission related (freeze frame, DTC count),
bit5 sets $0070 bit7 (lamp request), bit4 always use the maturing counter,
bit3 store at once, bits0-2 freeze frame priority.

Usage: python3 tools/gen_fault_docs.py --roms roms
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = 0x1200
FIRST, COUNT = 0xD4E3, 160

# OBD-II code titles (SAE J2012 generic codes, Chrysler P1xxx codes).
PCODE = {
    "P0107": ("MAP sensor voltage low", "Напряжение датчика MAP низкое"),
    "P0108": ("MAP sensor voltage high", "Напряжение датчика MAP высокое"),
    "P0112": ("Intake air temperature sensor voltage low", "Напряжение датчика температуры воздуха низкое"),
    "P0113": ("Intake air temperature sensor voltage high", "Напряжение датчика температуры воздуха высокое"),
    "P0117": ("Coolant temperature sensor voltage low", "Напряжение датчика температуры ОЖ низкое"),
    "P0118": ("Coolant temperature sensor voltage high", "Напряжение датчика температуры ОЖ высокое"),
    "P0121": ("TPS voltage does not agree with MAP", "Сигнал TPS не согласуется с MAP"),
    "P0122": ("TPS voltage low", "Напряжение TPS низкое"),
    "P0123": ("TPS voltage high", "Напряжение TPS высокое"),
    "P0125": ("Closed-loop temperature not reached", "Не достигнута температура замкнутого контура"),
    "P0132": ("Upstream O2 sensor shorted to voltage", "Передний датчик O2: замыкание на питание"),
    "P0133": ("Upstream O2 sensor slow response", "Передний датчик O2: медленный отклик"),
    "P0134": ("Upstream O2 sensor stays at center", "Передний датчик O2: нет активности"),
    "P0135": ("Upstream O2 sensor heater failure", "Нагреватель переднего датчика O2"),
    "P0138": ("Downstream O2 sensor shorted to voltage", "Задний датчик O2: замыкание на питание"),
    "P0139": ("Downstream O2 sensor slow response", "Задний датчик O2: медленный отклик"),
    "P0141": ("Downstream O2 sensor heater failure", "Нагреватель заднего датчика O2"),
    "P0152": ("Bank 2 O2 sensor shorted to voltage", "Датчик O2 второго ряда: замыкание на питание"),
    "P0153": ("Bank 2 O2 sensor slow response", "Датчик O2 второго ряда: медленный отклик"),
    "P0154": ("Bank 2 O2 sensor stays at center", "Датчик O2 второго ряда: нет активности"),
    "P0155": ("Bank 2 O2 sensor heater failure", "Нагреватель датчика O2 второго ряда"),
    "P0159": ("Bank 2 downstream O2 sensor slow response", "Задний датчик O2 второго ряда: медленный отклик"),
    "P0161": ("Bank 2 downstream O2 sensor heater failure", "Нагреватель заднего датчика O2 второго ряда"),
    "P0171": ("Fuel system lean", "Топливная система: бедная смесь"),
    "P0172": ("Fuel system rich", "Топливная система: богатая смесь"),
    "P0174": ("Fuel system lean, bank 2", "Бедная смесь, второй ряд"),
    "P0175": ("Fuel system rich, bank 2", "Богатая смесь, второй ряд"),
    "P0176": ("Fuel composition (flex fuel) sensor circuit", "Цепь датчика состава топлива (flex fuel)"),
    "P0178": ("Fuel composition sensor voltage low", "Напряжение датчика состава топлива низкое"),
    "P0179": ("Fuel composition sensor voltage high", "Напряжение датчика состава топлива высокое"),
    "P0182": ("Fuel temperature sensor voltage low", "Напряжение датчика температуры топлива низкое"),
    "P0183": ("Fuel temperature sensor voltage high", "Напряжение датчика температуры топлива высокое"),
    "P0300": ("Random misfire", "Случайные пропуски зажигания"),
    "P0325": ("Knock sensor 1 circuit", "Цепь датчика детонации 1"),
    "P0330": ("Knock sensor 2 circuit", "Цепь датчика детонации 2"),
    "P0335": ("Crankshaft position sensor circuit", "Цепь датчика положения коленвала"),
    "P0340": ("Camshaft position sensor circuit", "Цепь датчика положения распредвала"),
    "P0401": ("EGR system: insufficient flow", "Система EGR: недостаточный расход"),
    "P0403": ("EGR solenoid circuit", "Цепь соленоида EGR"),
    "P0411": ("Secondary air: incorrect flow", "Вторичный воздух: неверный расход"),
    "P0412": ("Secondary air switching solenoid circuit", "Цепь соленоида вторичного воздуха"),
    "P0422": ("Catalyst efficiency below threshold", "Эффективность катализатора ниже порога"),
    "P0441": ("EVAP purge flow", "Расход продувки EVAP"),
    "P0443": ("EVAP purge solenoid circuit", "Цепь соленоида продувки EVAP"),
    "P0500": ("Vehicle speed sensor", "Датчик скорости автомобиля"),
    "P0505": ("Idle air control motor circuits", "Цепи мотора РХХ"),
    "P0551": ("Power steering pressure switch", "Датчик давления ГУР"),
    "P0605": ("Internal controller failure", "Внутренняя неисправность контроллера"),
    "P0712": ("Transmission fluid temperature sensor voltage low", "Датчик температуры масла АКПП: низкое напряжение"),
    "P0713": ("Transmission fluid temperature sensor voltage high", "Датчик температуры масла АКПП: высокое напряжение"),
    "P0740": ("Torque converter clutch system", "Система блокировки гидротрансформатора"),
    "P0743": ("Torque converter clutch solenoid circuit", "Цепь соленоида блокировки гидротрансформатора"),
    "P0750": ("Shift solenoid A (overdrive) circuit", "Цепь соленоида переключения A (овердрайв)"),
    "P1292": ("CNG pressure sensor voltage high", "Датчик давления газа (CNG): высокое напряжение"),
    "P1293": ("CNG pressure sensor voltage low", "Датчик давления газа (CNG): низкое напряжение"),
    "P1294": ("Target idle speed not reached", "Не достигнуты целевые обороты ХХ"),
    "P1297": ("No change in MAP from start to run", "Нет изменения MAP при переходе от пуска к работе"),
    "P1299": ("Vacuum leak detected", "Обнаружен подсос воздуха"),
    "P1390": ("Timing belt skipped a tooth or more", "Ремень ГРМ перескочил на зуб или больше"),
    "P1391": ("Intermittent loss of cam or crank signal", "Пропадание сигнала распредвала или коленвала"),
    "P1489": ("High speed fan relay circuit", "Цепь реле вентилятора, высокая скорость"),
    "P1490": ("Low speed fan relay circuit", "Цепь реле вентилятора, низкая скорость"),
    "P1491": ("Radiator fan relay circuit", "Цепь реле вентилятора радиатора"),
    "P1698": ("No CCD messages from the transmission controller", "Нет сообщений CCD от контроллера АКПП"),
    "P1899": ("Park/neutral switch stuck", "Выключатель P/N залип"),
}
for c in range(1, 11):
    PCODE["P02%02d" % c] = ("Injector %d control circuit" % c, "Цепь управления форсункой %d" % c)
for c in range(1, 5):
    PCODE["P030%d" % c] = ("Cylinder %d misfire" % c, "Пропуски зажигания в цилиндре %d" % c)
for c, l in zip(range(1, 6), "ABCDE"):
    PCODE["P035%d" % c] = ("Ignition coil %s primary circuit" % l, "Первичная цепь катушки %s" % l)

# Chrysler flash code titles (key-on-off-on blink codes, SBEC era).
FLASH = {
    0x11: ("No crank reference / timing", "Нет опорного сигнала коленвала / фаза"),
    0x12: ("Battery disconnected (memory lost)", "Отключался аккумулятор (память сброшена)"),
    0x13: ("MAP: no change in vacuum", "MAP: нет изменения разрежения"),
    0x14: ("MAP sensor voltage", "Напряжение датчика MAP"),
    0x15: ("Vehicle speed signal", "Сигнал скорости"),
    0x16: ("Knock sensor", "Датчик детонации"),
    0x17: ("Engine too cold too long", "Мотор слишком долго холодный"),
    0x21: ("O2 sensor", "Датчик O2"),
    0x22: ("Coolant temperature sensor", "Датчик температуры ОЖ"),
    0x23: ("Air temperature sensor", "Датчик температуры воздуха"),
    0x24: ("Throttle position sensor", "Датчик положения дросселя"),
    0x25: ("Idle air control", "Регулятор холостого хода"),
    0x26: ("Injector peak current", "Пиковый ток форсунок"),
    0x27: ("Injector control circuit", "Цепь управления форсунками"),
    0x31: ("EVAP purge", "Продувка EVAP"),
    0x32: ("EGR", "EGR"),
    0x33: ("A/C clutch relay", "Реле муфты кондиционера"),
    0x34: ("Speed control", "Круиз-контроль"),
    0x35: ("Radiator fan relay", "Реле вентилятора"),
    0x37: ("Transmission (PTU / TCC, temperature)", "АКПП (PTU / TCC, температура)"),
    0x41: ("Generator field", "Обмотка возбуждения генератора"),
    0x42: ("ASD relay / supply", "Реле ASD / питание"),
    0x43: ("Ignition coil / misfire", "Катушка зажигания / пропуски"),
    0x44: ("Battery temperature sensor", "Датчик температуры аккумулятора"),
    0x45: ("Overboost / overdrive", "Перенаддув / овердрайв"),
    0x46: ("Charging voltage high", "Напряжение зарядки высокое"),
    0x47: ("Charging voltage low", "Напряжение зарядки низкое"),
    0x51: ("Fuel system lean", "Бедная смесь"),
    0x52: ("Fuel system rich", "Богатая смесь"),
    0x53: ("Internal controller failure", "Внутренняя неисправность контроллера"),
    0x54: ("Camshaft sync signal", "Сигнал синхронизации распредвала"),
    0x61: ("Baro read solenoid", "Соленоид замера барометрического давления"),
    0x62: ("Emission maintenance reminder mileage", "Пробег напоминателя ТО"),
    0x63: ("EEPROM write failure", "Ошибка записи EEPROM"),
    0x64: ("Catalyst / fuel sensors", "Катализатор / датчики топлива"),
    0x65: ("Power steering switch", "Выключатель ГУР"),
    0x66: ("No CCD bus messages", "Нет сообщений шины CCD"),
    0x76: ("Fuel pump resistor bypass relay", "Реле шунта резистора бензонасоса"),
    0x77: ("Speed control relay", "Реле круиз-контроля"),
}

T = {
    "en": dict(
        title="Fault codes",
        intro=("Generated by `tools/gen_fault_docs.py` from the fault descriptors at `$D4E3` "
               "(160 entries of 8 bytes, index × 8 + $D4E3). Do not edit by hand."),
        layout="Descriptor layout",
        lay_rows=[("+0", "Fault index (0-159)"),
                  ("+1", "Maturing count: how many failed tests before the fault is stored (1 = at once)"),
                  ("+2", "Chrysler flash code, BCD"),
                  ("+3", "Flags, see below"),
                  ("+4, +5", "Bit mask and byte offset of the fault bit in the bitmap at `$0135`"),
                  ("+6, +7", "OBD-II code in BCD, for example `01 22` = P0122; `00 00` = none")],
        flags="Flags (byte +3)",
        flag_rows=[("7", "Fault enabled. When clear, `ThrowNonCriticalError` returns without storing anything", "[code]"),
                   ("6", "Emission related: counted in `$010D` (number of OBD-II codes) and captures a freeze frame", "[code]"),
                   ("5", "Sets `$0070` bit 7, which the lamp logic (`CheckIfCheckEngineLightShouldBeOn_A_MM`) reads. Set only on charging-system faults, so probably the charge indicator lamp", "[inferred]"),
                   ("4", "Always go through the maturing counter", "[code]"),
                   ("3", "Store at once, without the maturing counter", "[code]"),
                   ("0-2", "Freeze frame priority: a higher value overwrites a stored frame", "[code]")],
        storage="How faults are stored",
        storage_text=(
            "`ThrowNonCriticalError` ($5B0A) takes the descriptor address in Y. A fault that is not stored at "
            "once uses one of two maturing slots (`$0054`/`$0055`, counters at `$0056`/`$0057`) and is stored "
            "when the counter reaches byte +1. A stored fault sets its bit in the bitmap at `$0135` and is "
            "pushed into the list of the last eight stored faults at `$001B`-`$0022` (most recent at "
            "`$0022`), which the DRB reads with command `$10`. The key-on counters at `$0023`-`$0025` age "
            "old codes out.\n\n"
            "An emission-related fault also captures a **freeze frame** at `$011E`-`$0126` "
            "(`CaptureFreezeFrame`, $EC86): fault index, load, coolant, short-term and adaptive fuel trim, "
            "RPM, vehicle speed and two more values. `LECD7` later compares the current RPM and MAP with "
            "the frame (the OBD-II \"similar conditions\" check). Together with the ISO 9141 routines this "
            "means the 1995 FCC already carries most of the OBD-II machinery."),
        variants="Differences between the images",
        table="Descriptor table",
        cols="| # | Addr | Flash | OBD-II | Meaning | Enabled | Flags | Count | Bit | Reported by |",
        yes="yes", no="—",
        legend=("**Enabled** is for 5269718; a different value in 5007033 is shown after a slash. "
                "**Meaning** comes from the OBD-II code when there is one, otherwise from the flash code "
                "(*italic*). **Reported by** lists the routines that load this descriptor directly; many "
                "descriptors are reached through an index (index × 8 + $D4E3) and show none."),
        note_53=("**Checksum (code 53).** In both images descriptor 2, which `CaculateChecksum` reports, has "
                 "the enable bit clear, so a checksum mismatch is not stored at all. In the factory B559 images "
                 "(table at $D4E9) it is enabled, so keep fixing the sum after edits."),
        diff_none="none",
    ),
    "ru": dict(
        title="Коды ошибок",
        intro=("Генерируется `tools/gen_fault_docs.py` из дескрипторов ошибок по адресу `$D4E3` "
               "(160 записей по 8 байт, индекс × 8 + $D4E3). Не редактируйте вручную."),
        layout="Формат дескриптора",
        lay_rows=[("+0", "Индекс ошибки (0-159)"),
                  ("+1", "Счётчик созревания: сколько неудачных проверок до записи кода (1 = сразу)"),
                  ("+2", "Мигающий код Chrysler, BCD"),
                  ("+3", "Флаги, см. ниже"),
                  ("+4, +5", "Маска и смещение байта бита ошибки в битовой карте `$0135`"),
                  ("+6, +7", "Код OBD-II в BCD, например `01 22` = P0122; `00 00` — нет")],
        flags="Флаги (байт +3)",
        flag_rows=[("7", "Ошибка включена. Если бит сброшен, `ThrowNonCriticalError` выходит, ничего не записав", "[код]"),
                   ("6", "Влияет на токсичность: учитывается в `$010D` (число кодов OBD-II) и сохраняет стоп-кадр", "[код]"),
                   ("5", "Ставит бит 7 в `$0070`, который читает логика лампы (`CheckIfCheckEngineLightShouldBeOn_A_MM`). Стоит только у ошибок зарядки, так что, вероятно, это лампа зарядки", "[выведено]"),
                   ("4", "Всегда проходить через счётчик созревания", "[код]"),
                   ("3", "Записать сразу, без счётчика", "[код]"),
                   ("0-2", "Приоритет стоп-кадра: больший перезаписывает сохранённый", "[код]")],
        storage="Как сохраняются ошибки",
        storage_text=(
            "`ThrowNonCriticalError` ($5B0A) получает адрес дескриптора в Y. Ошибка, которая не пишется "
            "сразу, занимает один из двух слотов созревания (`$0054`/`$0055`, счётчики `$0056`/`$0057`) и "
            "записывается, когда счётчик дойдёт до байта +1. Записанная ошибка ставит свой бит в карте "
            "`$0135` и попадает в список восьми последних кодов `$001B`-`$0022` (последний — `$0022`), "
            "который DRB читает командой `$10`. Счётчики включений зажигания `$0023`-`$0025` стирают "
            "старые коды.\n\n"
            "Ошибка, влияющая на токсичность, сохраняет ещё и **стоп-кадр** в `$011E`-`$0126` "
            "(`CaptureFreezeFrame`, $EC86): индекс ошибки, нагрузку, температуру ОЖ, кратковременную и "
            "адаптивную коррекцию топлива, обороты, скорость и ещё два значения. `LECD7` потом сравнивает "
            "текущие обороты и MAP с кадром (проверка OBD-II «схожих условий»). Вместе с подпрограммами "
            "ISO 9141 это значит, что FCC 1995 года уже несёт большую часть механики OBD-II."),
        variants="Различия между образами",
        table="Таблица дескрипторов",
        cols="| # | Адрес | Мигающий | OBD-II | Значение | Включена | Флаги | Счёт | Бит | Кто сообщает |",
        yes="да", no="—",
        legend=("**Включена** — для 5269718; другое значение в 5007033 показано через косую черту. "
                "**Значение** взято из кода OBD-II, если он есть, иначе из мигающего кода (*курсив*). "
                "**Кто сообщает** — подпрограммы, которые загружают дескриптор напрямую; многие "
                "дескрипторы выбираются по индексу (индекс × 8 + $D4E3), и для них поле пустое."),
        note_53=("**Контрольная сумма (код 53).** В обоих образах у дескриптора 2, который сообщает "
                 "`CaculateChecksum`, сброшен бит включения, так что несовпадение суммы вообще не "
                 "записывается. В заводских образах B559 (таблица по адресу $D4E9) он включён, поэтому сумму "
                 "после правок всё равно подгоняйте."),
        diff_none="нет",
    ),
}


def descriptors(img):
    out = []
    for i in range(COUNT):
        a = FIRST + i * 8
        out.append((a, img[a - BASE:a - BASE + 8]))
    return out


def reporters():
    """Routines that load a descriptor address directly (ldy/ldx/cpy #imm)."""
    import re, bisect, collections
    sys.path.insert(0, HERE)
    from gen_source import Gen
    from fccdis import Rom
    g = Gen(Rom(os.path.join(ROOT, "roms", "5269718.bin")))
    g.analyse()
    ents = sorted(a for a, n in g.names.items()
                  if a in g.an.insn and not re.match(r'^L[0-9A-F]{4}$', n))
    want = set(range(FIRST, FIRST + COUNT * 8, 8))
    x = collections.defaultdict(set)
    for a, i in g.an.insn.items():
        if not i.mn.startswith(("ld", "cp")):
            continue
        for op in i.ops:
            if op[0] == "imm" and op[1] in want:
                x[op[1]].add(g.names[ents[bisect.bisect_right(ents, a) - 1]])
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roms", default=os.path.join(ROOT, "roms"))
    args = ap.parse_args()
    imgs = {pn: open(os.path.join(args.roms, pn + ".bin"), "rb").read()
            for pn in ("5269718", "5007033")}
    da, db = descriptors(imgs["5269718"]), descriptors(imgs["5007033"])
    rep = reporters()
    for lang, t in T.items():
        L = 0 if lang == "en" else 1
        o = ["# " + t["title"], "", t["intro"], "", "## " + t["layout"], "",
             "| Byte | |", "|---|---|"]
        o += ["| %s | %s |" % r for r in t["lay_rows"]]
        o += ["", "## " + t["flags"], "", "| Bit | | |", "|---|---|---|"]
        o += ["| %s | %s | %s |" % r for r in t["flag_rows"]]
        o += ["", "## " + t["storage"], "", t["storage_text"], "", t["note_53"], "",
              "## " + t["variants"], ""]
        diffs = [(a, x, y) for (a, x), (_, y) in zip(da, db) if x != y]
        if not diffs:
            o.append(t["diff_none"])
        for a, x, y in diffs:
            o.append("- `$%04X` (#%d): `%s` → `%s` (5269718 → 5007033)" % (a, x[0], x.hex(" "), y.hex(" ")))
        o += ["", "## " + t["table"], "", t["legend"], "", t["cols"],
              "|---|---|---|---|---|---|---|---|---|---|"]
        for (a, d), (_, e) in zip(da, db):
            if d[2] == 0 and d[6] == 0 and d[7] == 0:
                continue
            pc = "P%02X%02X" % (d[6], d[7]) if (d[6] or d[7]) else ""
            if pc in PCODE:
                mean = PCODE[pc][L]
            elif d[2] in FLASH:
                mean = "*%s*" % FLASH[d[2]][L]
            else:
                mean = ""
            en = t["yes"] if d[3] & 0x80 else t["no"]
            if (d[3] & 0x80) != (e[3] & 0x80):
                en += " / " + (t["yes"] if e[3] & 0x80 else t["no"])
            fl = []
            for b, s in ((6, "E"), (5, "L"), (4, "C"), (3, "I")):
                if d[3] & (1 << b):
                    fl.append(s)
            if d[3] & 7:
                fl.append("P%d" % (d[3] & 7))
            flags = "`%02X` %s" % (d[3], " ".join(fl))
            bit = "%02X.%d" % (d[5], d[4].bit_length() - 1) if d[4] else ""
            who = ", ".join("`%s`" % n for n in sorted(rep.get(a, ())))
            o.append("| %d | `$%04X` | %X | %s | %s | %s | %s | %d | %s | %s |" % (
                d[0], a, d[2], pc, mean, en, flags, d[1], bit, who))
        o += ["", ("Flags column: E emission, L lamp request, C counter, I immediate, P freeze frame priority. "
                   "Bit column: byte offset in `$0135` and bit number.") if lang == "en" else
              ("Столбец флагов: E токсичность, L запрос лампы, C счётчик, I сразу, P приоритет стоп-кадра. "
               "Столбец бита: смещение байта в `$0135` и номер бита."), ""]
        path = os.path.join(ROOT, "docs", lang, "fault_codes.md")
        open(path, "w", encoding="utf-8").write("\n".join(o))
        print("wrote", path)


if __name__ == "__main__":
    main()
