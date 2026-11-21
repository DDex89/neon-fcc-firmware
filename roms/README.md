# ROM dumps / Дампы ПЗУ

ROM images are not part of this repository. You only need them to regenerate `src/` with
`tools/gen_source.py`; building and verifying works without them.

Образы ПЗУ в репозиторий не входят. Они нужны только для перегенерации `src/` через
`tools/gen_source.py`; сборка и проверка работают без них.

Put the 60,928-byte dumps (address range $1200-$FFFF) here, named by part number:
Положите сюда дампы размером 60 928 байт (адреса $1200-$FFFF) с именами по номеру детали:

| File / Файл | SHA-256 |
|---|---|
| `5269718.bin` | `db0b88190e14bdb86be18f655cd4b49d87675876aeb89dabfd47410c5669bab7` |
| `5007033.bin` | `12182bc24d611152e1d17195b11808677e1e73f528f8f4b8c4f97b3018c3bdc6` |

Source / Где взять: the "1995 Neon FCC" folder of the Turbonator release (BoostButton):
`5269718` is `jeffball718.bin` inside `jeffball718-*.zip`, `5007033` is `5007033.bin` inside
`5007033.zip`. A dump read from your own controller works as well if its hash matches.

Папка «1995 Neon FCC» в релизах Turbonator (BoostButton): `5269718` — это `jeffball718.bin` из
архива `jeffball718-*.zip`, `5007033` — `5007033.bin` из `5007033.zip`. Подойдёт и дамп, считанный
с собственного блока, если хеш совпадает.
