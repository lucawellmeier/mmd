function! InlineAndBlockMath()
    syn keyword math_text PROPOSITION LEMMA THEOREM COROLLARY PROOF
    syn region inline_math start=/\$/ end=/\$/
	syn region inline_math start=/\\(/ end=/\\)/
	syn region display_math start=/\$\$/ end=/\$\$/
	syn region display_math start=/\\\[/ end=/\\\]/

    hi link math_text Keyword
	hi link inline_math Function
	hi link display_math Function
endfunction

au BufRead,BufNewFile *.mmd setfiletype markdown
autocmd BufRead,BufNewFile,BufEnter *.mmd call InlineAndBlockMath()
autocmd BufRead,BufNewFile,BufEnter *.mmd nnoremap <F1> :w \| !python -m mmd % <CR>
autocmd BufRead,BufNewFile,BufEnter *.mmd nnoremap <F2> :w \| !detach surf %:r.html <CR>
