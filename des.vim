" Vim syntax file for NetHack DES file format

if exists("b:current_syntax")
  finish
endif

" various des declarations
" level specifiers...
syn keyword desDirective MAZE LEVEL FLAGS INIT_MAP GEOMETRY NOMAP
" terrain features...
syn keyword desDirective ALTAR SINK TREE THRONE STAIR DOOR ROOMDOOR DRAWBRIDGE
syn keyword desDirective LADDER FOUNTAIN POOL GRAVE
" things on the level...
syn keyword desDirective OBJECT MONSTER CONTAINER TRAP PORTAL GOLD ENGRAVING
" LEVEL-type specific things...
syn keyword desDirective ROOM SUBROOM CORRIDOR RANDOM_CORRIDORS
" terrain commands...
syn keyword desDirective TERRAIN REPLACE_TERRAIN MAZEWALK WALLIFY MINERALIZE
" regions...
syn keyword desDirective REGION NON_DIGGABLE NON_PASSWALL TELEPORT_REGION BRANCH
" control statements...
syn keyword desStatement IF ELSE EXIT LOOP FOR TO SWITCH CASE BREAK DEFAULT FUNCTION SHUFFLE

" constants...
syn match desNumber '\d\+'      " basic numbers
syn match desNumber '\d\+%'     " percentage
syn match desNumber '[-+]\d\+'  " +n, -n, e.g. for spe
syn match desNumber '\d\+d\d\+' " dice notation, e.g. 2d6
syn match desVariable '\$[a-zA-Z_]\+'
syn region desString start='"' end='"'
syn region desChar start='\'' end='\''
syn region desMapBlock start="^MAP" end="^ENDMAP"
syn match desComment '#.*$'

let b:current_syntax = "des"
hi def link desComment    Comment
hi def link desDirective  Type
hi def link desNumber     Constant
hi def link desString     Constant
hi def link desChar       Constant
hi def link desVariable   Identifier
hi def link desStatement  Statement
hi def link desMapBlock   Special
