function! Pepgen(...)
	let log = ['++++']
	echom string(a:1)
	call add(log, string(a:000))
	" first call for column response
	if a:1 == 1
		echom getline('.')
		let line_words = split(getline('.'))
		if (len(line_words) > 0)
			echom line_words[-1]
"		let last_word_ind = strridx(getline('.'), " ")
"		call add(log, last_word_ind + 1)
			let b:pepgen_no_item = 0
			return col('.')
		else
			echom "no compl"
			let b:pepgen_no_item = 1
			return -1
		endif
"		call add(log, '----')
"		call writefile(log, '/tmp/pepgen.log')

	else " second call for word list
		if (b:pepgen_no_item == 1)
			return []
		else
			let ret_list = []
			let last_word = split(getline('.'))[-1]
			let cmd = printf("echo '%s' | nc localhost 1392", last_word)
			let sugg = split(system(cmd))
			if (len(sugg) > 0)
				for sug in sugg
					let ret_item = {}
					echom sug
					let dcol_idx = stridx(sug, ":")
					echom dcol_idx
					let ret_item.word = sug[0:str2nr(dcol_idx) - 1]
					let ret_item.menu = sug[str2nr(dcol_idx): strlen(sug)]
					call add(ret_list, ret_item)
				endfor
				return ret_list
			else
				return []
			endif

		endif
	endif
endfunction

set omnifunc=Pepgen

" au BufRead,BufNewFile *.txt set textwidth=60
